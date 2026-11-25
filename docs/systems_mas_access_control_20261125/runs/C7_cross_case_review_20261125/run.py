"""Preregistered official gold review before and after false-OR normalization."""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "third_party/K06-autocedar"
CASES = SOURCE / "dataset/gold-reference-dataset/cases"
ENV = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env"
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
PYTHON = ENV / "venv/bin/python"
MARKER = "(!(true) || "
SELECTED = ("case-001", "case-052", "case-101", "case-151")
REQUEST_ENV = {
    "case-001": ("User", 'Action::"executeContract"', "Contract"),
    "case-052": ("User", 'Action::"sendCommand"', "Device"),
    "case-101": ("User", 'Action::"approveClearToClose"', "EscrowFile"),
    "case-151": ("User", 'Action::"launchCampaign"', "Campaign"),
}
if (HERE / "raw.jsonl").exists() or (HERE / "result.json").exists():
    raise RuntimeError("C7 raw data exists; preserve and use a new run ID")

spec = importlib.util.spec_from_file_location("d1_api_for_c7", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MAX_CALLS = 8
d1.RUN_CAP_USD = 0.10

def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()

def normalize_false_or(source):
    output = source
    changes = 0
    while MARKER in output:
        start = output.index(MARKER)
        depth = 0
        end = None
        for offset in range(start, len(output)):
            if output[offset] == "(":
                depth += 1
            elif output[offset] == ")":
                depth -= 1
                if depth == 0:
                    end = offset
                    break
        if end is None:
            raise ValueError("unbalanced false-OR expression")
        remainder = output[start + len(MARKER):end]
        if not remainder:
            raise ValueError("false-OR has no remainder")
        output = output[:start] + "(" + remainder + ")" + output[end + 1:]
        changes += 1
    return output, changes

files = sorted(CASES.glob("case-*/gold/gold.cedar"))
assert len(files) == 200
with_marker = [f for f in files if MARKER in f.read_text()]
assert len(with_marker) == 184
chosen = []
for lo, hi in ((1, 50), (51, 100), (101, 150), (151, 200)):
    eligible = [f for f in with_marker if lo <= int(f.parent.parent.name[-3:]) <= hi]
    chosen.append(eligible[0].parent.parent.name)
assert tuple(chosen) == SELECTED

policies = {}
for case_id in SELECTED:
    case = CASES / case_id
    original = (case / "gold/gold.cedar").read_text()
    principal_type, action, resource_type = REQUEST_ENV[case_id]
    assert original.splitlines()[0] == (
        f"permit (principal is {principal_type}, action == {action}, resource is {resource_type})")
    normalized, changes = normalize_false_or(original)
    assert changes >= 1 and normalized != original
    requirement = (case / "requirement.md").read_text()
    (HERE / f"{case_id}_original.cedar").write_text(original)
    (HERE / f"{case_id}_normalized.cedar").write_text(normalized)
    policies[case_id] = {"requirement": requirement, "original": original,
                         "normalized": normalized, "rewrites": changes,
                         "requirement_sha256": sha(requirement),
                         "original_sha256": sha(original),
                         "normalized_sha256": sha(normalized)}

env = os.environ.copy()
env.update({"PYTHONPATH": str(SOURCE), "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "CEDAR": str(ENV / "cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"),
            "CVC5": str(ENV / "cvc5")})
verifications = []
for case_id in SELECTED:
    workspace = HERE / f"verify_{case_id}"
    workspace.mkdir(exist_ok=False)
    (workspace / "candidate.cedar").write_text(policies[case_id]["normalized"])
    (workspace / "reference.cedar").write_text(policies[case_id]["original"])
    (workspace / "schema.cedarschema").write_bytes(
        (CASES / case_id / "gold/schema.cedarschema").read_bytes())
    plan = """from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = COMMON_HERE
    return [
        dict(common, name="normalized_implies_original", description="No extra permission",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="original_implies_normalized", description="No false denial",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
"""
    principal_type, action, resource_type = REQUEST_ENV[case_id]
    plan = plan.replace("COMMON_HERE", repr({"principal_type": principal_type,
                                            "action": action, "resource_type": resource_type}))
    (workspace / "verification_plan.py").write_text(plan)
    argv = [str(PYTHON), "-c", "import sys; from autocedar.cli import main; sys.exit(main())",
            "verify", str(workspace)]
    p = subprocess.run(argv, cwd=HERE, env=env, text=True,
                       capture_output=True, timeout=90, check=False)
    verifications.append({"case_id": case_id, "argv": argv, "exit_code": p.returncode,
                          "stdout": p.stdout, "stderr": p.stderr})
    if p.returncode != 0:
        (HERE / "verification_failure.json").write_text(json.dumps(verifications, indent=2) + "\n")
        raise RuntimeError(f"formal equivalence not verified for {case_id}; no model calls")

system = ("Review whether the candidate Cedar policy grants exactly the permissions "
          "stated by the user requirement, including both allowed and denied requests. "
          "Return only JSON with keys approve (boolean) and reason (string). "
          "Reject a policy if it is too broad or too restrictive. Treat the code as "
          "a single Cedar permit policy; no other permits exist. Do not assume omitted "
          "conditions are enforced elsewhere.")
order = (("case-001", "original"), ("case-001", "normalized"),
         ("case-052", "normalized"), ("case-052", "original"),
         ("case-101", "original"), ("case-101", "normalized"),
         ("case-151", "normalized"), ("case-151", "original"))
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
    for case_id, form in order:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "User requirement:\n" + policies[case_id]["requirement"]
             + "\nCandidate policy:\n" + policies[case_id][form]},
        ]
        try:
            response = api.call(f"{model}_{case_id}_{form}", messages)
            if not isinstance(response.get("approve"), bool):
                raise ValueError("review approve is not boolean")
            error = None
        except (ValueError, KeyError, TypeError) as exc:
            response, error = None, f"{type(exc).__name__}: {exc}"
        reviews.append({"model": model, "case_id": case_id, "form": form,
                        "model_review": response, "error": error,
                        "gold_approve": True,
                        "correct": response is not None and response["approve"] is True})
    costs.append({"model": model, "calls": api.calls, "input_tokens": api.input_tokens,
                  "output_tokens": api.output_tokens, "estimated_cost_usd": round(api.cost, 8)})

result = {"kind": "CROSS_CASE_FORMAL_EQUIVALENCE_AND_BLIND_GOLD_REVIEW",
          "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
          "corpus_gold_cases": len(files), "corpus_false_or_cases": len(with_marker),
          "selected": chosen,
          "policies": {case_id: {key: value for key, value in detail.items()
                                if key.endswith("sha256") or key == "rewrites"}
                       for case_id, detail in policies.items()},
          "verifications": verifications, "order": order, "reviews": reviews, "costs": costs,
          "total_estimated_cost_usd": round(sum(row["estimated_cost_usd"] for row in costs), 8)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"verified": len(verifications), "selected": chosen,
                  "verdicts": [(r["model"], r["case_id"], r["form"], r["model_review"]["approve"])
                               for r in reviews], "costs": costs,
                  "total_estimated_cost_usd": result["total_estimated_cost_usd"]}))
