"""Original AutoCedar verifier on a researcher schema-extension and Cedar effects."""

import json
import os
import sqlite3
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "third_party/K06-autocedar"
CASE = SOURCE / "dataset/gold-reference-dataset/cases/case-011"
C4 = ROOT / "docs/systems_mas_access_control_20261125/runs/C4_blind_policy_review_20261125"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
PYTHON = ENV / "venv/bin/python"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
CVC5 = ENV / "cvc5"
if (HERE / "result.json").exists() or (HERE / "service_state.sqlite").exists():
    raise RuntimeError("C11 result exists; preserve and use a new run ID")

gold = (CASE / "gold/gold.cedar").read_text()
schema = (CASE / "gold/schema.cedarschema").read_text()
assert 'action deletePullRequest' not in schema
assert 'deletePullRequest' not in gold
new_action = 'action deletePullRequest appliesTo { principal: [User], resource: [PullRequest], context: {} };\n'
schema_extended = schema + "\n" + new_action
extra_permit = ('permit (principal is User, action == Action::"deletePullRequest", '
                'resource is PullRequest);\n')
candidate = gold + "\n" + extra_permit
(HERE / "schema_extended.cedarschema").write_text(schema_extended)
(HERE / "gold.cedar").write_text(gold)
(HERE / "overgrant.cedar").write_text(candidate)
empty_context = HERE / "empty_context.json"
empty_context.write_text("{}\n")

env = os.environ.copy()
env.update({"PYTHONPATH": str(SOURCE), "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "CEDAR": str(CEDAR), "CVC5": str(CVC5)})
verifications = []
for arm, close_action in (("plan_scope_only", False), ("plan_closed_actions", True)):
    workspace = HERE / arm
    workspace.mkdir(exist_ok=False)
    (workspace / "candidate.cedar").write_text(candidate)
    (workspace / "reference.cedar").write_text(gold)
    (workspace / "schema.cedarschema").write_text(schema_extended)
    plan = '''from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    merge = {"principal_type": "User", "action": 'Action::"mergePullRequest"',
             "resource_type": "PullRequest"}
    checks = [
        dict(merge, name="merge_candidate_implies_gold", description="No extra merge",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(merge, name="gold_implies_merge_candidate", description="No missing merge",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
    EXTRA_CHECK
    return checks
'''
    extra = ('checks.append({"principal_type": "User", "action": '
             '\'Action::"deletePullRequest"\', "resource_type": "PullRequest", '
             '"name": "delete_candidate_implies_gold", "description": "No extra delete", '
             '"type": "implies", "reference_path": str(HERE / "reference.cedar")})'
             if close_action else "pass")
    (workspace / "verification_plan.py").write_text(plan.replace("EXTRA_CHECK", extra))
    argv = [str(PYTHON), "-c", "import sys; from autocedar.cli import main; sys.exit(main())",
            "verify", str(workspace)]
    p = subprocess.run(argv, cwd=HERE, env=env, capture_output=True,
                       text=True, timeout=90, check=False)
    verifications.append({"arm": arm, "argv": argv, "exit_code": p.returncode,
                          "stdout": p.stdout, "stderr": p.stderr})

decisions = []
with sqlite3.connect(HERE / "service_state.sqlite") as db:
    db.execute("CREATE TABLE effects(id INTEGER PRIMARY KEY, policy TEXT, request TEXT, "
               "action TEXT, state_before TEXT, state_after TEXT)")
    for policy_name, policy_path in (("gold", HERE / "gold.cedar"),
                                      ("overgrant", HERE / "overgrant.cedar")):
        for request_name, action, context_path in (
            ("normal_merge", "mergePullRequest", C4 / "context_normal.json"),
            ("unauthorized_delete", "deletePullRequest", empty_context),
        ):
            argv = [str(CEDAR), "authorize", "--policies", str(policy_path),
                    "--entities", str(C4 / "entities_normal.json"),
                    "--principal", 'User::"maintainer"',
                    "--action", f'Action::"{action}"',
                    "--resource", 'PullRequest::"pr-11"',
                    "--context", str(context_path), "--verbose"]
            p = subprocess.run(argv, cwd=HERE, capture_output=True, text=True,
                               timeout=20, check=False)
            decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
            state_before = "open"
            state_after = ("merged" if action == "mergePullRequest" else "deleted") if decision == "ALLOW" else "open"
            if decision == "ALLOW" and p.returncode == 0:
                db.execute("INSERT INTO effects(policy,request,action,state_before,state_after) "
                           "VALUES(?,?,?,?,?)",
                           (policy_name, request_name, action, state_before, state_after))
            effect_delta = int(decision == "ALLOW" and p.returncode == 0)
            decisions.append({"policy": policy_name, "request": request_name, "argv": argv,
                              "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                              "decision": decision, "state_before": state_before,
                              "state_after": state_after, "effect_delta": effect_delta})
    db.commit()

result = {"kind": "AUTOCEDAR_UNSCOPED_ACTION_VERIFIER_AND_LOCAL_EFFECT",
          "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
          "schema_extension": new_action.strip(), "candidate_extra_permit": extra_permit.strip(),
          "verifications": verifications, "decisions": decisions, "api_cost_usd": 0}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"verification_exit": [(x["arm"], x["exit_code"]) for x in verifications],
                  "decisions": [(x["policy"], x["request"], x["decision"], x["effect_delta"])
                                for x in decisions]}))
