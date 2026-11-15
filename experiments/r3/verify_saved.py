"""Verify shared R3 evidence without third_party checkouts, virtual environments or API calls.

Replays the saved evidence: hashes, the R3 oracle, the expectation check, the paper-definition
reference model, replicate agreement, command exit codes, the static-check and mutation-check
results, the quote verification, pre-registration order and a sensitive-pattern scan. It is a
consistency check of saved evidence, NOT a runtime reproduction.
  python3 experiments/r3/verify_saved.py                  # verify
  python3 experiments/r3/verify_saved.py --write-manifest # once, after all results exist
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
R2 = ROOT / 'experiments/r2'
BASE = ROOT / 'results/r3'
MANIFEST = BASE / 'analysis-manifest.json'
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import oracle as r3_oracle  # noqa: E402
import reference_model  # noqa: E402

PREREG = 'd7bfe9b610474294d5c0ad94ee4302d663c3db51'
PINNED = '59cfe60930d247d1890b366ded686c718020a11e'
RUNS = {'run-01': 'oracle-01.json', 'run-02-replicate': 'oracle-02-replicate.json'}
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


def signature(run, oracle_file):
    results = {r['condition_id']: r for r in json.loads((BASE / oracle_file).read_text())['results']}
    out = defaultdict(lambda: {'verifier': [], 'finality': []})
    for e in load_events(run):
        d = out[e['condition_id']]
        if e['event_type'] == 'verify_decision':
            d['verifier'].append((e['requester'], e['allowed'], tuple(e['reason_codes'])))
        if e['event_type'] == 'finality_attempt':
            d['finality'].append((e['caller_agent'], e['result_ok'], e['result_reason'], e['new_effect']))
        if e['event_type'] == 'hop_applied':
            d.setdefault('hops', []).append((e['stage'], e['source']))
    for cid, d in out.items():
        r = results[cid]
        d['oracle'] = (r['oracle_result'], r['safety_oracle_result'], r['completion_result'],
                       tuple(r['violation_types']), r['world_effect_count'])
    return dict(out)


def check():
    config = json.loads((HERE / 'config.json').read_text())
    runnable = [c for c in config['conditions'] if c['execution'] == 'RUN']
    report = {}
    for run, oracle_file in RUNS.items():
        manifest = json.loads((BASE / run / 'manifest.json').read_text())
        for key, path in (('events_sha256', BASE / run / 'events.jsonl'), ('world_state_sha256', BASE / run / 'world_state.json'),
                          ('summary_sha256', BASE / run / 'summary.json'), ('config_sha256', HERE / 'config.json')):
            assert sha(path) == manifest[key], f'{run}: {key}'
        for name, expected in manifest['code_sha256'].items():
            path = (HERE / name[3:]) if name.startswith('r3/') else (R2 / name[3:])
            assert sha(path) == expected, f'{run}: {name} changed after the run'
        assert manifest['original_continuity']['head'] == PINNED, f'{run}: original SHA'
        assert manifest['original_continuity']['working_tree_clean'] is True, f'{run}: original modified'
        assert manifest['uncommitted_code_paths'] == [], f'{run}: code was not committed before the run'
        assert manifest['tracked_files_dirty'] is False, f'{run}: tracked files dirty'
        summary = json.loads((BASE / run / 'summary.json').read_text())
        assert summary['model_calls'] == 0 and summary['trial_count'] == len(runnable)
        assert all(t['adapter_errors'] == 0 for t in summary['trials']), f'{run}: adapter errors'
        events = load_events(run)
        worlds = json.loads((BASE / run / 'world_state.json').read_text())
        results, records = r3_oracle.analyze(events, worlds)
        saved = json.loads((BASE / oracle_file).read_text())
        assert results == saved['results'] and records == saved['records'], f'{run}: oracle replay mismatch'
        assert not any(r['structural_errors'] for r in results), f'{run}: structural errors'
        report[run] = dict(trials=len(results), events=len(events), oracle=saved['oracle_outcome_counts'])
    # reference model, static check, provenance, mutation check
    reference = json.loads((BASE / 'reference-model-01.json').read_text())
    assert reference['computed'] == reference_model.compute(config), 'reference model replay mismatch'
    assert reference['matches_preregistered_expectation'] is True
    expressiveness = json.loads((BASE / 'expressiveness-01.json').read_text())
    assert expressiveness['all_preregistered_predictions_hold'] is True and expressiveness['original_head'] == PINNED
    core = ROOT / 'third_party/continuity/src/continuity/core.py'
    report['static_core_hash'] = ('recomputed and equal' if core.exists() and sha(core) == expressiveness['core_sha256']
                                  else 'saved value only (original checkout not present)')
    provenance = json.loads((BASE / 'research-provenance.json').read_text())
    assert provenance['quotes_found'] == provenance['quote_count'] and provenance['vera_artifact']['executed'] is False
    mutation = json.loads((BASE / 'mutation-check-01.json').read_text())
    assert mutation['baseline_passes'] and not mutation['survived']
    report['static_reference_provenance_mutation'] = dict(
        static=[c['id'] for c in expressiveness['checks'] if c['holds']], reference_matches=True,
        quotes=f"{provenance['quotes_found']}/{provenance['quote_count']}", mutants_killed=f"{mutation['killed']}/{mutation['mutants']}")
    # expectation replay (run-01)
    events = load_events('run-01')
    by = defaultdict(list)
    for e in events:
        by[e['condition_id']].append(e)
    oracle_rows = {r['condition_id']: r for r in json.loads((BASE / 'oracle-01.json').read_text())['results']}
    replay = classify.classify_all(config, by, oracle_rows, expressiveness, reference, provenance)
    saved_rows = {r['condition_id']: r for r in json.loads((BASE / 'expectation-check-01.json').read_text())['results']}
    for row in replay:
        saved = saved_rows[row['condition_id']]
        assert (saved['r3_verdict'], saved['prior_art_status'], saved['prediction_matched']) == \
               (row['r3_verdict'], row['prior_art_status'], row['prediction_matched']), row['condition_id']
    report['expectation_check'] = dict(conditions=len(saved_rows), matched=sum(bool(r['prediction_matched']) for r in saved_rows.values()),
                                       verdicts={r['condition_id']: r['r3_verdict'] for r in saved_rows.values()})
    assert signature('run-01', 'oracle-01.json') == signature('run-02-replicate', 'oracle-02-replicate.json')
    report['replicate_outcomes_identical'] = True
    count = 0
    for meta in sorted((BASE / 'commands').glob('*.json')):
        command = json.loads(meta.read_text())
        assert f'EXIT_CODE={command["exit_code"]}' in (ROOT / command['log']).read_text(), meta
        count += 1
    report['command_records'] = count
    assert git('log', '-n1', '--format=%H', '--', 'experiments/r3/config.json') == PREREG, 'config changed after pre-registration'
    first = git('log', '--diff-filter=A', '--format=%H', '--', 'results/r3/run-01/events.jsonl')
    if first:
        first = first.splitlines()[-1]
        assert subprocess.call(['git', 'merge-base', '--is-ancestor', PREREG, first], cwd=ROOT) == 0 and PREREG != first
        report['prereg_before_results'] = 'VERIFIED'
    else:
        report['prereg_before_results'] = 'UNKNOWN (run not committed yet)'
    hits = []
    docs = [ROOT / 'docs' / n for n in ('R3_PRIOR_ART_COMPARISON.md', 'R3_DELEGATION_SEMANTICS.md', 'R3_HYPOTHESIS_PREREG.md')]
    for path in list(BASE.rglob('*')) + list(HERE.glob('*.py')) + list(HERE.glob('*.json')) + docs:
        if (path.is_file() and path != MANIFEST and path.name != 'verify_saved.py'
                and path.suffix in ('.json', '.jsonl', '.txt', '.csv', '.py', '.md') and SENSITIVE.search(path.read_text(errors='ignore'))):
            hits.append(str(path.relative_to(ROOT)))
    assert not hits, f'sensitive-looking patterns in {hits}'
    report['sensitive_pattern_hits'] = 0
    return dict(status='VERIFIED', classification='SAVED_EVIDENCE_REPLAY_NOT_RUNTIME_REPRODUCTION', **report)


def tracked_outputs():
    paths = [p for p in BASE.rglob('*') if p.is_file() and p != MANIFEST]
    paths += list(HERE.glob('*.py')) + [HERE / 'config.json', ROOT / 'scripts/r3_run.py']
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
            scope='Canonical run is run-01; run-02-replicate is an unmodified replicate. G3-G5 were not run on CONTINUITY.',
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
