"""Fixed C4 policies, verified semantic normalization, two blind model reviews."""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
C4 = ROOT / "docs/systems_mas_access_control_20261125/runs/C4_blind_policy_review_20261125"
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
SOURCE = ROOT / "third_party/K06-autocedar"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
PYTHON = ENV / "venv/bin/python"
CEDAR = ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
CVC5 = ENV / "cvc5"
if any((HERE / name).exists() for name in ("raw.jsonl", "result.json")):
    raise RuntimeError("C6 raw data already exists; preserve and use a new run ID")

spec = importlib.util.spec_from_file_location("d1_api_for_c6", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MAX_CALLS = 7
d1.RUN_CAP_USD = 0.08

c4 = json.loads((C4 / "result.json").read_text())
raw = [json.loads(line) for line in (C4 / "raw.jsonl").read_text().splitlines()]
order = c4["order"]
assert len(raw) == len(order) == 7
assert [entry["phase"] for entry in raw] == [f"review_{policy_id}" for policy_id in order]

policies = {}
for policy_id in ("p0", "p1", "p2", "p3", "p4", "p5", "p6"):
    original = (C4 / f"{policy_id}.cedar").read_text()
    normalized = original.replace("(!(true) || (principal != resource.author))",
                                  "(principal != resource.author)")
    if "approvalCount >= 1" in normalized or "approvalCount >= 2" in normalized:
        old = "(((resource.approvalCount >= 0)) && "
        assert normalized.count(old) == 1, policy_id
        normalized = normalized.replace(old, "")
    assert normalized != original, policy_id
    (HERE / f"{policy_id}.cedar").write_text(normalized)
    policies[policy_id] = {"original": original, "normalized": normalized,
                           "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
                           "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest()}

env = os.environ.copy()
env.update({"PYTHONPATH": str(SOURCE), "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "CEDAR": str(CEDAR), "CVC5": str(CVC5)})
verifications = []
for policy_id in policies:
    workspace = HERE / f"verify_{policy_id}"
    workspace.mkdir(exist_ok=False)
    (workspace / "candidate.cedar").write_text(policies[policy_id]["normalized"])
    (workspace / "reference.cedar").write_text(policies[policy_id]["original"])
    (workspace / "schema.cedarschema").write_bytes(
        (C4 / f"verify_{policy_id}/schema.cedarschema").read_bytes())
    plan = '''from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = {"principal_type": "User", "action": 'Action::"mergePullRequest"',
              "resource_type": "PullRequest"}
    return [
        dict(common, name="normalized_implies_original", description="No new permission",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="original_implies_normalized", description="No new false denial",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
'''
    (workspace / "verification_plan.py").write_text(plan)
    argv = [str(PYTHON), "-c", "import sys; from autocedar.cli import main; sys.exit(main())",
            "verify", str(workspace)]
    p = subprocess.run(argv, cwd=HERE, env=env, text=True,
                       capture_output=True, timeout=60, check=False)
    verifications.append({"policy_id": policy_id, "argv": argv, "exit_code": p.returncode,
                          "stdout": p.stdout, "stderr": p.stderr})
    if p.returncode != 0:
        (HERE / "verification_failure.json").write_text(json.dumps(verifications, indent=2) + "\n")
        raise RuntimeError(f"normalization not verified for {policy_id}; no model calls")

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
    for policy_id, entry in zip(order, raw):
        original_messages = entry["request"]["messages"]
        assert len(original_messages) == 2
        head, separator, original_policy = original_messages[1]["content"].partition("\nCandidate policy:\n")
        assert separator and original_policy == policies[policy_id]["original"]
        messages = [original_messages[0],
                    {"role": "user", "content": head + separator + policies[policy_id]["normalized"]}]
        try:
            response = api.call(f"{model}_review_{policy_id}", messages)
            if not isinstance(response.get("approve"), bool):
                raise ValueError("review approve is not boolean")
            error = None
        except (ValueError, KeyError, TypeError) as exc:
            response, error = None, f"{type(exc).__name__}: {exc}"
        reviews.append({"model": model, "policy_id": policy_id, "gold_approve": policy_id == "p0",
                        "model_review": response, "error": error,
                        "correct": response is not None and response["approve"] == (policy_id == "p0")})
    costs.append({"model": model, "calls": api.calls, "input_tokens": api.input_tokens,
                  "output_tokens": api.output_tokens, "estimated_cost_usd": round(api.cost, 8)})

result = {"kind": "VERIFIED_NORMALIZATION_BLIND_POLICY_REVIEW",
          "source_commit": c4["source_commit"], "order": order,
          "policies": {policy_id: {key: value for key, value in details.items()
                                   if key.endswith("sha256")}
                       for policy_id, details in policies.items()},
          "verifications": verifications, "reviews": reviews,
          "review_correct": {model: sum(row["correct"] for row in reviews if row["model"] == model)
                             for model in ("gpt-4.1-mini-2025-04-14", "gpt-4.1-2025-04-14")},
          "costs": costs,
          "total_estimated_cost_usd": round(sum(row["estimated_cost_usd"] for row in costs), 8)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"verified": len(verifications), "review_correct": result["review_correct"],
                  "errors": [(row["model"], row["policy_id"]) for row in reviews if not row["correct"]],
                  "costs": costs, "total_estimated_cost_usd": result["total_estimated_cost_usd"]}))
