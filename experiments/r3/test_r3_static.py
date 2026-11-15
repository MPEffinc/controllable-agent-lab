"""Tests for the R3 static checker and the paper-definition reference models (stdlib only).

The checker tests plant a violation in a synthetic source and require detection, so a
passing real check cannot be a vacuous one. The reference-model tests assert
properties stated by the papers independently of config.json, then confirm the
pre-registered expectations.
"""
import dataclasses
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import expressiveness_check as ec  # noqa: E402
import reference_model as rm  # noqa: E402

CONFIG = json.loads((Path(__file__).resolve().parent / 'config.json').read_text())


@dataclasses.dataclass(frozen=True)
class CleanGrant:
    grant_id: str
    delegation_scope: frozenset


@dataclasses.dataclass(frozen=True)
class LineageGrant:
    grant_id: str
    parent_grant_id: str


@dataclasses.dataclass(frozen=True)
class WiderState:
    policy_id: str
    policy_digest: str
    policy_epoch: int
    revoked_ids: frozenset
    revoked_edges: frozenset


class StaticCheckerDetectsViolations(unittest.TestCase):
    def test_s1_flags_a_parent_field(self):
        self.assertTrue(ec.s1_no_lineage_field(CleanGrant)['holds'])
        self.assertFalse(ec.s1_no_lineage_field(LineageGrant)['holds'])

    def test_s2_flags_an_extra_state_field(self):
        self.assertFalse(ec.s2_runtime_state_fields(WiderState)['holds'])

    def test_s3_flags_revocation_by_an_unlisted_identifier(self):
        clean = 'def f(g, state):\n    return g.grant_id in state.revoked_ids\n'
        bad = 'def f(g, state):\n    return g.parent_edge in state.revoked_ids\n'
        self.assertEqual(ec.s3_revocation_operands(clean)['holds'], False)  # 'g.grant_id' is not an allowed spelling
        named = 'def f(grant, state):\n    return grant.grant_id in state.revoked_ids\n'
        self.assertTrue(ec.s3_revocation_operands(named)['holds'])
        self.assertFalse(ec.s3_revocation_operands(bad)['holds'])
        self.assertFalse(ec.s3_revocation_operands('x = 1\n')['holds'])  # no revocation test at all is not a pass

    def test_s4_flags_a_verification_read_of_approval_digest(self):
        base = ('CONTEXT_ATOMIC_PATHS = frozenset({"/context/approval_digest"})\n'
                'class SecurityContext:\n    approval_digest: str = None\n')
        self.assertTrue(ec.s4_approval_digest_unused(base)['holds'])
        read = base + 'def verify(c):\n    return bool(c.approval_digest)\n'
        self.assertFalse(ec.s4_approval_digest_unused(read)['holds'])

    def test_s5_requires_the_parent_argument_to_be_rejected(self):
        self.assertTrue(ec.s5_parent_argument_rejected(CleanGrant('g', frozenset()))['holds'])
        self.assertFalse(ec.s5_parent_argument_rejected(LineageGrant('g', 'p'))['holds'])

    def test_s6_flags_lineage_quorum_and_edge_tokens(self):
        self.assertTrue(ec.s6_no_lineage_tokens({'f': 'def f(x):\n    return x.actor\n'})['holds'])
        for word in ('parent', 'lineage', 'quorum', 'approver', 'edge'):
            self.assertFalse(ec.s6_no_lineage_tokens({'f': f'def f(x):\n    return x.{word}\n'})['holds'], word)

    def test_s7_flags_an_unexpected_use_of_delegation_scope(self):
        ok = ('def f(c, g):\n    return c.delegation_scope.issubset(g.delegation_scope)\n'
              'def h(a, c):\n    return a not in c.delegation_scope\n')
        self.assertTrue(ec.s7_delegation_scope_uses(ok)['holds'])
        derive = ok + 'def mint(c):\n    return list(c.delegation_scope)\n'
        self.assertFalse(ec.s7_delegation_scope_uses(derive)['holds'])
        build = ok + 'def mk(c):\n    return RootGrant(c)\n'
        self.assertFalse(ec.s7_delegation_scope_uses(build)['holds'])


class ReferenceModelsFollowTheDefinitions(unittest.TestCase):
    def test_vera_target_is_the_edge_dominance_set_not_the_subtree(self):
        chain = {'R': ['R', 'A'], 'AC': ['A', 'C']}
        edges = {k: tuple(v) for k, v in chain.items()}
        self.assertEqual(rm.reach(['R'], edges) - rm.reach(['R'], edges, frozenset({'R'})), {'A', 'C'})
        diamond = {'e1': ('R1', 'X'), 'e2': ('R2', 'X')}
        self.assertEqual(rm.reach(['R1', 'R2'], diamond) - rm.reach(['R1', 'R2'], diamond, frozenset({'e1'})), set())

    def test_vera_batch_target_is_not_the_union_of_single_edge_targets(self):  # VERA-8
        edges = {'a': ('R', 'A'), 'b': ('R', 'B'), 'ac': ('A', 'C'), 'bc': ('B', 'C')}
        single = [rm.reach(['R'], edges) - rm.reach(['R'], edges, frozenset({e})) for e in ('ac', 'bc')]
        joint = rm.reach(['R'], edges) - rm.reach(['R'], edges, frozenset({'ac', 'bc'}))
        self.assertEqual(single[0] | single[1], set())
        self.assertEqual(joint, {'C'})

    def test_succession_excludes_multi_parent_and_conjunctive_graphs(self):
        for gid in ('G4', 'G5'):
            self.assertEqual(rm.succession(CONFIG['reference_graphs'][gid]), {'expressible': False})
        self.assertEqual(rm.succession(CONFIG['reference_graphs']['G3']),
                         {'C_current_after_edge_e2': False, 'C_current_after_root_edge_e1': False})

    def test_revocation_strict_subset_of_a_conjunctive_witness_cannot_authorize(self):  # REV-4
        out = rm.revocation(CONFIG['reference_graphs']['G5'])
        self.assertFalse(out['strict_subset_can_authorize'])
        self.assertFalse(out['C_authorized_after_root_edge_e1'])

    def test_revocation_rebinds_to_an_independent_support_that_excludes_the_retired_atom(self):  # REV-7
        out = rm.revocation(CONFIG['reference_graphs']['G4'])
        self.assertTrue(out['C_authorized_after_root_edge_e1'])
        self.assertTrue(out['rebind_to_independent_support'])
        self.assertEqual(out['C_authorized_after_edge_e2'], 'NOT_EXPRESSIBLE')

    def test_residualauth_selected_parent_can_be_dead_while_another_path_remains(self):  # RES-6
        out = rm.residualauth(CONFIG['reference_graphs']['G4'])
        self.assertTrue(out['graph_C_effective_after_root_edge_e1'])
        self.assertFalse(out['ledger_selected_parent_e2_after_root_edge_e1'])
        self.assertTrue(out['ledger_selected_parent_e3_after_root_edge_e1'])

    def test_vera_or_semantics_violates_a_conjunctive_policy(self):  # VERA-1
        out = rm.vera(CONFIG['reference_graphs']['G5'])
        self.assertEqual((out['expressible'], out['and_policy_violated_by_or_semantics']), (False, True))

    def test_compare_reports_a_changed_expectation(self):
        computed = rm.compute(CONFIG)
        tampered = json.loads(json.dumps(CONFIG['reference_model_expected']))
        tampered['G4']['VERA']['C_active_after_edge_e2'] = False
        self.assertEqual(len(rm.compare(tampered, computed)), 1)

    def test_preregistered_expectation_matches_the_computed_definitions(self):
        self.assertEqual(rm.compare(CONFIG['reference_model_expected'], rm.compute(CONFIG)), [])


if __name__ == '__main__':
    unittest.main()
