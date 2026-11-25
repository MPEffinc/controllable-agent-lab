"""Small offline query of upstream Progent generated-policy subset function."""

import contextlib
import io
import json
from pathlib import Path

from secagent.policy_analysis import security_policy_subset_check


OUT = Path(__file__).resolve().parent


def policy(tool, values):
    return {tool: [(100, 0, {"recipient": {"type": "string", "enum": values}}, 0)]}


old = policy("transfer", ["approved", "second"])
cases = [
    ("identical", old),
    ("narrow", policy("transfer", ["approved"])),
    ("wide", policy("transfer", ["approved", "second", "unapproved"])),
    ("new_tool", {**old, **policy("export", ["approved"])}),
]
results = []
for name, new in cases:
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        decision = security_policy_subset_check(old, new)
    results.append({"case": name, "old": old, "new": new, "subset": decision, "stderr": err.getvalue(), "model_calls": 0, "external_api_cost_usd": 0})

(OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps([{"case": x["case"], "subset": x["subset"]} for x in results], indent=2))
