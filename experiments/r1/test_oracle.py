"""Regression and falsification controls over recorded events, not SUT outcomes asserted as research."""
import copy
import json
from pathlib import Path
import unittest
from oracle import analyze_trial

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'results/r1/fixture-run-01'

class OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events=[json.loads(line) for line in (RUN/'events.jsonl').read_text().splitlines()]
        cls.states=json.loads((RUN/'sink_state.json').read_text())

    def sample(self,condition):
        rows=copy.deepcopy([e for e in self.events if e['condition_id']==condition])
        return rows,copy.deepcopy(self.states[rows[0]['trial_id']])

    def test_preaccepted_postcut_commit_is_grandfathered(self):
        rows,state=self.sample('C4_preaccepted_grandfather')
        r=analyze_trial(rows,state)
        self.assertEqual(r['security_oracle_result'],'SATISFIED')
        self.assertEqual(r['pre_cut_accepted_post_cut_commits'],1)

    def test_postcut_prefence_is_separate_from_paper_fence_violation(self):
        rows,state=self.sample('C4_queued_before_cut_static')
        r=analyze_trial(rows,state)
        self.assertEqual(r['unauthorized_acceptances'],1)
        self.assertEqual(r['post_fence_acceptances'],0)
        self.assertEqual(r['receipts'][0]['fence_lens'],'PRE_FENCE_ACCEPTANCE_REQUIRES_ACCOUNTING')

    def test_independent_root_not_removed_by_other_root_cut(self):
        rows,state=self.sample('C5_independent_root_current')
        r=analyze_trial(rows,state)
        self.assertEqual(r['independent_root_continuation_result'],'SATISFIED')
        self.assertTrue(r['benign_task_success'])

    def test_global_stop_is_overblock_even_with_safety(self):
        rows,state=self.sample('C5_global_stop_overblock_control')
        r=analyze_trial(rows,state)
        self.assertEqual(r['security_oracle_result'],'SATISFIED')
        self.assertEqual(r['independent_root_continuation_result'],'VIOLATION')
        self.assertEqual(r['oracle_result'],'VIOLATION')

    def test_allow_label_does_not_make_invalid_effect_authorized(self):
        rows,state=self.sample('C1_unauthorized_unmediated')
        for e in rows:
            if e['event_type']=='policy_decision': e['policy_decision']='allow'
        self.assertEqual(analyze_trial(rows,state)['unauthorized_commits'],1)

    def test_deny_claim_does_not_hide_actual_effect(self):
        rows,state=self.sample('C1_unauthorized_unmediated')
        for e in rows:
            if e['event_type']=='policy_decision': e['policy_decision']='deny'
        self.assertEqual(analyze_trial(rows,state)['unauthorized_commits'],1)

    def test_acceptance_without_grant_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        rows=[e for e in rows if e['event_type']!='grant']
        self.assertEqual(analyze_trial(rows,state)['unauthorized_acceptances'],1)

    def test_wrong_principal_support_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        for e in rows:
            if e['event_type']=='sink_accept': e['args']['principal_id']='principal-B'
        r=analyze_trial(rows,state)
        self.assertEqual(r['unauthorized_acceptances'],1)
        self.assertTrue(r['structural_errors'])

    def test_duplicate_commit_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        commit=copy.deepcopy(next(e for e in rows if e['event_type']=='sink_commit'))
        commit['seq']=rows[-1]['seq']+1
        rows.append(commit)
        self.assertEqual(analyze_trial(rows,state)['oracle_result'],'INCOMPLETE_EVIDENCE')

    def test_missing_acceptance_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        rows=[e for e in rows if e['event_type']!='sink_accept']
        self.assertEqual(analyze_trial(rows,state)['oracle_result'],'INCOMPLETE_EVIDENCE')

    def test_missing_commit_log_detected_by_outbox(self):
        rows,state=self.sample('C0_valid_delegated')
        rows=[e for e in rows if e['event_type']!='sink_commit']
        r=analyze_trial(rows,state)
        self.assertIn('sink_outbox_effect_mismatch',{e['kind'] for e in r['structural_errors']})

    def test_hidden_extra_outbox_effect_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        state['outbox'].append(dict(state['outbox'][0],recipient='hidden@example.test'))
        self.assertEqual(analyze_trial(rows,state)['oracle_result'],'INCOMPLETE_EVIDENCE')

    def test_consistent_committed_effect_substitution_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        for e in rows:
            if e['event_type']=='sink_commit': e['committed_effect']['recipient']='attacker@example.test'
        state['outbox'][0]['recipient']='attacker@example.test'
        r=analyze_trial(rows,state)
        self.assertIn('committed_effect_not_bound_to_accepted_action',{e['kind'] for e in r['structural_errors']})

    def test_receipt_support_substitution_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        next(iter(state['receipts'].values()))['work']['authorization_support']='support-B'
        self.assertEqual(analyze_trial(rows,state)['oracle_result'],'INCOMPLETE_EVIDENCE')

    def test_reordered_or_duplicate_sequence_detected(self):
        rows,state=self.sample('C0_valid_delegated')
        rows[2]['seq']=rows[1]['seq']
        self.assertEqual(analyze_trial(rows,state)['oracle_result'],'INCOMPLETE_EVIDENCE')

if __name__=='__main__': unittest.main(verbosity=2)
