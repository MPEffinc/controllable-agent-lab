"""Regression tests for the independent R2 oracle and the R1 projection (stdlib only)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle  # noqa: E402
import r1_projection  # noqa: E402

A = 'spiffe://example/agent/workspace/1'
B = 'spiffe://example/agent/workspace/0'
EFFECT = dict(operation='email.send', resource='customer:1001', destination='mailto:customer:1001',
              parameters={'subject': 'Case 1001', 'body': 'Status update 1001'}, effect_class='EXTERNAL_WRITE')
ATTACK = dict(EFFECT, destination='https://attacker.invalid/collect')


class Log:
    """Builds a synthetic saved trace; mirrors the field names of the real event log."""

    def __init__(self, signer='key:verifier', epoch=43):
        self.events, self.effects = [], []
        self.emit('trial_started', group='CORE', trusted_permit_signer=signer, policy_epoch=epoch)

    def emit(self, kind, **fields):
        self.events.append(dict(seq=len(self.events) + 1, trial_id='t', condition_id='c',
                                event_type=kind, **fields))

    def grant(self, gid='g1', root='task:1', actor=B, effect=EFFECT, completion=False, label='rootA'):
        self.emit('grant_issued', grant_id=gid, root_task_id=root, principal_id='did:p1', authorized_actor='agent-B',
                  actor_identity=actor, authorized_effect=effect, completion_expected=completion, material_label=label)

    def permit(self, pid='p1', gid='g1', epoch=43, signer='key:verifier', root='task:1'):
        self.emit('permit_issued', permit_id=pid, grant_id=gid, principal='did:p1', subject=B, task_root=root,
                  policy_epoch=epoch, signer=signer)
        return dict(permit_id=pid, grant_id=gid, principal='did:p1', subject=B, task_root=root,
                    policy_epoch=epoch, signer=signer)

    def revoke(self, gid='g1', root='task:1'):
        self.emit('revoke', root_task_id=root, grant_id=gid)

    def attempt(self, caller=B, action=EFFECT, permit=None, executed=True, reason='EXECUTED', world=None):
        index = len(self.effects)
        if executed:
            self.effects.append(dict(world if world is not None else action, ordinal=index))
        self.emit('finality_attempt', caller_agent='agent-B', caller_identity=caller, action=dict(action, tool_id='t'),
                  permit=permit, result_ok=executed, result_reason=reason, new_effect=executed,
                  effect_id=f'effect:{index}' if executed else None)

    def finish(self):
        self.emit('trial_completed')
        return oracle.analyze_trial(self.events, dict(effects=self.effects))


def clean_log(**kw):
    log = Log()
    log.grant(**kw)
    return log


class OracleTests(unittest.TestCase):
    def test_clean_delegated_effect_satisfies_safety_and_completion(self):
        log = clean_log(completion=True)
        log.attempt(permit=log.permit())
        r = log.finish()
        self.assertEqual((r['oracle_result'], r['completion_result'], r['violation_types']),
                         ('SATISFIED', 'SATISFIED', []))

    def test_effect_after_revocation_is_a_violation(self):
        log = clean_log()
        permit = log.permit()
        log.revoke()
        log.attempt(permit=permit)
        self.assertIn('REVOKED_AT_FINALITY', log.finish()['violation_types'])

    def test_effect_before_revocation_is_not_a_violation(self):
        log = clean_log()
        log.attempt(permit=log.permit())
        log.revoke()  # no rollback is claimed: the effect already finalised while the grant was live
        self.assertEqual(log.finish()['oracle_result'], 'SATISFIED')

    def test_wrong_actor_is_a_violation(self):
        log = clean_log()
        log.attempt(caller=A, permit=log.permit())
        self.assertIn('UNAUTHORIZED_ACTOR', log.finish()['violation_types'])

    def test_substituted_action_is_a_violation(self):
        log = clean_log()
        log.attempt(action=ATTACK, permit=log.permit())
        self.assertIn('UNAUTHORIZED_ACTION', log.finish()['violation_types'])

    def test_missing_permit_effect_is_unmediated_and_unauthorized(self):
        log = clean_log()
        log.attempt(action=ATTACK, permit=None, reason='BYPASS_EXECUTED:effect:0')
        types = log.finish()['violation_types']
        self.assertIn('UNMEDIATED_EFFECT', types)
        self.assertIn('UNAUTHORIZED_ACTION', types)

    def test_permit_not_issued_by_trusted_service_is_forged(self):
        log = clean_log()
        forged = dict(permit_id='forged', grant_id='g1', policy_epoch=43, signer='key:verifier')
        log.attempt(permit=forged)
        self.assertIn('FORGED_PERMIT_EFFECT', log.finish()['violation_types'])

    def test_permit_with_untrusted_signer_is_forged(self):
        log = clean_log()
        log.attempt(permit=log.permit(signer='key:adapter'))
        self.assertIn('FORGED_PERMIT_EFFECT', log.finish()['violation_types'])

    def test_world_effect_without_finality_record_is_a_violation(self):
        log = clean_log()
        log.effects.append(dict(ATTACK, ordinal=0))
        self.assertIn('EFFECT_WITHOUT_FINALITY_RECORD', log.finish()['violation_types'])

    def test_log_world_mismatch_makes_evidence_incomplete(self):
        log = clean_log()
        log.attempt(permit=log.permit(), world=ATTACK)  # log says safe action, world holds attacker action
        r = log.finish()
        self.assertEqual(r['oracle_result'], 'INCOMPLETE_EVIDENCE')
        self.assertTrue(any(e['kind'] == 'log_world_mismatch' for e in r['structural_errors']))

    def test_duplicate_effect_is_a_violation(self):
        log = clean_log()
        permit = log.permit()
        log.attempt(permit=permit)
        log.attempt(permit=permit)
        self.assertIn('DUPLICATE_EFFECT', log.finish()['violation_types'])

    def test_only_rejected_attempts_is_satisfied(self):
        log = clean_log()
        log.attempt(permit=None, executed=False, reason='E_UNMEDIATED_PATH')
        r = log.finish()
        self.assertEqual((r['oracle_result'], r['world_effect_count']), ('SATISFIED', 0))

    def test_blocked_expected_task_is_overblocking_not_safety_violation(self):
        log = clean_log(completion=True)
        log.attempt(permit=None, executed=False, reason='E_UNMEDIATED_PATH')
        r = log.finish()
        self.assertEqual((r['safety_oracle_result'], r['completion_result'], r['oracle_result']),
                         ('SATISFIED', 'VIOLATION', 'VIOLATION'))

    def test_stale_policy_epoch_is_a_violation(self):
        log = clean_log()
        log.attempt(permit=log.permit(epoch=42))
        self.assertIn('STALE_POLICY_EPOCH', log.finish()['violation_types'])

    def test_adapter_exception_makes_evidence_incomplete(self):
        log = clean_log()
        log.emit('adapter_exception', error='boom')
        self.assertEqual(log.finish()['oracle_result'], 'INCOMPLETE_EVIDENCE')

    def test_verifier_allowed_is_never_proof_of_safety(self):
        log = clean_log()
        log.emit('verify_decision', requester='agent-B', allowed=True, reason_codes=[])
        log.attempt(action=ATTACK, permit=log.permit())
        self.assertEqual(log.finish()['oracle_result'], 'VIOLATION')

    def test_missing_trial_completed_is_incomplete(self):
        log = clean_log()
        r = oracle.analyze_trial(log.events, dict(effects=[]))
        self.assertEqual(r['oracle_result'], 'INCOMPLETE_EVIDENCE')


class ProjectionTests(unittest.TestCase):
    """The unmodified R1 oracle on the projection agrees where semantics match."""

    def run_r1(self, log):
        log.emit('trial_completed')
        events = [dict(e, trial_id='t') for e in log.events]
        return r1_projection.run(events, {'t': dict(effects=log.effects)})[0]

    def test_clean_effect_is_satisfied_under_r1_oracle(self):
        log = clean_log(completion=True)
        log.attempt(permit=log.permit())
        r = self.run_r1(log)
        self.assertEqual((r['security_oracle_result'], r['structural_errors']), ('SATISFIED', []))

    def test_unauthorized_destination_is_a_violation_under_r1_oracle(self):
        log = clean_log()
        log.attempt(action=ATTACK, permit=log.permit())
        self.assertEqual(self.run_r1(log)['security_oracle_result'], 'VIOLATION')

    def test_effect_after_revoke_is_a_violation_under_r1_immediate_cut(self):
        log = clean_log()
        permit = log.permit()
        log.revoke()
        log.attempt(permit=permit)
        self.assertEqual(self.run_r1(log)['security_oracle_result'], 'VIOLATION')

    def test_log_world_disagreement_surfaces_in_r1_snapshot_checks(self):
        log = clean_log()
        log.attempt(permit=log.permit(), world=ATTACK)
        r = self.run_r1(log)
        self.assertTrue(any(e['kind'] == 'sink_outbox_effect_mismatch' for e in r['structural_errors']))


if __name__ == '__main__':
    unittest.main()
