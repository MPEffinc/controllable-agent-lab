"""Verify shared R1 evidence without vendor checkouts, environments or API calls."""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys
from oracle import analyze_events

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'results/r1'
MANIFEST=BASE/'analysis-manifest.json'
LOCAL_RAW={'continuity-quick-01/raw_results.csv','continuity-quick-01/ablation_raw.csv'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def rows(p):
    with p.open(newline='') as f: return list(csv.DictReader(f))

def check():
    run=BASE/'fixture-run-01'
    manifest=json.loads((run/'manifest.json').read_text())
    for key,p in [('code_sha256',ROOT/'experiments/r1/scenario.py'),
                  ('config_sha256',ROOT/'experiments/r1/config.json'),
                  ('events_sha256',run/'events.jsonl'),('sink_state_sha256',run/'sink_state.json'),
                  ('summary_sha256',run/'summary.json')]:
        assert sha(p)==manifest[key],str(p)
    events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
    snapshots=json.loads((run/'sink_state.json').read_text())
    observed=analyze_events(events,snapshots)
    oracle=json.loads((BASE/'oracle-02.json').read_text())
    assert observed==oracle['results'],'canonical oracle replay mismatch'
    assert not any(r['structural_errors'] for r in observed)
    summary=rows(BASE/'condition_summary.csv')
    assert len(summary)==len(observed)
    for exported,actual in zip(summary,observed):
        assert exported['condition_id']==actual['condition_id']
        assert int(exported['commits'])==actual['sink_commits']
        assert int(exported['unauthorized_commits'])==actual['unauthorized_commits']
        assert exported['overall_result']==actual['oracle_result']
    command_count=0
    for p in sorted((BASE/'commands').glob('*.json')):
        command=json.loads(p.read_text())
        text=(ROOT/command['log']).read_text()
        assert f'EXIT_CODE={command["exit_code"]}' in text,p
        command_count+=1
    continuity=BASE/'continuity-quick-01'
    cm=json.loads((continuity/'manifest.json').read_text())
    projection=rows(continuity/'score_projection.csv')
    assert len(projection)==cm['system_scenario_runs']
    by_system=defaultdict(list)
    for row in projection:
        by_system[row['system']].append(row)
        if row['kind']=='attack':
            threshold=1 if row['fault'] in ('NONCE_REPLAY','RETRY_DUPLICATE') else 0
            assert (int(row['effect_count'])>threshold)==(row['violation_accepted']=='True')
    for item in rows(continuity/'summary.csv'):
        selected=by_system[item['system']]
        attack=[r for r in selected if r['kind']=='attack']
        assert len(selected)==cm['scenarios']
        assert len(attack)==int(item['attack_instances'])
        asr=sum(r['violation_accepted']=='True' for r in attack)/len(attack)
        assert abs(asr-float(item['effect_attack_success_rate']))<1e-12
    con=json.loads((BASE/'continuity-source-runtime.json').read_text())
    for name,expected in con['output_sha256'].items():
        p=continuity/name
        if p.exists(): assert sha(p)==expected,name
        elif f'continuity-quick-01/{name}' not in LOCAL_RAW: raise AssertionError(name)
    return dict(status='VERIFIED',classification='SAVED_EVIDENCE_REPLAY_NOT_RUNTIME_REPRODUCTION',
                fixture_trials=len(observed),fixture_events=len(events),
                security_outcomes=oracle['security_outcome_counts'],
                continuation_outcomes=oracle['continuation_outcome_counts'],
                command_records=command_count,continuity_projection_rows=len(projection),
                continuity_ablation_projection_rows=len(rows(continuity/'ablation_score_projection.csv')))

def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--write-manifest',action='store_true')
    args=parser.parse_args()
    result=check()
    if args.write_manifest:
        if MANIFEST.exists(): parser.error('preserve evidence; manifest already exists')
        paths=[ROOT/p for p in ['experiments/progent_policy_component.py','scripts/r1_run.py']]
        paths+=list((ROOT/'experiments/r1').glob('*.py'))+[ROOT/'experiments/r1/config.json']
        paths+=[p for p in BASE.rglob('*') if p.is_file() and p!=MANIFEST
                and str(p.relative_to(BASE)) not in LOCAL_RAW]
        manifest=dict(scope='Canonical oracle02; oracle01 retained as initial safety-only diagnostic',
                      executed_fixture_source=manifest_source(),
                      source_files_and_outputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
                      observed_verification=result)
        MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(MANIFEST.read_text())
        for p,expected in manifest['source_files_and_outputs'].items():
            assert sha(ROOT/p)==expected,p
    print(json.dumps(result))

def manifest_source():
    d=json.loads((BASE/'fixture-run-01/manifest.json').read_text())
    return {k:d[k] for k in ('parent_commit','code_sha256','config_sha256','source_commits','source_file_sha256')}

if __name__=='__main__': main()
