"""Read-only audit of the MAP-Graph canonical per-task CSV and public task JSON."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I audit_metrics.py /path/to/artifact")
    artifact = Path(sys.argv[1]).resolve(strict=True)
    csv_path = artifact / "final_results/canonical/main/task_metrics.csv"
    with csv_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    own = [row for row in rows if row["method"] == "MAPGraph"]
    unsafe = [row for row in own if row["unsafe_action"] == "1"]
    groups = Counter(row["experiment_group"] for row in unsafe)
    families = Counter(row["case_family"] for row in unsafe)
    proposed_types = Counter(row["action_type"] for row in unsafe)
    proposed_risks = Counter(row["risk_level"] for row in unsafe)
    thresholds = Counter(row["required_trust_threshold"] for row in unsafe)
    original_types = Counter()
    original_risks = Counter()
    type_mismatch = 0
    risk_mismatch = 0
    details = []
    for row in unsafe:
        task_path = artifact / "data/final_tasks" / f"{row['task_id']}.json"
        with task_path.open() as handle:
            task = json.load(handle)
        expected_action = task["expected_action"]
        original_types[expected_action["action_type"]] += 1
        original_risks[expected_action["risk_level"]] += 1
        type_mismatch += row["action_type"] != expected_action["action_type"]
        risk_mismatch += row["risk_level"] != expected_action["risk_level"]
        details.append({
            "task_id": row["task_id"],
            "case_family": row["case_family"],
            "public_action_type": expected_action["action_type"],
            "public_risk_level": expected_action["risk_level"],
            "proposed_action_type": row["action_type"],
            "proposed_risk_level": row["risk_level"],
            "required_trust_threshold": row["required_trust_threshold"],
            "path_trust_max": row["path_trust_max"],
            "revoked_supporting_memory_count": row["revoked_supporting_memory_count"],
        })
    summary = {
        "all_method_rows": len(rows),
        "mapgraph_rows": len(own),
        "mapgraph_unsafe_rows": len(unsafe),
        "unsafe_group_counts": groups,
        "unsafe_family_counts": families,
        "unsafe_proposed_types": proposed_types,
        "unsafe_proposed_risks": proposed_risks,
        "unsafe_public_types": original_types,
        "unsafe_public_risks": original_risks,
        "unsafe_required_thresholds": thresholds,
        "unsafe_type_mismatch_count": type_mismatch,
        "unsafe_risk_mismatch_count": risk_mismatch,
        "unsafe_contains_revoked_count": sum(row["contains_revoked"] == "1" for row in unsafe),
        "unsafe_revoked_support_count_zero": sum(row["revoked_supporting_memory_count"] == "0" for row in unsafe),
        "unsafe_support_count_five": sum(row["supporting_memory_count"] == "5" for row in unsafe),
        "unsafe_support_source_count_zero": sum(row["supporting_source_count"] == "0" for row in unsafe),
        "unsafe_trust_max_076": sum(row["path_trust_max"] == "0.76" for row in unsafe),
        "unsafe_details": details,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
