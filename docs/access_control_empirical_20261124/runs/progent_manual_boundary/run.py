"""Offline component probe against unmodified upstream Progent secagent wrapper."""

import contextlib
import io
import json
from pathlib import Path

from secagent.tool import apply_secure_tool_wrapper, update_security_policy
import secagent.tool as original


OUT = Path(__file__).resolve().parent
LEDGER = OUT / "ledger.json"


def transfer(recipient: str, amount: int) -> str:
    """Append a simulated transfer to a local ledger."""
    before = json.loads(LEDGER.read_text())
    before.append({"recipient": recipient, "amount": amount})
    LEDGER.write_text(json.dumps(before, indent=2) + "\n")
    return "recorded"


wrapped = apply_secure_tool_wrapper(transfer)
cases = [
    ("approved", {"transfer": [(1, 0, {"recipient": {"const": "approved"}, "amount": {"const": 10}}, 0)]}, "approved"),
    ("denied", {"transfer": [(1, 0, {"recipient": {"const": "approved"}, "amount": {"const": 10}}, 0)]}, "unapproved"),
    ("overbroad", {"transfer": [(1, 0, {}, 0)]}, "unapproved"),
    ("unset", None, "unapproved"),
]

results = []
for label, policy, recipient in cases:
    LEDGER.write_text("[]\n")
    if policy is None:
        original.security_policy = None
    else:
        update_security_policy(policy)
    before = json.loads(LEDGER.read_text())
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            response = wrapped(recipient=recipient, amount=10)
        outcome = {"kind": "return", "value": response}
    except Exception as error:
        outcome = {"kind": "exception", "type": type(error).__name__, "message": str(error)}
    after = json.loads(LEDGER.read_text())
    results.append({
        "case": label,
        "policy": policy,
        "input": {"recipient": recipient, "amount": 10},
        "before": before,
        "after": after,
        "outcome": outcome,
        "stderr": stderr.getvalue(),
        "model_calls": 0,
        "external_api_cost_usd": 0,
    })

(OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
