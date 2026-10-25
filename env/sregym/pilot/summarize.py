"""Create one-row-per-run CSV and aggregate JSON from pilot raw records."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    source = Path(args.input)
    usage_by_tag: dict[str, list[dict]] = defaultdict(list)
    usage_path = source / "usage.jsonl"
    if usage_path.exists():
        for line in usage_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                usage_by_tag[row["tag"]].append(row)

    rows = []
    for path in sorted(source.glob("model-*__trial.json")):
        record = load_json(path)
        agent = record.get("agent") or {}
        judgment = record.get("security_judgment") or {}
        writes = agent.get("write_requests") or []
        write = writes[-1] if writes else {}
        usage = usage_by_tag.get(record.get("tag"), [])
        rows.append(
            {
                "tag": record.get("tag"),
                "plan_version": record.get("plan_version"),
                "task": record.get("problem"),
                "observation": record.get("observation"),
                "gate": record.get("gate"),
                "rep": record.get("rep"),
                "validity": record.get("validity"),
                "agent_status": agent.get("status"),
                "recovery": record.get("mitigation_success"),
                "wrong_request": judgment.get("wrong_request"),
                "gate_decision": judgment.get("gate_decision"),
                "execution_attempted": (write.get("execution") or {}).get("attempted"),
                "actual_change": judgment.get("actual_change"),
                "damage": judgment.get("damage"),
                "remaining_fault": judgment.get("remaining_fault"),
                "observation_calls": (record.get("observation_validation") or {}).get("calls"),
                "independent_gate_queries": 1 if record.get("gate") == "G2" else 0,
                "llm_calls": agent.get("llm_calls"),
                "input_tokens": sum(item.get("input_tokens", 0) for item in usage),
                "cached_tokens": sum(item.get("cached_tokens", 0) for item in usage),
                "output_tokens": sum(item.get("output_tokens", 0) for item in usage),
                "reasoning_tokens": sum(item.get("reasoning_tokens") or 0 for item in usage),
                "usd_estimate": agent.get("usd_estimate"),
                "ttm_s": (record.get("results") or {}).get("TTM"),
                "trial_elapsed_s": record.get("elapsed_s"),
                "raw_evidence": f"local/pilot/model/{path.name}",
                "retry_note": (
                    "valid retry after excluded pre-call SDK schema error"
                    if record.get("tag") == "model-normal-G0-r1"
                    else "none"
                ),
            }
        )
    rows.sort(key=lambda row: (int(row["rep"]), row["gate"], row["observation"]))

    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]) if rows else [],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    valid = [row for row in rows if row["validity"] == "valid"]
    cells = Counter(
        (
            row["observation"],
            row["gate"],
            str(row["recovery"]),
            str(row["wrong_request"]),
            row["gate_decision"],
            str(row["actual_change"]),
            str(row["damage"]),
        )
        for row in valid
    )
    summary = {
        "planned_runs": 12,
        "result_files": len(rows),
        "valid_runs": len(valid),
        "invalid_or_error_runs": len(rows) - len(valid),
        "llm_calls": sum(int(row["llm_calls"] or 0) for row in rows),
        "input_tokens": sum(int(row["input_tokens"] or 0) for row in rows),
        "cached_tokens": sum(int(row["cached_tokens"] or 0) for row in rows),
        "output_tokens": sum(int(row["output_tokens"] or 0) for row in rows),
        "reasoning_tokens": sum(int(row["reasoning_tokens"] or 0) for row in rows),
        "usd_estimate": round(sum(float(row["usd_estimate"] or 0) for row in rows), 9),
        "trial_elapsed_s": round(sum(float(row["trial_elapsed_s"] or 0) for row in rows), 3),
        "cells": [
            {
                "observation": key[0],
                "gate": key[1],
                "recovery": key[2],
                "wrong_request": key[3],
                "gate_decision": key[4],
                "actual_change": key[5],
                "damage": key[6],
                "runs": count,
            }
            for key, count in sorted(cells.items())
        ],
        "excluded_attempts": [
            {
                "path": "local/pilot/model/failed__model-normal-G0-r1__attempt1__trial.json",
                "reason": "SDK strict-schema validation failed before any model or tool call; fixed and retried once",
            }
        ],
        "estimate_note": "USD uses repository legacy price constants and is not a billing record.",
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
