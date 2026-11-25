"""Read-only correction of CLI DENY exit code and schema-enabled decision replay."""

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCHEMA = ROOT / "third_party/K06-autocedar/dataset/gold-reference-dataset/cases/case-101/gold/schema.cedarschema"
source = json.loads((HERE / "result.json").read_text())
replay = []
for row in source["cases"]:
    argv = row["argv"].copy()
    position = argv.index("--entities")
    argv[position:position] = ["--schema", str(SCHEMA)]
    p = subprocess.run(argv, cwd=HERE, capture_output=True, text=True, timeout=20, check=False)
    decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
    replay.append({"policy": row["policy"], "case_name": row["case_name"],
                   "expected": row["expected"], "argv": argv,
                   "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                   "decision": decision, "matches_expected": decision == row["expected"]})
analysis = {
    "original_decision_match": sum(row["decision"] == row["expected"] for row in source["cases"]),
    "original_exit_codes": sorted(set(row["exit_code"] for row in source["cases"])),
    "original_run_matches_expected_field": source["matches_expected"],
    "note": "Original score counted only exit 0; Cedar CLI returns 2 for an expected DENY.",
    "schema_enabled_replay": replay,
    "schema_enabled_decision_match": sum(row["matches_expected"] for row in replay),
}
(HERE / "typed_recheck.json").write_text(json.dumps(analysis, indent=2) + "\n")
print(json.dumps({"original_decision_match": analysis["original_decision_match"],
                  "schema_enabled_decision_match": analysis["schema_enabled_decision_match"],
                  "total": len(replay), "exit_codes": analysis["original_exit_codes"]}))
