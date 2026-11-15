"""Verify shared R2 evidence without third_party checkouts, virtual environments or API calls.

This replays the saved evidence (hashes, oracle, R1 projection, expectation check,
replicate agreement, command exit codes, pre-registration order, sensitive-pattern
scan). It is a consistency check of saved evidence, NOT a runtime reproduction.
  python3 experiments/r2/verify_saved.py                  # verify
  python3 experiments/r2/verify_saved.py --write-manifest # once, after all results exist
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'results/r2'
MANIFEST = BASE / 'analysis-manifest.json'
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import oracle  # noqa: E402
import r1_projection  # noqa: E402

PREREG = '75870a95fc0161176e108c03d7c0f5c6e5344bb5'
PINNED = '59cfe60930d247d1890b366ded686c718020a11e'
RUNS = {'run-01': ('oracle-01.json', 'r1-oracle-01.json'), 'run-02-replicate': ('oracle-02-replicate.json', None)}
SENSITIVE = re.compile(r'sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,}|ghp_[A-Za-z0-9]{16,}|BEGIN [A-Z ]*PRIVATE KEY|'
                       r'LLM_API_KEY|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|\.ac\.kr')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_events(run):
    return [json.loads(x) for x in (BASE / run / 'events.jsonl').read_text().splitlines() if x.strip()]


def git(*args):
    try:
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def outcome_signature(run, oracle_file):
    events = load_events(run)
    results = {r['condition_id']: r for r in json.loads((BASE / oracle_file).read_text())['results']}
    out = defaultdict(lambda: {'verifier': [], 'finality': []})
    for e in events:
        d = out[e['condition_id']]
        if e['event_type'] == 'verify_decision':
            d['verifier'].append((e['requester'], e['allowed'], tuple(e['reason_codes'])))
        if e['event_type'] == 'finality_attempt':
            d['finality'].append((e['caller_agent'], e['result_ok'], e['result_reason'], e['new_effect']))
    for cid, d in out.items():
        r = results[cid]
        d['oracle'] = (r['oracle_result'], r['safety_oracle_result'], r['completion_result'],
                       tuple(r['violation_types']), r['world_effect_count'])
    return dict(out)


def check():
    config = json.loads((HERE / 'config.json').read_text())
    report = {}
    for run, (oracle_file, r1_file) in RUNS.items():
        manifest = json.loads((BASE / run / 'manifest.json').read_text())
        for key, path in (('events_sha256', BASE / run / 'events.jsonl'), ('world_state_sha256', BASE / run / 'world_state.json'),
                          ('summary_sha256', BASE / run / 'summary.json'), ('config_sha256', HERE / 'config.json')):
            assert sha(path) == manifest[key], f'{run}: {key}'
        for name, expected in manifest['code_sha256'].items():
            # the executed adapter code must be exactly the committed code (no silent edit after the run)
            assert sha(HERE / name) == expected, f'{run}: {name} changed after the run'
        assert manifest['original_continuity']['head'] == PINNED, f'{run}: original SHA'
        assert manifest['original_continuity']['working_tree_clean'] is True, f'{run}: original modified'
        assert manifest['uncommitted_code_paths'] == [], f'{run}: code was not committed before the run'
        assert manifest['tracked_files_dirty'] is False, f'{run}: tracked files dirty'
        summary = json.loads((BASE / run / 'summary.json').read_text())
        assert summary['model_calls'] == 0 and summary['trial_count'] == len(config['conditions'])
        assert all(t['adapter_errors'] == 0 for t in summary['trials']), f'{run}: adapter errors'
        events = load_events(run)
        worlds = json.loads((BASE / run / 'world_state.json').read_text())
        replay = oracle.analyze_events(events, worlds)
        saved = json.loads((BASE / oracle_file).read_text())
        assert replay == saved['results'], f'{run}: oracle replay mismatch'
        assert not any(r['structural_errors'] for r in replay), f'{run}: structural errors'
        report[run] = dict(trials=len(replay), events=len(events), oracle=saved['oracle_outcome_counts'])
        if r1_file:
            r1_saved = json.loads((BASE / r1_file).read_text())['results']
            r1_replay = r1_projection.run(events, worlds)
            drop = ('r1_equivalence', 'r1_semantics_applicable')
            assert [{k: v for k, v in r.items() if k not in drop} for r in r1_saved] == r1_replay, 'R1 projection replay mismatch'
            report[run]['r1_security'] = {s: sum(r['security_oracle_result'] == s for r in r1_replay)
                                          for s in ('SATISFIED', 'VIOLATION', 'INCOMPLETE_EVIDENCE')}
    # expectation check replay (run-01)
    events = load_events('run-01')
    oracle_rows = {r['condition_id']: r for r in oracle.analyze_events(events, json.loads((BASE / 'run-01/world_state.json').read_text()))}
    by = defaultdict(list)
    for e in events:
        by[e['condition_id']].append(e)
    saved_check = {r['condition_id']: r for r in json.loads((BASE / 'expectation-check-01.json').read_text())['results']}
    for condition in config['conditions']:
        cid = condition['id']
        verifier, finality = classify.observed_from_events(by[cid])
        miss = classify.check(condition['expected'], verifier, finality, oracle_rows[cid])
        lab = classify.label(condition['group'], oracle_rows[cid], not miss)
        assert (saved_check[cid]['prediction_matched'], saved_check[cid]['label']) == (not miss, lab), cid
    report['expectation_check'] = dict(conditions=len(saved_check),
                                       matched=sum(r['prediction_matched'] for r in saved_check.values()))
    # replicate agreement
    assert outcome_signature('run-01', 'oracle-01.json') == outcome_signature('run-02-replicate', 'oracle-02-replicate.json')
    report['replicate_outcomes_identical'] = True
    # command records
    count = 0
    for meta in sorted((BASE / 'commands').glob('*.json')):
        command = json.loads(meta.read_text())
        assert f'EXIT_CODE={command["exit_code"]}' in (ROOT / command['log']).read_text(), meta
        count += 1
    report['command_records'] = count
    # config frozen since pre-registration, and run committed after it
    assert git('log', '-n1', '--format=%H', '--', 'experiments/r2/config.json') == PREREG, 'config changed after pre-registration'
    first = git('log', '--diff-filter=A', '--format=%H', '--', 'results/r2/run-01/events.jsonl')
    if first:
        first = first.splitlines()[-1]
        order = subprocess.call(['git', 'merge-base', '--is-ancestor', PREREG, first], cwd=ROOT)
        assert order == 0 and PREREG != first, 'pre-registration is not an ancestor of the commit that added the run'
        report['prereg_before_results'] = 'VERIFIED'
    else:
        report['prereg_before_results'] = 'UNKNOWN (run not committed yet)'
    # sensitive pattern scan over shared R2 evidence
    hits = []
    for path in list(BASE.rglob('*')) + list(HERE.glob('*.py')) + list(HERE.glob('*.json')) + [ROOT / 'docs/R2_SEMANTIC_ALIGNMENT.md']:
        if (path.is_file() and path != MANIFEST and path.name != 'verify_saved.py'  # its own regex text would match
                and path.suffix in ('.json', '.jsonl', '.txt', '.csv', '.py', '.md')):
            if SENSITIVE.search(path.read_text(errors='ignore')):
                hits.append(str(path.relative_to(ROOT)))
    assert not hits, f'sensitive-looking patterns in {hits}'
    report['sensitive_pattern_hits'] = 0
    return dict(status='VERIFIED', classification='SAVED_EVIDENCE_REPLAY_NOT_RUNTIME_REPRODUCTION', **report)


def tracked_outputs():
    paths = [p for p in BASE.rglob('*') if p.is_file() and p != MANIFEST]
    paths += list(HERE.glob('*.py')) + [HERE / 'config.json', HERE / 'requirements-input.txt',
                                        HERE / 'requirements-observed.txt', ROOT / 'scripts/r2_run.py']
    return sorted(set(paths))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--write-manifest', action='store_true')
    args = parser.parse_args()
    result = check()
    if args.write_manifest:
        if MANIFEST.exists():
            parser.error('preserve evidence; manifest already exists')
        MANIFEST.write_text(json.dumps(dict(
            scope='Canonical run is run-01; run-02-replicate is an unmodified replicate; original_crosscheck is confirmatory (post-hoc).',
            preregistration_commit=PREREG, original_continuity_sha=PINNED,
            source_files_and_outputs={str(p.relative_to(ROOT)): sha(p) for p in tracked_outputs()},
            observed_verification=result), indent=2) + '\n')
    else:
        manifest = json.loads(MANIFEST.read_text())
        for path, expected in manifest['source_files_and_outputs'].items():
            assert sha(ROOT / path) == expected, path
    print(json.dumps(result))


if __name__ == '__main__':
    main()
