"""R3 oracle: the R2 independent oracle, UNCHANGED, plus the R3 record fields (stdlib only).

The safety and completion verdicts come from experiments/r2/oracle.py exactly as in
R2 (IMMEDIATE_CUT_AT_FINALITY, judged from the saved world snapshot; the verifier's
allowed=True and the sink's success return are never proof of safety). This wrapper
adds, per trial, the items R3 must record: root principal, current and delegating
actor, parent and independent authority support, grant issuer, signed delegation
evidence, revoked grant or edge, permit, finality decision, actual effect and the
oracle verdict. For CONTINUITY the parent support is always NONE and the signed
delegation evidence proves WORK delegation only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2_ORACLE = HERE.parent / 'r2' / 'oracle.py'


def load_r2_oracle():
    spec = importlib.util.spec_from_file_location('r2_oracle_unchanged', R2_ORACLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def r3_record(rows, result):
    """rows: the events of one trial. result: the R2 oracle result of the same trial."""
    grants = {e['grant_id']: e for e in rows if e['event_type'] == 'grant_issued'}
    records = {e['grant_id']: e for e in rows if e['event_type'] == 'grant_record'}
    supports = [dict(grant_id=gid, root_principal=records[gid]['root_principal'],
                     grant_issuer=records[gid]['grant_issuer'], support_kind=records[gid]['support_kind'],
                     parent_support=records[gid]['parent_support'],
                     independent_supports=records[gid]['independent_supports'],
                     authorized_actor=grants[gid]['authorized_actor'])
                for gid in grants if gid in records]
    contexts = [dict(work_id=e['work_id'], current_actor=e['current_actor'], delegating_actor=e['delegating_actor'],
                     delegation_kind=e['delegation_kind'],
                     authority_delegation_evidence=e['authority_delegation_evidence'])
                for e in rows if e['event_type'] == 'delegation_context']
    hops = [dict(stage=e['stage'], agent=e['source'], signer=e['signer'], input_digest=e['input_digest'],
                 output_digest=e['output_digest']) for e in rows if e['event_type'] == 'hop_applied']
    attempts = []
    for e in rows:
        if e['event_type'] != 'finality_attempt':
            continue
        permit = e.get('permit') or {}
        attempts.append(dict(current_actor=e['caller_identity'], caller_agent=e['caller_agent'],
                             permit_id=permit.get('permit_id'), permit_grant_id=permit.get('grant_id'),
                             permit_subject=permit.get('subject'),
                             finality_decision=dict(ok=e['result_ok'], reason=e['result_reason']),
                             effect_id=e.get('effect_id'), runtime_revoked_ids=e['state']['revoked_ids']))
    return dict(
        trial_id=result['trial_id'], condition_id=result['condition_id'],
        root_principals=sorted({s['root_principal'] for s in supports}),
        grant_issuers=sorted({s['grant_issuer'] for s in supports}),
        authority_supports=supports,
        work_delegation_chain=contexts,
        signed_delegation_evidence=dict(
            work_delegation_receipts=len(hops), hops=hops,
            authority_delegation_evidence='NONE',
            meaning='stage receipts prove that WORK moved and the context was preserved; CONTINUITY has no signed authority-delegation object'),
        revoked=dict(grants=[e['grant_id'] for e in rows if e['event_type'] == 'revoke'], edges='NOT_REPRESENTABLE'),
        finality_attempts=attempts,
        actual_effects=result['effects'], world_effect_count=result['world_effect_count'],
        independent_oracle_verdict=dict(overall=result['oracle_result'], safety=result['safety_oracle_result'],
                                        completion=result['completion_result'], violation_types=result['violation_types']))


def analyze(events, worlds):
    r2 = load_r2_oracle()
    results = r2.analyze_events(events, worlds)
    grouped = defaultdict(list)
    for event in events:
        grouped[event['trial_id']].append(event)
    records = [r3_record(grouped[r['trial_id']], r) for r in results]
    return results, records


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--world', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    events = [json.loads(x) for x in args.events.read_text().splitlines() if x.strip()]
    results, records = analyze(events, json.loads(args.world.read_text()))
    count = lambda key, values: {v: sum(r[key] == v for r in results) for v in values}  # noqa: E731
    out = dict(classification='R3_ORACLE_R2_UNCHANGED_PLUS_RECORD',
               r2_oracle_sha256=hashlib.sha256(R2_ORACLE.read_bytes()).hexdigest(),
               trials=len(results), results=results, records=records,
               oracle_outcome_counts=count('oracle_result', ('SATISFIED', 'VIOLATION', 'INCOMPLETE_EVIDENCE')),
               completion_outcome_counts=count('completion_result', ('SATISFIED', 'VIOLATION', 'NOT_EXERCISED')),
               world_effects_total=sum(r['world_effect_count'] for r in results))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k not in ('results', 'records')}))
    return 2 if any(r['structural_errors'] for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
