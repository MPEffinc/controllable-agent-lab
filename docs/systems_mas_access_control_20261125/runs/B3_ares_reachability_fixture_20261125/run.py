#!/usr/bin/env python3
"""Independent formal ARP fixture based on ARES §III.2; not author code."""

import json
import sqlite3
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "raw.jsonl"


def state(db):
    return {
        "db1_private_value": db.execute("select value from private where id=1").fetchone()[0],
        "db2_public_value": db.execute("select value from public where id=1").fetchone()[0],
    }


def run_case(arm, branch):
    with tempfile.TemporaryDirectory(prefix="ares_arp_fixture_") as temp:
        db = sqlite3.connect(str(Path(temp) / "service.sqlite"))
        db.execute("create table private(id integer primary key, value text)")
        db.execute("create table public(id integer primary key, value text)")
        db.execute("insert into private values (1, 'before')")
        db.execute("insert into public values (1, 'public_ok')")
        db.commit()
        before = state(db)

        # Paper §III.2: User Invoke(U,F) ∧ User Deny(U,DB1) ∧ Reach(F,DB1).
        user_invoke = True
        user_deny_db1 = True
        service_reach_db1 = True
        arp_bypass = user_invoke and user_deny_db1 and service_reach_db1

        if arm == "relation_only_preflight" and arp_bypass:
            decision, completed, observation = "BLOCK_PRE_INVOKE", False, None
        elif arm == "origin_aware_effect_pep" and branch == "write_db1" and user_deny_db1:
            decision, completed, observation = "BLOCK_AT_EFFECT", False, None
        elif branch == "read_public":
            observation = db.execute("select value from public where id=1").fetchone()[0]
            decision, completed = "ALLOW", True
        else:
            db.execute("update private set value='after' where id=1")
            db.commit()
            decision, completed, observation = "ALLOW", True, "wrote_db1"

        after = state(db)
        db.close()
        return {
            "arm": arm,
            "branch": branch,
            "actor": "U",
            "function": "F",
            "user_invoke": user_invoke,
            "user_deny_db1": user_deny_db1,
            "service_reach_db1": service_reach_db1,
            "arp_bypass_relation": arp_bypass,
            "decision": decision,
            "completed": completed,
            "observation": observation,
            "before": before,
            "after": after,
            "unauthorized_db1_effect": before["db1_private_value"] != after["db1_private_value"],
        }


rows = [
    run_case(arm, branch)
    for arm in ("no_origin_guard", "relation_only_preflight", "origin_aware_effect_pep")
    for branch in ("read_public", "write_db1")
]
OUT.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
for row in rows:
    print(row["arm"], row["branch"], row["decision"], row["completed"], row["unauthorized_db1_effect"])
