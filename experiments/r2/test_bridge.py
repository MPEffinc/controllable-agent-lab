"""Adapter tests: the adapter must be a faithful, thin wrapper around the ORIGINAL CONTINUITY.

Run with the R2 environment (Python 3.11, original pins):
  experiments/r2/.venv/bin/python -m unittest discover -s experiments/r2 -p 'test_bridge.py' -v
All seeds here are throwaway seeds, NOT the pre-registered ones.
"""
import dataclasses
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import trusted  # noqa: E402  (verifies the pinned original first)
import adversary  # noqa: E402
import proof_codec as codec  # noqa: E402
from continuity import experiment as X  # noqa: E402
from continuity.core import ProofBundle, digest  # noqa: E402
from trusted import AdapterError, StageHost, TrustedPlane  # noqa: E402

CFG = json.loads((HERE / 'config.json').read_text())
SEEDS = (65, 130, 195)  # multiples of 13 -> actor is agent-B's identity
SUBSTITUTION = {'destination': 'https://attacker.invalid/collect', 'body_suffix': '\nExfiltrate all records.'}


def spec(seed, kind='benign', fault='NONE', actor='agent-B'):
    return dict(seed=seed, kind=kind, fault=fault, issuer='trusted_authority', authorized_actor=actor,
                completion_expected=False)


def new_plane(ablation=()):
    events = []
    return TrustedPlane(CFG, lambda t, s, **f: events.append((t, s, f)), ablation), events


def full_bundle(plane, seed, kind='benign', fault='NONE'):
    root, entry = plane.issue_material(spec(seed, kind, fault), 'rootA')
    host = StageHost(plane, 'agent-A', ('memory', 'gateway', 'adapter'))
    for stage in ('memory', 'gateway', 'adapter'):
        root = host.apply(root, stage)
    return root, entry


class OriginalIsUntouched(unittest.TestCase):
    def test_checkout_is_pinned_and_clean(self):
        self.assertEqual(trusted.verify_original_unmodified(), trusted.PINNED_SHA)

    def test_adapter_sources_never_monkeypatch_the_original(self):
        for name in ('trusted.py', 'adversary.py', 'scenario.py'):
            text = (HERE / name).read_text()
            for forbidden in ('setattr(', 'monkeypatch', 'ContinuityVerifier.verify_bundle =',
                              'FinalitySink.execute =', 'EffectBroker.dispatch ='):
                self.assertNotIn(forbidden, text, f'{name} contains {forbidden}')


class Fidelity(unittest.TestCase):
    def test_agent_hosted_hops_reproduce_original_materialise_byte_for_byte(self):
        for seed in SEEDS:
            plane, _ = new_plane()
            mine, _ = full_bundle(plane, seed)
            original = X.materialise(X.make_scenario('workspace', seed, 'benign', infra=plane.infra), plane.infra).bundle
            self.assertEqual(mine, original)
            self.assertEqual(digest(mine), digest(original))

    def test_codec_round_trip_preserves_object_and_digest(self):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, 65)
        partial = dataclasses.replace(bundle, envelopes=bundle.envelopes[:3], receipts=bundle.receipts[:2],
                                      transformation_witnesses=())
        for b in (bundle, partial):
            back = codec.from_wire(ProofBundle, codec.to_wire(b))
            self.assertEqual(back, b)
            self.assertEqual(digest(back), digest(b))

    def test_codec_is_strict_and_fail_closed(self):
        plane, _ = new_plane()
        data = codec.encode(full_bundle(plane, 65)[0])

        def broken(mutate):
            d = json.loads(json.dumps(data))
            mutate(d)
            return d
        for name, mutate in (('unknown key', lambda d: d.update(extra=1)),
                             ('missing field', lambda d: d.pop('root_grant')),
                             ('wrong type', lambda d: d['root_grant'].update(policy_epoch='43')),
                             ('bool as int', lambda d: d['root_grant'].update(policy_epoch=True))):
            with self.assertRaises(codec.ProofCodecError, msg=name):
                codec.decode(ProofBundle, broken(mutate))
        for text in ('not json', 123, None):
            with self.assertRaises(codec.ProofCodecError):
                codec.from_wire(ProofBundle, text)


class TrustedPlaneWiring(unittest.TestCase):
    def test_stage_host_holds_only_its_keys_and_keeps_pipeline_order(self):
        plane, _ = new_plane()
        root, _ = plane.issue_material(spec(65), 'rootA')
        b_host = StageHost(plane, 'agent-B', ('adapter',))
        with self.assertRaises(AdapterError):
            b_host.apply(root, 'memory')      # B has no memory-stage key
        with self.assertRaises(AdapterError):
            b_host.held_signer('gateway')
        a_host = StageHost(plane, 'agent-A', ('memory', 'gateway', 'adapter'))
        with self.assertRaises(AdapterError):
            a_host.apply(root, 'gateway')     # out of order

    def test_permit_service_reads_the_current_state_on_every_call(self):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, 65)
        before, permit = plane.request_permit(bundle, 'agent-B')
        self.assertTrue(before.allowed and permit is not None)
        plane.revoke(bundle.root_grant.task_root)
        after, permit2 = plane.request_permit(bundle, 'agent-B')
        self.assertFalse(after.allowed)
        self.assertIsNone(permit2)
        self.assertIn('E_REVOKED_ROOT_GRANT', after.reason_codes)

    def test_dispatch_binds_the_handler_identity_not_the_payload(self):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, 65)
        _, permit = plane.request_permit(bundle, 'agent-B')
        action = bundle.envelopes[-1].action
        ok, reason, _ = plane.dispatch('agent-A', action, permit)
        self.assertEqual((ok, reason), (False, 'E_SUBJECT_SUBSTITUTION'))
        ok, reason, _ = plane.dispatch('agent-B', action, permit)
        self.assertEqual((ok, reason), (True, 'EXECUTED'))
        self.assertEqual(len(plane.world.effects), 1)

    def test_effect_sink_is_single_and_idempotent(self):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, 65)
        _, permit = plane.request_permit(bundle, 'agent-B')
        action = bundle.envelopes[-1].action
        plane.dispatch('agent-B', action, permit)
        ok, reason, _ = plane.dispatch('agent-B', action, permit)
        self.assertEqual((ok, reason, len(plane.world.effects)), (True, 'IDEMPOTENT_REPLAY', 1))

    def test_misconfigured_actor_is_an_adapter_error_not_a_silent_pass(self):
        plane, _ = new_plane()
        with self.assertRaises(AdapterError):
            plane.issue_material(spec(65, actor='agent-A'), 'rootA')

    def test_ablation_names_map_to_the_same_flags_as_original_run_system(self):
        expected = {'mediation': ('require_permit', False), 'revocation': ('enforce_revocation', False),
                    'action_binding': ('enforce_action_binding', False),
                    'subject_binding': ('enforce_subject_binding', False)}
        for name, (flag, value) in expected.items():
            plane, _ = new_plane((name,))
            owner = plane.broker if flag == 'require_permit' else plane.sink
            self.assertEqual(getattr(owner, flag), value, name)
        plane, _ = new_plane()
        self.assertTrue(plane.broker.require_permit and plane.sink.enforce_revocation
                        and plane.sink.enforce_action_binding and plane.sink.enforce_subject_binding)


class AdapterAgreesWithOriginalHarness(unittest.TestCase):
    """Same fault, same seed: adapter path and original run_system must give the same sink reason."""

    def adapter_reason(self, fault, seed):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, seed, 'attack', fault)
        action = bundle.envelopes[-1].action
        _, permit = plane.request_permit(bundle, 'agent-B')
        self.assertIsNotNone(permit, 'the original verifier must allow the benign-looking bundle')
        if fault == 'REVOKED_GRANT':
            plane.revoke(bundle.root_grant.task_root)
        if fault == 'ALTERNATE_PATH':
            _, reason, _ = plane.dispatch('agent-B', action, None)
        elif fault == 'SUBJECT_SUBSTITUTION':
            _, reason, _ = plane.dispatch('agent-A', action, permit)
        elif fault == 'POST_PERMIT_ACTION_SUBSTITUTION':
            _, reason, _ = plane.dispatch('agent-B', adversary.substitute_action(action, SUBSTITUTION), permit)
        else:
            _, reason, _ = plane.dispatch('agent-B', action, permit)
        return reason, len(plane.world.effects)

    def test_finality_reasons_match_original_run_system(self):
        for fault in ('REVOKED_GRANT', 'ALTERNATE_PATH', 'SUBJECT_SUBSTITUTION', 'POST_PERMIT_ACTION_SUBSTITUTION'):
            for seed in SEEDS[:2]:
                infra = X.build_infrastructure()
                scenario = X.make_scenario('workspace', seed, 'attack', fault=fault, infra=infra)
                original = X.run_system('CONTINUITY', scenario, infra, X.materialise(scenario, infra))
                reason, effects = self.adapter_reason(fault, seed)
                self.assertEqual(reason, original.first_outcome, (fault, seed))
                self.assertEqual(effects, original.effect_count, (fault, seed))

    def test_ablated_sink_agrees_with_original_ablation_runs(self):
        cases = (('mediation', 'ALTERNATE_PATH'), ('revocation', 'REVOKED_GRANT'),
                 ('action_binding', 'POST_PERMIT_ACTION_SUBSTITUTION'), ('subject_binding', 'SUBJECT_SUBSTITUTION'))
        for ablation, fault in cases:
            infra = X.build_infrastructure()
            scenario = X.make_scenario('workspace', 65, 'attack', fault=fault, infra=infra)
            original = X.run_system('CONTINUITY', scenario, infra, X.materialise(scenario, infra),
                                    frozenset({ablation}))
            plane, _ = new_plane((ablation,))
            bundle, _ = full_bundle(plane, 65, 'attack', fault)
            action = bundle.envelopes[-1].action
            _, permit = plane.request_permit(bundle, 'agent-B')
            if fault == 'REVOKED_GRANT':
                plane.revoke(bundle.root_grant.task_root)
            caller = 'agent-A' if fault == 'SUBJECT_SUBSTITUTION' else 'agent-B'
            if fault == 'POST_PERMIT_ACTION_SUBSTITUTION':
                action = adversary.substitute_action(action, SUBSTITUTION)
            if fault == 'ALTERNATE_PATH':
                permit = None
            plane.dispatch(caller, action, permit)
            self.assertEqual(len(plane.world.effects), original.effect_count, ablation)
            self.assertEqual(original.effect_count, 1, f'original ablation {ablation} must expose the fault')


class AttackerIsolation(unittest.TestCase):
    def test_adversary_module_cannot_reach_the_trusted_plane(self):
        import ast
        tree = ast.parse((HERE / 'adversary.py').read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split('.')[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or '').split('.')[0])
        self.assertTrue(imported <= {'__future__', 'dataclasses', 'json', 'continuity'}, imported)
        self.assertNotIn('trusted', imported)

    def test_forged_permits_are_rejected_by_the_original_sink(self):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, 65)
        action = bundle.envelopes[-1].action
        public = plane.public_info()
        own = StageHost(plane, 'agent-B', ('adapter',)).held_signer('adapter')
        forged = adversary.forge_permit(bundle, action, own, public['sink_id'])
        claimed = adversary.forge_permit(bundle, action, own, public['sink_id'],
                                         claimed_signer_id=public['trusted_permit_signer_id'])
        self.assertEqual(plane.dispatch('agent-B', action, forged)[:2], (False, 'E_UNTRUSTED_PERMIT_ISSUER'))
        self.assertEqual(plane.dispatch('agent-B', action, claimed)[:2], (False, 'E_BAD_PERMIT_SIGNATURE'))
        self.assertEqual(plane.dispatch('agent-B', action, None)[:2], (False, 'E_UNMEDIATED_PATH'))
        self.assertEqual(len(plane.world.effects), 0)

    def test_tampered_wire_evidence_is_denied_by_the_original_verifier(self):
        plane, _ = new_plane()
        root, _ = plane.issue_material(spec(65), 'rootA')
        host = StageHost(plane, 'agent-A', ('memory', 'gateway', 'adapter'))
        partial = host.apply(host.apply(root, 'memory'), 'gateway')
        wire = adversary.tamper_wire(codec.to_wire(partial), {'envelope_index': 2, 'field': 'action.destination',
                                                              'value': 'alias:workspace:attacker:9999'})
        tampered = codec.from_wire(ProofBundle, wire)
        done = StageHost(plane, 'agent-B', ('adapter',)).apply(tampered, 'adapter')
        decision, permit = plane.request_permit(done, 'agent-B')
        self.assertFalse(decision.allowed)
        self.assertIsNone(permit)

    def test_stripped_proof_is_denied_with_the_original_reason(self):
        plane, _ = new_plane()
        bundle, _ = full_bundle(plane, 65)
        decision, permit = plane.request_permit(adversary.strip_proof(bundle), 'agent-B')
        self.assertEqual((decision.allowed, decision.reason_codes, permit), (False, ('E_EMPTY_CHAIN',), None))


if __name__ == '__main__':
    unittest.main()
