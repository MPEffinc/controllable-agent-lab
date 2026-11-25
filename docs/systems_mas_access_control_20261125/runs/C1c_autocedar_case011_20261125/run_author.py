#!/usr/bin/env python3
"""Run pinned AutoCedar author CLI with a bounded synthetic gold case."""

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "third_party/K06-autocedar"
CASE = SOURCE / "dataset/gold-reference-dataset/cases/case-011"
OLD_ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
PYTHON = OLD_ENV / "venv/bin/python"
CEDAR = OLD_ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
CVC5 = OLD_ENV / "cvc5"
SESSION = HERE / "session"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_key():
    path = ROOT / "local/progent-vm/.env"
    for line in path.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            key = line.partition("=")[2].strip().strip('"').strip("'")
            if key:
                return key
    raise RuntimeError("OPENAI_API_KEY unavailable")


for file in (PYTHON, CEDAR, CVC5, CASE / "requirement.md", CASE / "gold/schema.cedarschema"):
    if not file.is_file():
        raise RuntimeError(f"missing prerequisite: {file}")
if SESSION.exists():
    raise RuntimeError("session already exists; preserve raw run and use a new Run ID")

cmd = [
    str(PYTHON), "-c", "import sys, compat_adapter; from autocedar.cli import main; sys.exit(main())",
    "author", str(CASE / "requirement.md"), "--out", str(SESSION),
    "--session-id", "C1c_case011", "--schema", str(CASE / "gold/schema.cedarschema"),
    "--provider", "openai", "--model", "gpt-4.1-mini-2025-04-14",
    "--model-review", "--review-provider", "openai",
    "--review-model", "gpt-4.1-mini-2025-04-14",
    "--max-schema-gap-repairs", "0", "--max-map-rounds", "1", "--max-proposals", "16",
]
env = os.environ.copy()
env.update({
    "PYTHONPATH": str(HERE) + os.pathsep + str(SOURCE), "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
    "CEDAR": str(CEDAR), "CVC5": str(CVC5), "OPENAI_API_KEY": load_key(),
})
start = time.monotonic()
try:
    result = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True,
                            text=True, timeout=240, check=False)
    code, stdout, stderr = result.returncode, result.stdout, result.stderr
except subprocess.TimeoutExpired as exc:
    code = 124
    stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
    stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")

(HERE / "stdout.txt").write_text(stdout)
(HERE / "stderr.txt").write_text(stderr)
(HERE / "run_meta.json").write_text(json.dumps({
    "command": cmd, "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
    "case_requirement_sha256": sha(CASE / "requirement.md"),
    "gold_schema_sha256": sha(CASE / "gold/schema.cedarschema"),
    "cedar_sha256": sha(CEDAR), "cvc5_sha256": sha(CVC5),
    "model": "gpt-4.1-mini-2025-04-14", "adapter_patch": "omit reasoning; prompt JSON and locally validate output type", "seed": "NOT_SET_BY_CLI",
    "temperature": "NOT_SET_BY_CLI", "exit_code": code,
    "elapsed_seconds": round(time.monotonic() - start, 3),
}, indent=2) + "\n")
print(f"C1c author exit={code}; elapsed={time.monotonic()-start:.1f}s")
