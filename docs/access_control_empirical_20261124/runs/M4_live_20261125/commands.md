# H12 local service-effect replay — commands and fixed environment

Run from `/home/cclab/controllable_agent` after reading [prereg.md](prereg.md). This run was executed once, with exit 0:

```bash
python3 -I docs/access_control_empirical_20261124/runs/M4_live_20261125/run.py docs/access_control_empirical_20261124/runs/M4_live_20261125 > docs/access_control_empirical_20261124/runs/M4_live_20261125/raw.jsonl
```

Python 3.10.12, stdlib SQLite/loopback HTTP; original M4 `guard()` imported from unmodified `third_party/M4-memory-rebirth` commit `15dcd20b3c0de4f27d9a8dd10a830dea91641b81`. Source SHA-256 `e85f804019fcfbd2e8cbc05a7ebd3997c2267259094be3ebddecf214232dcabf`; independent `run.py` SHA-256 `abfdf7c0e938e5fc4c4cfdb1f8964675e4bcb43cbab5e0b7ea5849e3c40d0c68`; `raw.jsonl` SHA-256 `ac8c9bda7faecd49bafa92104f4a81615c54b1af3cbb0c9728b5904be5187154`; `service_state.sqlite` SHA-256 `bb12a00e49b523b52b522ace88009759e3ac3a243e482bab2755def6ed850775`.

The run refuses to overwrite an existing `service_state.sqlite`; for re-execution, copy `prereg.md` and `run.py` to a new empty run directory and pass that directory as the argument. The HTTP server binds `127.0.0.1` on an ephemeral port for each case and closes it. Model calls 0, model/temperature/seed N/A, paid API USD 0 of the authorized USD 5 cap, external service/data 0. Original source tree status clean after the run.
