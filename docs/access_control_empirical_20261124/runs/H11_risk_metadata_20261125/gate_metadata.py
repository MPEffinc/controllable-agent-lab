"""Independent, synthetic input to unmodified MAP-Graph gate_action."""

from __future__ import annotations

import json
import sys
import importlib.util
from pathlib import Path
from types import ModuleType


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I gate_metadata.py /path/to/artifact")
    artifact = Path(sys.argv[1]).resolve(strict=True)
    # Package __init__ eagerly imports an optional OpenAI client. Import only
    # the two unchanged source files needed for this pure gate experiment.
    for package in ("src", "src.map_graph", "src.memory_baselines"):
        module = ModuleType(package)
        module.__path__ = [str(artifact / package.replace(".", "/"))]
        sys.modules[package] = module

    def load_source(name: str, file: Path):
        spec = importlib.util.spec_from_file_location(name, file)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    base_module = load_source("src.memory_baselines.base", artifact / "src/memory_baselines/base.py")
    trust_module = load_source("src.map_graph.trust", artifact / "src/map_graph/trust.py")
    MemoryRecord = base_module.MemoryRecord
    MAPGraphTrustEngine = trust_module.MAPGraphTrustEngine
    TrustResult = trust_module.TrustResult

    task = {
        "task_id": "synthetic_h11_boundary",
        "expected_action": {"type": "send_email", "risk_level": "high"},
    }
    support = MemoryRecord(memory_id="current_support", content="Synthetic current support", owner_agent="executor")
    engine = MAPGraphTrustEngine()

    def trust(*, revoked: bool = False) -> TrustResult:
        return TrustResult(
            trust=0.76,
            source_trust=0.76,
            path_integrity=1.0,
            transformation_factor=1.0,
            permission_validity=1.0,
            verification_bonus=1.0,
            agent_reliability=1.0,
            transformation_loss=0.0,
            affected_ancestors=["revoked_source"] if revoked else [],
            contamination_reasons={},
            untrusted_ancestors=[],
            private_ancestors=[],
            revoked_ancestors=["revoked_source"] if revoked else [],
        )

    cases = [
        ("correct_high", {"action_type": "send_email", "risk_level": "high"}, False),
        ("downgraded_type", {"action_type": "answer", "risk_level": "medium"}, False),
        ("downgraded_risk", {"action_type": "send_email", "risk_level": "medium"}, False),
        ("revoked_control", {"action_type": "send_email", "risk_level": "high"}, True),
    ]
    for case, metadata, revoked in cases:
        action = {"agent_id": "executor", **metadata}
        result = engine.gate_action(action, task, [support], {support.memory_id: trust(revoked=revoked)})
        print(json.dumps({"case": case, "task": task, "action": action, "support_path_trust": 0.76,
                          "support_revoked_ancestor": revoked, "effect_observed": False, "gate": result},
                         ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
