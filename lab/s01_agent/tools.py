"""S1 도구 1개. 데이터는 전부 가짜이고 메모리 안에서만 동작한다."""

ACCOUNTS = {
    "acct-7": {"env": "staging", "role": "viewer", "status": "active"},
    "acct-9": {"env": "prod", "role": "admin", "status": "locked"},
}

GET_ACCOUNT_STATUS = {
    "name": "get_account_status",
    "description": "계정 id 하나의 환경(env), 권한(role), 상태(status)를 조회한다. 읽기 전용.",
    "parameters": {
        "type": "object",
        "properties": {"account_id": {"type": "string", "description": "예: acct-7"}},
        "required": ["account_id"],
    },
}


def get_account_status(account_id: str) -> dict:
    return ACCOUNTS.get(account_id, {"error": "not found"})


TOOLS = [GET_ACCOUNT_STATUS]
HANDLERS = {"get_account_status": get_account_status}
