"""Independent target experiment using pinned AutoCedar verifier and Cedar CLI."""

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "third_party/K06-autocedar"
CASE = SOURCE / "dataset/gold-reference-dataset/cases/case-011/gold"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
PYTHON = ENV / "venv/bin/python"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
CVC5 = ENV / "cvc5"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


gold = (CASE / "gold.cedar").read_text()
marker = " && (context.onVpn)"
assert gold.count(marker) == 1, "unexpected source policy; do not change marker silently"
wrong = gold.replace(marker, "")
(HERE / "gold.cedar").write_text(gold)
(HERE / "candidate_missing_vpn.cedar").write_text(wrong)
shutil.copyfile(CASE / "schema.cedarschema", HERE / "schema.cedarschema")

run_env = os.environ.copy()
run_env.update({"PYTHONPATH": str(SOURCE), "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1", "CEDAR": str(CEDAR), "CVC5": str(CVC5)})

verifier = []
for arm in ("self_reference", "independent_gold"):
    workspace = HERE / arm
    workspace.mkdir(exist_ok=False)
    shutil.copyfile(HERE / "schema.cedarschema", workspace / "schema.cedarschema")
    shutil.copyfile(HERE / "candidate_missing_vpn.cedar", workspace / "candidate.cedar")
    reference = workspace / "reference.cedar"
    reference.write_text(wrong if arm == "self_reference" else gold)
    plan = f'''"""Research-authored plan, not an AutoCedar generated target."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = {{"principal_type": "User", "action": 'Action::"mergePullRequest"',
              "resource_type": "PullRequest"}}
    return [
        dict(common, name="candidate_implies_target", description="Candidate within target",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="target_implies_candidate", description="Candidate covers target",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
'''
    (workspace / "verification_plan.py").write_text(plan)
    argv = [str(PYTHON), "-c", "import sys; from autocedar.cli import main; sys.exit(main())",
            "verify", str(workspace)]
    p = subprocess.run(argv, cwd=HERE, env=run_env, text=True,
                       capture_output=True, timeout=90, check=False)
    verifier.append({"arm": arm, "argv": argv, "exit_code": p.returncode,
                     "stdout": p.stdout, "stderr": p.stderr,
                     "candidate_sha256": digest(workspace / "candidate.cedar"),
                     "reference_sha256": digest(reference)})

entities = [
    {"uid": {"type": "User", "id": "maintainer"},
     "attrs": {"roles": [{"__entity": {"type": "Role", "id": "Maintainer"}}]}, "parents": []},
    {"uid": {"type": "User", "id": "author"},
     "attrs": {"roles": [{"__entity": {"type": "Role", "id": "Maintainer"}}]}, "parents": []},
    {"uid": {"type": "PullRequest", "id": "pr-11"},
     "attrs": {"approvalCount": 1,
               "author": {"__entity": {"type": "User", "id": "author"}},
               "targetBranch": "hotfix/critical"}, "parents": []},
]
(HERE / "entities.json").write_text(json.dumps(entities, indent=2) + "\n")

effects = []
for policy_name, policy_file in (("gold", HERE / "gold.cedar"),
                                 ("missing_vpn", HERE / "candidate_missing_vpn.cedar")):
    for case_name, principal, vpn in (
        ("normal", "maintainer", True),
        ("off_vpn", "maintainer", False),
        ("self_author", "author", True),
    ):
        context_path = HERE / f"context_{case_name}.json"
        context_path.write_text(json.dumps({"onVpn": vpn}) + "\n")
        argv = [str(CEDAR), "authorize", "--policies", str(policy_file),
                "--entities", str(HERE / "entities.json"),
                "--principal", f'User::"{principal}"',
                "--action", 'Action::"mergePullRequest"',
                "--resource", 'PullRequest::"pr-11"',
                "--context", str(context_path), "--verbose"]
        p = subprocess.run(argv, cwd=HERE, env=run_env, text=True,
                           capture_output=True, timeout=15, check=False)
        decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
        before = "open"
        after = "merged" if decision == "ALLOW" else before
        effects.append({"policy": policy_name, "case": case_name, "argv": argv,
                        "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                        "decision": decision, "pr_state_before": before,
                        "pr_state_after": after})

summary = {"kind": "INDEPENDENT_TARGET_ORACLE_WITH_ORIGINAL_VERIFIER",
           "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
           "cedar_sha256": digest(CEDAR), "cvc5_sha256": digest(CVC5),
           "source_gold_sha256": digest(CASE / "gold.cedar"),
           "schema_sha256": digest(CASE / "schema.cedarschema"),
           "verifier": verifier, "effects": effects,
           "hypothesis_supported": (verifier[0]["exit_code"] == 0 and
                                    verifier[1]["exit_code"] == 1 and
                                    [e["decision"] for e in effects] ==
                                    ["ALLOW", "DENY", "DENY", "ALLOW", "ALLOW", "DENY"])}
(HERE / "raw.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"verifier": [(v["arm"], v["exit_code"]) for v in verifier],
                  "effects": [(e["policy"], e["case"], e["decision"], e["pr_state_after"])
                              for e in effects],
                  "hypothesis_supported": summary["hypothesis_supported"]}))
if not summary["hypothesis_supported"]:
    raise SystemExit(1)
