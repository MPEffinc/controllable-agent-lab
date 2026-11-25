"""Independent, offline input-boundary probe for the authors' unmodified guard()."""

import json
import sys
from pathlib import Path

source_dir = Path('/home/cclab/controllable_agent/third_party/M4-memory-rebirth/guard')
sys.path.insert(0, str(source_dir))
from stale_guard import guard  # noqa: E402

revoked = {
    'id': 'revoked_source',
    'fact': 'Deployment may be approved by one reviewer.',
    'created_at': '2025-01-01T00:00:00+00:00',
    'expired_at': '2026-01-01T00:00:00+00:00',
}
replacement = {
    'id': 'current_replacement',
    'fact': 'Deployment requires two independent reviewers.',
    'created_at': '2026-02-01T00:00:00+00:00',
}
journal = {
    'id': 'current_journal',
    'fact': 'Deployment may be approved by one reviewer.',
    'created_at': '2026-03-01T00:00:00+00:00',
}

for case, rows in (
    ('unmarked_journal', [revoked, replacement, journal]),
    ('externally_marked_journal', [
        revoked,
        replacement,
        {**journal, 'revoked_at': '2026-03-02T00:00:00+00:00'},
    ]),
):
    result = guard(rows)
    kept_ids = [x['id'] for x in result.kept]
    assert 'revoked_source' not in kept_ids
    if case == 'unmarked_journal':
        assert 'current_journal' in kept_ids
    else:
        assert 'current_journal' not in kept_ids
    print(json.dumps({
        'case': case,
        'input': rows,
        'kept_ids': kept_ids,
        'withheld': result.withheld,
        'notes': result.notes,
        'effect_observed': False,
    }, ensure_ascii=False, sort_keys=True))
