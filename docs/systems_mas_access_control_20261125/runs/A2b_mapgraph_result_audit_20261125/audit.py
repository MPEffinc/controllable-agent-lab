#!/usr/bin/env python3
"""Read-only audit of pinned MAP-Graph summary rows; no model/API calls."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "third_party/MAP-Graph/artifact/final_results/canonical/main/task_metrics.csv"
OUT = Path(__file__).with_name("summary.json")

with SOURCE.open(newline="", encoding="utf-8") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames or []
    rows = list(reader)

exp5 = [row for row in rows if row["experiment_group"] == "exp_5_action_risk_sensitivity"]
map_rows = [row for row in exp5 if row["method"] == "MAPGraph"]
unexpected_allow = [
    row for row in map_rows
    if row["expected_decision"] == "BLOCK" and row["actual_decision"] == "ALLOW"
]
summary = {
    "source": str(SOURCE.relative_to(ROOT)),
    "all_task_rows": len(rows),
    "exp5_rows_by_method": dict(sorted(Counter(row["method"] for row in exp5).items())),
    "mapgraph_exp5_rows": len(map_rows),
    "mapgraph_exp5_expected_block_actual_allow": len(unexpected_allow),
    "unexpected_allow_task_ids": [row["task_id"] for row in unexpected_allow],
    "has_model_response_column": any(
        key in fields for key in ("model_response", "model_content", "raw_output")
    ),
    "has_parser_origin_column": any(
        key in fields for key in ("action_origin", "parser_origin", "used_fallback")
    ),
    "has_provider_effect_column": any(
        key in fields for key in ("provider_effect", "service_effect", "external_effect")
    ),
}
OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in summary.items() if key != "unexpected_allow_task_ids"}, sort_keys=True))
