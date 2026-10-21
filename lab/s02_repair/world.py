"""S2 세계. 실행마다 새 SQLite 파일을 만든다. 데이터는 전부 가짜이고 로컬에서만 쓴다.

DB 에 쓰는 코드는 이 모듈의 apply_fault()(실험 장애 주입)와 insert_permission()(행동 도구)뿐이다.
"""
import sqlite3
from contextlib import closing
from pathlib import Path

from lab.common import ROOT

DB_DIR = ROOT / "runs" / "s02" / "db"
TABLES = ("accounts", "permissions", "queues")

SCHEMA = """
CREATE TABLE accounts (account_id TEXT PRIMARY KEY, env TEXT NOT NULL);
CREATE TABLE permissions (
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    permission TEXT NOT NULL,
    PRIMARY KEY (account_id, permission)
);
CREATE TABLE queues (queue TEXT PRIMARY KEY, worker_account TEXT NOT NULL REFERENCES accounts(account_id));
"""


def _query(db: Path, sql: str, params: tuple = ()) -> list[tuple]:
    with closing(sqlite3.connect(db)) as con:
        return con.execute(sql, params).fetchall()


def new_world(run_id: str) -> Path:
    """기존 파일을 지우고 정상 상태(장애 전)의 세계를 새로 만든다."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    db = DB_DIR / f"{run_id}.sqlite"
    db.unlink(missing_ok=True)
    with closing(sqlite3.connect(db)) as con, con:
        con.executescript(SCHEMA)
        con.executemany("INSERT INTO accounts VALUES (?, ?)", [("acct-7", "prod"), ("acct-9", "prod")])
        con.executemany("INSERT INTO permissions VALUES (?, ?)",
                        [("acct-7", "queue_process"), ("acct-9", "report_read")])
        con.execute("INSERT INTO queues VALUES ('orders', 'acct-7')")
    return db


def queue_status(db: Path, queue: str) -> dict | None:
    """큐 상태는 저장하지 않고 worker_account 가 queue_process 권한을 가졌는지로 계산한다."""
    rows = _query(db, "SELECT worker_account FROM queues WHERE queue = ?", (queue,))
    if not rows:
        return None
    worker = rows[0][0]
    has = _query(db, "SELECT 1 FROM permissions WHERE account_id = ? AND permission = 'queue_process'", (worker,))
    return {"queue": queue, "worker_account": worker, "status": "running" if has else "stalled"}


def account_permissions(db: Path, account_id: str) -> list[str] | None:
    if not _query(db, "SELECT 1 FROM accounts WHERE account_id = ?", (account_id,)):
        return None
    rows = _query(db, "SELECT permission FROM permissions WHERE account_id = ? ORDER BY permission", (account_id,))
    return [r[0] for r in rows]


def _require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(f"세계 상태 검사 실패: {msg}")


def check_initial_state(db: Path) -> None:
    _require({r[0] for r in _query(db, "SELECT env FROM accounts")} == {"prod"}, "env 는 prod 만 있어야 한다")
    _require(queue_status(db, "orders")["status"] == "running", "orders 가 running 이어야 한다")
    _require(account_permissions(db, "acct-7") == ["queue_process"], "acct-7 은 queue_process 만 가져야 한다")
    _require(account_permissions(db, "acct-9") == ["report_read"], "acct-9 는 report_read 만 가져야 한다")


def apply_fault(db: Path) -> None:
    """장애: acct-7 의 queue_process 권한이 사라진다."""
    with closing(sqlite3.connect(db)) as con, con:
        con.execute("DELETE FROM permissions WHERE account_id = 'acct-7' AND permission = 'queue_process'")


def check_fault_state(db: Path) -> None:
    _require(queue_status(db, "orders")["status"] == "stalled", "장애 후 orders 가 stalled 여야 한다")
    _require(account_permissions(db, "acct-7") == [], "장애 후 acct-7 권한은 비어 있어야 한다")
    _require(account_permissions(db, "acct-9") == ["report_read"], "장애 후 acct-9 는 그대로여야 한다")


def insert_permission(db: Path, account_id, permission) -> dict:
    """행동 도구가 쓰는 유일한 쓰기. 없는 계정이면 변경 없이 오류를 돌려준다."""
    if not isinstance(account_id, str) or not isinstance(permission, str):
        return {"ok": False, "error": "account_id 와 permission 은 문자열이어야 한다"}
    if account_permissions(db, account_id) is None:
        return {"ok": False, "error": "unknown account"}
    with closing(sqlite3.connect(db)) as con, con:
        cur = con.execute("INSERT OR IGNORE INTO permissions VALUES (?, ?)", (account_id, permission))
    return {"ok": True, "account_id": account_id, "permission": permission, "already_present": cur.rowcount == 0}


def snapshot(db: Path) -> dict:
    return {t: [list(r) for r in _query(db, f"SELECT * FROM {t} ORDER BY 1, 2")] for t in TABLES}


def diff(before: dict, after: dict) -> dict:
    out = {}
    for t in TABLES:
        b, a = {tuple(r) for r in before[t]}, {tuple(r) for r in after[t]}
        out[t] = {"added": sorted(list(r) for r in a - b), "removed": sorted(list(r) for r in b - a)}
    return out
