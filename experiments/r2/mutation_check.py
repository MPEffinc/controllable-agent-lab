"""Mutation check of the R2 oracle test-suite (stdlib only).

Each mutant disables ONE check of oracle.py in a temporary copy and the oracle
tests must fail. A surviving mutant would mean a check is not protected by any test.
The repository files are never modified; copies live in a temporary directory.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
R1_ORACLE = HERE.parent / 'r1' / 'oracle.py'

MUTANTS = {
    'no-revocation-check': ("if grant['grant_id'] in revokes and revokes[grant['grant_id']] < seq:", 'if False:'),
    'no-actor-check': ("if attempt.get('caller_identity') != grant['actor_identity']:", 'if False:'),
    'trust-any-permit': ('if not provenance_ok:', 'if False:'),
    'no-unmediated-check': ("if permit is None:\n            found.append('UNMEDIATED_EFFECT')",
                            "if False:\n            found.append('UNMEDIATED_EFFECT')"),
    'no-log-world-compare': ("elif _project(attempt.get('action', {})) != _project(world_effects[index]):", 'elif False:'),
    'no-action-check': ("if _project(effect) != _project(grant['authorized_effect']):", 'if False:'),
    'no-epoch-check': ("if permit.get('policy_epoch') != policy_epoch:", 'if False:'),
    'no-duplicate-check': ('if len(ordinals) > 1:', 'if False:'),
}


def run_tests(directory: Path):
    result = subprocess.run([sys.executable, '-m', 'unittest', 'test_oracle'], cwd=directory,
                            capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
    return result.returncode, result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ''


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    original = (HERE / 'oracle.py').read_text()
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'r2').mkdir()
        (root / 'r1').mkdir()
        shutil.copy(R1_ORACLE, root / 'r1' / 'oracle.py')
        for name in ('r1_projection.py', 'test_oracle.py'):
            shutil.copy(HERE / name, root / 'r2' / name)
        (root / 'r2' / 'oracle.py').write_text(original)
        code, tail = run_tests(root / 'r2')
        rows.append(dict(mutant='BASELINE (no mutation)', tests_passed=code == 0, last_line=tail))
        for name, (old, new) in MUTANTS.items():
            if old not in original:
                raise SystemExit(f'mutation target not found for {name}')
            (root / 'r2' / 'oracle.py').write_text(original.replace(old, new, 1))
            code, tail = run_tests(root / 'r2')
            rows.append(dict(mutant=name, killed=code != 0, last_line=tail))
    killed = sum(1 for r in rows[1:] if r['killed'])
    out = dict(classification='ORACLE_TEST_SUITE_MUTATION_CHECK', baseline_passes=rows[0]['tests_passed'],
               mutants=len(MUTANTS), killed=killed, survived=[r['mutant'] for r in rows[1:] if not r['killed']], rows=rows)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('baseline_passes', 'mutants', 'killed', 'survived')}))
    return 0 if out['baseline_passes'] and not out['survived'] else 1


if __name__ == '__main__':
    sys.exit(main())
