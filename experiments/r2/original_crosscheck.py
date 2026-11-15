"""Confirmatory (post-hoc) cross-check: A2A-hosted path vs the ORIGINAL harness alone.

For the pre-registered seeds, run the original run_system / verify_bundle with no
A2A, queue or adapter, and compare with what the saved R2 run observed. Equal
outcomes mean the multi-agent hosting did not change the original decision for
that artifact. This is NOT part of the pre-registration, uses no adapter code and
does not compare attack-success rates across corpora (the corpora differ).
Run with the R2 environment.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTINUITY = ROOT / 'third_party/continuity'
PINNED = '59cfe60930d247d1890b366ded686c718020a11e'
head = subprocess.check_output(['git', '-C', str(CONTINUITY), 'rev-parse', 'HEAD'], text=True).strip()
if head != PINNED:
    sys.exit(f'original is {head}, expected {PINNED}')
sys.dont_write_bytecode = True
sys.path.insert(0, str(CONTINUITY / 'src'))
from continuity import experiment as X  # noqa: E402
from continuity.core import ContinuityVerifier  # noqa: E402

INFRA = X.build_infrastructure()


def scenario(seed, kind, fault='NONE'):
    return X.make_scenario('workspace', seed, kind, fault=fault, infra=INFRA)


def harness(seed, kind, fault, disabled=()):
    sc = scenario(seed, kind, fault)
    r = X.run_system('CONTINUITY', sc, INFRA, X.materialise(sc, INFRA), frozenset(disabled))
    return dict(disposition=r.disposition, first_outcome=r.first_outcome, effects=r.effect_count,
                reasons=sorted(r.reason.split(';')) if r.disposition in ('DENY', 'ESCALATE') and r.first_outcome == 'NOT_ATTEMPTED' else [])


def verify(seed, kind, fault='NONE', revoked=False, tamper=False, strip=False):
    sc = scenario(seed, kind, fault)
    bundle = X.materialise(sc, INFRA).bundle
    if tamper:
        env = list(bundle.envelopes)
        env[2] = dataclasses.replace(env[2], action=dataclasses.replace(env[2].action, destination='alias:workspace:attacker:9999'))
        bundle = dataclasses.replace(bundle, envelopes=tuple(env))
    if strip:
        bundle = dataclasses.replace(bundle, envelopes=(), receipts=())
    state = INFRA.deployment.runtime_state
    if revoked:
        state = dataclasses.replace(state, revoked_ids=frozenset({sc.root_grant.grant_id}))
    verifier = ContinuityVerifier(INFRA.keyring, INFRA.contracts, dataclasses.replace(INFRA.deployment, runtime_state=state),
                                  INFRA.signers['verifier'])
    d = verifier.verify_bundle(bundle, X.NOW)
    return dict(allowed=d.allowed, reasons=sorted(d.reason_codes))


# condition -> (original-harness computation, how to read the saved R2 observation)
CASES = {
    'R2-0_valid_delegated': (lambda: harness(1001, 'benign', 'NONE'), 'finality0'),
    'R2-1a_unauthorized_destination_attempt': (lambda: verify(89999, 'attack', 'UNTRUSTED_FIELD_BINDING'), 'verifier0'),
    'R2-1b_post_permit_action_substitution': (lambda: harness(1001, 'attack', 'POST_PERMIT_ACTION_SUBSTITUTION'), 'finality0'),
    'R2-3a_stale_permit_after_revocation': (lambda: harness(1001, 'attack', 'REVOKED_GRANT'), 'finality0'),
    'R2-3b_retained_work_after_revocation': (lambda: verify(1001, 'benign', revoked=True), 'verifier0'),
    'R2-5_dispatch_without_permit': (lambda: harness(1001, 'attack', 'ALTERNATE_PATH'), 'finality0'),
    'NC-subject_delegator_uses_delegatee_permit': (lambda: harness(1001, 'attack', 'SUBJECT_SUBSTITUTION'), 'finality0'),
    'NC-missing_proof_empty_chain': (lambda: verify(1001, 'benign', strip=True), 'verifier0'),
    'NC-attacker_minted_root': (lambda: verify(2002, 'attack', 'UNTRUSTED_ROOT_PRODUCER'), 'verifier0'),
    'X-created_after_cut': (lambda: verify(1001, 'benign', revoked=True), 'verifier0'),
    'X-single_agent_post_cut': (lambda: verify(1002, 'benign', revoked=True), 'verifier0'),
    'AB-mediation_off_after_A_deny': (lambda: harness(1001, 'attack', 'ALTERNATE_PATH', ('mediation',)), 'finality0'),
    'AB-revocation_recheck_off': (lambda: harness(1001, 'attack', 'REVOKED_GRANT', ('revocation',)), 'finality0'),
    'AB-action_binding_off': (lambda: harness(1001, 'attack', 'POST_PERMIT_ACTION_SUBSTITUTION', ('action_binding',)), 'finality0'),
    'AB-subject_binding_off': (lambda: harness(1001, 'attack', 'SUBJECT_SUBSTITUTION', ('subject_binding',)), 'finality0'),
}


def observed(events):
    verifier = [(e['allowed'], sorted(e['reason_codes'])) for e in events if e['event_type'] == 'verify_decision']
    finality = [(e['result_reason'], e['world_effect_count_after']) for e in events if e['event_type'] == 'finality_attempt']
    return verifier, finality


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    by = defaultdict(list)
    for line in args.events.read_text().splitlines():
        if line.strip():
            e = json.loads(line)
            by[e['condition_id']].append(e)
    rows = []
    for cid, (compute, mode) in CASES.items():
        original = compute()
        v, f = observed(by[cid])
        if mode == 'verifier0':
            r2 = dict(allowed=v[0][0], reasons=v[0][1])
            equal = (original['allowed'], original['reasons']) == (r2['allowed'], r2['reasons'])
        else:
            first_reason, effects_after = f[0]
            r2 = dict(first_outcome=first_reason.split(':')[0] if first_reason.startswith('BYPASS') else first_reason,
                      effects=effects_after)
            o_first = original['first_outcome']
            o_first = o_first.split(':')[0] if o_first.startswith('BYPASS') else o_first
            equal = (o_first, original['effects']) == (r2['first_outcome'], r2['effects'])
        rows.append(dict(condition_id=cid, mode=mode, original_harness=original, r2_a2a_path=r2, equal=equal))
    out = dict(classification='ORIGINAL_HARNESS_CROSSCHECK_CONFIRMATORY', original_head=head,
               conditions_compared=len(rows), equal=sum(r['equal'] for r in rows),
               not_compared='R2-2 ladder, R2-4 (composed), NC-queue_tamper (a different artifact path): covered by unit tests / composed of compared parts',
               rows=rows)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('conditions_compared', 'equal')}))
    for r in rows:
        if not r['equal']:
            print('DIFFERENT', r['condition_id'], r['original_harness'], r['r2_a2a_path'])
    return 0 if out['equal'] == out['conditions_compared'] else 1


if __name__ == '__main__':
    sys.exit(main())
