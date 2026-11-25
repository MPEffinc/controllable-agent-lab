# H10 source-authority gate local replay commands

Run from `/home/cclab/controllable_agent` after auditing `third_party/EAL-Bench/pyproject.toml` and `uv.lock`. Source SHA `51648690bc52d7a9c7ac080a2c67a784fe9d56cb`, clean original checkout; `uv.lock` SHA-256 `8c79b25b1b9b0fea501419bf759a0096d9741729e4b9c371ac9e11c9c5c065bb`.

```bash
UV_PROJECT_ENVIRONMENT=/home/cclab/controllable_agent/docs/access_control_empirical_20261124/env/EAL/venv uv sync --frozen --no-dev --project /home/cclab/controllable_agent/third_party/EAL-Bench
docs/access_control_empirical_20261124/env/EAL/venv/bin/python -I docs/access_control_empirical_20261124/runs/H10_source_scope_20261125/run.py > docs/access_control_empirical_20261124/runs/H10_source_scope_20261125/raw.jsonl
docs/access_control_empirical_20261124/env/EAL/venv/bin/python -I -m analysis.source_authority_gating --domain procurement > docs/access_control_empirical_20261124/runs/H10_source_scope_20261125/author_selfcheck.json
```

The first command installed 54 pinned Python packages into a separate ignored venv and returned exit 0. The second ran the authors' unmodified source gate, procurement semantics and canonical oracle on a corpus case and wrote six JSONL observations, exit 0. The third ran the authors' own 12-case offline contract self-check, exit 0; saved SHA256 `c8627baed34aedfdd65eb2e40baffe7828d333a758bf895cfff5bd8237428f25`. It used no model/API or external provider. Python 3.12.15. The local effect ledger is implemented in `run.py` and is reset per arm. Re-running overwrites `raw.jsonl`; copy it first to preserve the current artifact.
