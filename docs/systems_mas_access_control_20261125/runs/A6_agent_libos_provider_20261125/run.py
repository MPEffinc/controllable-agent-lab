"""Research adapter around unmodified Agent libOS Runtime and local provider."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from agent_libos import Runtime
from agent_libos.models import CapabilityRight
from agent_libos.substrate import LocalResourceProviderSubstrate


def main() -> int:
    run_dir = Path(__file__).resolve().parent
    workspace = run_dir / "workspace"
    workspace.mkdir(exist_ok=True)
    for name in ("A.txt", "B.txt"):
        (workspace / name).write_text("baseline\n", encoding="utf-8")
    runtime = Runtime.open(run_dir / "runtime.sqlite", substrate=LocalResourceProviderSubstrate(workspace))
    rows: list[dict[str, object]] = []

    def snapshot() -> dict[str, str]:
        return {name: (workspace / name).read_text(encoding="utf-8") for name in ("A.txt", "B.txt")}

    def write(case: str, pid: str, name: str, value: str) -> None:
        before = snapshot()
        start = time.perf_counter_ns()
        try:
            result = runtime.filesystem.write_text(pid, name, value)
            status, error = "return", None
            result_type = type(result).__name__
        except Exception as exc:  # record the original denial class and text
            status, error = "exception", f"{type(exc).__name__}: {exc}"
            result_type = None
        rows.append({
            "case": case,
            "actor_pid": pid,
            "target": name,
            "status": status,
            "error": error,
            "result_type": result_type,
            "elapsed_ns": time.perf_counter_ns() - start,
            "before": before,
            "after": snapshot(),
        })

    try:
        def spec(name: str, depth: int, delegable: bool) -> dict[str, object]:
            return {
                "resource": f"filesystem:workspace:{name}",
                "rights": ["write"],
                "delegable": delegable,
                "revocable": True,
                "max_delegation_depth": depth,
            }

        a = runtime.process.spawn(goal="task A and B host authority", authority_manifest={
            "authorized_capabilities": [spec("A.txt", 3, True), spec("B.txt", 3, True)],
            "permitted_effects": ["filesystem.*"],
        })
        b = runtime.process.spawn_child(a, "task A child", authority_manifest={
            "authorized_capabilities": [spec("A.txt", 3, True)],
            "permitted_effects": ["filesystem.*"],
        })
        c = runtime.process.spawn_child(b, "task A grandchild", authority_manifest={
            "authorized_capabilities": [spec("A.txt", 3, False)],
            "permitted_effects": ["filesystem.*"],
        })
        denied_effect = runtime.process.spawn_child(a, "task A effect-deny child", authority_manifest={
            "authorized_capabilities": [spec("A.txt", 3, False)],
            "permitted_effects": [],
        })
        subjects = {"A": a, "B": b, "C": c, "deny_effect": denied_effect}
        manifests = {}
        for label, pid in subjects.items():
            manifest = runtime.authority_manifests.get_for_process(pid)
            manifests[label] = {
                "pid": pid,
                "manifest_id": manifest.manifest_id if manifest else None,
                "parent_manifest_id": manifest.parent_manifest_id if manifest else None,
                "permitted_effects": manifest.permitted_effects if manifest else None,
                "authorized_resources": [s["resource"] for s in manifest.authorized_capabilities] if manifest else [],
                "capabilities": [
                    {"cap_id": cap.cap_id, "resource": cap.resource, "parent_cap_id": cap.parent_cap_id, "active": cap.active}
                    for cap in runtime.capability.list_subject(pid)
                    if cap.resource.startswith("filesystem:workspace:")
                ],
            }

        write("parent_B_normal", a, "B.txt", "parent B normal\n")
        write("child_A_normal", b, "A.txt", "child A normal\n")
        write("grandchild_A_normal", c, "A.txt", "grandchild A normal\n")
        write("child_B_forbidden", b, "B.txt", "child B forbidden\n")
        write("child_effect_ceiling_empty", denied_effect, "A.txt", "ceiling forbidden\n")

        parent_a_cap = next(
            cap for cap in runtime.capability.list_subject(a)
            if cap.resource == "filesystem:workspace:A.txt" and CapabilityRight.WRITE in cap.rights
        )
        revoked = runtime.capability.revoke(parent_a_cap.cap_id, revoked_by="host", require_authority=False)
        write("grandchild_A_after_parent_revoke", c, "A.txt", "post revoke forbidden\n")
        evidence = {
            "subjects": subjects,
            "manifests_before_revoke": manifests,
            "revoked_parent_cap_id": parent_a_cap.cap_id,
            "revoked_parent_cap_active": revoked.active,
            "rows": rows,
            "external_effects": [
                {"provider": effect.provider, "operation": effect.operation, "state_mutation": effect.state_mutation,
                 "effect_state": effect.effect_state, "transaction_state": effect.transaction_state,
                 "pid": effect.pid}
                for effect in runtime.store.list_external_effects()
            ],
        }
        (run_dir / "raw.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"rows": [{"case": row["case"], "status": row["status"], "error": row["error"], "after": row["after"]} for row in rows]}))
        return 0
    finally:
        runtime.close()


if __name__ == "__main__":
    sys.exit(main())
