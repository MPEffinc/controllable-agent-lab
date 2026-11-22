"""System-management tool interface; backend remains trusted and private."""

from secagent import apply_secure_tool_wrapper


class MockResourceBackend:
    def __init__(self):
        self.resources = {"lab-vm-01": "running", "lab-vm-02": "running"}
        self.invocations = []

    def list_resources(self) -> list[str]:
        return sorted(self.resources)

    def status(self, resource_id: str) -> str:
        if resource_id not in self.resources:
            raise ValueError("Unknown resource")
        self.invocations.append({"action": "status", "resource_id": resource_id})
        return self.resources[resource_id]

    def start(self, resource_id: str) -> str:
        if self.resources.get(resource_id) != "stopped":
            raise ValueError("start requires stopped resource")
        self.resources[resource_id] = "running"
        self.invocations.append({"action": "start", "resource_id": resource_id})
        return "running"

    def stop(self, resource_id: str) -> str:
        if self.resources.get(resource_id) != "running":
            raise ValueError("stop requires running resource")
        self.resources[resource_id] = "stopped"
        self.invocations.append({"action": "stop", "resource_id": resource_id})
        return "stopped"

    def restart(self, resource_id: str) -> str:
        if self.resources.get(resource_id) != "running":
            raise ValueError("restart requires running resource")
        self.invocations.append({"action": "restart", "resource_id": resource_id})
        return "running"


def build_tools(backend):
    backend.tool_calls = []

    def invoke(method, *args):
        # This marker is inside the original Progent wrapper. A denied call
        # never reaches it, even when the controller operation is read-only.
        backend.tool_calls.append({"method": method, "args": list(args)})
        return getattr(backend, method)(*args)

    def list_resources() -> list[str]:
        """Discover resource IDs managed by this experiment."""
        return invoke("list_resources")

    def get_resource_status(resource_id: str) -> str:
        """Get the current runtime status of a discovered resource."""
        return invoke("status", resource_id)

    def start_resource(resource_id: str) -> str:
        """Start a created or stopped resource; this is not a restart."""
        return invoke("start", resource_id)

    def stop_resource(resource_id: str) -> str:
        """Stop a running resource."""
        return invoke("stop", resource_id)

    def restart_resource(resource_id: str) -> str:
        """Restart a running resource; this is not a start."""
        return invoke("restart", resource_id)

    functions = [list_resources, get_resource_status, start_resource, stop_resource, restart_resource]
    return {func.__name__: apply_secure_tool_wrapper(func) for func in functions}
