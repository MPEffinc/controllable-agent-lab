"""Mutation check of the R3 static-check and reference-model tests (stdlib only).

Each mutant breaks ONE statement of expressiveness_check.py or reference_model.py in a
temporary copy; the tests in test_r3_static.py must then fail. A surviving mutant would
mean a check or a model rule is protected by no test. Repository files are never modified.
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

MUTANTS = [
    ('reference_model.py', 'reach-ignores-removed-edges', "if edge_id not in removed and parent == node and child not in seen:",
     "if parent == node and child not in seen:"),
    ('reference_model.py', 'vera-ignores-conjunctive-policy', "    if graph['conjunctive_roots']:\n        removed = frozenset(graph['revocations']['edge_e2'])",
     "    if False:\n        removed = frozenset(graph['revocations']['edge_e2'])"),
    ('reference_model.py', 'succession-allows-multi-parent', " or any(len(incoming(edges, n)) > 1 for n in {c for _, c in edges.values()}):", ":"),
    ('reference_model.py', 'revocation-strict-subset-authorizes',
     "out['strict_subset_can_authorize'] = any(w <= current for w in support if len(w) < len(support[0]))",
     "out['strict_subset_can_authorize'] = any(w & current for w in support)"),
    ('reference_model.py', 'revocation-never-rebinds', "out['rebind_to_independent_support'] = any(", "out['rebind_to_independent_support'] = False and any("),
    ('reference_model.py', 'residualauth-ignores-selected-parent', "return True if parent is None else effective(parent, revoked)",
     "return True if parent is None else True"),
    ('expressiveness_check.py', 's1-always-holds', "return dict(id='S1', holds=not hits,", "return dict(id='S1', holds=True,"),
    ('expressiveness_check.py', 's2-always-holds', "return dict(id='S2', holds=names == RUNTIME_STATE_FIELDS,", "return dict(id='S2', holds=True,"),
    ('expressiveness_check.py', 's3-always-holds', "holds = bool(operands) and set(operands) <= ALLOWED_REVOKED_OPERANDS", "holds = True"),
    ('expressiveness_check.py', 's4-always-holds', "holds = not reads and fields == 1 and strings == ['/context/approval_digest']", "holds = True"),
    ('expressiveness_check.py', 's6-always-holds', "return dict(id='S6', holds=not hits,", "return dict(id='S6', holds=True,"),
    ('expressiveness_check.py', 's7-always-holds', "holds = bool(uses) and not other and constructor_calls == 0", "holds = True"),
]


def run_tests(directory: Path):
    result = subprocess.run([sys.executable, '-m', 'unittest', 'test_r3_static'], cwd=directory, capture_output=True,
                            text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
    return result.returncode, (result.stderr.strip().splitlines() or [''])[-1]


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name in ('config.json', 'expressiveness_check.py', 'reference_model.py', 'test_r3_static.py'):
            shutil.copy(HERE / name, work / name)
        code, tail = run_tests(work)
        rows.append(dict(mutant='BASELINE (no mutation)', tests_passed=code == 0, last_line=tail))
        for filename, label, old, new in MUTANTS:
            original = (HERE / filename).read_text()
            if old not in original:
                raise SystemExit(f'mutation target not found for {label}')
            (work / filename).write_text(original.replace(old, new, 1))
            code, tail = run_tests(work)
            rows.append(dict(mutant=label, file=filename, killed=code != 0, last_line=tail))
            (work / filename).write_text(original)
    killed = sum(1 for r in rows[1:] if r['killed'])
    out = dict(classification='R3_STATIC_AND_REFERENCE_TEST_MUTATION_CHECK', baseline_passes=rows[0]['tests_passed'],
               mutants=len(MUTANTS), killed=killed, survived=[r['mutant'] for r in rows[1:] if not r['killed']], rows=rows)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('baseline_passes', 'mutants', 'killed', 'survived')}))
    return 0 if out['baseline_passes'] and not out['survived'] else 1


if __name__ == '__main__':
    sys.exit(main())
