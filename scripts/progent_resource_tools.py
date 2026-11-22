"""System-management tool interface; backend remains trusted and private."""

from secagent import apply_secure_tool_wrapper


def build_tools(backend):
    def list_resources() -> list[str]:
        """Discover resource IDs managed by this experiment."""
        return backend.list_resources()

    def get_resource_status(resource_id: str) -> str:
        """Get the current runtime status of a discovered resource."""
        return backend.status(resource_id)

    def start_resource(resource_id: str) -> str:
        """Start a created or stopped resource; this is not a restart."""
        return backend.start(resource_id)

    def stop_resource(resource_id: str) -> str:
        """Stop a running resource."""
        return backend.stop(resource_id)

    def restart_resource(resource_id: str) -> str:
        """Restart a running resource; this is not a start."""
        return backend.restart(resource_id)

    functions = [list_resources, get_resource_status, start_resource, stop_resource, restart_resource]
    return {func.__name__: apply_secure_tool_wrapper(func) for func in functions}
