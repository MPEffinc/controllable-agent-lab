# Exact command and environment

Date 2026-11-25 UTC. Run from `/home/cclab/controllable_agent`. First-author-associated supplementary candidate `third_party/MAP-Graph` commit `d94b0bf3c73efdb60fcc08014989b44ce8eae99d`, clean before/after; source evaluation commit correspondence is unverified. Python 3.10.12. Author source read, not modified. The experiment driver imports only original `base.py`/`trust.py` through an isolated package shim because the normal package initializer imports an optional model client. No dependency install, no model/API call, no network, no actual provider effect. Paid cost USD 0, shared cap USD 5.

```bash
python3 -I docs/access_control_empirical_20261124/runs/H11_counterfactual_20261125/run.py third_party/MAP-Graph/artifact docs/access_control_empirical_20261124/runs/H11_counterfactual_20261125
```

Exit 0 on the first run. The script writes `component_decisions.jsonl`, `mock_effects.jsonl`, `archived_projection.jsonl`, and `projection_summary.json`. It reads public `corp_exp5_041.json`, 21,600-row canonical CSV, and 900 public task JSONs; all 900 individual counterfactual final decisions are marked `UNKNOWN_RAW_SUPPORT_TRACE_MISSING`.

| File | SHA-256 |
|---|---|
| original `artifact/src/map_graph/trust.py` | `3dbcc82e992912181f8c7b960bb79b8623cff85f758fd21a78c132763c66e649` |
| original `artifact/final_results/canonical/main/task_metrics.csv` | `23ed3ac13c00c24e7064d75fd9cc85bc65dff8a4e4b9c6e1f47f145c1dfc5e24` |
| `run.py` | `7ed9a0a113372ccf6887ac13d74561c3b756486d1c0c1f757417a3db0f824237` |
| `component_decisions.jsonl` | `ea716df5ea3e4fccbdcd99f5146c8124da46b350ef8beaea4b686f4472a1aa6a` |
| `mock_effects.jsonl` | `47ce81394a28e43738c93c744dee6ae0564b6ebc2f8727b195e75bc8d1b1fb7e` |
| `archived_projection.jsonl` | `a2f8b373b2e3fbf2cd164d988e251397e32e6f4c0bb968ed4a814f9b9a0841d5` |
| `projection_summary.json` | `8e5e1f3c8ed667f8460d0802dc78dcbe25f082f279f8ff9044d01e7cbdf19509` |
