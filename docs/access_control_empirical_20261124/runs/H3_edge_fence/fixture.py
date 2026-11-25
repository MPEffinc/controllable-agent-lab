#!/usr/bin/env python3
"""H3 local schedules: original VERA target_set_l2 plus independent atomic sink.

This is an abstract, deterministic counterexample/control fixture, not a
reproduction of VERA, Authorization Revocation, or a remote provider.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
import types
from pathlib import Path
from threading import RLock

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
VERA_SRC = REPO / "third_party/vera-artifact-anon/src"
sys.path.insert(0, str(VERA_SRC))

# The artifact package __init__ eagerly imports crypto/Ed25519, while this
# experiment uses only two dependency-free original modules. Preserve their
# relative imports without executing the unrelated package initializer.
vera_package = types.ModuleType("revocation")
vera_package.__path__ = [str(VERA_SRC / "revocation")]
sys.modules["revocation"] = vera_package

from revocation.dag import AgentNode, DelegationDAG, DelegationEdge  # noqa: E402
from revocation.granularity import target_set_l2  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph(with_x: bool) -> DelegationDAG:
    dag = DelegationDAG()
    for name in (["R", "A", "C", "X"] if with_x else ["R", "A", "C"]):
        dag.add_node(AgentNode(name, "synthetic_deployer"))
    for edge_id, parent, child in [("r_a", "R", "A"), ("a_c", "A", "C")]:
        dag.add_edge(DelegationEdge(edge_id, parent, child))
    if with_x:
        dag.add_edge(DelegationEdge("x_c", "X", "C"))
    return dag


class AtomicSink:
    """Single-lock acceptance, fence, and settlement over an in-memory ledger."""

    def __init__(self, *, stale: bool = False):
        self.lock = RLock()
        self.edges = {"r_a", "a_c", "x_c"}
        self.generation = 0
        self.receipts: dict[str, dict] = {}
        self.effects: list[dict] = []
        self.events: list[dict] = []
        self.stale = stale

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "active_edges": sorted(self.edges),
                "fence_generation": self.generation,
                "receipts": {key: value.copy() for key, value in sorted(self.receipts.items())},
                "effects": [item.copy() for item in self.effects],
            }

    def revoke(self, edge: str) -> None:
        with self.lock:
            assert edge in self.edges
            self.edges.remove(edge)
            self.generation += 1
            self.events.append({"event": "revoke_and_fence", "edge": edge, "generation": self.generation})

    def accept(self, request_id: str, *, allowed: tuple[frozenset[str], ...],
               selected: frozenset[str], action: str = "write:fixture_object") -> bool:
        with self.lock:
            if request_id in self.receipts:
                raise ValueError("duplicate request_id")
            digest = hashlib.sha256(action.encode()).hexdigest()
            if selected not in allowed:
                reason = "selected_witness_not_in_policy"
            elif not self.stale and not selected.issubset(self.edges):
                reason = "selected_witness_revoked_at_fence"
            else:
                reason = "accepted"
                self.receipts[request_id] = {
                    "selected_witness": sorted(selected),
                    "action_digest": digest,
                    "accepted_generation": self.generation,
                    "settled": False,
                    "stale_control": self.stale,
                }
            self.events.append({
                "event": "accept_decision", "request_id": request_id,
                "selected_witness": sorted(selected), "generation": self.generation,
                "reason": reason, "receipt_created": reason == "accepted",
            })
            return reason == "accepted"

    def settle(self, request_id: str) -> None:
        with self.lock:
            receipt = self.receipts[request_id]
            if receipt["settled"]:
                raise ValueError("duplicate settlement")
            receipt["settled"] = True
            kind = ("pre_fence_receipt_settled_later"
                    if receipt["accepted_generation"] < self.generation
                    else "current_generation_receipt")
            effect = {
                "request_id": request_id, "action_digest": receipt["action_digest"],
                "accepted_generation": receipt["accepted_generation"],
                "settled_generation": self.generation, "classification": kind,
            }
            self.effects.append(effect)
            self.events.append({"event": "effect_settled", **effect})


A_ONLY = (frozenset({"a_c"}),)
AND = (frozenset({"a_c", "x_c"}),)
OR = (frozenset({"a_c"}), frozenset({"x_c"}))


def run() -> dict:
    started = time.perf_counter()
    vera = {
        "target_without_alternate_x": sorted(target_set_l2(graph(False), "a_c")),
        "target_with_alternate_x": sorted(target_set_l2(graph(True), "a_c")),
        "original_function": "revocation.granularity.target_set_l2",
    }
    assert vera["target_without_alternate_x"] == ["C"]
    assert vera["target_with_alternate_x"] == []

    s1 = AtomicSink()
    s1_before = s1.snapshot()
    assert s1.accept("s1_old_A", allowed=A_ONLY, selected=frozenset({"a_c"}))
    s1_receipt = s1.snapshot()
    s1.revoke("a_c")
    s1_fenced = s1.snapshot()
    s1.settle("s1_old_A")
    assert not s1.accept("s1_new_A", allowed=A_ONLY, selected=frozenset({"a_c"}))
    assert len(s1.effects) == 1
    assert s1.effects[0]["classification"] == "pre_fence_receipt_settled_later"

    s2 = AtomicSink()
    s2.revoke("a_c")
    s2_before = s2.snapshot()
    a_accepted = s2.accept("s2_A", allowed=A_ONLY, selected=frozenset({"a_c"}))
    and_accepted = s2.accept("s2_AND", allowed=AND, selected=frozenset({"a_c", "x_c"}))
    assert not a_accepted and not and_accepted
    assert not s2.receipts and not s2.effects

    s3 = AtomicSink()
    s3.revoke("a_c")
    s3_before = s3.snapshot()
    assert s3.accept("s3_X", allowed=OR, selected=frozenset({"x_c"}))
    s3.settle("s3_X")
    assert len(s3.effects) == 1
    assert s3.receipts["s3_X"]["selected_witness"] == ["x_c"]

    negative = AtomicSink(stale=True)
    negative.revoke("a_c")
    negative_before = negative.snapshot()
    assert negative.accept("negative_stale_A", allowed=A_ONLY, selected=frozenset({"a_c"}))
    negative.settle("negative_stale_A")
    assert len(negative.effects) == 1

    return {
        "method": "original VERA L2 target function + independent deterministic in-memory sink",
        "vera_original_component": vera,
        "schedules": {
            "S1_pre_fence_receipt": {"before": s1_before, "after_accept": s1_receipt,
                                     "after_fence_before_settle": s1_fenced,
                                     "after": s1.snapshot(), "events": s1.events},
            "S2_post_fence_deny": {"before": s2_before, "after": s2.snapshot(),
                                   "events": s2.events},
            "S3_independent_OR": {"before": s3_before, "after": s3.snapshot(),
                                  "events": s3.events},
            "negative_stale_control": {"before": negative_before,
                                       "after": negative.snapshot(), "events": negative.events},
        },
        "environment": {
            "python": platform.python_version(), "platform": platform.platform(),
            "fixture_sha256": sha(HERE / "fixture.py"),
            "vera_granularity_sha256": sha(VERA_SRC / "revocation/granularity.py"),
            "vera_dag_sha256": sha(VERA_SRC / "revocation/dag.py"),
            "model_calls": 0, "api_calls": 0, "estimated_external_cost_usd": 0,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        },
        "assertions": "all_passed",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
