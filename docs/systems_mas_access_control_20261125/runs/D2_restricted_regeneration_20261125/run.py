"""Independent restricted-context replay of the fixed D1 A/B prompts."""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D1 = ROOT / "docs/systems_mas_access_control_20261125/runs/D1_live_writeback_20261125"
if (HERE / "raw.jsonl").exists() or (HERE / "service_state.sqlite").exists():
    raise RuntimeError("D2 raw data already exists; preserve it")

spec = importlib.util.spec_from_file_location("d1_runtime_for_d2", D1 / "run.py")
assert spec and spec.loader
d1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d1
spec.loader.exec_module(d1)
d1.HERE = HERE  # reuse identical model settings and logging in separate D2 directory

d1_calls = [json.loads(line) for line in (D1 / "raw.jsonl").read_text().splitlines()]
assert [x["phase"] for x in d1_calls] == [
    "agent_A_writeback", "agent_B_1_reviewers", "agent_B_2_reviewers"]
messages_a = json.loads(json.dumps(d1_calls[0]["request"]["messages"]))
body_a = json.loads(messages_a[1]["content"])
removed = body_a.pop("tool_record")
assert removed["id"] == "r1"
messages_a[1]["content"] = json.dumps(body_a)

api = d1.API()
journal = api.call("agent_A_regenerate_r2_only", messages_a)
if not isinstance(journal.get("fact"), str) or not isinstance(journal.get("support_ids"), list):
    raise ValueError("regenerated journal schema invalid")

records = [
    {"id": "r1", "fact": removed["text"],
     "created_at": "2026-01-01T00:00:00Z", "revoked_at": "2026-02-01T00:00:00Z"},
    {"id": "j1", "fact": journal["fact"], "created_at": "2026-11-25T00:00:00Z"},
]
guarded = d1.guard(records)
kept = [record["id"] for record in guarded.kept]
ancestry = {"j1": ["r2"]}
proposals = []
for i, count in enumerate((1, 2), start=1):
    messages_b = json.loads(json.dumps(d1_calls[i]["request"]["messages"]))
    body_b = json.loads(messages_b[1]["content"])
    assert body_b["request"]["independent_reviewers"] == count
    body_b["journal"] = journal["fact"]
    messages_b[1]["content"] = json.dumps(body_b)
    proposal = api.call(f"agent_B_{count}_reviewers_regenerated", messages_b)
    if not isinstance(proposal.get("approve"), bool) or proposal.get("approver_count") != count:
        raise ValueError("agent B proposal schema/count invalid")
    proposals.append({"requested_approvers": count, "proposal": proposal})

effects = []
with sqlite3.connect(HERE / "service_state.sqlite") as db:
    db.execute("CREATE TABLE effects(id INTEGER PRIMARY KEY, arm TEXT, request_id TEXT, "
               "approvers INTEGER, resource TEXT)")
    for item in proposals:
        count = item["requested_approvers"]
        requested = bool(item["proposal"]["approve"])
        request_id = f"{count}_reviewer"
        effects.append(d1.commit(db, "restricted_lineage", request_id, count,
                                 requested and "j1" in kept and "r1" not in ancestry["j1"]))
        effects.append(d1.commit(db, "current_service_pep", request_id, count,
                                 requested and count >= 2))

result = {"kind": "INDEPENDENT_RESTRICTED_CONTEXT_REGENERATION",
          "d1_source": str(D1.relative_to(ROOT)),
          "removed_source_id": "r1", "trusted_source_id": "r2",
          "regenerated_journal": journal, "code_owned_ancestry": ancestry,
          "m4_guard_kept_ids": kept, "m4_guard_withheld": guarded.withheld,
          "agent_B_proposals": proposals, "effects": effects,
          "input_tokens": api.input_tokens, "output_tokens": api.output_tokens,
          "estimated_cost_usd": round(api.cost, 8)}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"calls": api.calls, "estimated_cost_usd": result["estimated_cost_usd"],
                  "journal": journal, "proposals": proposals,
                  "effects": [(r["arm"], r["request_id"], r["effect_delta"])
                              for r in effects]}))
