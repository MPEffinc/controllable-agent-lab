"""Run the pinned AutoCedar CLI verifier without any model-provider command."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
SOURCE = ROOT / "third_party" / "K06-autocedar"
ENV = RUN / "env"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu" / "cedar"
CVC5 = ENV / "cvc5"
PYTHON = ENV / "venv" / "bin" / "python"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: run_verify.py INPUT_DIR LABEL")
    workspace = Path(sys.argv[1]).resolve()
    label = sys.argv[2]
    if not label.replace("_", "").isalnum():
        raise SystemExit("label must be alphanumeric or underscore")
    for path in [
        workspace / "schema.cedarschema",
        workspace / "candidate.cedar",
        workspace / "verification_plan.py",
        CEDAR,
        CVC5,
        PYTHON,
    ]:
        if not path.is_file():
            raise SystemExit(f"missing prerequisite: {path}")

    input_sha256 = {
        str(path.relative_to(workspace)): sha256(path)
        for path in sorted(workspace.rglob("*")) if path.is_file()
    }

    command = [
        str(PYTHON),
        "-c",
        "import sys; from autocedar.cli import main; sys.exit(main())",
        "verify",
        str(workspace),
    ]
    environment = os.environ.copy()
    environment.update({
        "PYTHONPATH": str(SOURCE),
        "CEDAR": str(CEDAR),
        "CVC5": str(CVC5),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=RUN,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        code = result.returncode
        stdout, stderr = result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        code = 124
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")

    (RUN / f"{label}.stdout").write_text(stdout)
    (RUN / f"{label}.stderr").write_text(stderr)
    (RUN / f"{label}.json").write_text(json.dumps({
        "command": command,
        "cwd": str(RUN),
        "returncode": code,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
        "cedar_version": "4.12.0 experimental",
        "cvc5_version": "1.4.2",
        "model": None,
        "seed": None,
        "api_cost_usd": 0,
        "input_sha256": input_sha256,
    }, indent=2) + "\n")
    print(f"{label}: exit={code}; elapsed={time.monotonic() - started:.3f}s")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
