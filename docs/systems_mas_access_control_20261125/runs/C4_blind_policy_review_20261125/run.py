"""Fixed case-011 policy mutations, blind model review, original verifier, local effects."""

import hashlib
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "third_party/K06-autocedar"
CASE = SOURCE / "dataset/gold-reference-dataset/cases/case-011"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
PYTHON = ENV / "venv/bin/python"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
CVC5 = ENV / "cvc5"
if (HERE / "raw.jsonl").exists() or (HERE / "result.json").exists():
    raise RuntimeError("C4 raw data already exists; use a new run ID")

spec = importlib.util.spec_from_file_location(
    "d1_api_for_c4", ROOT / "docs/systems_mas_access_control_20261125/runs/"
    "D1_live_writeback_20261125/run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MAX_CALLS = 7
api = d1.API()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


gold = (CASE / "gold/gold.cedar").read_text()
requirement = (CASE / "requirement.md").read_text()
markers = {
    "p1": (' && (context.onVpn)', ''),
    "p2": ('((principal.roles.contains(Role::"Maintainer"))) && ', ''),
    "p3": ('(!(true) || (principal != resource.author)) && ', ''),
    "p4": ('((resource.targetBranch like "hotfix/*")) && ', ''),
    "p5": (' && ((resource.approvalCount >= 1))', ''),
    "p6": ('approvalCount >= 1', 'approvalCount >= 2'),
}
policies = {"p0": gold}
for policy_id, (old, new) in markers.items():
    assert gold.count(old) == 1, (policy_id, "source changed")
    policies[policy_id] = gold.replace(old, new)
for policy_id, policy in policies.items():
    (HERE / f"{policy_id}.cedar").write_text(policy)

env = os.environ.copy()
env.update({"PYTHONPATH": str(SOURCE), "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "CEDAR": str(CEDAR), "CVC5": str(CVC5)})

order = ["p4", "p0", "p6", "p2", "p5", "p1", "p3"]
reviews = []
for policy_id in order:
    messages = [
        {"role": "system", "content":
         "Review whether the candidate Cedar policy grants exactly the permissions "
         "stated by the user requirement, including both allowed and denied requests. "
         "Return only JSON with keys approve (boolean) and reason (string). "
         "Reject a policy if it is too broad or too restrictive. Treat the code as "
         "a single Cedar permit policy; no other permits exist. Do not assume omitted "
         "conditions are enforced elsewhere."},
        {"role": "user", "content":
         "User requirement:\n" + requirement + "\nCandidate policy:\n" + policies[policy_id]},
    ]
    try:
        response = api.call(f"review_{policy_id}", messages)
        if not isinstance(response.get("approve"), bool):
            raise ValueError("review approve is not boolean")
        error = None
    except (ValueError, KeyError, TypeError) as exc:
        response, error = None, f"{type(exc).__name__}: {exc}"
    reviews.append({"policy_id": policy_id, "gold_approve": policy_id == "p0",
                    "model_review": response, "error": error,
                    "correct": response is not None and response["approve"] == (policy_id == "p0")})

verifications = []
for policy_id in policies:
    workspace = HERE / f"verify_{policy_id}"
    workspace.mkdir(exist_ok=False)
    (workspace / "candidate.cedar").write_text(policies[policy_id])
    (workspace / "reference.cedar").write_text(gold)
    (workspace / "schema.cedarschema").write_bytes((CASE / "gold/schema.cedarschema").read_bytes())
    plan = '''from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = {"principal_type": "User", "action": 'Action::"mergePullRequest"',
              "resource_type": "PullRequest"}
    return [
        dict(common, name="candidate_implies_gold", description="No extra permission",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="gold_implies_candidate", description="No false denial",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
'''
    (workspace / "verification_plan.py").write_text(plan)
    argv = [str(PYTHON), "-c", "import sys; from autocedar.cli import main; sys.exit(main())",
            "verify", str(workspace)]
    p = subprocess.run(argv, cwd=HERE, env=env, text=True,
                       capture_output=True, timeout=60, check=False)
    verifications.append({"policy_id": policy_id, "argv": argv, "exit_code": p.returncode,
                          "stdout": p.stdout, "stderr": p.stderr,
                          "expected_pass": policy_id == "p0"})


def request_files(case_name):
    principal = "author" if case_name == "self" else "reader" if case_name == "no_role" else "maintainer"
    vpn = case_name != "off_vpn"
    branch = "release/x" if case_name == "no_branch" else "hotfix/critical"
    approvals = 0 if case_name == "no_approval" else 1
    entities = [
        {"uid": {"type": "User", "id": "maintainer"},
         "attrs": {"roles": [{"__entity": {"type": "Role", "id": "Maintainer"}}]}, "parents": []},
        {"uid": {"type": "User", "id": "author"},
         "attrs": {"roles": [{"__entity": {"type": "Role", "id": "Maintainer"}}]}, "parents": []},
        {"uid": {"type": "User", "id": "reader"}, "attrs": {"roles": []}, "parents": []},
        {"uid": {"type": "PullRequest", "id": "pr-11"},
         "attrs": {"approvalCount": approvals,
                   "author": {"__entity": {"type": "User", "id": "author"}},
                   "targetBranch": branch}, "parents": []},
    ]
    path_entities = HERE / f"entities_{case_name}.json"
    path_context = HERE / f"context_{case_name}.json"
    path_entities.write_text(json.dumps(entities, indent=2) + "\n")
    path_context.write_text(json.dumps({"onVpn": vpn}) + "\n")
    return principal, path_entities, path_context


witness = {"p0": "off_vpn", "p1": "off_vpn", "p2": "no_role",
           "p3": "self", "p4": "no_branch", "p5": "no_approval", "p6": "normal"}
effects = []
with sqlite3.connect(HERE / "service_state.sqlite") as db:
    db.execute("CREATE TABLE effects(id INTEGER PRIMARY KEY, policy_id TEXT, case_name TEXT, "
               "action TEXT, resource TEXT)")
    for policy_id in policies:
        for case_name in dict.fromkeys(("normal", witness[policy_id])):
            principal, entities, context = request_files(case_name)
            argv = [str(CEDAR), "authorize", "--policies", str(HERE / f"{policy_id}.cedar"),
                    "--entities", str(entities), "--principal", f'User::"{principal}"',
                    "--action", 'Action::"mergePullRequest"',
                    "--resource", 'PullRequest::"pr-11"', "--context", str(context), "--verbose"]
            p = subprocess.run(argv, cwd=HERE, env=env, text=True,
                               capture_output=True, timeout=15, check=False)
            decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
            before = db.execute("SELECT COUNT(*) FROM effects WHERE policy_id=? AND case_name=?",
                                (policy_id, case_name)).fetchone()[0]
            if decision == "ALLOW":
                db.execute("INSERT INTO effects(policy_id,case_name,action,resource) VALUES(?,?,?,?)",
                           (policy_id, case_name, "mergePullRequest", "pr-11"))
            after = db.execute("SELECT COUNT(*) FROM effects WHERE policy_id=? AND case_name=?",
                               (policy_id, case_name)).fetchone()[0]
            effects.append({"policy_id": policy_id, "case_name": case_name,
                            "argv": argv, "exit_code": p.returncode, "stdout": p.stdout,
                            "stderr": p.stderr, "decision": decision,
                            "pr_state_before": "open", "pr_state_after":
                            "merged" if after > before else "open", "effect_delta": after - before})
    db.commit()

summary = {"kind": "BLIND_MODEL_POLICY_REVIEW_GOLD_VERIFY_LOCAL_EFFECT",
           "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
           "requirement_sha256": digest(CASE / "requirement.md"),
           "gold_sha256": digest(CASE / "gold/gold.cedar"),
           "order": order, "mutation_markers": markers,
           "reviews": reviews, "verifications": verifications, "effects": effects,
           "review_correct": sum(r["correct"] for r in reviews),
           "verify_correct": sum((r["exit_code"] == 0) == r["expected_pass"] for r in verifications),
           "input_tokens": api.input_tokens, "output_tokens": api.output_tokens,
           "estimated_cost_usd": round(api.cost, 8)}
(HERE / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"review_correct": summary["review_correct"],
                  "verify_correct": summary["verify_correct"],
                  "review_errors": [(r["policy_id"], r["model_review"])
                                    for r in reviews if not r["correct"]],
                  "effects": [(r["policy_id"], r["case_name"], r["decision"])
                              for r in effects],
                  "input_tokens": api.input_tokens, "output_tokens": api.output_tokens,
                  "estimated_cost_usd": summary["estimated_cost_usd"]}))
