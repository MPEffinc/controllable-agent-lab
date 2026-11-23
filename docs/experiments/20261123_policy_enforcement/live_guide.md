# 연구자 직접 실행: 수동 대화형 및 LLM Live

이 문서는 Phase 2의 기존 `vm_action` 실행기 안내다. 2026-11-22에 추가한 Resource Discovery·Docker·gpt-6-luna 경로는 [live_results.md](live_results.md)의 `system-live` 명령을 사용한다. 아래 `live` 모드의 `RUN` 확인 절차는 기존 실행기에만 적용된다.

프로젝트 `.env` 파일에 키를 보관하고 값을 출력하지 않는 설정 확인 명령은 [API 환경 설정](api_env.md)을 참조한다. 현재 시스템 관리 Live 실행기를 확인할 때는 `bash scripts/progent_vm.sh check-env`를 먼저 사용한다. 이 명령은 API를 호출하지 않는다.

최신 **Mock·Docker·Kata와 Luna Custom Runner/AgentDojo Custom Suite**의 전체 실행 절차는 [Progent × AgentDojo × Kata 실습 가이드](hands_on_guide.md)를 따른다. 이 문서의 아래 Mode A/B는 과거 `vm_action` 실행기 안내로 보존한다.

## Mode A: API 없는 수동 대화형 시험

```bash
cd /home/cclab/controllable_agent
bash scripts/progent_vm.sh manual
```

프롬프트에 VM ID, `status`/`shutdown`/`restart`, `scoped` 또는 `status-both` 정책 프로필을 입력한다. 각 입력은 새로 원본 Wrapper를 통과하며 이전 결과의 Replay가 아니다. `reset`은 두 Mock VM을 `running`으로 되돌리고 호출 이력을 지운다. `quit` 또는 Ctrl-D로 종료하면 프로세스 메모리 상태는 사라진다. 별도 JSONL 로그는 `local/progent-vm/manual/<run-id>.jsonl`에 남으며 Git에서 제외된다. 이 모드는 LLM/API를 호출하지 않는다.

## Mode B: 연구자가 실행할 실제 LLM Live — NOT RUN

먼저 본인 터미널에서 인증정보를 입력한다. 키 값을 명령행 인자로 쓰거나 로그·Git에 넣지 않는다.

```bash
cd /home/cclab/controllable_agent
read -rsp 'OPENAI_API_KEY: ' OPENAI_API_KEY; echo
export OPENAI_API_KEY
export OPENAI_BASE_URL=https://api.openai.com/v1
```

기본 모델은 원본 정책 모델과 과거 CLI 실행에서 사용한 `gpt-4o-2024-08-06`이다. 제공자 계정에서 두 모델의 접근 가능 여부를 확인하려면 연구자가 다음을 실행한다. 이 확인 자체가 최대 2회의 API 요청을 한다.

```bash
bash scripts/progent_vm.sh live --check-models --agent-model gpt-4o-2024-08-06 --policy-model gpt-4o-2024-08-06
```

새 자연어 요청으로 자동 생성 정책만 평가하는 명령:

```bash
bash scripts/progent_vm.sh live --policy-mode generated --agent-model gpt-4o-2024-08-06 --policy-model gpt-4o-2024-08-06 --max-turns 3 --max-policy-requests 2 --max-tool-calls 3
```

관리자 수동 규칙을 먼저 넣은 **별도 실험** 명령:

```bash
bash scripts/progent_vm.sh live --policy-mode admin-plus-generated --agent-model gpt-4o-2024-08-06 --policy-model gpt-4o-2024-08-06 --max-turns 3 --max-policy-requests 2 --max-tool-calls 3
```

예시 요청: `lab-vm-01의 상태를 조회해줘` 또는 `lab-vm-01을 종료해줘`. 실행기는 endpoint·두 모델·한도·비용 가능성을 먼저 표시하며, 연구자가 `RUN`을 입력하기 전에는 API를 호출하지 않는다. 기본 한도는 정책 요청 최대 2회 + 업무 Agent 요청 최대 3회 = **총 최대 5회**, Tool 호출 최대 3회다. 원본 정책 생성의 재시도도 어댑터 카운터에 포함된다. API 요금·모델 지원은 제공자에 따라 다르며 이번 단계에서 확인하지 않았다.

실행기는 **원본** `generate_security_policy`로 정책을 만들고, 업무 모델의 실제 tool call 인자만 Tool Schema → 원본 Wrapper → Mock Backend에 전달한다. `[USER TASK]`, `[POLICY GENERATION]`, `[GENERATED POLICY]`, `[AGENT TOOL CALL]`, `[POLICY CHECK]`, `[ALLOW]`/`[DENY / INPUT ERROR]`, `[BACKEND EXECUTION]`, `[FINAL STATE]`를 출력한다. `admin-plus-generated`는 원본의 수동 규칙 보존·priority 동작을 관찰하는 실험 구성일 뿐, 관리자 Deny와 생성 Allow의 일반적 안전 결합을 보장하지 않는다. Tool을 Agent가 제안하지 않으면 Wrapper Deny가 관찰된 것으로 해석하지 않는다.

Live 로그는 `local/progent-vm/live/<run-id>.json`에 기록된다. 사용자 요청·정책·Tool Call이 포함될 수 있어 **검토 없이 Git에 추가하지 않는다**. 종료 시 Mock Backend는 프로세스와 함께 사라진다. 새 실행이 독립적인 초기 상태로 시작된다. 이 경로는 원본 AgentDojo Benchmark가 아닌 Custom Agent Adapter이며 실제 SSH/VM/OS 집행을 연결하지 않는다.
