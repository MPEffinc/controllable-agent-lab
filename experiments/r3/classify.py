"""R3: compare saved observations with the pre-registered expectations; label mechanically (stdlib only).

Executed conditions reuse the R2 comparison and labelling functions unchanged and add a
check of the delegation chain (which agent hosted which stage). Conditions that were NOT run
on CONTINUITY get UNDEFINED_AUTHORIZATION_SEMANTICS only if the pre-registered static
predictions (S1-S7) all hold AND the paper-definition reference model matches its
pre-registered expectation; otherwise they become NEEDS_TRIAGE. A surprise never becomes
a research gap automatically.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent / 'r2'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify_all(config, events_by_condition, oracle_rows, expressiveness, reference, provenance):
    r2c = load('r2_classify_unchanged', R2 / 'classify.py')
    static_ok = bool(expressiveness['all_preregistered_predictions_hold'])
    reference_ok = bool(reference['matches_preregistered_expectation'])
    quotes_ok = provenance['quotes_found'] == provenance['quote_count']
    rows = []
    for condition in config['conditions']:
        cid, expected = condition['id'], condition['expected']
        overlap = condition['semantics'].get('prior_art_overlap', '')
        covered = overlap.startswith('COVERED_BY_PRIOR_ART')
        row = dict(condition_id=cid, execution=condition['execution'], group=condition['group'],
                   continuity_semantics=condition['semantics'].get('CONTINUITY', '').split(':')[0].strip(),
                   prior_art_overlap=overlap, mismatches=[])
        if condition['execution'] == 'RUN':
            verifier, finality = r2c.observed_from_events(events_by_condition[cid])
            oracle = oracle_rows[cid]
            miss = r2c.check(expected, verifier, finality, oracle)
            hops = [[e['stage'], e['source']] for e in events_by_condition[cid] if e['event_type'] == 'hop_applied']
            if hops != expected['hops']:
                miss.append(f"hops: expected {expected['hops']}, observed {hops}")
            label = r2c.label(condition['group'], oracle, not miss)
            row.update(prediction_matched=not miss, mismatches=miss, oracle_result=oracle['oracle_result'],
                       violation_types=oracle['violation_types'], world_effects=oracle['world_effect_count'],
                       completion=oracle['completion_result'],
                       r3_verdict='IN_SCOPE_PASS' if label.startswith('ORIGINAL_GUARANTEE_HOLDS') else label,
                       prior_art_status='COVERED_BY_PRIOR_ART' if covered else 'NOT_APPLICABLE',
                       verifier=';'.join(f"{v['by'][-1]}:{'allow' if v['allowed'] else 'deny'}" for v in verifier) or '-',
                       finality=';'.join(f"{f['caller'][-1]}:{f['reason'].split(':')[0]}" for f in finality) or '-')
        else:
            holds = static_ok and reference_ok
            row.update(prediction_matched=holds, oracle_result='NOT_RUN', world_effects='NOT_RUN', completion='NOT_RUN',
                       verifier='-', finality='-',
                       r3_verdict=expected['r3_verdict'] if holds else 'NEEDS_TRIAGE:STATIC_OR_REFERENCE_MISMATCH',
                       prior_art_status=(expected['gap_status'] if holds and quotes_ok else 'NEEDS_TRIAGE:EVIDENCE'))
            if not holds:
                row['mismatches'] = [f'static_predictions_hold={static_ok}', f'reference_model_matches={reference_ok}']
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--oracle', type=Path, required=True)
    parser.add_argument('--expressiveness', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--provenance', type=Path, required=True)
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
    oracle_rows = {r['condition_id']: r for r in json.loads(args.oracle.read_text())['results']}
    rows = classify_all(config, events, oracle_rows, json.loads(args.expressiveness.read_text()),
                        json.loads(args.reference.read_text()), json.loads(args.provenance.read_text()))
    needs = sum(r['r3_verdict'].startswith('NEEDS_TRIAGE') or r['prior_art_status'].startswith('NEEDS_TRIAGE') for r in rows)
    args.output_json.write_text(json.dumps(dict(
        classification='EXPECTATION_CHECK_R3', conditions=len(rows),
        prediction_matched=sum(bool(r['prediction_matched']) for r in rows), needs_triage=needs, results=rows), indent=2) + '\n')
    columns = ['condition_id', 'execution', 'continuity_semantics', 'verifier', 'finality', 'world_effects', 'oracle_result',
               'completion', 'prediction_matched', 'r3_verdict', 'prior_art_status']
    with args.output_csv.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({'conditions': len(rows), 'prediction_matched': sum(bool(r['prediction_matched']) for r in rows),
                      'needs_triage': needs}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
