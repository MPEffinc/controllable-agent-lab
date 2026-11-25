"""Independent Cedar request oracle and local SQLite effect for C13."""
import json
import sqlite3
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CEDAR = ROOT / 'docs/access_control_empirical_20261124/runs/K06_verify_20261124/env/cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar'
POLICY = HERE / 'session/C13_owner_read/harness_runs/scenario/candidate.cedar'
if (HERE / 'decisions.json').exists():
    raise RuntimeError('C13 decision result already exists')

entities = [
    {'uid': {'type': 'User', 'id': who}, 'attrs': {}, 'parents': []}
    for who in ('alice', 'bob')
]
entities.append({'uid': {'type': 'Document', 'id': 'doc1'},
                 'attrs': {'owner': {'__entity': {'type': 'User', 'id': 'alice'}}},
                 'parents': []})
(HERE / 'entities.json').write_text(json.dumps(entities, indent=2) + '\n')
(HERE / 'context.json').write_text('{}\n')

cases = [('owner_read', 'alice', 'readDocument'),
         ('nonowner_read', 'bob', 'readDocument'),
         ('owner_delete', 'alice', 'deleteDocument')]
rows = []
with sqlite3.connect(HERE / 'effect.sqlite') as conn:
    conn.execute('CREATE TABLE document(id TEXT PRIMARY KEY, reads INTEGER, deleted INTEGER)')
    conn.execute("INSERT INTO document VALUES ('doc1',0,0)")
    for name, principal, action in cases:
        before = conn.execute('SELECT reads,deleted FROM document').fetchone()
        argv = [str(CEDAR), 'authorize', '--policies', str(POLICY),
                '--schema', str(HERE / 'schema.cedarschema'),
                '--entities', str(HERE / 'entities.json'),
                '--principal', f'User::"{principal}"',
                '--action', f'Action::"{action}"',
                '--resource', 'Document::"doc1"',
                '--context', str(HERE / 'context.json'), '--verbose']
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        decision = 'ALLOW' if '\nALLOW\n' in proc.stdout else 'DENY' if '\nDENY\n' in proc.stdout else 'UNKNOWN'
        if decision == 'ALLOW' and proc.returncode == 0:
            if action == 'readDocument':
                conn.execute("UPDATE document SET reads=reads+1 WHERE id='doc1'")
            else:
                conn.execute("UPDATE document SET deleted=1 WHERE id='doc1'")
        after = conn.execute('SELECT reads,deleted FROM document').fetchone()
        rows.append({'case': name, 'decision': decision, 'exit_code': proc.returncode,
                     'before': before, 'after': after, 'argv': argv,
                     'stdout': proc.stdout, 'stderr': proc.stderr})
    conn.commit()
(HERE / 'decisions.json').write_text(json.dumps(rows, indent=2) + '\n')
print([(r['case'], r['decision'], r['before'], r['after'], r['exit_code']) for r in rows])
