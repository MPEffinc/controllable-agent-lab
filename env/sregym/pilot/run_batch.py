"""Run the precommitted 12-cell model order with one preserved retry per error."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TRIAL = ROOT / "env" / "sregym" / "pilot" / "run_trial.py"
WRAPPER = ROOT / "env" / "sregym" / "sregym.sh"
ORDER = (
    ("normal", "G0", 1),
    ("forged", "G0", 1),
    ("forged", "G1", 1),
    ("normal", "G1", 1),
    ("normal", "G2", 1),
    ("forged", "G2", 1),
    ("forged", "G2", 2),
    ("normal", "G2", 2),
    ("normal", "G1", 2),
    ("forged", "G1", 2),
    ("forged", "G0", 2),
    ("normal", "G0", 2),
)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def preserve_attempt(outdir: Path, tag: str, attempt: int) -> None:
    for suffix in ("__trial.json", "__events.jsonl", "__agent.json", "__run.log"):
        path = outdir / f"{tag}{suffix}"
        if path.exists():
            path.rename(outdir / f"failed__{tag}__attempt{attempt}{suffix}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--limit", type=int, default=len(ORDER))
    args = parser.parse_args()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    progress = outdir / "progress.jsonl"
    selected = ORDER[: max(0, min(args.limit, len(ORDER)))]

    for index, (observation, gate, rep) in enumerate(selected, start=1):
        tag = f"model-{observation}-{gate}-r{rep}"
        result_path = outdir / f"{tag}__trial.json"
        if load(result_path).get("validity") == "valid":
            with progress.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "tag": tag, "status": "skip-valid"}) + "\n")
            continue

        for attempt in (1, 2):
            log_path = outdir / f"{tag}__run.log"
            command = [
                str(WRAPPER),
                "--py",
                str(TRIAL),
                "--kind",
                "model",
                "--observation",
                observation,
                "--gate",
                gate,
                "--rep",
                str(rep),
                "--outdir",
                str(outdir),
            ]
            started = time.monotonic()
            with log_path.open("w", encoding="utf-8") as log:
                proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True, timeout=1800)
            result = load(result_path)
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "order": index,
                "tag": tag,
                "attempt": attempt,
                "returncode": proc.returncode,
                "validity": result.get("validity"),
                "agent_status": (result.get("agent") or {}).get("status"),
                "elapsed_s": round(time.monotonic() - started, 3),
            }
            with progress.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(json.dumps(entry, ensure_ascii=False), flush=True)
            if result.get("validity") == "valid":
                break
            if attempt == 1:
                preserve_attempt(outdir, tag, attempt)
        else:
            print(f"batch stopped after two failed attempts: {tag}", flush=True)
            raise SystemExit(2)


if __name__ == "__main__":
    main()
