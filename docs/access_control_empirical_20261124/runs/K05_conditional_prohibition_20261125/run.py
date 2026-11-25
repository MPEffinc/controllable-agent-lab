"""Independent Cedar conditional prohibition and local effect check."""

import hashlib
import json
import subprocess
from pathlib import Path


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
CLI = ROOT / "docs/access_control_empirical_20261124/runs/K06_verify_20261124/env/cedar-policy-cli-experimental-x86_64-unknown-linux-gnu/cedar"
POLICY = RUN / "policy.cedar"
ENTITIES = RUN / "entities.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ledger: list[dict[str, str]] = []
cases = []
for state, context_file in [(False, RUN / "context_false.json"), (True, RUN / "context_true.json")]:
    argv = [
        str(CLI), "authorize", "--policies", str(POLICY), "--entities", str(ENTITIES),
        "--principal", 'User::"student"', "--action", 'Action::"read"',
        "--resource", 'Document::"doc"', "--context", str(context_file), "--verbose",
    ]
    before = len(ledger)
    p = subprocess.run(argv, text=True, capture_output=True, check=False, timeout=10)
    decision = "ALLOW" if "\nALLOW\n" in p.stdout else "DENY" if "\nDENY\n" in p.stdout else "UNKNOWN"
    if decision == "UNKNOWN":
        raise RuntimeError(f"Unrecognized Cedar output; exit={p.returncode}")
    if decision == "ALLOW":
        ledger.append({"action": "read", "resource": "doc", "registration_open": state})
    cases.append({
        "registration_open": state,
        "argv": argv,
        "exit_code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
        "decision": decision,
        "effect_before": before,
        "effect_after": len(ledger),
    })

output = {
    "kind": "INDEPENDENT_CEDAR_CONDITIONAL_PROHIBITION",
    "version": subprocess.run([str(CLI), "--version"], text=True, capture_output=True, check=False).stdout.strip(),
    "sha256": {str(x.relative_to(ROOT)): sha256(x) for x in [CLI, POLICY, ENTITIES, RUN / "context_false.json", RUN / "context_true.json"]},
    "cases": cases,
    "ledger": ledger,
    "pass": cases[0]["decision"] == "DENY" and cases[0]["effect_after"] == 0 and cases[1]["decision"] == "ALLOW" and cases[1]["effect_after"] == 1,
}
(RUN / "raw.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"cases": [{k: c[k] for k in ["registration_open", "exit_code", "decision", "effect_before", "effect_after"]} for c in cases], "pass": output["pass"]}, ensure_ascii=False))
if not output["pass"]:
    raise SystemExit(1)
