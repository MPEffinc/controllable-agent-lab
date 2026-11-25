"""Replay only C10 unrelated inputs with complete hierarchy facts."""

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
C10 = ROOT / "docs/systems_mas_access_control_20261125/runs/C10_oracle_refinement_bias_20261125"
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
if (HERE / "raw.jsonl").exists() or (HERE / "result.json").exists():
    raise RuntimeError("C10b raw data exists; preserve and use a new run ID")

spec = importlib.util.spec_from_file_location("d1_api_for_c10b", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MAX_CALLS = 2
d1.RUN_CAP_USD = 0.05

raw = [json.loads(line) for line in (C10 / "raw.jsonl").read_text().splitlines()]
inputs = {}
for row in raw:
    phase = row["phase"]
    if "_unrelated_" in phase:
        model, arm = phase.split("_unrelated_")
        inputs[(model, arm)] = row["request"]["messages"]
assert len(inputs) == 4
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
    for arm in ("blind", "exposed"):
        prior_messages = inputs[(model, arm)]
        user = json.loads(prior_messages[1]["content"])
        facts = user["request_facts"]
        facts["group_parent_edges_are_complete"] = True
        facts["south_parent_group"] = None
        facts["south_is_not_root"] = True
        messages = [prior_messages[0], {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]
        try:
            response = api.call(f"{model}_{arm}", messages)
            if response.get("decision") not in ("ALLOW", "DENY"):
                raise ValueError("oracle decision invalid")
            error = None
        except (ValueError, KeyError, TypeError) as exc:
            response, error = None, f"{type(exc).__name__}: {exc}"
        reviews.append({"model": model, "arm": arm, "gold_expected": "DENY",
                        "response": response, "error": error,
                        "correct": response is not None and response["decision"] == "DENY"})
    costs.append({"model": model, "calls": api.calls, "input_tokens": api.input_tokens,
                  "output_tokens": api.output_tokens, "estimated_cost_usd": round(api.cost, 8)})

result = {"kind": "C10_UNRELATED_COMPLETE_HIERARCHY_FACT_CONTROL",
          "c10_source": str(C10.relative_to(ROOT)), "reviews": reviews, "costs": costs,
          "total_estimated_cost_usd": round(sum(x["estimated_cost_usd"] for x in costs), 8)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"correct": sum(row["correct"] for row in reviews), "total": len(reviews),
                  "verdicts": [(row["model"], row["arm"],
                                None if row["response"] is None else row["response"]["decision"])
                               for row in reviews],
                  "total_estimated_cost_usd": result["total_estimated_cost_usd"]}))
