"""Audit archived AutoCedar completion/approval split and local mock effect."""

import hashlib
import json
import os
import sqlite3
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "third_party/K06-autocedar"
ARCHIVE = (SOURCE / "experiments/fig2_cyberchair/haiku-4-5-2026-10-27/output/"
           "cyberchair-haiku45")
WORKSPACE = ARCHIVE / "harness_runs/scenario"
CANDIDATE = WORKSPACE / "candidate.cedar"
DECISION = ARCHIVE / "stage2_5/final_user_decision.json"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
PYTHON = ENV / "venv/bin/python"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
CVC5 = ENV / "cvc5"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if (HERE / "raw.json").exists() or (HERE / "service_state.sqlite").exists():
    raise RuntimeError("C3 raw data exists; preserve and use a new run ID")
assert digest(CANDIDATE) == digest(ARCHIVE / "stage3/final_candidate.cedar")
approval = json.loads(DECISION.read_text())
assert isinstance(approval["approved"], bool)

env = os.environ.copy()
env.update({"PYTHONPATH": str(SOURCE), "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "CEDAR": str(CEDAR), "CVC5": str(CVC5)})
completion_code = (
    "from pathlib import Path; from types import SimpleNamespace; "
    "from autocedar.cli import _authoring_completed; import sys; "
    "print(_authoring_completed(SimpleNamespace(candidate_path=Path(sys.argv[1]), "
    "final_user_approved=False)))"
)
completion_argv = [str(PYTHON), "-c", completion_code, str(CANDIDATE)]
completion = subprocess.run(completion_argv, env=env, cwd=HERE, text=True,
                            capture_output=True, timeout=15, check=False)
completed = completion.returncode == 0 and completion.stdout.strip() == "True"

verify_argv = [str(PYTHON), "-c", "import sys; from autocedar.cli import main; sys.exit(main())",
               "verify", str(WORKSPACE)]
verify = subprocess.run(verify_argv, env=env, cwd=HERE, text=True,
                        capture_output=True, timeout=180, check=False)

entities = [
    {"uid": {"type": "User", "id": "author"}, "attrs": {}, "parents": []},
    {"uid": {"type": "Submission", "id": "paper"},
     "attrs": {"authors": [{"__entity": {"type": "User", "id": "author"}}],
               "step1Open": True}, "parents": []},
]
(HERE / "entities.json").write_text(json.dumps(entities, indent=2) + "\n")
(HERE / "context.json").write_text("{}\n")
authorize_argv = [str(CEDAR), "authorize", "--policies", str(CANDIDATE),
                  "--entities", str(HERE / "entities.json"),
                  "--principal", 'User::"author"', "--action", 'Action::"submitStep1"',
                  "--resource", 'Submission::"paper"', "--context", str(HERE / "context.json"),
                  "--verbose"]
authorize = subprocess.run(authorize_argv, env=env, cwd=HERE, text=True,
                           capture_output=True, timeout=15, check=False)
decision = ("ALLOW" if "\nALLOW\n" in authorize.stdout else
            "DENY" if "\nDENY\n" in authorize.stdout else "UNKNOWN")

effects = []
with sqlite3.connect(HERE / "service_state.sqlite") as db:
    db.execute("CREATE TABLE effects (id INTEGER PRIMARY KEY, arm TEXT, action TEXT, resource TEXT)")
    for arm, allowed in (
        ("completion_only", completed and verify.returncode == 0 and decision == "ALLOW"),
        ("approval_gate", completed and verify.returncode == 0 and
         approval["approved"] and decision == "ALLOW"),
    ):
        before = db.execute("SELECT COUNT(*) FROM effects WHERE arm=?", (arm,)).fetchone()[0]
        if allowed:
            db.execute("INSERT INTO effects(arm,action,resource) VALUES(?,?,?)",
                       (arm, "submitStep1", "paper"))
        after = db.execute("SELECT COUNT(*) FROM effects WHERE arm=?", (arm,)).fetchone()[0]
        effects.append({"arm": arm, "before": before, "after": after,
                        "effect_delta": after - before})
    db.commit()

result = {"kind": "ARCHIVED_AUTHOR_CANDIDATE_INDEPENDENT_CONSUMER_EFFECT",
          "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
          "archive_kind": "manual AITL target debugging trace, not paper 19 error candidates",
          "candidate_sha256": digest(CANDIDATE), "schema_sha256": digest(WORKSPACE / "schema.cedarschema"),
          "decision_sha256": digest(DECISION), "approval_record": approval,
          "completion": {"argv": completion_argv, "exit_code": completion.returncode,
                         "stdout": completion.stdout, "stderr": completion.stderr,
                         "completed": completed},
          "verify": {"argv": verify_argv, "exit_code": verify.returncode,
                     "stdout": verify.stdout, "stderr": verify.stderr},
          "authorize": {"argv": authorize_argv, "exit_code": authorize.returncode,
                        "stdout": authorize.stdout, "stderr": authorize.stderr,
                        "decision": decision},
          "effects": effects,
          "predicted": (completed and verify.returncode == 0 and not approval["approved"]
                        and decision == "ALLOW" and
                        [x["effect_delta"] for x in effects] == [1, 0])}
(HERE / "raw.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"completed": completed, "approval": approval["approved"],
                  "verify_exit": verify.returncode, "authorize": decision,
                  "effects": [(x["arm"], x["effect_delta"]) for x in effects],
                  "predicted": result["predicted"]}))
if not result["predicted"]:
    raise SystemExit(1)
