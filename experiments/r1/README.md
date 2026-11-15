# R1 deterministic intervention-boundary fixture

Classification: **SYNTHETIC MULTI-AGENT EXPERIMENT**. This is neither an original
paper reproduction nor a measurement of LLM or prompt-injection success.

`scenario.py` uses the original, unmodified A2ASecBench
`harness.a2a_lab.sdk_protocol.OfficialA2AFunctionAgent` helper. Both agents are
actual official `a2a-sdk` AgentCard/JSON-RPC services transported in process with
`httpx.ASGITransport`. Agent A deterministically constructs a message and can
enqueue work for Agent B. An `asyncio.Queue` is drained under an explicit,
sequential schedule. No concurrency-race, multi-host or autonomous-planning claim
is made. The default policy engine is the original Progent
`apply_secure_tool_wrapper` / `update_security_policy`, not a rewritten checker.

## Authority and effect semantics

- A trusted fixture issuer records `grant` events binding **one** support to one
  root task, principal, tool and recipient. Each Progent allow rule is one
  conjunction over that grant; independently collected field enums are not used.
- `static` installs grant-time rules again at dispatch. `current` builds the
  same schema rules from still-active fixture grants. These are experiment
  configurations using Progent's public policy API. The grant registry and its
  update protocol are testbed code, not a reproduced revocation method.
- An authorization cut invalidates supports of the selected root in the fixture
  ledger. Message creation and queue enqueue/dequeue do not accept a protected
  effect. `sink_accept` creates an in-memory protected receipt; `sink_commit`
  appends the actual effect to an in-memory outbox. These are distinct events.
- The default acceptance oracle is the **strong experimental choice**
  `IMMEDIATE_CUT_AT_ACCEPT`: sufficient matching current authority is required
  at sink acceptance. An authorized pre-cut receipt can commit later under the
  `grandfather_preaccepted_receipts` schedule. Post-cut commit by itself is not
  a violation under that choice.
- The optional fixture sink fence rejects new accepts for one root and cancels
  its pending receipts. This stronger cancel-pending rule is a **testbed
  control**, not the Authorization Revocation paper implementation or a claim
  about its allowed cut-to-fence interval. A separate post-fence admission lens
  must be distinguished when interpreting these observations.
- Root B has its own principal and grant. The `global_stop` control deliberately
  disables every tool after any cut to expose collateral overblocking.

Agent-side labels and fixture counts are not the independent security oracle.
Every raw record leaves `oracle_result` and unobserved fields as
`NOT_OBSERVED`. `policy_decision=allow` is logged at protected callable entry
after an actual original-wrapper check; `deny` comes from the original
`ValidationError`. Unmediated calls use `NOT_APPLIED`. The independent oracle
must replay authority and inspect the actual sink state rather than trust these
labels. `sink_state.json` is exported from receipt/outbox objects separately
from the event log; it is a final checkpoint, not crash/restart instrumentation.

The trusted grant ledger/labels are synthetic and non-cryptographic. We do not
evaluate adversarial forgery of the issuer, identity authentication, regrant,
alternative minimal authorization supports, distributed consistency, provider
acceptance, crash recovery, dynamic membership, or complete mediation discovery.

## Conditions

`config.json` contains 17 conditions, one deterministic repetition each:

| Group | Comparison |
|---|---|
| C0 | Valid Root A task delegated to B, current policy, normal effect |
| C1/C2 | Identical attacker recipient without mediation / with direct original wrapper |
| C3 | A denial followed by B dispatch: A-only / all-agent mediation; handoff removed; single-agent replay |
| C4 | Before-cut queued work executed after cut: static / current policy; after-cut message generation: static / current; single-agent static post-cut control |
| C4 receipt | Pre-cut protected acceptance, post-cut commit: grandfather / pending-cancel fence |
| C4 sink | Post-cut static policy dispatch with root sink fence |
| C5 | Root A cut while independently approved Root B continues: current policy / global-stop overblocking control |

The deliberately unmediated and stale-rule cases are baseline configurations.
Their unauthorized effects cannot establish a counterexample to an existing
method's stated guarantee. The single-agent control checks whether the stale
authority phenomenon requires a MAS at all. Fixture operation
`deny_then_queue` explicitly scripts adversarial forwarding after a decision;
it does not model an LLM's recovery decision.

## Recreate the isolated environment

The recorded environment was created offline using the already downloaded
Bootstrap packages. These are version snapshots, not an upstream project lock.
From the workspace root:

```bash
uv venv --python 3.10 experiments/r1/.venv
uv pip install --offline --python experiments/r1/.venv/bin/python -r results/setup/bootstrap-20261114/requirements-a2asecbench.txt -r results/setup/bootstrap-20261114/requirements-progent.txt
uv pip install --offline --no-deps --python experiments/r1/.venv/bin/python -e third_party/progent
```

The helper is imported from the pinned A2ASecBench source checkout; there is no
mixing of installed dependency directories. Source commits and hashes of the
exact reused files are in the run manifest. Network socket `connect` and
`create_connection` are explicitly rejected for this process; the official SDK
transport uses no sockets. This is not an OS sandbox. No provider client or
model-generation function is invoked. The original Progent module prints a
default model name at import, which does not represent a model API call.

## Execute and inspect

```bash
python3 scripts/r1_run.py --name fixture-run-02 --timeout 120 -- experiments/r1/.venv/bin/python experiments/r1/scenario.py --output-dir results/r1/fixture-run-02
```

Always choose a new command name/output directory; existing evidence is never
overwritten. Recorded first run: `results/r1/fixture-run-01/`, command metadata
`results/r1/commands/fixture-run-01.json`, exit **0**. Files:

- `events.jsonl`: full ordered authority/protocol/policy/queue/sink events.
- `sink_state.json`: final receipt and outbox checkpoint from actual objects.
- `summary.json`: measured event/decision/effect counts only; no hard-coded
  expected-result PASS verdicts.
- `manifest.json`: code/config/events/summary/sink SHA256, pinned reused source,
  Python and installed packages, parent Git commit. Parent commit alone is not
  the experiment code revision; the source SHA256 identifies executed code.

Run the separate root-owned `experiments/r1/oracle.py` to classify the saved
effects and regression tests. A successful fixture process alone is not a
security pass, a guarantee-violation finding, or evidence of novelty.
