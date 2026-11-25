# Progent Guided Study 01 — 논문의 두 집행 경계

학습일: 2026-11-18, Asia/Seoul. 상태: **원문·코드 정적 대조 완료, 첫 실습 미실행**. 이전 설치 기록을 새 실험 결과로 세지 않는다. 다른 여섯 연구의 학습 범위도 유지한다.

## 기준과 사례 분류

- 논문: [Progent: Securing AI Agents with Privilege Control, arXiv 2504.11703v3](https://arxiv.org/html/2504.11703v3), Tianneng Shi 외. §2–6, Figure 1–2, Algorithm 2–3을 기준으로 한다. v2의 절 번호·정책 구성·평가 결과와 혼합하지 않는다.
- 원본: [sunblaze-ucb/progent](https://github.com/sunblaze-ucb/progent), `b02783b896d4bf01a2adf24738015e258db8d35b`. 오늘 다시 읽은 Git HEAD와 working tree clean 상태를 확인했다. 논문 공개 당시의 정확한 evaluation commit이라는 확인은 없다.
- 환경: `local/guided-reproduction-20261117/envs/progent-agentdojo/`, Python 3.10.12, secagent0.1.0, 저자 수정 AgentDojo0.1.29. installed-distribution metadata 100개 확인. 오늘 설치/재설치/import smoke 재실행 없이 기존 환경을 재사용한다.
- 오늘의 비파괴 점검: `local/guided-reproduction-20261118/progent-session01-precheck.json`. 모듈 실행·모델·정책 검사·tool·benchmark는 수행하지 않았다.
- [Figure 1 원본 SVG](https://arxiv.org/html/2504.11703v3/teaser-horizontal_cropped.svg)를 변경 없이 다운로드했고 `local/guided-reproduction-20261118/figure1-source.json`에 URL/SHA256을 보존했다.

| 이번에 설명하는 사례 | 분류 | 범위 |
|---|---|---|
| Alice의 TODO 이메일 → 최근 이메일 요약 → Slack, 중간 외부 이메일 유출 시도 | **논문의 Motivating Example**, §2/Figure 1 | 설명용 실행과 정책 변화. 원본 평가 task와 동일한 runnable scenario라고 확인하지 않았다. |
| Workspace `UserTask13` | **원본 Evaluation harness의 Scenario 정의** | TODO 이메일에서 문서 수정·피드백 점수 이메일 발송을 알아내는 실제 task. Figure 1과 작업·도구가 다르다. task 정의 존재가 개별 저자 run 로그의 실행 증거는 아니다. |
| `secagent.policy_type_check.__main__` | **공식 Repository의 Demo** | 정적 정책 경고를 출력. tool 효과·LLM·SMT update를 실행하지 않는다. |
| 기존 `scripts/progent_guided_effect.py` | **학습을 위해 별도로 연결한 어댑터** | 원본 정책/요청/runtime/tool 구성요소 replay. 이번에는 사용하지 않는다. |

## 논문에서 먼저 읽을 구조

§2/Figure 1의 P1→P2는 필요한 새 tool을 추가하는 expansion, P2→P3는 Slack 수신자를 alice로 고정하는 narrowing이다. 악성 send_email 호출은 P4에 허용 규칙이 없어 차단한다. Figure 1a는 agent flow, 1b는 정책 예, 1c는 policy evolution을 함께 읽는다.

§3의 공격자는 외부 관찰 o_i(i>0)를 오염시킬 수 있고 초기 사용자 요청 o_0는 benign이다. 모델·system prompt를 직접 바꾸는 공격과 구분한다. 연구의 출발 문제는 비결정적 agent, 작업·실행 context의 변화, 정상 업무에 필요한 확장과 공격자가 유도한 확장이 같은 tool-return 채널로 들어오는 상황이다.

§4.1/Figure 2의 policy는 tool 이름·인자 조건·allow/forbid·fallback으로 구성된다. Algorithm 2는 한 호출을 검사한다. §4.3의 비교는 다음 수식으로 읽는다.

\[
A(P)=\{c\mid P(c)=c\},\qquad
\text{narrowing}\iff A(P')\subseteq A(P).
\]

새로 허용되는 호출이 하나라도 있으면 expansion이다. SMT 검사에서는 후보가 허용하지만 기존 정책이 거부하는 인자가 존재하는지, 즉 `Phi_new AND NOT Phi_old`의 만족 가능성을 확인한다. subset 검사의 역할은 악성 의도의 의미 판별이 아니라 허용 호출 집합 비교다.

§5/Algorithm 3은 초기 정책 생성 → agent 제안 → Algorithm 2 → tool/fallback 결과 → 후보 정책 생성 → subset 검사/승인 → 다음 step이다. update 필요성 판단에는 tool result를 직접 넣지 않고, 실제 후보 생성 단계에서 result와 현재 정책을 포함한다. 직접적인 result 노출을 분리하는 설계이지 필요성 판단 LLM을 형식 검증한 것은 아니다.

§6 Eq.(5)–(6)의 Monotonic Confinement는 승인된 확장 사이에서 허용 호출 집합이 단조 감소한다는 속성이다. 초기 정책의 의미적 정확성, 승인자의 판단 정확성, 정상 작업의 완수까지 증명하는 정리는 아니다. 모든 보호 효과가 중재 경계를 통과하고 비교/집행/승인 상태가 의도대로 동작한다는 전제가 필요하다. 허용 범위 안의 목표 왜곡과 자연어 출력 공격은 §3.2의 보장 범위 밖이다.

## 실제 코드 대응 — 입력·출력과 연결

아래 경로는 모두 `third_party/progent/` 기준이다. line은 이 SHA에서 확인했다. 논문은 정책 P를 값으로 표기하지만 Python 구현은 주로 module global `security_policy`를 갱신한다.

| 논문 컴포넌트 | 파일·함수·line | 입력 → 실제 출력/효과 | 다음 연결 |
|---|---|---|---|
| 초기화, Algorithm 3 line1 | `agentdojo/src/agentdojo/agent_pipeline/basic_elements.py:14 InitQuery.query` | 사용자 query·runtime/env/messages → query를 messages에 추가한 tuple | `generate_security_policy(query)` |
| 생성, §5 | `secagent/tool.py:375 generate_security_policy` | query와 global available tools → `None`, global 정책에 priority100 allow 규칙 추가 | `api_request`·JSON 추출·선택적 확인 |
| 도구 선택과 반복 | `agentdojo/src/agentdojo/agent_pipeline/agent_pipeline.py:140 AgentPipeline.from_config` | PipelineConfig → SystemMessage/InitQuery/LLM/ToolsExecutionLoop 구성 | `ToolsExecutor.query` |
| 도구 인자 검사·실행 | `agentdojo/src/agentdojo/functions_runtime.py:242 FunctionsRuntime.run_function` | env, tool name, kwargs → `(result, error)` | Pydantic 인자 검사·dependency 주입 후 wrapped Function |
| 호출 집행, Algorithm 2 | `secagent/tool.py:718 secure_tool_wrapper`, `573 check_tool_call`, `521 _check_tool_call`, `508 check_arg` | tool 이름·인자·global P → 정상 반환(None) 또는 예외 | 허용 시에만 원래 Python tool 호출 |
| update 필요성 판단, §5 | `secagent/tool.py:415 decide_whether_to_update` | tools/query/current tool call → bool | tool result는 이 prompt에서 제외 |
| 후보 생성·적용, Algorithm 3 line6–9 | `secagent/tool.py:435 generate_update_security_policy` | 호출 묶음·result, query/tools/current P → `None`, 후보를 폐기하거나 global P 교체 | 선택적 subset 검사와 manual check |
| 갱신 검사, §4.3 | `secagent/policy_analysis.py:381 security_policy_subset_check` | 기존·후보 policy dict → bool | 새 허용 값의 반례가 있거나 narrowing을 증명 못하면 False |
| 실제 관찰 뒤 update 연결 | `agentdojo/src/agentdojo/agent_pipeline/tool_execution.py:107–123 ToolsExecutor.query` | 원본 runtime 결과·error → tool messages; calls/results 수집 | `SECAGENT_UPDATE == "True"`일 때 update, manual_check=False |

### 집행 경계의 실제 코드

`secagent/tool.py:573–590`의 원본 18줄이다.

```python
def check_tool_call(tool_name, kwargs) -> None:
    global security_policy
    if security_policy is None:
        print("Warning: security policy is not set.", file=sys.stderr)
        return
    try:
        policies = security_policy.get(tool_name, None)
        if policies is None or len(policies) == 0:
            raise ValidationError(f"The tool '{tool_name}' is not allowed.")
        if len(policies) == 0:
            return
        need_update_policies = _check_tool_call(tool_name, kwargs, policies)
        if need_update_policies:
            for tool, policies in need_update_policies.items():
                security_policy[tool] = policies
            sort_policy()
    except Exception as e:
        raise ValidationError(f"{e}. Please try other tools or arguments and continue to finish the user task: {init_user_query}.")
```

이것은 bool 판정 API가 아니다. 정상 반환은 호출을 계속하게 하고, 예외는 wrapper의 후속 원본 tool 호출을 중단시킨다. `secure_tool_wrapper`의 757행이 이 검사이고 758행이 `return tool(*args, **kwargs)`이므로 순서가 중요하다. policy=None이면 경고 후 반환하므로 초기화 전제 없이 default-deny라고 설명하지 않는다.

### 논문과 고정 코드의 구성 차이

| 관점 | 고정 코드에서 확인한 사실 | 해석 |
|---|---|---|
| 우선순위 | `sort_policy:69`는 `(priority, -effect)` | 동일 priority에서 forbid가 우선한다. 모든 priority를 넘어 forbid가 항상 이긴다고 설명하지 않는다. §7 generic policy layers와 연결해 읽는다. |
| Auto-Approve | `agentdojo/run.sh:19–21`: UPDATE=True, ONLY_ALLOW_NARROW는 주석. executor:123은 manual_check=False | §8.2의 자동 확장 수락 평가와 대응하지만 이 경로는 subset 분류 자체를 건너뛴다. §6의 narrowing-only 구성과 동일시하지 않는다. |
| Auto-Deny 후보 | `tool.py:464–481`: ONLY_ALLOW_NARROW=True일 때 subset=False를 폐기 | unknown도 증명된 narrowing으로 취급하지 않는다. |
| 비교 대상 | `policy_analysis.py:382–391`: priority100 생성 규칙만, tool마다 한 항목을 가정 | 일반적인 whole-policy 식과의 완전한 의미 일치는 미검증이다. generic priority1은 비교에서 제외된다. |
| 수동 확인 | `tool.py:457–461`: subset 검사 전에 모든 후보를 확인 | 확장만 사람이 검토하는 절차와 정확히 같은 CLI profile은 확인하지 못했다. |
| 정적 checker | 실제 구현은 `policy_type_check.py:79`. `tool.py:121`의 동명 함수는 `# check()` 상태 | 생성/갱신 경로에서 정적 checker가 항상 강제된다고 설명하지 않는다. |

위 표는 정적 관찰이며, 새로운 공격 실증이나 버그 판정이 아니다.

## 원본 Evaluation과 현재 준비의 관계

§8.1 Figure 3의 AgentDojo ASR39.9%→1.0%, Figure 4의 ASB70.3%→3.9%는 저자 보고이며 이번 관측값이 아니다. §8.2는 Disable Update/Auto-Deny/Auto-Approve/Manual Approval을 구분한다. 주 평가의 Auto-Approve 수치에서 모든 확장을 사람이 검증했다고 추론하지 않는다. §8.3의 MCP 기반 단일/다중 agent 통합도 현재 로컬 AgentDojo 환경과 별도로 준비해야 한다.

현재는 원본 Progent와 저자가 수정한 AgentDojo의 독립 환경이다. 모델 호출·전체 평가·ASB/MCP 실험은 미실행이다. `agentdojo/run.sh`는 정상/공격 ×4 suites를 8개 background jobs로 실행하므로 첫 실습에 사용하지 않는다.

Workspace `UserTask13`의 정의는 `default_suites/v1/workspace/user_tasks.py:1403`과 `v1_1_2/workspace/user_tasks.py:65`, 원본 이메일은 `data/suites/workspace/include/inbox.yaml:356`에 있다. 제목은 TODOs for the week지만 sender는 David, 내용은 문서 추기와 feedback score 이메일 발송이다. Figure 1의 Alice/Slack과 같은 task라고 부르지 않는다. `search_emails`의 실제 인자도 `query,sender`로 그림의 `subject,sender`와 다르다.

점수는 `TaskSuite._check_user_task_utility`와 `_check_injection_task_security`가 state와 trace를 평가한다. 원본 `agentdojo/README.md:18`은 Slack injection5에서 차단된 호출도 trace에 남아 오판정하는 문제를 설명한다. 따라서 Allow/Deny, trace의 존재, 실제 tool effect, task utility/ASR을 따로 확인한다.

## 첫 번째 단일 실습

| 실행 전에 이해할 항목 | 이번 내용 |
|---|---|
| 현재 학습 주제 | policy correctness 중 타입과 제약 keyword의 정합성 |
| 목적 | 결정론적으로 집행할 policy 자체의 설정을 확인한다. 타입 경고·runtime Deny·tool effect를 구분한다. |
| 원본 근거 | §4.1/Figure 2의 인자 조건, §7의 JSON Schema 구현. 직접 실행하는 것은 공식 `secagent/policy_type_check.py:101`의 demo다. §6 정리나 ASR의 재현은 아니다. |
| 실행 구조 | Python + jsonschema + 원본 checker. LLM agent/tool/benchmark/SMT update는 실행하지 않는다. |
| 내부 순서 | module import → __main__의 literal policy와 tool schema → `security_policy_type_check` → JSON Schema schema 검사와 독자적인 keyword/type 검사 → warning list 출력 |
| 관찰 대상 | integer에 pattern을 지정한 규칙의 warning과 exit code. import 때 model 이름이 출력되었다는 사실만으로 API 호출이라고 해석하지 않는다. |
| 범위 | 공식 Repository Demo의 정적 컴포넌트 실습. Figure 1 실행 재현이나 LLM attack 재현이 아니다. |

원본 demo의 두 번째 recipient 조건은 `type: integer`와 문자열용 `pattern`의 조합이다. 전날 안내에서 의도적인 사례라고 기술했지만, **저자 의도를 뒷받침하는 설명은 확인하지 못했다**. 확인한 것은 코드와 warning 생성 경로다. 또한 이 조합을 JSON Schema 문법 오류로 단정하지 않는다. 해당 checker의 type-specific keyword 경고다.

실행 명령은 아래 하나다. 아직 실행하지 않았으며 사용자가 직접 실행한다.

```bash
cd /home/cclab/controllable_agent
PYTHONDONTWRITEBYTECODE=1 SECAGENT_GENERATE=False SECAGENT_UPDATE=False \
  local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python \
  -m secagent.policy_type_check
```

코드에서 예상한 값이며 관측 로그는 아니다.

```text
Policy Warning at send_money.recipient: 'pattern' is not allowed for type integer.
```

warning을 출력하고 정상 반환하므로 exit0과 양립한다. tool 실행을 거부했다는 증거가 아니다. policy와 사용자 의도의 일치, monotonic confinement, over-privilege 전반을 검증하는 실습도 아니다.

사용자의 실제 출력을 받은 뒤 실행 시각·정확한 명령·stdout/stderr·해석을 별도의 새 기록에 추가한다. 현재 실행 결과는 **NOT_RUN**이다. 다음은 결과 해석이며, 그 후 Algorithm 2의 실제 허용/거부와 tool effect로 진행한다. 자체 adapter보다 공식 컴포넌트와 원본 evaluation의 차이부터 이해한다.

## 후속 사용자 실행 보고

사용자가 원본 checker를 실행해 예상한 경고 한 건을 전달했다. 실행 전 NOT_RUN 기록은 보존하고, 실제 전달 출력·출처·해석·미확인 범위를 [별도 결과 기록](progent_study_01_result_20261118.md)에 추가했다. [다음 정상 요청 실습](progent_study_02_enforcement_20261118.md)은 아직 미실행이다.
