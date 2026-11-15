"""R3 wiring tests: the three-agent stage placement must be a faithful, thin use of the ORIGINAL.

Run with the R2 environment (Python 3.11, original pins):
  experiments/r2/.venv/bin/python -m unittest discover -s experiments/r3 -p 'test_r3_wiring.py' -v
Seeds are the pre-registered identities (1016, 1029) plus throwaway seeds. No scenario outcome
is computed here beyond what the original harness itself defines.
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent / 'r2'
sys.path.insert(0, str(R2))
import trusted  # noqa: E402  (verifies the pinned original first)
import proof_codec as codec  # noqa: E402
from continuity import experiment as X  # noqa: E402
from continuity.core import ProofBundle, digest  # noqa: E402
from trusted import AdapterError, StageHost, TrustedPlane  # noqa: E402

sys.path.insert(0, str(HERE))
import oracle as r3_oracle  # noqa: E402

CFG = json.loads((HERE / 'config.json').read_text())


def new_plane():
    events = []
    return TrustedPlane(CFG, lambda t, s, **f: events.append(dict(event_type=t, source=s, **f)), ()), events


def hosts(plane):
    return (StageHost(plane, 'agent-A', ('memory',)), StageHost(plane, 'agent-B', ('gateway',)),
            StageHost(plane, 'agent-C', ('adapter',)))


def spec(seed):
    return dict(seed=seed, kind='benign', fault='NONE', issuer='trusted_authority', authorized_actor='agent-C',
                completion_expected=False)


class ThreeAgentPlacementIsFaithful(unittest.TestCase):
    def test_a_b_c_hosting_one_stage_each_reproduces_original_materialise_byte_for_byte(self):
        for seed in (1016, 1029, 1042):  # 2 mod 13: the actor is agent-C
            plane, _ = new_plane()
            bundle, _ = plane.issue_material(spec(seed), 'rootA')
            host_a, host_b, host_c = hosts(plane)
            for host, stage in ((host_a, 'memory'), (host_b, 'gateway'), (host_c, 'adapter')):
                bundle = host.apply(bundle, stage)
            original = X.materialise(X.make_scenario('workspace', seed, 'benign', infra=plane.infra), plane.infra).bundle
            self.assertEqual(bundle, original)
            self.assertEqual(digest(bundle), digest(original))

    def test_each_agent_holds_only_its_own_stage_key_and_stages_stay_in_order(self):
        plane, _ = new_plane()
        root, _ = plane.issue_material(spec(1016), 'rootA')
        host_a, host_b, host_c = hosts(plane)
        for host, stage in ((host_b, 'memory'), (host_c, 'gateway'), (host_a, 'adapter')):
            with self.assertRaises(AdapterError):
                host.apply(root, stage)
        with self.assertRaises(AdapterError):
            host_b.apply(root, 'gateway')  # B holds the key, but memory must come first

    def test_wire_round_trip_between_hops_preserves_the_bundle(self):
        plane, _ = new_plane()
        bundle, _ = plane.issue_material(spec(1016), 'rootA')
        host_a, host_b, _ = hosts(plane)
        after_a = host_a.apply(bundle, 'memory')
        sent = codec.from_wire(ProofBundle, codec.to_wire(after_a))
        self.assertEqual(sent, after_a)
        self.assertEqual(host_b.apply(sent, 'gateway'), host_b.apply(after_a, 'gateway'))

    def test_every_preregistered_material_is_issued_to_agent_c(self):
        plane, events = new_plane()
        for condition in CFG['conditions']:
            for material in condition.get('materials', []):
                bundle, entry = plane.issue_material(material, material['label'])
                self.assertEqual(bundle.root_grant.actor, CFG['agents']['agent-C']['identity'])
                self.assertEqual(entry['authorized_actor'], 'agent-C')


class R3OracleRecordKeepsTheOracleVerdictUntouched(unittest.TestCase):
    def test_wrapper_loads_the_r2_oracle_unchanged_and_adds_only_record_fields(self):
        import hashlib
        self.assertEqual(r3_oracle.R2_ORACLE, R2 / 'oracle.py')
        module = r3_oracle.load_r2_oracle()
        self.assertTrue(hasattr(module, 'analyze_trial') and hasattr(module, 'analyze_events'))
        self.assertEqual(len(hashlib.sha256(r3_oracle.R2_ORACLE.read_bytes()).hexdigest()), 64)

    def test_record_marks_parent_support_none_and_authority_evidence_none(self):
        rows = [dict(seq=1, event_type='grant_issued', trial_id='t', condition_id='c', grant_id='g',
                     authorized_actor='agent-C'),
                dict(seq=2, event_type='grant_record', trial_id='t', condition_id='c', grant_id='g',
                     root_principal='did:p', grant_issuer='key:authority', support_kind='ROOT', parent_support=None,
                     independent_supports=[]),
                dict(seq=3, event_type='delegation_context', trial_id='t', condition_id='c', work_id='w',
                     current_actor='agent-B', delegating_actor='agent-A', delegation_kind='WORK_DELEGATION',
                     authority_delegation_evidence='NONE'),
                dict(seq=4, event_type='revoke', trial_id='t', condition_id='c', grant_id='g')]
        result = dict(trial_id='t', condition_id='c', effects=[], world_effect_count=0, oracle_result='SATISFIED',
                      safety_oracle_result='SATISFIED', completion_result='NOT_EXERCISED', violation_types=[])
        record = r3_oracle.r3_record(rows, result)
        support = record['authority_supports'][0]
        self.assertEqual((support['parent_support'], support['independent_supports'], support['support_kind']),
                         (None, [], 'ROOT'))
        self.assertEqual(record['signed_delegation_evidence']['authority_delegation_evidence'], 'NONE')
        self.assertEqual(record['revoked'], dict(grants=['g'], edges='NOT_REPRESENTABLE'))
        self.assertEqual(record['work_delegation_chain'][0]['delegating_actor'], 'agent-A')
        self.assertEqual(record['independent_oracle_verdict']['overall'], 'SATISFIED')


if __name__ == '__main__':
    unittest.main()
