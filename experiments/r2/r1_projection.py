"""Run the UNMODIFIED R1 oracle on a projection of R2 evidence (stdlib only).

Why a projection: R1's oracle judges (root, principal, support, tool, recipient)
at SINK ACCEPTANCE and allows a later commit of a pre-cut acceptance
(grandfather). CONTINUITY has no pending-receipt state: checking and effect are one
atomic finality call. The projection therefore emits each real effect as an
ADJACENT sink_accept + sink_commit pair, so only the immediate-cut safety lens of
R1 is exercised. The grandfather and cancel-pending/fence lenses are NOT
applicable (NON_EQUIVALENT_SEMANTICS) and conditions that depend on them are
labelled instead of being scored.

Sources: accept events come from the gateway's finality records (the log), the
R1 sink snapshot comes from the saved world (what really landed). A disagreement
between the two surfaces through R1's own snapshot checks.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R1_ORACLE = HERE.parent / 'r1' / 'oracle.py'
NOT = 'NOT_OBSERVED'
TOOL = 'email.send'


def load_r1_oracle():
    spec = importlib.util.spec_from_file_location('r1_oracle_unmodified', R1_ORACLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project_trial(rows, world):
    """rows: R2 events of one trial. Returns (r1_events, r1_sink_state)."""
    start = rows[0]
    labels = {}  # task root -> R1 root name, by material order of grant issuance
    for e in rows:
        if e['event_type'] == 'grant_issued':
            labels[e['root_task_id']] = 'root-A' if e['material_label'] == 'rootA' else 'root-B'
    completion = [e for e in rows if e['event_type'] == 'grant_issued' and e.get('completion_expected')]
    scenario = (('C0' if completion[0]['material_label'] == 'rootA' else 'C5') if len(completion) == 1
                else 'R2_NO_CONTINUATION_CLAIM')
    out, receipts, outbox = [], {}, []

    def emit(event_type, **fields):
        event = dict(seq=len(out) + 1, trial_id=start['trial_id'], scenario=scenario,
                     condition_id=start['condition_id'], event_type=event_type)
        event.update(fields)
        out.append(event)
        return event

    emit('trial_started')
    effects = (world or {}).get('effects', [])
    for e in rows:
        kind = e['event_type']
        if kind == 'grant_issued':
            emit('grant', grant=dict(support_id=e['grant_id'], root_task_id=labels[e['root_task_id']],
                                     principal_id=e['principal_id'], tool=TOOL,
                                     recipient=e['authorized_effect']['destination']))
        elif kind == 'revoke':
            emit('revoke', root_task_id=labels.get(e['root_task_id'], e['root_task_id']))
        elif kind == 'finality_attempt' and e.get('new_effect'):
            action = e['action']
            permit = e.get('permit') or {}
            root = labels.get(permit.get('task_root'), NOT)
            principal = permit.get('principal', NOT)
            support = permit.get('grant_id', NOT)
            receipt_id = f"{start['trial_id']}-receipt-{len(receipts) + 1}"
            args = dict(work_id=f'{receipt_id}-work', root_task_id=root, principal_id=principal,
                        authorization_support=support, recipient=action['destination'],
                        body=action['parameters'].get('body'))
            accept = emit('sink_accept', receipt_id=receipt_id, args=args, proposed_tool_call=TOOL)
            receipts[receipt_id] = dict(work=dict(args), accepted_at=accept['seq'],
                                        cancelled=False, committed=True)
            emit('sink_commit', receipt_id=receipt_id, committed_effect=dict(
                root_task_id=root, principal_id=principal, recipient=args['recipient'],
                body=args['body'], receipt_id=receipt_id))
    # The R1 snapshot is built from what really landed in the world, not from the log.
    for index, effect in enumerate(effects):
        receipt_id = f"{start['trial_id']}-receipt-{index + 1}"
        mapped = receipts.get(receipt_id, {}).get('work', {})
        outbox.append(dict(receipt_id=receipt_id, root_task_id=mapped.get('root_task_id', NOT),
                           principal_id=mapped.get('principal_id', NOT), recipient=effect['destination'],
                           body=effect['parameters'].get('body')))
    emit('trial_completed')
    return out, dict(receipts=receipts, outbox=outbox)


def run(events, worlds):
    r1 = load_r1_oracle()
    grouped = defaultdict(list)
    for event in events:
        grouped[event['trial_id']].append(event)
    all_events, sinks = [], {}
    for trial_id, rows in grouped.items():
        projected, sink = project_trial(rows, worlds[trial_id])
        all_events.extend(projected)
        sinks[trial_id] = sink
    return r1.analyze_events(all_events, sinks)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--world', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    events = [json.loads(x) for x in args.events.read_text().splitlines() if x.strip()]
    config = json.loads(args.config.read_text())
    equivalence = {c['id']: c['r1_equivalence'] for c in config['conditions']}
    rows = run(events, json.loads(args.world.read_text()))
    for row in rows:
        condition = row['condition_id']
        row['r1_equivalence'] = equivalence.get(condition, NOT)
        row['r1_semantics_applicable'] = row['r1_equivalence'] not in ('NON_EQUIVALENT_SEMANTICS',)
    result = dict(
        classification='R1_ORACLE_UNMODIFIED_ON_R2_PROJECTION',
        projection_semantics=('each real effect = adjacent sink_accept + sink_commit; grandfather and '
                              'cancel-pending lenses not applicable to CONTINUITY finality'),
        trials=len(rows), results=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    summary = {r['condition_id']: (r['security_oracle_result'], r['independent_root_continuation_result'],
                                   r['r1_semantics_applicable']) for r in rows}
    print(json.dumps(summary))
    return 2 if any(r['structural_errors'] for r in rows) else 0


if __name__ == '__main__':
    sys.exit(main())
