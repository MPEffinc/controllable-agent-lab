# M4 source-native guard boundary: exact local commands

Run directory: `/home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/M4_guard_boundary_20261125`.
Source: `/home/cclab/controllable_agent/third_party/M4-memory-rebirth`, commit `15dcd20b3c0de4f27d9a8dd10a830dea91641b81`; `guard/stale_guard.py` SHA-256 `e85f804019fcfbd2e8cbc05a7ebd3997c2267259094be3ebddecf214232dcabf`. Original source tree clean at audit.

```bash
python3 -I docs/access_control_empirical_20261124/runs/M4_guard_boundary_20261125/guard_boundary.py > docs/access_control_empirical_20261124/runs/M4_guard_boundary_20261125/decisions.jsonl
```

Run from repository root. This re-executes the deterministic offline script against the unmodified author `guard()`; no package install or model/network call. The first agent execution did not preserve a literal shell transcript, so the command above is the explicit verification/reproduction command used for the saved result. Python version, hashes, and success are recorded in `result.md`.
