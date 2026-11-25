"""Independent Cedar route composition check with local effects only."""

import hashlib
import json
import subprocess
from pathlib import Path


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
CLI = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env/cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
POLICY = RUN / "policy.cedar"
ENTITIES = RUN / "entities.json"
INPUTS = [
    ("closed_none", False, False, False, False),
    ("open_conditional", True, False, False, True),
    ("closed_alternate", False, True, False, True),
    ("open_both", True, True, False, True),
    ("closed_alternate_embargo", False, True, True, False),
    ("open_both_embargo", True, True, True, False),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


rows = []
hash_paths = [CLI, POLICY, ENTITIES]
for name, registration_open, alternate_allow, embargo_active, expected in INPUTS:
    ctx = RUN / f"context_{name}.json"
    ctx.write_text(json.dumps({
        "registration_open": registration_open,
        "alternate_allow": alternate_allow,
        "embargo_active": embargo_active,
    }, sort_keys=True) + "\n")
    hash_paths.append(ctx)
    argv = [
        str(CLI), "authorize", "--policies", str(POLICY), "--entities", str(ENTITIES),
        "--principal", 'User::"student"', "--action", 'Action::"read"',
        "--resource", 'Document::"doc"', "--context", str(ctx), "--verbose",
    ]
    p = subprocess.run(argv, capture_output=True, text=True, timeout=10, check=False)
    decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
    if decision == "UNKNOWN":
        raise RuntimeError(f"unknown decision in {name}: exit {p.returncode}")
    ledger_before = 0
    ledger_after = 1 if decision == "ALLOW" else 0
    rows.append({
        "case": name,
        "context": json.loads(ctx.read_text()),
        "expected_allow": expected,
        "argv": argv,
        "exit_code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
        "decision": decision,
        "effect_before": ledger_before,
        "effect_after": ledger_after,
        "matches_expected": (decision == "ALLOW") == expected and ledger_after == int(expected),
    })

record = {
    "kind": "INDEPENDENT_CEDAR_ROUTE_COMPOSITION",
    "version": subprocess.run([str(CLI), "--version"], capture_output=True, text=True, check=False).stdout.strip(),
    "sha256": {str(path.relative_to(ROOT)): digest(path) for path in hash_paths},
    "cases": rows,
    "pass": all(row["matches_expected"] for row in rows),
}
(RUN / "raw.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"decisions": [{"case": row["case"], "decision": row["decision"], "effect_after": row["effect_after"]} for row in rows], "pass": record["pass"]}))
if not record["pass"]:
    raise SystemExit(1)
