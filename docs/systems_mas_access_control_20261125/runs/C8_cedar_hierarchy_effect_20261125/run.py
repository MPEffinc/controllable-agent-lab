"""Official case-101 Cedar hierarchy decision and independent SQLite effect."""

import json
import sqlite3
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CASE = ROOT / "third_party/K06-autocedar/dataset/gold-reference-dataset/cases/case-101"
C7 = ROOT / "docs/systems_mas_access_control_20261125/runs/C7_cross_case_review_20261125"
CEDAR = (ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env/"
         "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar")
if (HERE / "result.json").exists() or (HERE / "service_state.sqlite").exists():
    raise RuntimeError("C8 result already exists; preserve and use a new run ID")

def ref(kind, name):
    return {"__entity": {"type": kind, "id": name}}

def entity(kind, name, attrs, parents=()):
    return {"uid": {"type": kind, "id": name}, "attrs": attrs,
            "parents": [{"type": "Group", "id": parent} for parent in parents]}

entities = [
    entity("Group", "root", {}),
    entity("Group", "child", {}, ("root",)),
    entity("Group", "leaf", {}, ("child",)),
    entity("Group", "south", {}),
    entity("User", "officer", {"assignedGroup": ref("Group", "root"),
                                "roles": [ref("Role", "TitleOfficer")],
                                "authorityLevel": 0}),
]
date = {"__extn": {"fn": "datetime", "arg": "2026-12-01T00:00:00Z"}}
context = {"currentTime": {"__extn": {"fn": "datetime", "arg": "2026-11-25T00:00:00Z"}},
           "dualControlVerified": False, "emergencyDeclared": False,
           "enhancedDueDiligenceCompleted": False,
           "enhancedDueDiligenceParties": [], "onCorporateNetwork": True}
(HERE / "context.json").write_text(json.dumps(context, indent=2) + "\n")

cases = (("same", "root", "ALLOW"), ("direct_child", "child", "ALLOW"),
         ("transitive_grandchild", "leaf", "ALLOW"), ("unrelated", "south", "DENY"))
policies = (("official_gold", CASE / "gold/gold.cedar"),
            ("verified_normalized", C7 / "case-101_normalized.cedar"))
results = []
with sqlite3.connect(HERE / "service_state.sqlite") as db:
    db.execute("CREATE TABLE effects(id INTEGER PRIMARY KEY, policy TEXT, case_name TEXT, "
               "resource TEXT, action TEXT)")
    for name, region, expected in cases:
        resource_id = f"escrow-{name}"
        scenario_entities = entities + [entity("EscrowFile", resource_id, {
            "closingDate": date, "disbursementTier": 0, "escrowOfficer": ref("User", "officer"),
            "fileCode": resource_id, "heldAmount": 0, "lienStatus": [],
            "parties": [], "payeeCount": 0, "region": ref("Group", region),
            "status": ref("EscrowFileStatusValue", "funded"), "titleCleared": True,
        })]
        entity_path = HERE / f"entities_{name}.json"
        entity_path.write_text(json.dumps(scenario_entities, indent=2) + "\n")
        for policy_name, policy_path in policies:
            argv = [str(CEDAR), "authorize", "--policies", str(policy_path),
                    "--entities", str(entity_path), "--principal", 'User::"officer"',
                    "--action", 'Action::"approveClearToClose"',
                    "--resource", f'EscrowFile::"{resource_id}"',
                    "--context", str(HERE / "context.json"), "--verbose"]
            p = subprocess.run(argv, cwd=HERE, capture_output=True, text=True,
                               timeout=20, check=False)
            decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
            before = db.execute("SELECT COUNT(*) FROM effects WHERE policy=? AND case_name=?",
                                (policy_name, name)).fetchone()[0]
            if p.returncode == 0 and decision == "ALLOW":
                db.execute("INSERT INTO effects(policy,case_name,resource,action) VALUES(?,?,?,?)",
                           (policy_name, name, resource_id, "clear_to_close"))
            after = db.execute("SELECT COUNT(*) FROM effects WHERE policy=? AND case_name=?",
                               (policy_name, name)).fetchone()[0]
            results.append({"case_name": name, "region": region, "policy": policy_name,
                            "expected": expected, "argv": argv, "exit_code": p.returncode,
                            "stdout": p.stdout, "stderr": p.stderr, "decision": decision,
                            "service_state_before": "open", "service_state_after":
                            "clear_to_close" if after > before else "open",
                            "effect_delta": after - before})
    db.commit()

result = {"kind": "CEDAR_HIERARCHY_OPERATOR_OFFICIAL_GOLD_LOCAL_EFFECT",
          "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
          "official_operator_reference": "https://docs.cedarpolicy.com/syntax-operators.html",
          "cases": results, "matches_expected": sum(row["decision"] == row["expected"]
                                                    and row["exit_code"] == 0 for row in results)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"matches_expected": result["matches_expected"], "total": len(results),
                  "effects": [(row["policy"], row["case_name"], row["decision"], row["effect_delta"])
                              for row in results]}))
