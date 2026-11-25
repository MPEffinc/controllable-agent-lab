"""Independent blind vs candidate-exposed authorization oracle control."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CASE = ROOT / "third_party/K06-autocedar/dataset/gold-reference-dataset/cases/case-101"
C8 = ROOT / "docs/systems_mas_access_control_20261125/runs/C8_cedar_hierarchy_effect_20261125"
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
if (HERE / "raw.jsonl").exists() or (HERE / "result.json").exists():
    raise RuntimeError("C10 raw data exists; preserve and use a new run ID")

spec = importlib.util.spec_from_file_location("d1_api_for_c10", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MAX_CALLS = 8
d1.RUN_CAP_USD = 0.10

gold = (CASE / "gold/gold.cedar").read_text()
old = "resource.region in principal.assignedGroup"
assert gold.count(old) == 1
candidate = gold.replace(old, "resource.region == principal.assignedGroup")
(HERE / "equality_only_candidate.cedar").write_text(candidate)
requirement = (CASE / "requirement.md").read_text()
schema = CASE / "gold/schema.cedarschema"
context = C8 / "context.json"
cases = (
    ("same", "root", "ALLOW"),
    ("direct_child", "child", "ALLOW"),
    ("transitive_grandchild", "leaf", "ALLOW"),
    ("unrelated", "south", "DENY"),
)
cli_results = []
for name, region, expected in cases:
    for form, policy in (("gold", CASE / "gold/gold.cedar"),
                         ("equality_only", HERE / "equality_only_candidate.cedar")):
        argv = [str(CEDAR), "authorize", "--policies", str(policy),
                "--schema", str(schema), "--entities", str(C8 / f"entities_{name}.json"),
                "--principal", 'User::"officer"', "--action", 'Action::"approveClearToClose"',
                "--resource", f'EscrowFile::"escrow-{name}"',
                "--context", str(context), "--verbose"]
        p = subprocess.run(argv, cwd=HERE, text=True, capture_output=True,
                           timeout=20, check=False)
        decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
        cli_results.append({"case_name": name, "policy": form, "argv": argv,
                            "exit_code": p.returncode, "stdout": p.stdout,
                            "stderr": p.stderr, "decision": decision, "gold_expected": expected})
expected_cli = {"same": "ALLOW", "direct_child": "DENY",
                "transitive_grandchild": "DENY", "unrelated": "DENY"}
assert all(row["decision"] == row["gold_expected"] for row in cli_results if row["policy"] == "gold")
assert all(row["decision"] == expected_cli[row["case_name"]]
           for row in cli_results if row["policy"] == "equality_only")

system = ("Derive the expected authorization decision from the user requirement and "
          "request facts. If a candidate decision or coverage report is supplied, "
          "treat it only as evidence of what the candidate did, not the correct answer. "
          "Return only JSON with keys decision ('ALLOW' or 'DENY') and reason (string).")
hierarchy = [{"child": "child", "parent": "root"},
             {"child": "leaf", "parent": "child"}]
arm_order = {
    "same": ("blind", "exposed"),
    "direct_child": ("exposed", "blind"),
    "transitive_grandchild": ("blind", "exposed"),
    "unrelated": ("exposed", "blind"),
}
reviews = []
costs = []
for model, input_rate, output_rate in (
    ("gpt-4.1-mini-2025-04-14", 0.40, 1.60),
    ("gpt-4.1-2025-04-14", 2.00, 8.00),
):
    d1.MODEL = model
    d1.INPUT_PER_M = input_rate
    d1.OUTPUT_PER_M = output_rate
    api = d1.API()
    for name, region, expected in cases:
        facts = {"user_role": "TitleOfficer", "user_assigned_group": "root",
                 "file_region": region, "group_parent_edges": hierarchy,
                 "file_status": "funded", "held_amount_cents": 0,
                 "payee_count": 0, "title_cleared": True,
                 "lien_status": [], "request_time_utc": "2026-11-25T00:00:00Z",
                 "closing_date_utc": "2026-12-01T00:00:00Z"}
        for arm in arm_order[name]:
            user = {"requirement": requirement, "request_facts": facts}
            if arm == "exposed":
                user["candidate_decision"] = expected_cli[name]
                user["coverage_report"] = (
                    "A prior oracle case disagreed with this candidate decision. "
                    "Re-derive the expectation from the requirement."
                    if expected_cli[name] != expected else
                    "No prior oracle/candidate disagreement was flagged.")
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]
            try:
                response = api.call(f"{model}_{name}_{arm}", messages)
                if response.get("decision") not in ("ALLOW", "DENY"):
                    raise ValueError("oracle decision invalid")
                error = None
            except (ValueError, KeyError, TypeError) as exc:
                response, error = None, f"{type(exc).__name__}: {exc}"
            reviews.append({"model": model, "case_name": name, "arm": arm,
                            "gold_expected": expected, "candidate_decision": expected_cli[name],
                            "response": response, "error": error,
                            "correct": response is not None and response["decision"] == expected})
    costs.append({"model": model, "calls": api.calls, "input_tokens": api.input_tokens,
                  "output_tokens": api.output_tokens, "estimated_cost_usd": round(api.cost, 8)})

result = {"kind": "INDEPENDENT_ORACLE_DISAGREEMENT_EXPOSURE_CONTROL",
          "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
          "reparo_reference": "https://arxiv.org/html/2610.41800v1",
          "cli_results": cli_results, "arm_order": arm_order,
          "reviews": reviews, "costs": costs,
          "total_estimated_cost_usd": round(sum(row["estimated_cost_usd"] for row in costs), 8)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"calls": sum(row["calls"] for row in costs),
                  "accuracy": {arm: sum(r["correct"] for r in reviews if r["arm"] == arm)
                               for arm in ("blind", "exposed")},
                  "errors": [(r["model"], r["case_name"], r["arm"],
                              None if r["response"] is None else r["response"]["decision"])
                             for r in reviews if not r["correct"]],
                  "total_estimated_cost_usd": result["total_estimated_cost_usd"]}))
