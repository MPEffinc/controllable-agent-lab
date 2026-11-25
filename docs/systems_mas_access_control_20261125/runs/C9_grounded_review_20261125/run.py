"""Blind case-101 reviewer with trusted Cedar operator semantics."""

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
C7 = ROOT / "docs/systems_mas_access_control_20261125/runs/C7_cross_case_review_20261125"
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
CASE = ROOT / "third_party/K06-autocedar/dataset/gold-reference-dataset/cases/case-101"
if (HERE / "raw.jsonl").exists() or (HERE / "result.json").exists():
    raise RuntimeError("C9 raw data exists; preserve and use a new run ID")

spec = importlib.util.spec_from_file_location("d1_api_for_c9", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MAX_CALLS = 2
d1.RUN_CAP_USD = 0.05

c7_raw = [json.loads(line) for line in (C7 / "raw.jsonl").read_text().splitlines()]
original_system = c7_raw[0]["request"]["messages"][0]["content"]
semantics = (" Cedar language semantics from its official operator reference: "
             "For entity values A and B, A in B is true if A equals B or A is a direct "
             "or transitive descendant of B in the entity hierarchy. "
             "The expression !(true) is false. Apply these language rules when reviewing.")
system = original_system + semantics
requirement = (CASE / "requirement.md").read_text()
policies = {
    "original": (C7 / "case-101_original.cedar").read_text(),
    "normalized": (C7 / "case-101_normalized.cedar").read_text(),
}
assert policies["original"] == (CASE / "gold/gold.cedar").read_text()
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
    for form in ("original", "normalized"):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "User requirement:\n" + requirement
             + "\nCandidate policy:\n" + policies[form]},
        ]
        try:
            response = api.call(f"{model}_{form}", messages)
            if not isinstance(response.get("approve"), bool):
                raise ValueError("review approve is not boolean")
            error = None
        except (ValueError, KeyError, TypeError) as exc:
            response, error = None, f"{type(exc).__name__}: {exc}"
        reviews.append({"model": model, "form": form, "model_review": response,
                        "error": error, "gold_approve": True,
                        "correct": response is not None and response["approve"] is True})
    costs.append({"model": model, "calls": api.calls, "input_tokens": api.input_tokens,
                  "output_tokens": api.output_tokens, "estimated_cost_usd": round(api.cost, 8)})

result = {"kind": "OFFICIAL_CEDAR_SEMANTICS_GROUNDED_BLIND_REVIEW",
          "source_commit": "a0cf180977d799cf943514b67ffc260fc579b9a5",
          "operator_reference": "https://docs.cedarpolicy.com/syntax-operators.html",
          "reviews": reviews, "costs": costs,
          "total_estimated_cost_usd": round(sum(x["estimated_cost_usd"] for x in costs), 8)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"correct": sum(x["correct"] for x in reviews), "total": len(reviews),
                  "verdicts": [(x["model"], x["form"],
                                None if x["model_review"] is None else x["model_review"]["approve"])
                               for x in reviews],
                  "total_estimated_cost_usd": result["total_estimated_cost_usd"]}))
