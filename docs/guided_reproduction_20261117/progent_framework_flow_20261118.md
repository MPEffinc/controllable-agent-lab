# Progent 전체 프레임워크 코드 흐름 — 먼저 읽을 지도

2026-11-18, Asia/Seoul. 원본 SHA `b02783b896d4bf01a2adf24738015e258db8d35b`. 사용자 요청에 따라 개별 실행 명령보다 전체 구조와 원본 코드 읽기를 먼저 진행한다. 이번 추가 작업은 소스 읽기와 학습 자료 기록이며 모델·정책 요청·도구·benchmark를 새로 실행하지 않았다.

## 저장소를 역할별로 읽기

Progent는 기존 agent의 도구 호출 경로에 붙이는 보안 라이브러리와 proxy를 제공한다. 이 저장소에는 핵심 구현과 저자가 통합한 benchmark/agent 코드가 함께 들어 있다.

```text
third_party/progent/
├── secagent/                  # Progent의 핵심 구현과 통합 hook
│   ├── tool.py                # 정책 상태·생성·집행·갱신·SDK wrapper
│   ├── policy_analysis.py     # Z3 기반 subset/overlap 분석
│   ├── policy_type_check.py   # 별도 정적 검사 유틸리티
│   ├── role_analyzer.py       # 정규식→SMT 변환 등 지원 코드
│   └── progent_proxy.py       # LLM/MCP proxy와 middleware
├── agentdojo/                 # 저자 수정 AgentDojo agent·환경·평가
├── asb/                       # 별도의 ASB 실험
├── agentdojo-mcp/             # MCP로 노출하는 평가 도구·환경
└── real-world-agents/         # LangChain/OpenAI SDK/OpenHands/AutoGen 통합
```

논문상 다른 역할들이 실제로는 `secagent/tool.py` 한 파일에 많이 모여 있다. 별도 PolicyEngine class를 가정하지 않고 원본 함수와 공유 상태를 따라 읽는다.

## 두 LLM 역할과 네 가지 상태

| 구분 | 입력 | 출력·용도 |
|---|---|---|
| 업무 agent LLM | 사용자 요청·현재 대화·도구 목록 | 다음 tool call 또는 최종 답변 |
| policy LLM | 초기 요청·도구 정의, 갱신 시 관찰과 현재 생성 정책 | JSON 형태의 허용 tool·인자 제약 |

같은 모델 checkpoint를 양쪽에 사용할 수 있지만 prompt와 호출 역할은 다르다. 개별 tool call 허용/거부 검사에는 LLM을 호출하지 않는다.

| 상태 | 실제 위치 | 의미 |
|---|---|---|
| `available_tools` | `secagent/tool.py:28` | 정책 생성에 사용할 도구 이름·설명·인자 schema |
| `security_policy` | `secagent/tool.py:31` | 현재 집행하는 이름별 rule 목록 |
| `messages` | AgentDojo pipeline 인자 | system/user/assistant/tool 대화와 관찰 |
| `env` | AgentDojo TaskEnvironment | 모의 계좌·이메일 등 실제 평가 상태 |

`query()`는 pipeline component의 공통 method 이름이다. 모든 query가 모델을 호출하는 것은 아니다. `InitQuery`는 초기화를 하고, `ToolsExecutor`는 도구를 실행하며, `OpenAILLM.query`가 업무 모델 요청을 수행한다.

## 실제 AgentDojo 통합 경로의 순서

아래 경로는 `third_party/progent/` 기준이며, 추가 AgentDojo 방어를 선택하지 않은 `config.defense is None` 분기를 읽는다. Progent wrapper의 활성화는 별도 suite 설정으로 결정된다.

### 0. 도구를 등록하고 wrapper를 붙인다

`agentdojo/src/agentdojo/task_suite/load_suites.py`가 suite registry를 구성한다. `default_suites/v1/banking/task_suite.py:39–45`는 `SECAGENT_SUITE=banking`일 때 각 tool을 `apply_secure_tool_wrapper`로 감싸 등록한다. wrapper 생성 과정에서 도구 metadata가 `available_tools`에 수집된다. generic read-only allow 규칙도 이 경로에서 추가한다.

### 1. 원본 평가 entry가 agent pipeline과 환경을 준비한다

`agentdojo/src/agentdojo/scripts/benchmark.py:186 main` → `benchmark_suite:23` → `AgentPipeline.from_config:140`.

`benchmark.py`의 정상/공격 runner가 task를 선택하고 `TaskSuite.run_task_with_pipeline`을 호출한다. task suite는 fixture 환경과 `FunctionsRuntime`을 준비하고 사용자 prompt를 pipeline에 전달한다. 공격 모드는 tool-return에 들어갈 injection을 선택하는 별도 준비 경로를 가진다.

### 2. 초기 정책을 생성한다 — 논문 §5/Algorithm3 초기화

`agent_pipeline/basic_elements.py:14 InitQuery.query` → `secagent/tool.py:375 generate_security_policy(query)` → `api_request`.

함수는 global 도구 정의와 사용자 query로 policy prompt를 만들고 JSON을 추출한다. 생성 항목마다 `(100, 0, allowed_tool["args"], 0)` 규칙을 global `security_policy`에 추가한다. 반환되는 policy 객체를 pipeline이 받는 방식이 아니라 공유 정책 상태를 바꾸는 방식이다. priority100은 생성 규칙이며, generic priority1 등의 규칙과 구분된다.

### 3. 업무 LLM이 다음 행동을 제안한다

`agent_pipeline/llms/openai_llm.py:161 OpenAILLM.query` → `chat_completion_request:116` → model API.

입력은 messages와 runtime의 도구 정의다. 출력은 assistant message이며, 그 안의 tool call을 `FunctionCall(function, args, id)` 데이터로 바꾼다. 이 지점의 tool call 데이터만으로 도구가 실행된 것은 아니다.

### 4. 실제 호출 직전에 정책을 검사한다 — §4.2/Algorithm2

`ToolsExecutor.query` → `FunctionsRuntime.run_function` → 등록된 `secure_tool_wrapper` → `check_tool_call` → `_check_tool_call` → `check_arg`.

runtime이 일반 인자를 검사하고 env dependency를 주입한다. wrapper가 이름·인자를 현재 정책과 대조하고, 정상 반환한 경우에만 원본 tool 본문을 호출한다. 거부는 예외로 나타나며 runtime이 `(result, error)`로 바꿔 반환할 수 있다. policy=None일 때 경고 후 허용하는 경로가 있으므로 초기화와 wrapper 등록을 함께 확인해야 한다.

### 5. 결과 또는 거부 오류를 agent의 다음 관찰로 돌려준다

`ToolsExecutor.query`는 `ChatToolResultMessage`에 result/error를 담는다. `openai_llm.py:68–75`는 tool message의 `error or content`를 모델 입력으로 직렬화한다. 따라서 거부된 호출도 오류 관찰을 통해 대안 행동을 유도할 수 있다. 거부가 곧바로 task 종료를 뜻하지는 않는다.

### 6. 설정이 켜져 있으면 정책 갱신을 제안·적용한다 — §5/Algorithm3 갱신

`tool_execution.py:119–123`에서 호출 목록과 포맷된 결과를 모아 `generate_update_security_policy`로 보낸다.

1. `decide_whether_to_update:415`: tools/query/tool-call 정보로 필요성을 판단한다. 결과 본문은 이 prompt에 직접 넣지 않는다.
2. `generate_update_security_policy:435`: 결과와 현재 생성 정책도 포함해 후보를 생성한다.
3. `ONLY_ALLOW_NARROW=True`이면 `policy_analysis.py:381 security_policy_subset_check`를 호출한다. narrowing을 증명하지 못하면 후보를 폐기한다.
4. 적용 시 기존 priority100 규칙을 제거하고 후보를 추가하며 generic 규칙은 보존한다.

현재 원본 `run.sh`의 기본 프로필은 업데이트를 켜지만 `ONLY_ALLOW_NARROW`가 주석이고 executor는 `manual_check=False`로 호출한다. 이 프로필에서는 subset 검사를 건너뛴다. 논문의 승인/SMT 구조와 실제로 선택한 프로필을 따로 읽어야 한다. 비교기의 대상 범위도 생성 규칙으로 제한되어 있다.

### 7. 다음 agent turn 또는 종료·평가

`ToolsExecutionLoop.query`는 `[ToolsExecutor(), llm]` 순서로 반복한다. 첫 업무 LLM 호출은 loop 앞에 있고, loop 안에서는 도구 실행/갱신 뒤 LLM을 다시 호출한다. assistant에 더 이상 tool call이 없으면 반복을 끝낸다.

`TaskSuite`가 전후 env와 trace에 대해 utility/security scorer를 호출한다. 정책 허용, 실제 effect, 정상 task 성공, 공격 성공은 서로 다른 관찰이다. Progent 자체가 업무 정답 채점까지 수행하는 것은 아니다.

## 다른 agent 통합도 같은 core를 재사용한다

- LangChain: `tool.py:609 SecAgentLangchainMiddleware.awrap_tool_call`, 검사 뒤 handler 호출.
- OpenAI Agents SDK: `tool.py:635 openai_tool_wrapper`, 원본 tool invoke 직전 검사.
- MCP proxy: `progent_proxy.py:293 ToolCallFilterMiddleware.on_call_tool`, 원격 tool 전달 전 검사.

이 경로들은 별도 engine 세 개가 아니라 같은 `check_tool_call`과 정책 상태를 다른 framework의 실행 경계에 연결한 구현이다. 연결 방식과 세션 상태 등 구체적 보장은 해당 통합 경로에서 별도로 확인한다.

## 지금까지 실습을 이 지도에 놓기

| 실습 | 전체 코드 흐름에서의 위치 | 실제 결과 |
|---|---|---|
| 원본 type-check Demo | 별도의 정책 정적 검사 유틸리티 | 사용자 출력으로 keyword/type 경고 한 건 확인 |
| 조교 benign 어댑터 | P와 요청을 수동으로 고정하고 4단계의 검사→도구 효과를 보려던 구성 | import 단계 실패, 정책/효과 미측정 |
| 어댑터 import 수정 점검 | 0단계의 등록·wrapper 존재만 확인 | import-only exit0. 실습 전체 성공이 아님 |

실패 로그·빈 출력 파일은 보존했다. 새 실습 명령보다 이 전체 호출 순서와 함수별 입력·출력을 먼저 이해한다.

## 지도 순서

앞으로는 전체 흐름에서 현재 읽는 위치를 표시하고, 해당 함수의 입력·상태 변화·출력을 먼저 설명한다. 다음 코드 읽기는 초기 정책 생성의 `TOOLS + USER_QUERY → policy prompt → JSON 추출 → security_policy`이며, 이후 한 번의 실제 tool call과 결과 feedback, 마지막으로 정책 갱신 경계로 연결한다. 실험은 그 코드의 역할과 관찰할 상태가 정리된 뒤 한 가지 목표로 진행한다.

## 질의 기록 — wrapper의 원리와 원본 AgentDojo 수정 여부

사용자의 이해: AgentDojo가 모의 작업 환경과 agent loop를 제공하고, Progent는 실제 도구 실행 전에 도구 이름·인자를 현재 정책과 비교해 허용/거부한다. 현재 읽는 AgentDojo 통합 경로에 대해 맞는 이해다. LLM이 반환한 tool-call 요청 데이터와 실제 Python 도구 실행은 구분한다.

### 함수 본문을 고치는 것과 호출할 함수 객체를 등록하는 것

`banking/task_suite.py:41–44`에는 두 등록 경로가 있다.

```python
[make_function(tool) for tool in TOOLS]
[make_function(apply_secure_tool_wrapper(tool)) for tool in TOOLS]
```

첫 줄은 원래 함수 객체, 둘째 줄은 새 wrapper 함수 객체를 등록한다. `apply_secure_tool_wrapper`는 내부에서 `secure_tool_wrapper`를 호출한다. 원본 `send_money`의 본문을 다시 쓰거나 module 안의 모든 참조를 자동 교체하는 방식은 아니다.

`secure_tool_wrapper`는 원본 함수를 `tool`로 받아 안쪽에 `wrapper`를 정의하고 그 함수 객체를 반환한다. 안쪽 함수는 바깥의 `tool` 참조를 기억한다. 이것이 closure다. `@wraps(tool)`은 이름·docstring·annotation과 원본 참조 등의 metadata를 보존한다. 정책 검사 자체는 `check_tool_call` 호출에서 일어난다.

`make_function`은 `functions_runtime.py:129–136`에서 `name=function.__name__`, `run=function`을 저장한다. 따라서 도구 이름은 여전히 send_money이고 실제 실행 함수는 wrapper다. runtime이 그 이름을 찾으면 wrapper→정책 검사→원본 도구 순서로 호출된다.

### 저자의 통합 수정과 현재 로컬 원본 보존

Progent artifact에 포함된 AgentDojo에는 저자들의 통합 코드가 있다. 도구 등록 외에도 `InitQuery.query`의 정책 생성 hook과 `ToolsExecutor.query`의 정책 갱신 hook을 확인했다. 이들은 실제 소스에서 확인한 연결이며 upstream AgentDojo와의 전체 diff를 조사한 결과는 아니다. wrapper 부착에 원본 도구 본문이나 모델 가중치 변경이 필요한 것은 아니다.

우리가 보존하는 `third_party/progent`는 그 저자 artifact의 고정 버전이다. 이번 작업에서 이 원본 소스는 수정하지 않았다. 앞서 수정한 것은 별도 조교 어댑터의 import 순서다.

Progent에는 proxy 통합도 있다. `progent_proxy.py:293 ToolCallFilterMiddleware.on_call_tool`이 `check_tool_call` 뒤에 `call_next`로 실제 요청을 넘긴다. 이 방식에서는 도구 등록 코드를 직접 고치는 대신 MCP 연결을 proxy로 경유시킨다.

보장은 이 중재 경계를 통과하는 호출에 의존한다. wrapper 등록은 원본 함수를 어디서 직접 부르더라도 자동 차단하는 OS 격리를 만들지 않는다. 실제 실행 경로가 등록된 wrapper/proxy를 통과하는지가 검증 대상이다. 새 실행은 수행하지 않았다.
