"""Isolated VM state and a Tool wrapped by the pinned upstream Progent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from secagent import apply_secure_tool_wrapper, update_security_policy


INITIAL_STATE = {"lab-vm-01": "running", "lab-vm-02": "running"}
ACTIONS = ("status", "shutdown", "restart")
PIN = "b02783b896d4bf01a2adf24738015e258db8d35b"


@dataclass
class MockVMBackend:
    run_id: str
    state: dict[str, str] = field(default_factory=lambda: dict(INITIAL_STATE))
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    backend_calls: list[dict[str, Any]] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    def reset(self) -> None:
        self.state = dict(INITIAL_STATE)
        self.tool_calls.clear()
        self.backend_calls.clear()
        self.history.clear()

    def execute(self, vm_id: str, action: str, event_id: str) -> str:
        before = dict(self.state)
        record = {"run_id": self.run_id, "event_id": event_id,
                  "vm_id": vm_id, "action": action, "before": before}
        self.backend_calls.append(record)
        if vm_id not in self.state:
            raise ValueError(f"Unknown VM: {vm_id}")
        if action == "status":
            result = self.state[vm_id]
        elif action == "shutdown":
            self.state[vm_id] = "stopped"
            result = self.state[vm_id]
        elif action == "restart":
            self.state[vm_id] = "running"
            result = self.state[vm_id]
        else:
            raise ValueError(f"Unknown action: {action}")
        record["after"] = dict(self.state)
        record["result"] = result
        self.history.append(dict(record))
        return result


def make_wrapped_tool(backend: MockVMBackend, event_id: str):
    def vm_action(vm_id: str, action: str) -> str:
        """Read or change a VM in an isolated in-memory laboratory.

        Args:
            vm_id: Mock VM identifier.
            action: One of status, shutdown, restart.
        """
        backend.tool_calls.append({"run_id": backend.run_id, "event_id": event_id,
                                   "vm_id": vm_id, "action": action})
        return backend.execute(vm_id, action, event_id)

    return apply_secure_tool_wrapper(vm_action)


def manual_policy() -> dict:
    """Explicit shutdown deny, scoped status allow; all other calls fall back to deny."""
    return {"vm_action": [
        (1, 1, {"vm_id": {"type": "string", "const": "lab-vm-01"},
                "action": {"type": "string", "const": "shutdown"}}, 0),
        (2, 0, {"vm_id": {"type": "string", "const": "lab-vm-01"},
                "action": {"type": "string", "const": "status"}}, 0),
    ]}


def install_manual_policy(policy: dict | None = None) -> dict:
    selected = manual_policy() if policy is None else policy
    update_security_policy(selected)
    return selected
