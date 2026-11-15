#!/usr/bin/env python3
"""Read existing checkouts, installed metadata and saved runs; never install/run a benchmark."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'results/setup/bootstrap-20261114'
REPOS = {
    'a2asecbench': 'https://github.com/SaFo-Lab/A2ASecBench',
    'orbit': 'https://github.com/wlanderson0/orbit',
    'camel': 'https://github.com/google-research/camel-prompt-injection',
    'progent': 'https://github.com/sunblaze-ucb/progent',
    'drift': 'https://github.com/SaFo-Lab/DRIFT',
    'agentdojo': 'https://github.com/sequrity-ai/agentdojo',
    'agentcap': 'https://github.com/yunwei37/agentcap',
    'openshell': 'https://github.com/NVIDIA/OpenShell',
    'sasy': 'https://github.com/sasy-labs/sasy',
    'forge': 'https://github.com/sasy-labs/forge',
}

def git(path, *args):
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1')
    return subprocess.check_output(['git', '-C', str(path), *args], env=env, text=True).strip()

def snapshot():
    repos = []
    for name, url in REPOS.items():
        path = ROOT / 'third_party' / name
        files = git(path, 'ls-tree', '-r', '--name-only', 'HEAD').splitlines()
        licenses = [f for f in files if '/' not in f and f.upper().startswith(('LICENSE', 'COPYING'))]
        repos.append(dict(name=name, url=url, commit=git(path, 'rev-parse', 'HEAD'),
                          origin=git(path, 'remote', 'get-url', 'origin'),
                          license_files=licenses, tracked_tree_paths=len(files),
                          checkout_status=git(path, 'status', '--porcelain=v1').splitlines(),
                          sparse=git(path, 'config', '--get', 'core.sparseCheckout')
                          if (path / '.git/info/sparse-checkout').exists() else 'false'))
    (EVIDENCE / 'source-manifest.json').write_text(json.dumps(repos, indent=2)+'\n')
    envs = {}
    for name, path in {
        'a2asecbench': ROOT / 'third_party/a2asecbench/.venv/bin/python',
        'camel': ROOT / 'third_party/camel/.venv/bin/python',
        'progent': ROOT / 'third_party/progent/.venv/bin/python',
        'orbit-release': ROOT / 'experiments/orbit-release/.venv/bin/python',
    }.items():
        if not path.exists():
            envs[name] = {'status': 'NOT_RUN', 'reason': 'no interpreter'}
            continue
        code = ('import sys,json,importlib.metadata as m; '
                'print(json.dumps(dict(python=sys.version,packages=sorted('
                '[(d.metadata["Name"],d.version) for d in m.distributions()]))))')
        result = subprocess.run([str(path), '-I', '-c', code], text=True, capture_output=True, timeout=30)
        envs[name] = json.loads(result.stdout) if result.returncode == 0 else {'error':result.stderr}
        envs[name]['interpreter'] = str(path.relative_to(ROOT))
        packages = envs[name].get('packages', [])
        # The editable research artifact itself must be installed from the pinned source separately.
        exclude = {'a2asecbench': {'a2asecbench'}, 'camel': {'camel'},
                   'progent': {'secagent'}, 'orbit-release': {'orbit'}}[name]
        requirements = '\n'.join(f'{n}=={v}' for n, v in packages if n.lower() not in exclude)
        (EVIDENCE / f'requirements-{name}.txt').write_text(requirements+'\n')
    (EVIDENCE / 'environment-inventory.json').write_text(json.dumps(envs, indent=2)+'\n')
    runs = []
    for path in sorted(EVIDENCE.glob('*.json')):
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or not {'command','exit_code','log'} <= data.keys():
            continue
        log = ROOT / data['log']
        text = log.read_text()
        if f'EXIT_CODE={data["exit_code"]}' not in text:
            raise ValueError(f'missing matching exit marker: {log}')
        runs.append(dict(name=data['name'], command=data['command'], exit_code=data['exit_code'],
                         start_utc=data['start_utc'], end_utc=data['end_utc'],
                         metadata=str(path.relative_to(ROOT)), log=data['log'],
                         log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    (EVIDENCE / 'command-index.json').write_text(json.dumps(runs, indent=2)+'\n')
    original = EVIDENCE / 'a2a-asrf-original/trials.jsonl'
    rows = [json.loads(x) for x in original.read_text().splitlines()]
    chosen = [next(r for r in rows if r['details']['is_control'] == control) for control in (False, True)]
    (EVIDENCE / 'a2a-asrf-sample.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in chosen))
    observations = []
    for row in rows:
        details = row['details']
        observations.append({
            'case_id': row['case_id'], 'trial_index': row['trial_index'],
            'timestamp': row['timestamp'], 'config_hash': row['config_hash'],
            'is_control': details['is_control'], 'success': row['success'],
            'control_pass': details['control_pass'], 'errors': row['errors'],
            'forbidden_uri_dereferences': details['metrics']['forbidden_uri_dereferences'],
            'benign_uri_dereferences': details['metrics']['benign_uri_dereferences'],
            'sink_events': [e for e in details['events'] if e['event_type'] == 'uri_dereference'],
        })
    (EVIDENCE / 'a2a-asrf-observations.jsonl').write_text(
        ''.join(json.dumps(r)+'\n' for r in observations))
    summary = json.loads(original.with_name('summary.json').read_text())
    observed = dict(records=len(rows), attack_records=sum(not r['details']['is_control'] for r in rows),
                    control_records=sum(r['details']['is_control'] for r in rows),
                    attack_successes=sum(r['success'] for r in rows if not r['details']['is_control']),
                    control_passes=sum(bool(r['details']['control_pass']) for r in rows if r['details']['is_control']),
                    raw_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                    raw_bytes=original.stat().st_size, model_calls='NOT INFERRED; deterministic backend in source/config',
                    summary={k:v for k,v in summary.items() if k != 'counts_per_case'})
    assert observed['records'] == summary['total_trials']
    assert observed['attack_successes'] == summary['total_successes']
    (EVIDENCE / 'a2a-verified-counts.json').write_text(json.dumps(observed, indent=2)+'\n')
    print(json.dumps(dict(repositories=len(repos), environments=list(envs), saved_commands=len(runs),
                          attack_successes=observed['attack_successes'], control_passes=observed['control_passes'])))

def verify_saved():
    """Check shared evidence without third-party trees, environments, or raw trials."""
    sources = json.loads((EVIDENCE / 'source-manifest.json').read_text())
    assert len(sources) == len(REPOS)
    for source in sources:
        assert source['url'] == REPOS[source['name']]
        assert re.fullmatch('[0-9a-f]{40}', source['commit'])
    runs = json.loads((EVIDENCE / 'command-index.json').read_text())
    for run in runs:
        log = ROOT / run['log']
        assert hashlib.sha256(log.read_bytes()).hexdigest() == run['log_sha256'], log
        assert f'EXIT_CODE={run["exit_code"]}' in log.read_text(), log
        metadata = json.loads((ROOT / run['metadata']).read_text())
        for key in ('command', 'exit_code', 'start_utc', 'end_utc', 'log'):
            assert metadata[key] == run[key], (run['name'], key)
    rows = [json.loads(x) for x in (EVIDENCE / 'a2a-asrf-observations.jsonl').read_text().splitlines()]
    summary = json.loads((EVIDENCE / 'a2a-asrf-original/summary.json').read_text())
    attack = [r for r in rows if not r['is_control']]
    control = [r for r in rows if r['is_control']]
    assert len({r['case_id'] for r in rows}) == len(rows) == summary['total_trials']
    assert len(attack) == summary['a2a_attack_trials']
    assert len(control) == summary['control_trials']
    assert sum(r['success'] for r in attack) == summary['total_successes']
    assert sum(r['success'] for r in attack) / len(attack) == summary['a2a_attack_asr']
    assert sum(bool(r['control_pass']) for r in control) / len(control) == summary['control_pass_rate']
    assert sum(r['success'] for r in rows) / len(rows) == summary['asr']
    for row in rows:
        assert row['config_hash'] == summary['config_hash']
        forbidden = sum(e['private_tags']['uri_class'] == 'forbidden_internal' for e in row['sink_events'])
        assert forbidden == row['forbidden_uri_dereferences'], row['case_id']
        if not row['is_control']:
            assert bool(forbidden) == row['success'], row['case_id']
    inventories = json.loads((EVIDENCE / 'environment-inventory.json').read_text())
    own = {'a2asecbench':'a2asecbench', 'camel':'camel', 'progent':'secagent', 'orbit-release':'orbit'}
    for name, data in inventories.items():
        expected = sorted(f'{n}=={v}' for n,v in data['packages'] if n.lower() != own[name])
        actual = sorted((EVIDENCE / f'requirements-{name}.txt').read_text().split())
        assert actual == expected, name
    print(json.dumps(dict(status='VERIFIED', repositories=len(sources), command_logs=len(runs),
                          projected_trial_rows=len(rows), attack_asr=summary['a2a_attack_asr'],
                          control_pass_rate=summary['control_pass_rate'],
                          scope='saved evidence integrity/counts only; no benchmark rerun or independent reproduction')))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--verify-saved', action='store_true',
                        help='Verify shared evidence only; no vendor checkout or installed environments required')
    args = parser.parse_args()
    verify_saved() if args.verify_saved else snapshot()
