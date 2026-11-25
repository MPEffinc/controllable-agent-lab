"""Replay exact C4 blind policy-review messages using gpt-4.1."""

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
C4 = ROOT / "docs/systems_mas_access_control_20261125/runs/C4_blind_policy_review_20261125"
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
if (HERE / "raw.jsonl").exists() or (HERE / "result.json").exists():
    raise RuntimeError("C5 raw data exists; use a new run ID")

spec = importlib.util.spec_from_file_location("d1_api_for_c5", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE
d1.MODEL = "gpt-4.1-2025-04-14"
d1.INPUT_PER_M = 2.00
d1.OUTPUT_PER_M = 8.00
d1.MAX_CALLS = 7
d1.RUN_CAP_USD = 0.05
api = d1.API()

c4 = json.loads((C4 / "result.json").read_text())
raw = [json.loads(line) for line in (C4 / "raw.jsonl").read_text().splitlines()]
order = c4["order"]
assert [entry["phase"] for entry in raw] == [f"review_{policy_id}" for policy_id in order]
reviews = []
for policy_id, entry in zip(order, raw):
    # Only the C4 input messages are replayed; prior responses and gold stay hidden.
    messages = entry["request"]["messages"]
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

summary = {"kind": "STRONGER_MODEL_SAME_BLIND_POLICY_REVIEW",
           "c4_source": str(C4.relative_to(ROOT)),
           "model": d1.MODEL, "seed": d1.SEED, "temperature": 0,
           "order": order, "reviews": reviews,
           "review_correct": sum(x["correct"] for x in reviews),
           "c4_review_correct": c4["review_correct"],
           "c4_verify_correct": c4["verify_correct"],
           "input_tokens": api.input_tokens, "output_tokens": api.output_tokens,
           "estimated_cost_usd": round(api.cost, 8)}
(HERE / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"model": d1.MODEL, "review_correct": summary["review_correct"],
                  "errors": [(x["policy_id"], x["model_review"])
                             for x in reviews if not x["correct"]],
                  "input_tokens": api.input_tokens, "output_tokens": api.output_tokens,
                  "estimated_cost_usd": summary["estimated_cost_usd"]}))
