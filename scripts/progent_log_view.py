"""Read-only viewer for preserved Progent stderr and original AgentDojo traces.

ANSI highlighting is a terminal overlay. Removing ANSI codes yields the source
bytes selected from the original local log or Trace file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path("local/progent-vm")
RUN_DIRS = (ROOT / "live", ROOT / "agentdojo")
RUN_ID = re.compile(r"^[A-Za-z0-9_-]+$")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def source_text(log: dict) -> str:
    """Return captured source stderr segments without rewriting their contents."""
    if "source_generation_stderr" in log:
        return log.get("source_policy_setup_stderr", "") + log["source_generation_stderr"]
    return log.get("policy_setup_stderr", "") + log.get("source_stderr", "")


def highlight_native(value: str, enabled: bool) -> str:
    """Color whole existing lines; do not change any underlying characters."""
    if not enabled:
        return value
    output = []
    for line in value.splitlines(keepends=True):
        body, ending = (line[:-1], "\n") if line.endswith("\n") else (line, "")
        lower = body.lower()
        if ("validationerror" in lower or "not allowed" in lower or
                "policy_denied" in lower or re.search(r'"error"\s*:\s*"', body)):
            color = "31"  # red: an actual source Tool error or denial
        elif "security policy updated" in lower or '"utility": false' in lower:
            color = "33"  # yellow: policy state or incomplete task
        elif "user_query:" in lower or '"tool_call"' in lower or '"function"' in lower:
            color = "36"  # cyan: user input and actual Tool Calls
        elif '"utility": true' in lower or '"error": null' in lower:
            color = "32"  # green: successful source trace field
        else:
            color = None
        output.append(f"\x1b[{color}m{body}\x1b[0m{ending}" if color else line)
    rendered = "".join(output)
    assert ANSI.sub("", rendered) == value
    return rendered


def select_run(run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id):
        raise ValueError("run ID must contain only letters, numbers, underscore or hyphen")
    matches = [directory / f"{run_id}.json" for directory in RUN_DIRS
               if (directory / f"{run_id}.json").is_file()]
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one local Run JSON for {run_id}; found {len(matches)}")
    return matches[0]


def trace_text(log: dict, run_id: str) -> str:
    raw = log.get("source_trace")
    if not raw:
        raise ValueError("this Run has no AgentDojo source Trace")
    path = Path(raw)
    if path.name != f"{run_id}.json":
        raise ValueError("legacy shared Trace path may have been overwritten; use a newer Run")
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Trace path is outside the experiment log directory")
    return path.read_text()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id", nargs="?")
    parser.add_argument("--latest", action="store_true", help="open the newest local Live Run")
    parser.add_argument("--list", action="store_true", help="list recent local Live Run IDs")
    parser.add_argument("--section", choices=("auto", "source", "trace"), default="auto")
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    args = parser.parse_args()
    files = sorted((path for directory in RUN_DIRS for path in directory.glob("*.json")),
                   key=lambda path: path.stat().st_mtime)
    if args.list:
        for path in files[-20:]:
            print(path.stem)
        return
    if args.latest:
        if args.run_id or not files:
            parser.error("--latest requires no Run ID and at least one local Run")
        path = files[-1]
    elif args.run_id:
        try:
            path = select_run(args.run_id)
        except (ValueError, FileNotFoundError) as exc:
            parser.error(str(exc))
    else:
        parser.error("provide a Run ID, --latest or --list")
    log = json.loads(path.read_text())
    run_id = path.stem
    section = ("trace" if log.get("source_trace") else "source") if args.section == "auto" else args.section
    try:
        value = trace_text(log, run_id) if section == "trace" else source_text(log)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if not value:
        parser.error(f"{section} section is empty for {run_id}")
    use_color = args.color == "always" or (args.color == "auto" and sys.stdout.isatty()
                                             and "NO_COLOR" not in os.environ)
    sys.stdout.write(highlight_native(value, use_color))


if __name__ == "__main__":
    main()
