# Regression and independent result checks

2026-11-22 UTC. Python: `local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python`. Source Progent checkout remains pinned at `b02783b896d4bf01a2adf24738015e258db8d35b` and unchanged.

## Test runner and failures retained

`python -m pytest -q tests` exited 1 before collection: `No module named pytest`. No dependency was installed because the repository's tests use `unittest`; `python -m unittest discover -s tests -v` is the working runner. First execution: 8/10 passed, two failures. The old ledger test expected the previous 30-request ceiling, while the authorized ceiling is now 60. The old Suite Utility fixture lacked a discovery event, while the new Utility requires the task's discovery step. Both fixtures were updated to the new explicit conditions. Rerun: **10/10 passed**. This did not relax a Deny rule or remove an outcome check.

Additional `scripts.progent_agentdojo_test` and `scripts.progent_system_evaluation_test` tests check required `resource_id` schemas, wrong-target rejection, direct Controller entry on Deny, exact command and final-state Utility, order of composite steps, safe dotenv parsing, and the 60-request ceiling. These tests passed after the fixes. Compile checks passed. None of these tests uses an LLM API.

## Actual Docker regression

`PYTHONPATH=. local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python -m scripts.progent_docker_experiment` ran with Run ID `docker-20261122T150621Z-152d45`, exit 0, `status PASS`, and `cleanup owned resources removed`. Direct-harness calls: status Allow running→running; stop Allow running→exited; start Allow exited→running; explicit stop Deny running→running with zero mutations; out-of-scope status Deny running→running; broad-policy unknown target reached Controller and returned `BACKEND_EXECUTION_FAILED` with no mutation. All six matched the expected classification and independent Docker inspect state. This is **not** a Luna Agent run. Raw JSON: ignored `local/progent-vm/docker/docker-20261122T150621Z-152d45.json`.

This run preceded the later source-commit logging field. Root HEAD at execution was `9225a1eea08a514f549dc9e1d82ae52a24575f97` with uncommitted regression edits; the subsequent `9c4866e0a4fed8f5b1dcacea6b00fe55fe4c8a09` commit contains those edits plus metadata logging. This earlier run is not an exact clean-commit reproduction. Future runs include `source_commit` and `source_dirty` fields.

AgentDojo source TaskSuite + GroundTruth direct-call diagnostics also passed Mock A/B and Docker A/B (Run IDs in `agentdojo_live_evaluation.md`). The Docker B status was independently `running→exited`. The original four SREGym/kind containers were still the only entries in `docker ps` after cleanup. No Kata guest, actual AgentDojo Luna run, or Luna Docker end-to-end result was produced.
