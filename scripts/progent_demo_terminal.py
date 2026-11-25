#!/usr/bin/env python3
"""Display saved Progent evidence or manually release a benign live-run checkpoint.

Standard library only. Never imports Progent, sends requests, executes a tool,
loads credentials, or changes policies. Replay is read-only. Follow writes only
the .continue files expected by scripts/progent_live_visible.py after Enter.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "local/guided-reproduction-20261118/runs/progent-live"
SAVED = {"success": RUNS / "luna-visible-on-02", "failure": RUNS / "luna-clean-on-01"}
ROLES = {
    "policy_initial": "초기 정책 생성 LLM",
    "agent": "업무 Agent LLM",
    "policy_update_decision": "정책 갱신 필요성 판단 LLM",
    "policy_update_candidate": "정책 갱신 후보 생성 LLM",
    "compatibility_probe": "모델 연결 확인",
}
EVENTS = {
    "api_request", "api_response", "generate_security_policy_after", "tool_request",
    "policy_check", "tool_return", "generate_update_security_policy_after", "session_stopped",
}


def clean(value):
    text = str(value)
    return "".join(ch if ch in "\n\t" or ch.isprintable() else "?" for ch in text)


def emit(value=""):
    print(clean(value), flush=True)


def dump(value):
    emit(json.dumps(value, ensure_ascii=False, indent=2))


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def read_events(run):
    path = run / "events.jsonl"
    if not path.exists():
        return []
    events = []
    for line in path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # A concurrently appended final line may be incomplete.
            continue
    return events


def pause(prompt="Enter=다음 화면 / q=종료: "):
    try:
        return input(clean(prompt)).strip().lower() != "q"
    except EOFError:
        return False


def show_policy(policy):
    if policy is None:
        emit("정책 상태: None — 미초기화 상태의 허용 경로를 확인해야 합니다.")
        return
    generic, generated = {}, {}
    for name, rules in policy.items():
        for rule in rules:
            target = generated if rule[0] == 100 else generic
            target.setdefault(name, []).append(rule)
    emit("기본 규칙 도구: " + ", ".join(sorted(generic)))
    emit("LLM 생성 규칙 (priority=100):")
    dump(generated)


def show_request(run, event, full):
    rid = event["request_id"]
    data = read_json(run / f"api-{rid:02d}-request.json")
    if data is None:
        emit("요청 파일을 아직 읽을 수 없습니다.")
        return
    body = data.get("body", {})
    emit(f"API {rid:02d} / {ROLES.get(event.get('role'), event.get('role'))}")
    emit(f"model={body.get('model')} / 정의된 도구={len(body.get('tools', []))}")
    emit("전송 입력 (원본 파일: " + str(run / f"api-{rid:02d}-request.json") + ")")
    messages = body.get("messages", [])
    for message in messages:
        if message.get("role") == "system" and not full:
            emit("[system prompt 생략 — --full로 전체 표시]")
            continue
        dump(message)
    if full and body.get("tools"):
        emit("도구 schema:")
        dump(body["tools"])


def show_response(run, event):
    rid = event["request_id"]
    data = read_json(run / f"api-{rid:02d}-response.json")
    if data is None:
        emit("응답 파일이 아직 없거나 기록 중입니다.")
        return
    body = data.get("body", {})
    emit(f"API {rid:02d} 저장 응답 / HTTP {data.get('status')}")
    if body.get("error"):
        dump({"error": body["error"]})
    for choice in body.get("choices", []):
        dump(choice.get("message", {}))
    if body.get("usage"):
        dump({"usage": body["usage"]})


def show_event(run, event, full=False):
    kind = event.get("event")
    emit("\n" + "=" * 72)
    emit(f"{kind} / seq={event.get('seq', '-')} / checkpoint={event.get('checkpoint', '-')}")
    if kind == "api_request":
        show_request(run, event, full)
    elif kind == "api_response":
        show_response(run, event)
    elif kind in {"generate_security_policy_after", "generate_update_security_policy_after"}:
        show_policy(event.get("policy"))
    elif kind == "policy_check":
        dump({key: event.get(key) for key in ["tool", "arguments", "decision", "error"]})
    elif kind == "tool_request":
        emit("실제 도구 실행 전 제안:")
        dump({"tool": event.get("tool"), "arguments": event.get("arguments")})
    elif kind == "tool_return":
        emit("도구 실행 후 결과와 모의 거래 변화:")
        dump({key: event.get(key) for key in ["tool", "result", "error", "transaction_delta"]})
    else:
        dump(event)


def show_summary(run):
    summary = read_json(run / "summary.json")
    if summary is None:
        emit("summary.json은 아직 없습니다.")
        return
    emit("\n" + "=" * 72)
    emit("최종 결과 — 원본 task utility와 모의 환경 효과")
    dump({key: summary.get(key) for key in [
        "status", "model", "utility", "attack", "attack_success", "requests",
        "transaction_delta", "new_transactions", "error_type", "error", "adaptation",
    ]})
    snapshots = read_json(run / "environment-snapshots.json") or {}
    counts = {}
    for label in ["initial", "final"]:
        state = snapshots.get(label)
        if state is not None:
            counts[label] = len(state.get("bank_account", {}).get("transactions", []))
    if counts:
        dump({"transaction_counts": counts})
    emit("공격 미실행. utility 성공과 공격 방어 검증을 구분합니다.")


def replay(args):
    run = args.run_dir.resolve() if args.run_dir else SAVED[args.case]
    events = [event for event in read_events(run) if event.get("event") in EVENTS]
    if not events or read_json(run / "summary.json") is None:
        raise ValueError("완료된 실행의 events.jsonl과 summary.json이 필요합니다.")
    emit("[기존 실제 실행 기록 재생 / READ ONLY / 새 API·도구 실행 없음]")
    emit("기록 경로: " + str(run))
    emit("원본 컴포넌트 + 모델·출력 형식·관찰 어댑터 변경 조건의 실행입니다.")
    for index, event in enumerate(events, 1):
        emit(f"\n화면 {index}/{len(events)}")
        show_event(run, event, args.full)
        if not args.all and not pause("Enter=다음 화면 / q=종료: "):
            return
    show_summary(run)


def follow(args):
    run = args.run_dir.resolve()
    if (run / "summary.json").exists():
        raise ValueError("이미 summary.json이 있는 경로는 진행시키지 않습니다. replay를 사용하세요.")
    emit("[새 정상 실행의 수동 진행 / API 호출은 별도 실행기에서 발생]")
    emit("연결 경로: " + str(run))
    emit("Enter는 표시된 checkpoint를 계속 진행시킵니다. q는 뷰어만 종료합니다.")
    shown_responses, shown_decisions, shown_checkpoints = set(), set(), set()
    deadline = time.monotonic() + 1200
    while time.monotonic() < deadline:
        config = read_json(run / "configuration.json")
        if config is None:
            time.sleep(0.2)
            continue
        if not config.get("stepwise") or config.get("attack") is not None or config.get("task") != "user_task_0":
            raise ValueError("정상 user_task_0의 stepwise 실행만 연결합니다.")
        events = read_events(run)
        for event in events:
            seq = event.get("seq")
            if event.get("event") == "api_response" and seq not in shown_responses:
                show_event(run, event, args.full)
                shown_responses.add(seq)
            if event.get("event") == "policy_check" and seq not in shown_decisions:
                show_event(run, event, args.full)
                shown_decisions.add(seq)
        pending = [path for path in sorted(run.glob("checkpoint-*.json"))
                   if path.name not in shown_checkpoints and not path.with_suffix(".continue").exists()]
        if pending:
            path = pending[0]
            data = read_json(path)
            if data is None:
                time.sleep(0.2)
                continue
            show_event(run, data, args.full)
            emit("진행 파일: " + str(path.with_suffix(".continue")))
            if not pause("Enter=이 checkpoint 진행 / q=뷰어 종료: "):
                emit("진행 파일을 만들지 않았습니다. 실행 중단은 실행기 터미널에서 Ctrl+C 하세요.")
                return
            try:
                with path.with_suffix(".continue").open("x") as handle:
                    handle.write("manually continued by terminal operator\n")
            except FileExistsError:
                emit("다른 조작자가 이미 진행시킨 checkpoint입니다.")
            shown_checkpoints.add(path.name)
        elif read_json(run / "summary.json") is not None:
            show_summary(run)
            return
        time.sleep(0.2)
    raise ValueError("20분 동안 실행이 종료되지 않았습니다. 실행기 터미널 상태를 확인하세요.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    saved = modes.add_parser("replay", help="기존 실제 실행 기록 읽기 — API 없음")
    saved.add_argument("--case", choices=sorted(SAVED), default="success")
    saved.add_argument("--run-dir", type=Path)
    saved.add_argument("--all", action="store_true", help="Enter 대기 없이 모든 기록 표시")
    saved.add_argument("--full", action="store_true", help="system prompt·tool schema도 표시")
    live = modes.add_parser("follow", help="별도 정상 실행기의 checkpoint 수동 진행")
    live.add_argument("--run-dir", type=Path, required=True)
    live.add_argument("--full", action="store_true")
    args = parser.parse_args()
    try:
        replay(args) if args.mode == "replay" else follow(args)
    except (ValueError, OSError) as exc:
        emit("ERROR: " + str(exc))
        return 1
    except KeyboardInterrupt:
        emit("\n뷰어 종료. 별도 실행기는 필요하면 해당 터미널에서 Ctrl+C 하세요.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
