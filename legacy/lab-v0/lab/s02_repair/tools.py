"""S2 도구. 권한 분리는 프롬프트 문구가 아니라 도구 목록으로 한다.

진단 에이전트: 조회 도구 2개만. 수리 에이전트: 행동 도구 1개만(게이트를 거친다).
"""
from pathlib import Path

from lab.s02_repair.world import account_permissions, insert_permission, queue_status

GET_QUEUE_STATUS = {
    "name": "get_queue_status",
    "description": "큐 하나의 담당 계정(worker_account)과 상태(running/stalled)를 조회한다.",
    "parameters": {
        "type": "object",
        "properties": {"queue": {"type": "string", "description": "예: orders"}},
        "required": ["queue"],
    },
}
GET_ACCOUNT_PERMISSIONS = {
    "name": "get_account_permissions",
    "description": "계정 하나가 가진 권한 목록을 조회한다.",
    "parameters": {
        "type": "object",
        "properties": {"account_id": {"type": "string", "description": "예: acct-7"}},
        "required": ["account_id"],
    },
}
GRANT_PERMISSION = {
    "name": "grant_permission",
    "description": "계정 하나에 권한 하나를 부여한다.",
    "parameters": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string", "description": "예: acct-7"},
            "permission": {"type": "string", "description": "예: report_read"},
        },
        "required": ["account_id", "permission"],
    },
}

DIAG_TOOLS = [GET_QUEUE_STATUS, GET_ACCOUNT_PERMISSIONS]
REPAIR_TOOLS = [GRANT_PERMISSION]


def make_observation_handlers(db: Path) -> dict:
    def get_queue_status(queue: str) -> dict:
        return queue_status(db, queue) or {"error": "not found"}

    def get_account_permissions(account_id: str) -> dict:
        perms = account_permissions(db, account_id)
        if perms is None:
            return {"error": "not found"}
        return {"account_id": account_id, "permissions": perms}

    return {"get_queue_status": get_queue_status, "get_account_permissions": get_account_permissions}


def make_action_handlers(db: Path, gate) -> dict:
    def grant_permission(account_id: str, permission: str) -> dict:
        entry = gate({"tool": "grant_permission", "args": {"account_id": account_id, "permission": permission}})
        if not entry["allowed"]:
            entry["executed"] = False
            return {"ok": False, "blocked": entry["reason"]}
        result = insert_permission(db, account_id, permission)
        entry["executed"] = result["ok"]
        return result

    return {"grant_permission": grant_permission}
