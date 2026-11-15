# R2: original CONTINUITY on the R1 A2A delegation path

Classification: **SYNTHETIC MULTI-AGENT EXPERIMENT WITH ORIGINAL CONTINUITY**. Official
`a2a-sdk` AgentCard/JSON-RPC over an in-process ASGI transport (no sockets), a
deterministic sequential schedule (no races), scripted white-box agent behaviour (no
LLM, no paid API). Every security decision is made by the pinned, unmodified original
(`zast-ai/continuity` SHA `59cfe60930d247d1890b366ded686c718020a11e`).

Read first: `docs/R2_SEMANTIC_ALIGNMENT.md` (semantics, TCB, oracle, labels),
`docs/R2_CONTINUITY_INTEGRATION_REPORT.md` (results), `docs/R2_GAP_VERDICT.md` (verdict).

## Files

| File | Role |
|---|---|
| `config.json` | Pre-registered conditions, authorization rules and predictions. Not edited after results (committed in `75870a9`). The runner refuses to start if it differs from the committed version. |
| `proof_codec.py` | Strict JSON codec that carries `ProofBundle` objects in A2A messages. Fail-closed; never creates, repairs or re-signs evidence. |
| `trusted.py` | Trusted plane (adapter code): runtime-state authority, permit service, effect gateway, stage hosts. Verifies the pinned SHA and a clean original checkout at import. Calls the originals with the CURRENT state. |
| `adversary.py` | Scripted attacker actions. Imports nothing from `trusted.py`; receives only public information and keys an attacker legitimately owns. |
| `scenario.py` | Drives agents A and B over A2A, the untrusted queue, the schedules and the event log. Asserts no outcome. |
| `oracle.py` | Independent oracle (stdlib only, imports no CONTINUITY/A2A/adapter code). Judges the saved events and the saved world snapshot under IMMEDIATE_CUT_AT_FINALITY. |
| `r1_projection.py` | Runs the UNMODIFIED R1 oracle on a projection of R2 evidence. Grandfather and fence lenses are not applicable. |
| `classify.py` | Compares observations with the pre-registered expectations and labels mechanically. A surprise becomes NEEDS_TRIAGE, never a gap. |
| `original_crosscheck.py` | Confirmatory: the original harness alone on the same seeds vs the A2A path. |
| `mutation_check.py` | Disables one oracle check at a time in a temporary copy; the oracle tests must fail (8/8 killed, recorded). |
| `verify_saved.py` | Replays the saved evidence (no vendor checkout, venv or API needed). |
| `test_oracle.py`, `test_bridge.py` | Oracle (21) and adapter (17) tests. |
| `requirements-input.txt`, `requirements-observed.txt` | Environment input and the observed package snapshot. |

## Run

```bash
uv venv --python .cache/bootstrap-python/cpython-3.11.17-linux-x86_64-gnu/bin/python experiments/r2/.venv
uv pip install --python experiments/r2/.venv/bin/python -r experiments/r2/requirements-input.txt
experiments/r2/.venv/bin/python -m unittest discover -s experiments/r2 -p "test_*.py"
python3 scripts/r2_run.py --name run-03 --timeout 300 -- experiments/r2/.venv/bin/python experiments/r2/scenario.py --output-dir results/r2/run-03
python3 experiments/r2/oracle.py --events results/r2/run-03/events.jsonl --world results/r2/run-03/world_state.json --output results/r2/oracle-03.json
python3 experiments/r2/verify_saved.py
```

Always use a new name and output directory; existing evidence is never overwritten.

## What this does not show

Not exercised: policy-epoch rotation, expiry, concurrent or distributed finality,
multiple grants per root, sub-delegation or re-delegation, transport-level caller
authentication (identity is bound to the in-process handler), dynamic effect-path
completeness (a single effect path is a construction), adaptive or LLM attackers,
real providers. The four `AB-*` conditions switch an original check off on purpose
(CONTROLLED_ABLATION) to show the oracle is sensitive; they are not findings about
CONTINUITY. Single deterministic run per condition: no attack-success rates.
