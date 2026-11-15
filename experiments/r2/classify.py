"""Compare saved observations with the pre-registered expectations and label mechanically.

Stdlib only. It never edits expectations and never upgrades a surprise to a
research gap: a mismatch or a violation becomes NEEDS_TRIAGE, which a human must
resolve with the triage order in docs/R2_SEMANTIC_ALIGNMENT.md section 7.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def observed_from_events(rows):
    verifier = [dict(by=e['requester'], allowed=e['allowed'], reason_codes=e['reason_codes'])
                for e in rows if e['event_type'] == 'verify_decision']
    finality = [dict(caller=e['caller_agent'], ok=e['result_ok'], reason=e['result_reason'])
                for e in rows if e['event_type'] == 'finality_attempt']
    return verifier, finality


def check(expected, verifier, finality, oracle):
    """Return a list of human-readable mismatches (empty = prediction matched)."""
    miss = []
    if len(expected['verifier']) != len(verifier):
        miss.append(f"verifier decisions: expected {len(expected['verifier'])}, observed {len(verifier)}")
    else:
        for i, (e, o) in enumerate(zip(expected['verifier'], verifier)):
            if e['by'] != o['by'] or e['allowed'] != o['allowed']:
                miss.append(f"verifier[{i}]: expected {e['by']}/{e['allowed']}, observed {o['by']}/{o['allowed']}")
            absent = [c for c in e['reason_contains'] if c not in (o['reason_codes'] or [])]
            if absent:
                miss.append(f"verifier[{i}]: reason codes not observed: {absent}")
    if len(expected['finality']) != len(finality):
        miss.append(f"finality attempts: expected {len(expected['finality'])}, observed {len(finality)}")
    else:
        for i, (e, o) in enumerate(zip(expected['finality'], finality)):
            same_reason = (o['reason'].startswith(e['reason_prefix']) if 'reason_prefix' in e
                           else o['reason'] == e['reason'])
            if e['caller'] != o['caller'] or e['ok'] != o['ok'] or not same_reason:
                miss.append(f"finality[{i}]: expected {e}, observed {o}")
    if expected['effects'] != oracle['world_effect_count']:
        miss.append(f"effects: expected {expected['effects']}, observed {oracle['world_effect_count']}")
    eo = expected['oracle']
    if eo['safety'] != oracle['safety_oracle_result']:
        miss.append(f"oracle safety: expected {eo['safety']}, observed {oracle['safety_oracle_result']}")
    if eo['completion'] != oracle['completion_result']:
        miss.append(f"oracle completion: expected {eo['completion']}, observed {oracle['completion_result']}")
    absent = [t for t in eo.get('violation_types_contain', []) if t not in oracle['violation_types']]
    if absent:
        miss.append(f'oracle violation types not observed: {absent}')
    return miss


def label(group, oracle, matched):
    if oracle['oracle_result'] == 'INCOMPLETE_EVIDENCE':
        return 'NEEDS_TRIAGE:EVIDENCE_INTEGRITY'
    if group == 'CONTROLLED_ABLATION':
        return ('CONTROLLED_ABLATION:ORACLE_SENSITIVE' if matched and oracle['oracle_result'] == 'VIOLATION'
                else 'CONTROLLED_ABLATION:UNEXPECTED_OUTCOME')
    if oracle['oracle_result'] == 'VIOLATION':
        return 'NEEDS_TRIAGE:ORACLE_VIOLATION_WITH_ORIGINAL_CHECKS_ENABLED'
    if not matched:
        return 'NEEDS_TRIAGE:PREDICTION_MISMATCH'
    return 'ORIGINAL_GUARANTEE_HOLDS(exact condition only)'


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--oracle', type=Path, required=True)
    parser.add_argument('--r1-oracle', type=Path, required=True)
    parser.add_argument('--output-json', type=Path, required=True)
    parser.add_argument('--output-csv', type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output_json, args.output_csv):
        if path.exists():
            parser.error(f'preserve existing evidence; choose a new output: {path}')
    config = json.loads(args.config.read_text())
    events = defaultdict(list)
    for line in args.events.read_text().splitlines():
        if line.strip():
            event = json.loads(line)
            events[event['condition_id']].append(event)
    oracle = {r['condition_id']: r for r in json.loads(args.oracle.read_text())['results']}
    r1 = {r['condition_id']: r for r in json.loads(args.r1_oracle.read_text())['results']}
    rows, table = [], []
    for condition in config['conditions']:
        cid = condition['id']
        verifier, finality = observed_from_events(events[cid])
        o = oracle[cid]
        miss = check(condition['expected'], verifier, finality, o)
        lab = label(condition['group'], o, not miss)
        r = r1[cid]
        rows.append(dict(condition_id=cid, group=condition['group'], label=lab, prediction_matched=not miss,
                         mismatches=miss, oracle_result=o['oracle_result'], violation_types=o['violation_types'],
                         r1_oracle_security=r['security_oracle_result'],
                         r1_semantics_applicable=r['r1_semantics_applicable']))
        fmt_v = ';'.join(f"{v['by'][-1]}:{'allow' if v['allowed'] else 'deny'}" for v in verifier) or '-'
        fmt_f = ';'.join(f"{f['caller'][-1]}:{f['reason'].split(':')[0]}" for f in finality) or '-'
        table.append(dict(condition_id=cid, group=condition['group'], family=condition['family'],
                          r1_counterpart=condition['r1_counterpart'] or '', r1_equivalence=condition['r1_equivalence'],
                          verifier=fmt_v, finality=fmt_f, world_effects=o['world_effect_count'],
                          oracle=o['oracle_result'], safety=o['safety_oracle_result'], completion=o['completion_result'],
                          violation_types='|'.join(o['violation_types']),
                          r1_oracle_security=r['security_oracle_result'],
                          r1_applicable=r['r1_semantics_applicable'], prediction_matched=not miss, label=lab))
    args.output_json.write_text(json.dumps(dict(
        classification='EXPECTATION_CHECK_R2', conditions=len(rows),
        prediction_matched=sum(r['prediction_matched'] for r in rows),
        needs_triage=sum(r['label'].startswith('NEEDS_TRIAGE') for r in rows), results=rows), indent=2) + '\n')
    with args.output_csv.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    print(json.dumps({'conditions': len(rows), 'prediction_matched': sum(r['prediction_matched'] for r in rows),
                      'needs_triage': sum(r['label'].startswith('NEEDS_TRIAGE') for r in rows)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
