"""Offline MAP-Graph gate contrast and archived metric threshold projection.

The script imports original source files without executing the package's eager
model-client import. It never invokes a network or model endpoint.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType


def load_source(artifact: Path):
    for name in ("src", "src.map_graph", "src.memory_baselines"):
        module = ModuleType(name)
        module.__path__ = [str(artifact / name.replace(".", "/"))]
        sys.modules[name] = module

    def one(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    base = one("src.memory_baselines.base", artifact / "src/memory_baselines/base.py")
    trust = one("src.map_graph.trust", artifact / "src/map_graph/trust.py")
    return base.MemoryRecord, trust.TrustResult, trust.MAPGraphTrustEngine


def record_trust(TrustResult, score: float, revoked: bool):
    ancestors = ["revoked_source"] if revoked else []
    return TrustResult(
        trust=score,
        source_trust=score,
        path_integrity=1.0,
        transformation_factor=1.0,
        permission_validity=1.0,
        verification_bonus=1.0,
        agent_reliability=1.0,
        transformation_loss=0.0,
        affected_ancestors=ancestors,
        contamination_reasons={},
        untrusted_ancestors=[],
        private_ancestors=[],
        revoked_ancestors=ancestors,
    )


def public_task(raw: dict) -> dict:
    action = dict(raw.get("expected_action") or {})
    for key in ("expected_decision", "ground_truth_decision", "should_block"):
        action.pop(key, None)
    return {"task_id": raw["task_id"], "expected_action": action}


def bound_action(action: dict, task: dict) -> dict:
    expected = task["expected_action"]
    return {
        **action,
        "action_type": expected.get("action_type") or expected.get("type"),
        "risk_level": expected["risk_level"],
    }


def component(artifact: Path, out_dir: Path, MemoryRecord, TrustResult, Engine) -> None:
    raw_task = json.loads((artifact / "data/final_tasks/corp_exp5_041.json").read_text())
    exp5 = public_task(raw_task)
    normal = {
        "task_id": "synthetic_normal_send_email",
        "expected_action": {"type": "send_email", "action_type": "send_email", "risk_level": "high"},
    }
    cases = (
        ("correct_high", exp5, {"action_type": "send_email", "risk_level": "high"}, 0.76, False, "BLOCK"),
        ("same_type_risk_downgrade", exp5, {"action_type": "send_email", "risk_level": "medium"}, 0.76, False, "BLOCK"),
        ("normal_high_trust", normal, {"action_type": "send_email", "risk_level": "high"}, 0.95, False, "ALLOW"),
        ("revoked_ancestor_control", exp5, {"action_type": "send_email", "risk_level": "high"}, 0.95, True, "BLOCK"),
    )
    engine = Engine()
    decisions = []
    effects = []
    for case, task, metadata, score, revoked, expected in cases:
        support = MemoryRecord(memory_id="synthetic_support", content="Synthetic support; no real personal data", owner_agent="executor")
        support_trust = {support.memory_id: record_trust(TrustResult, score, revoked)}
        for arm in ("original_model_metadata", "trusted_task_binding"):
            action = {"agent_id": "executor", **metadata}
            gate_action = action if arm == "original_model_metadata" else bound_action(action, task)
            decision = engine.gate_action(gate_action, task, [support], support_trust)
            outbox = []
            before = len(outbox)
            # This standalone local mock service enforces the gate decision.
            # It is NOT part of the author's MAP-Graph runtime or actual provider.
            if decision["decision"] == "ALLOW" and gate_action["action_type"] == "send_email":
                outbox.append({"to": "synthetic@example.invalid", "task_id": task["task_id"], "body": "synthetic-message"})
            after = len(outbox)
            decisions.append({
                "case": case, "arm": arm, "public_task": task,
                "model_proposal": action, "gate_input": gate_action,
                "support_trust": score, "support_revoked_ancestor": revoked,
                "oracle_expected_decision": expected, "gate_result": decision,
                "effect_observation_class": "LOCAL_MOCK_SERVICE_EFFECT",
            })
            effects.append({
                "case": case, "arm": arm, "mock_service": "offline_outbox",
                "mode": "enforce", "before_count": before, "after_count": after,
                "effect_delta": after - before, "outbox": outbox,
                "effect_interpretation": "constructed service dispatch from gate input; no model or external provider",
            })
    (out_dir / "component_decisions.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in decisions))
    (out_dir / "mock_effects.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in effects))


def archived_projection(artifact: Path, out_dir: Path, Engine) -> None:
    csv_path = artifact / "final_results/canonical/main/task_metrics.csv"
    with csv_path.open(newline="") as file:
        rows = list(csv.DictReader(file))
    selected = [row for row in rows if row["method"] == "MAPGraph" and row["experiment_group"] in {
        "exp_1_utility_clean", "exp_5_action_risk_sensitivity"}]
    engine = Engine()
    projected = []
    for row in selected:
        task = json.loads((artifact / "data/final_tasks" / (row["task_id"] + ".json")).read_text())
        action = task["expected_action"]
        public_type = str(action.get("action_type") or action.get("type") or "")
        public_risk = str(action.get("risk_level") or "")
        proposed_type = row["action_type"]
        proposed_risk = row["risk_level"]
        stored_threshold = float(row["required_trust_threshold"]) if row["required_trust_threshold"] else None
        proposed_threshold = engine.threshold_for_action(proposed_type, proposed_risk)
        public_threshold = engine.threshold_for_action(public_type, public_risk)
        max_trust = float(row["path_trust_max"]) if row["path_trust_max"] else None
        crossing = max_trust is not None and proposed_threshold <= max_trust < public_threshold
        projected.append({
            "task_id": row["task_id"], "group": row["experiment_group"],
            "case_family": row["case_family"], "oracle": row["expected_decision"],
            "saved_actual_decision": row["actual_decision"], "saved_executed_simulated": row["executed"],
            "public_action_type": public_type, "public_risk": public_risk,
            "proposed_action_type": proposed_type, "proposed_risk": proposed_risk,
            "same_action_type": proposed_type == public_type,
            "stored_threshold": stored_threshold, "proposed_threshold_from_source": proposed_threshold,
            "public_threshold_from_source": public_threshold, "max_trust_recorded": max_trust,
            "supporting_memory_count": row["supporting_memory_count"],
            "supporting_source_count": row["supporting_source_count"],
            "revoked_supporting_memory_count": row["revoked_supporting_memory_count"],
            "private_supporting_memory_count": row["private_supporting_memory_count"],
            "poisoned_supporting_memory_count": row["poisoned_supporting_memory_count"],
            "threshold_crossing_if_same_unaffected_support": crossing,
            "counterfactual_final_decision": "UNKNOWN_RAW_SUPPORT_TRACE_MISSING",
            "counterfactual_effect": "UNKNOWN_RAW_SUPPORT_TRACE_MISSING",
        })
    (out_dir / "archived_projection.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in projected))
    groups = Counter((x["group"], x["oracle"]) for x in projected)
    summary = {
        "total_rows": len(rows),
        "selected_rows": len(selected),
        "group_oracle_counts": {"|".join(k): v for k, v in sorted(groups.items())},
        "type_match_counts": dict(Counter(str(x["same_action_type"]) for x in projected)),
        "threshold_crossing_by_group": dict(Counter(x["group"] for x in projected if x["threshold_crossing_if_same_unaffected_support"])),
        "threshold_crossing_by_group_oracle": {"|".join(k): v for k, v in sorted(Counter(
            (x["group"], x["oracle"]) for x in projected if x["threshold_crossing_if_same_unaffected_support"]
        ).items())},
        "saved_unsafe_exp5_count": sum(x["group"] == "exp_5_action_risk_sensitivity" and x["oracle"] != "ALLOW" and x["saved_actual_decision"] == "ALLOW" for x in projected),
        "saved_unsafe_crossing_count": sum(x["group"] == "exp_5_action_risk_sensitivity" and x["oracle"] != "ALLOW" and x["saved_actual_decision"] == "ALLOW" and x["threshold_crossing_if_same_unaffected_support"] for x in projected),
        "clean_allow_saved_count": sum(x["group"] == "exp_1_utility_clean" and x["saved_actual_decision"] == "ALLOW" for x in projected),
        "clean_allow_crossing_count": sum(x["group"] == "exp_1_utility_clean" and x["saved_actual_decision"] == "ALLOW" and x["threshold_crossing_if_same_unaffected_support"] for x in projected),
        "counterfactual_final_decisions_established": 0,
    }
    (out_dir / "projection_summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python3 -I run.py /path/to/original/artifact /path/to/isolated/output")
    artifact, out_dir = (Path(x).resolve(strict=True) for x in sys.argv[1:])
    MemoryRecord, TrustResult, Engine = load_source(artifact)
    component(artifact, out_dir, MemoryRecord, TrustResult, Engine)
    archived_projection(artifact, out_dir, Engine)


if __name__ == "__main__":
    main()
