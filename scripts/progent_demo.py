#!/usr/bin/env python3
"""Inspect configuration or start ONE new Progent/AgentDojo terminal experiment.

config / --dry-run never imports the benchmark, prepares injections, calls an
LLM, runs a simulated tool, or creates a run directory. Live modes require a
terminal confirmation and pause before every HTTP request and simulated tool.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit
import uuid

# Reuse the existing successful observer's source pin and original checkout.
from progent_live_visible import PIN, ROOT, UPSTREAM, RunStop
from progent_demo_terminal import clean

PRICE_SOURCE = "https://developers.openai.com/api/docs/models/gpt-6-luna"
PRICE_CHECKED = "2026-11-19"
TASK_SOURCE = UPSTREAM / "agentdojo/src/agentdojo/default_suites/v1/banking/user_tasks.py"
AUTH_NAME = re.compile(r"(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|ORG_ID|PROJECT_ID)", re.I)
ENV_NAMES = {
    "LLM_API_KEY", "OPENAI_API_KEY", "LLM_BASE_URL", "OPENAI_BASE_URL", "LLM_MODEL",
    "OPENAI_ORG_ID", "OPENAI_PROJECT_ID", "SECAGENT_POLICY_MODEL", "SECAGENT_GENERATE",
    "SECAGENT_UPDATE", "SECAGENT_ONLY_ALLOW_NARROW", "SECAGENT_IGNORE_UPDATE_ERROR",
    "PROGENT_AGENT_MODEL", "PROGENT_PROFILE", "PROGENT_AGENT_OPTIONS", "PROGENT_POLICY_OPTIONS",
    "PROGENT_AGENT_INPUT_PRICE", "PROGENT_AGENT_OUTPUT_PRICE",
    "PROGENT_POLICY_INPUT_PRICE", "PROGENT_POLICY_OUTPUT_PRICE",
}


class Redactor:
    def __init__(self, env):
        self.secrets = sorted({str(v) for k, v in env.items() if AUTH_NAME.search(k) and v}, key=len, reverse=True)

    def text(self, value):
        text = str(value)
        for secret in self.secrets:
            text = text.replace(secret, "[REDACTED]")
            # Some exceptions/SDKs render escaped JSON rather than raw strings.
            text = text.replace(json.dumps(secret)[1:-1], "[REDACTED]")
        text = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", text)
        return clean(text)

    def value(self, value):
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        if isinstance(value, dict):
            return {self.text(k): ("[REDACTED]" if re.search(
                r"api.?key|authorization|password|secret|access.?token|refresh.?token", str(k), re.I
            ) else self.value(v)) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.value(v) for v in value]
        if isinstance(value, str):
            return self.text(value)
        if value is None or isinstance(value, (int, float, bool)):
            return value
        return self.text(value)


def boolean(env, name, default):
    value = env.get(name, str(default)).lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{name}: True 또는 False를 사용하세요.")
    return value == "true"


def positive(value):
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("유한한 양수를 사용하세요.")
    return result


def load_environment(path):
    env = dict(os.environ)
    if path is not None:
        from dotenv import dotenv_values
        # Data parsing only; never source an arbitrary shell script or expand $VAR.
        if not path.is_file():
            raise ValueError("--env-file 파일이 없습니다.")
        values = dotenv_values(path, interpolate=False)
        for name in ENV_NAMES:
            if values.get(name) and not env.get(name):
                env[name] = values[name]
    return env


def original_prompt():
    tree = ast.parse(TASK_SOURCE.read_text())
    task = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "UserTask0")
    for node in task.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PROMPT" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("원본 UserTask0.PROMPT를 찾지 못했습니다.")


def source_state():
    def git(*args):
        return subprocess.check_output(["git", "-C", str(UPSTREAM), *args], text=True, stderr=subprocess.DEVNULL).strip()
    sha = git("rev-parse", "HEAD")
    return {"sha": sha, "expected_sha": PIN, "clean": not bool(git("status", "--porcelain")), "pin_matches": sha == PIN}


def endpoint(value):
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError:
        raise ValueError("Base URL 형식이 올바르지 않습니다.") from None
    if url.username or url.password or url.query or url.fragment:
        raise ValueError("Base URL에는 인증정보, query, fragment를 넣지 마세요.")
    if not url.hostname or (url.scheme != "https" and not (
        url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1", "::1"}
    )):
        raise ValueError("HTTPS 또는 localhost HTTP Base URL이 필요합니다.")
    base = urlunsplit((url.scheme, url.netloc, url.path.rstrip("/"), "", ""))
    provider = "OpenAI" if url.scheme == "https" and url.hostname == "api.openai.com" and port in {None, 443} else "OpenAI-compatible (사용자 지정)"
    return base, provider


def model_config(model, preset, options, input_price, output_price, provider, cap):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,160}", model):
        raise ValueError("모델 ID 형식이 올바르지 않습니다.")
    if preset == "auto":
        preset = "luna" if model == "gpt-6-luna" else "chat"
    if preset == "luna" and model != "gpt-6-luna":
        raise ValueError("luna preset은 gpt-6-luna 전용입니다.")
    try:
        overrides = json.loads(options or "{}")
    except json.JSONDecodeError:
        raise ValueError("모델 options는 JSON object여야 합니다.") from None
    if not isinstance(overrides, dict) or set(overrides) - {"temperature", "seed", "reasoning_effort"}:
        raise ValueError("options 허용 필드: temperature, seed, reasoning_effort")
    if "temperature" in overrides and not (isinstance(overrides["temperature"], (int, float)) and math.isfinite(overrides["temperature"]) and 0 <= overrides["temperature"] <= 2):
        raise ValueError("temperature는 0~2의 숫자여야 합니다.")
    if "seed" in overrides and (not isinstance(overrides["seed"], int) or isinstance(overrides["seed"], bool)):
        raise ValueError("seed는 정수여야 합니다.")
    if "reasoning_effort" in overrides and overrides["reasoning_effort"] not in {"none", "minimal", "low", "medium", "high", "xhigh", "max"}:
        raise ValueError("지원하는 reasoning_effort 값이 필요합니다.")
    effective = {"reasoning_effort": "none"} if preset == "luna" else (
        {"reasoning_effort": "low"} if preset == "reasoning" else {"temperature": 0.0, "seed": 0})
    effective.update(overrides)
    if preset == "luna" and (effective.get("reasoning_effort") != "none" or {"temperature", "seed"} & effective.keys()):
        raise ValueError("luna Chat Completions: reasoning_effort=none, temperature/seed 제외가 필요합니다.")
    effective["max_completion_tokens" if preset in {"luna", "reasoning"} else "max_tokens"] = cap
    official_luna = provider == "OpenAI" and model == "gpt-6-luna"
    def price(value, default):
        return positive(value) if value is not None else default
    rates = {"input": price(input_price, 0.10 if official_luna else None),
             "output": price(output_price, 0.50 if official_luna else None)}
    return {"model": model, "preset": preset, "request_options": effective, "price_per_million": rates,
            "price_source": PRICE_SOURCE if official_luna and input_price is None and output_price is None else "사용자 입력; provider 요금 확인 필요",
            "price_checked": PRICE_CHECKED if official_luna else None,
            "removed_request_fields": ["temperature", "seed", "reasoning_effort", "max_tokens", "max_completion_tokens"]}


def make_config(args, env):
    base, provider = endpoint(args.base_url or env.get("LLM_BASE_URL") or env.get("OPENAI_BASE_URL") or "https://api.openai.com/v1")
    agent = args.agent_model or env.get("PROGENT_AGENT_MODEL") or env.get("LLM_MODEL") or "gpt-6-luna"
    policy = args.policy_model or env.get("SECAGENT_POLICY_MODEL") or agent
    if policy.startswith(("claude", "gemini", "vertex_ai/", "meta-llama/", "Qwen/")):
        raise ValueError("이 셸 어댑터는 정책 모델의 기본 OpenAI-compatible 분기만 지원합니다. 해당 모델의 native provider/localhost 분기는 원본 CLI로 별도 구성하세요.")
    profile = args.profile or env.get("PROGENT_PROFILE", "auto-approve")
    if profile not in {"auto-approve", "auto-deny", "no-update", "off"}:
        raise ValueError("PROGENT_PROFILE이 올바르지 않습니다.")
    generate = boolean(env, "SECAGENT_GENERATE", True)
    update = boolean(env, "SECAGENT_UPDATE", True)
    narrow = boolean(env, "SECAGENT_ONLY_ALLOW_NARROW", False)
    if args.profile or env.get("PROGENT_PROFILE"):
        generate, update, narrow = profile != "off", profile not in {"off", "no-update"}, profile == "auto-deny"
    else:
        profile = "custom-env" if not generate else ("no-update" if not update else ("auto-deny" if narrow else "auto-approve"))
    auth = next((name for name in ["LLM_API_KEY", "OPENAI_API_KEY"] if env.get(name)), None)
    models = {}
    for role, name in [("agent", agent), ("policy", policy)]:
        prefix = role.upper()
        models[role] = model_config(name, getattr(args, role + "_preset"),
            getattr(args, role + "_options") or env.get("PROGENT_" + prefix + "_OPTIONS"),
            getattr(args, role + "_input_price") or env.get("PROGENT_" + prefix + "_INPUT_PRICE"),
            getattr(args, role + "_output_price") or env.get("PROGENT_" + prefix + "_OUTPUT_PRICE"),
            provider, args.max_completion_tokens)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = (args.output or ROOT / "local/guided-reproduction-20261119/runs/progent-live" / f"{args.mode}-{stamp}-{uuid.uuid4().hex[:8]}").resolve()
    if out.exists():
        raise ValueError("출력 폴더가 이미 존재합니다. 새 --output 경로를 사용하세요.")
    return dict(mode=args.mode, suite="banking", task="user_task_0", benchmark_version="v1.1.2",
        user_prompt=original_prompt(), models=models, base_url=base, provider=provider,
        authentication=dict(selected_environment_variable=auth, present=bool(auth),
                            organization_present=bool(env.get("OPENAI_ORG_ID")), project_present=bool(env.get("OPENAI_PROJECT_ID"))),
        environment_file=str(args.env_file.resolve()) if args.env_file else None,
        dotenv_auto_load=False, source=source_state(), output=str(out), stepwise=True,
        attack="important_instructions" if args.mode == "attack" else None,
        injection_task="injection_task_0" if args.mode == "attack" else None,
        profile=profile, policy_format=args.policy_format, manual_check=False,
        policy_environment={"SECAGENT_SUITE": None if profile == "off" else "banking",
            "SECAGENT_GENERATE": str(generate), "SECAGENT_UPDATE": str(update),
            "SECAGENT_ONLY_ALLOW_NARROW": str(narrow), "SECAGENT_IGNORE_UPDATE_ERROR": str(boolean(env, "SECAGENT_IGNORE_UPDATE_ERROR", True)),
            "SECAGENT_POLICY_MODEL": policy, "SECAGENT_TASK_TYPE": "general", "ENABLE_SECAGENT": "False"},
        limits=dict(budget_usd=args.budget_usd, max_requests=args.max_requests,
                    max_completion_tokens=args.max_completion_tokens, max_request_bytes=120000,
                    max_active_seconds=args.max_seconds, http_timeout_seconds=60, sdk_retries=0),
        adaptation="Live02 관찰 방식 재사용; 모델/client 교체, request options, 선택적 name/args 안내; 원본 소스 유지")


def emit_config(config, emit=print):
    emit("\n1. 원본 사용자 Task / banking / user_task_0 / v1.1.2")
    emit(config["user_prompt"])
    emit("\n2. LLM·정책 설정 (API 요청 없음)")
    emit(f"Provider: {config['provider']} / Base URL: {config['base_url']}")
    for role, title in [("agent", "업무 Agent"), ("policy", "정책 LLM")]:
        model = config["models"][role]
        emit(f"{title}: {model['model']} / preset={model['preset']}")
        emit("  전송 옵션: " + json.dumps(model["request_options"], ensure_ascii=False))
        rates = model["price_per_million"]
        emit(f"  USD/1M tokens: input={rates['input']}, output={rates['output']} / {model['price_source']}")
    auth = config["authentication"]
    emit(f"인증: {'있음' if auth['present'] else '없음'} / 선택 변수={auth['selected_environment_variable']} (값 비공개)")
    emit(f"SDK 조직 설정 존재={auth['organization_present']} / 프로젝트 설정 존재={auth['project_present']} (값 비공개)")
    emit(f"env 파일: {config['environment_file'] or '사용 안 함'} / shell 환경 우선 / 자동 dotenv 읽기 꺼짐")
    emit(f"profile={config['profile']} / manual_check=False / policy-format={config['policy_format']}")
    for name, value in config["policy_environment"].items():
        emit(f"  {name}={value}")
    limits = config["limits"]
    emit(f"한도: USD {limits['budget_usd']}, HTTP 최대 {limits['max_requests']}회, 요청별 출력 최대 {limits['max_completion_tokens']} tokens")
    emit("비용 예약: (2×요청 JSON bytes+4096)×입력단가×2 + 출력한도×출력단가×2, /1M; provider 청구 한도 아님.")
    emit("Live02는 7 HTTP 요청. 새 실행의 횟수·비용·성공은 사전 확정할 수 없습니다.")
    # Historical usage is evidence for an illustrative estimate only.
    saved = ROOT / "local/guided-reproduction-20261118/runs/progent-live/luna-visible-on-02/summary.json"
    if saved.is_file():
        previous = json.loads(saved.read_text())
        rates = [config["models"][r]["price_per_million"] for r in ["agent", "policy"]]
        if all(v is not None for r in rates for v in r.values()):
            estimate = (previous["prompt_tokens"] * max(r["input"] for r in rates) + previous["completion_tokens"] * max(r["output"] for r in rates)) / 1e6
            emit(f"과거 token 수에 현재 두 모델 중 높은 단가를 적용한 정상 1건 참고치: USD {estimate:.6f} (새 실행 견적 보장 아님)")
    if config["mode"] == "attack":
        emit("원본 important_instructions / injection_task_0 한 쌍. 새 payload·공격자 LLM 없음.")
        emit("원본 사전 검사(Injection Task를 사용자 요청으로 실행) + canary fixture 탐색 + 공격 적용 실행. 총 한도는 전부 합산.")
    source = config["source"]
    emit(f"원본: {source['sha']} / clean={source['clean']} / pin 일치={source['pin_matches']}")
    emit("새 로그 경로: " + config["output"])
    emit("실행 명령: " + shlex.join([str(ROOT / "scripts/progent_demo.sh"), *sys.argv[1:]]))


def parser():
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="예: scripts/progent_demo.sh config\n    scripts/progent_demo.sh normal --dry-run\n    scripts/progent_demo.sh normal\n    scripts/progent_demo.sh attack --dry-run\n\nEnter=다음 동작 / q 또는 Ctrl+C=실행 전체 중단. 자동 승인 옵션은 제공하지 않습니다.")
    result.add_argument("mode", choices=["config", "normal", "attack", "help"], nargs="?", default="help")
    result.add_argument("--dry-run", action="store_true", help="설정·비용 검토만; import·API·도구·주입 준비·파일 생성 없음")
    result.add_argument("--env-file", type=Path, help="명시한 dotenv 데이터만 읽기; 현재 shell 변수가 우선")
    result.add_argument("--base-url", help="두 모델이 공유하는 OpenAI-compatible Chat Completions endpoint")
    for role in ["agent", "policy"]:
        result.add_argument(f"--{role}-model")
        result.add_argument(f"--{role}-preset", choices=["auto", "luna", "chat", "reasoning"], default="auto")
        result.add_argument(f"--{role}-options", help='JSON: temperature / seed / reasoning_effort')
        result.add_argument(f"--{role}-input-price", type=positive, help="USD/1M input tokens; 다른 모델/provider에서 필수")
        result.add_argument(f"--{role}-output-price", type=positive, help="USD/1M output tokens")
    result.add_argument("--profile", choices=["auto-approve", "auto-deny", "no-update", "off"], help="명시하면 SECAGENT_GENERATE/UPDATE/ONLY_ALLOW_NARROW보다 우선")
    result.add_argument("--policy-format", choices=["original", "explicit-args"], default="explicit-args")
    result.add_argument("--budget-usd", type=positive, default=0.85)
    result.add_argument("--max-requests", type=int, default=20)
    result.add_argument("--max-completion-tokens", type=int, default=4096)
    result.add_argument("--max-seconds", type=positive, default=600, help="Enter 대기를 제외한 활동 시간 한도")
    result.add_argument("--output", type=Path, help="존재하지 않는 새 디렉터리; 기본값은 UTC+랜덤 suffix")
    return result


def main():
    cli = parser()
    args = cli.parse_args()
    if args.mode == "help":
        cli.print_help()
        return 0
    redactor = Redactor(os.environ)
    try:
        env = load_environment(args.env_file)
        redactor = Redactor(env)
        if args.max_requests <= 0 or args.max_completion_tokens <= 0:
            raise ValueError("요청 수와 출력 token 한도는 양수여야 합니다.")
        config = make_config(args, env)
        emit_config(config, lambda text: print(redactor.text(text), flush=True))
        if not config["source"]["clean"] or not config["source"]["pin_matches"]:
            raise ValueError("원본 source pin/clean 검사가 실패했습니다. 실행하지 않습니다.")
        if args.mode == "config" or args.dry_run:
            print("\nPREPARED_NO_API_CALL / HTTP=0 / simulated tools=0 / run directory 생성 없음")
            return 0
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError("새 실행은 사람이 조작하는 터미널이 필요합니다. pipe 자동 진행은 지원하지 않습니다.")
        if not config["authentication"]["present"]:
            raise ValueError("LLM_API_KEY 또는 OPENAI_API_KEY를 shell/env 파일에 설정하세요. 키를 인자로 전달하지 마세요.")
        key = env[config["authentication"]["selected_environment_variable"]]
        if not key.isascii() or any(ch.isspace() for ch in key):
            raise ValueError("인증값에 공백·개행·비ASCII 문자가 있습니다. 값은 표시하지 않습니다.")
        if any(v is None for m in config["models"].values() for v in m["price_per_million"].values()):
            raise ValueError("선택한 모델/provider의 입력·출력 단가를 각각 설정해야 비용 한도를 사용할 수 있습니다.")
        print("\n새 유료 실행을 시작합니다. 각 API/모의 도구 전에도 멈춥니다.", flush=True)
        if input("시작하려면 RUN 입력 / 그 외=취소: ").strip() != "RUN":
            print("CANCELLED / HTTP=0 / 도구 실행 없음")
            return 0
        # Import live dependencies only after explicit, interactive confirmation.
        from progent_demo_session import run
        return run(config, env, redactor)
    except (ValueError, OSError, subprocess.SubprocessError, argparse.ArgumentTypeError) as exc:
        print("ERROR: " + redactor.text(exc), file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("\nCANCELLED")
        return 130


if __name__ == "__main__":
    sys.exit(main())
