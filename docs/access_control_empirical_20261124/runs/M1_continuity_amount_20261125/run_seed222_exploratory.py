"""Small independent amount-bound adaptation of the pinned CONTINUITY artifact.

No changes to original author sources, models, external providers, or real money.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "third_party" / "continuity" / "src"))

from continuity import experiment as exp  # noqa: E402
from continuity.core import (  # noqa: E402
    EffectBroker,
    FinalitySink,
    NonceLedger,
    PredicateSpec,
    SimulatedWorld,
)


def scenario(infra: exp.Infrastructure, *, seed: int, amount: int, limit: int, fault: str):
    original_constraints = exp._root_constraints

    def params(domain: str, _seed: int):
        assert domain == "finance"
        return {"amount_cents": amount, "currency": "EUR"}

    def constraints(domain: str):
        original = original_constraints(domain)
        return tuple(
            replace(item, predicate=PredicateSpec("int_range", {"min": 1, "max": limit}))
            if item.path == "/action/parameters/amount_cents"
            else item
            for item in original
        )

    def malicious(domain: str, *, extreme: bool = False):
        assert domain == "finance" and extreme
        return 900_000

    kind = "attack" if fault != "NONE" else "benign"
    with (
        patch.object(exp, "_params", params),
        patch.object(exp, "_root_constraints", constraints),
        patch.object(exp, "_malicious_value", malicious),
    ):
        return exp.make_scenario("finance", seed, kind, fault=fault, infra=infra)


def main() -> None:
    infra = exp.build_infrastructure()
    verifier = exp._verifier(infra)
    world = SimulatedWorld()
    ledger = NonceLedger()
    sink_id = "spiffe://example/finality/finance"
    sink = FinalitySink(
        sink_id,
        infra.keyring,
        infra.signers["verifier"].key_id,
        infra.signers["sink"],
        ledger,
        world,
    )
    broker = EffectBroker(sink)
    cases = [
        ("N_normal_root_120_action_120", scenario(infra, seed=111, amount=12_000, limit=12_000, fault="NONE")),
        (
            "A_root_120_action_9000",
            scenario(infra, seed=111, amount=12_000, limit=12_000, fault="ROOT_FIELD_CONSTRAINT_BYPASS"),
        ),
        (
            "W_wide_root_9000_action_9000",
            scenario(infra, seed=222, amount=900_000, limit=900_000, fault="NONE"),
        ),
    ]
    outputs = []
    for label, case in cases:
        before = {"count": len(world.effects), "digest": world.state_digest}
        trace = exp.materialise(case, infra)
        decision = verifier.verify_bundle(trace.bundle, exp.NOW)
        result = {"accepted": False, "reason": "VERIFIER_DENY", "receipt": None}
        if decision.allowed:
            permit = verifier.issue_permit(decision, trace.final, sink_id, exp.NOW)
            accepted, reason, receipt = broker.dispatch(
                trace.final.action,
                permit,
                exp.NOW,
                trace.final.context.actor or "",
                infra.deployment.runtime_state,
            )
            result = {
                "accepted": accepted,
                "reason": reason,
                "receipt": None
                if receipt is None
                else {
                    "effect_id": receipt.effect_id,
                    "status": receipt.status,
                    "state_digest": receipt.state_digest,
                },
            }
        outputs.append(
            {
                "case": label,
                "scenario_id": case.scenario_id,
                "root_grant_id": case.root_grant.grant_id,
                "root_issuer": case.root_grant.issuer,
                "root_max_amount_cents": next(
                    c.predicate.parameters["max"]
                    for c in case.root_grant.field_constraints
                    if c.path == "/action/parameters/amount_cents"
                ),
                "action_amount_cents": trace.final.action.parameters["amount_cents"],
                "currency": trace.final.action.parameters["currency"],
                "verifier_allowed": decision.allowed,
                "verifier_reason_codes": list(decision.reason_codes),
                "sink": result,
                "before": before,
                "after": {"count": len(world.effects), "digest": world.state_digest},
            }
        )
    record = {
        "artifact_commit": "59cfe60930d247d1890b366ded686c718020a11e",
        "model_calls": 0,
        "paid_api_usd": 0,
        "world_type": "CONTINUITY SimulatedWorld",
        "shared_world": True,
        "shared_nonce_ledger": True,
        "cases": outputs,
        "final_effects": world.effects,
    }
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
