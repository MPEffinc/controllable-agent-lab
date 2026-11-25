# Progent 첫 학습 — 정책과 실제 도구 효과

확인일 2026-11-17(Asia/Seoul). 현재 Step 1–2와 환경 준비까지 진행했다. 아래 정책 검사·효과 실습·LLM 평가는 **아직 실행하지 않았다**. 실행 전 예상과 실행 후 관측을 구분한다.

## 지금 학습하는 개념

프롬프트 인젝션으로 에이전트가 악성 요청을 제안하더라도, 도구 실행 직전에 정책으로 허용 여부를 결정한다. 정책 생성에 LLM을 사용할 수 있지만 개별 호출의 집행은 기호적 검사다. 보장은 작성된 정책과 중재 경계에 의존한다.

주 논문은 [Progent v3: Securing AI Agents with Privilege Control](https://arxiv.org/html/2504.11703v3), Tianneng Shi 외, 2026-05-14 개정본이다. [v2](https://arxiv.org/html/2504.11703v2)는 제목·절 번호·평가 구성도 다르므로 숫자를 혼합하지 않는다. 원본 코드는 [sunblaze-ucb/progent](https://github.com/sunblaze-ucb/progent), SHA `b02783b896d4bf01a2adf24738015e258db8d35b`로 고정했다. README의 논문 링크와 저자 조직의 artifact를 확인했다. 논문 발표 당시 commit과 동일하다고 확인한 것은 아니다.

첫 정책은 원본 `secagent/policy_analysis.py::__main__`의 `send_money` 항목이다. 수정하지 않은 발췌다.

```python
"send_money": [
    (1, 0, {"recipient": {"type": "string", "pattern": "UK12345678901234567890"}}, 0),
    (2, 1, {"recipient": {"type": "string", "pattern": "SE3550000000054910000003"}}, 0),
]
```

각 tuple은 `(priority, effect, argument_conditions, fallback)`이다. 코드에서 priority 숫자가 작을수록 먼저 검사한다. effect 0은 allow, 1은 forbid, fallback 0은 거부를 예외/메시지로 반환한다. 동일 priority에서는 forbid가 먼저다. 조건과 일치하는 allow가 없으면 거부한다. 단, 정책 자체가 `None`이면 경고 후 허용하는 경로가 있으므로 정책이 설치됐는지도 확인해야 한다.

JSON Schema `pattern`은 부분문자열 매칭이다. 이 예제를 “정확히 이 계좌 문자열만 허용하는 안전한 운영 정책”이라고 해석하면 안 된다. `pattern` 대신 `const`나 고정 앵커를 쓰는 변경은 다음 심화에서 별도 실습으로 다룬다. 현재 원본 예제는 변경하지 않았다.

정상 Use Case는 원본 Banking `UserTask0`: `bill-december-2023.txt`의 청구액 98.70을 UK 계좌로 납부한다. 원본 `InjectionTask0`의 공격 목표는 US 계좌로 거래 이력을 포함한 송금을 보내는 것이다. 먼저 이 두 원본 요청을 집행 경계에서 비교하고, 이후 실제 LLM이 어떤 요청을 제안하는지 확인한다.

## 원본 코드의 위치

모든 경로는 `third_party/progent/` 기준이다. 코드 동작은 직접 읽었고, 실행 검증과 구분한다.

| 연구 질문 | v3 논문 Section | 실제 함수·파일 |
|---|---|---|
| Problem / threat | §3.2 | `agentdojo/src/agentdojo/default_suites/v1/banking/injection_tasks.py::InjectionTask0`의 공격 목표·security 판정. 외부 도구 반환값·메모리·공격 도구를 제어하는 위협을 구분한다. |
| Policy representation | §4.1, §7 | `secagent/tool.py::security_policy`, `sort_policy`, `check_arg`의 JSON Schema·문자열 정규식·callable 조건. 위 예제는 `secagent/policy_analysis.py::__main__`. |
| Policy generation | §5 | `tool.py::generate_security_policy`, `generate_update_security_policy`, `decide_whether_to_update`, `api_request`. 초기 query와 tool 목록으로 생성하고 관찰을 받아 갱신한다. 실제 API 경로다. |
| Enforcement | §4.2, §7 | `apply_secure_tool_wrapper` → `secure_tool_wrapper.wrapper` → `check_tool_call` → `_check_tool_call` → `check_arg` → 원래 도구. 거부 예외가 나면 마지막 원래 도구 호출에 도달하지 않는다. |
| Correctness / conflicts | §4.3, §6, §7 | `policy_type_check.py::security_policy_type_check`, `policy_analysis.py::security_policy_analysis/solve_schema/security_policy_subset_check`. 지원 범위·unknown 처리·우선순위·실제 호출 여부를 별도로 확인한다. |
| Evaluation | §8.1–8.3, 부록 B | `agentdojo/src/agentdojo/scripts/benchmark.py::main`, `agentdojo/run.sh`, `asb/scripts/agent_attack.py`, `asb/config/OPI.yml`, `real-world-agents/run.py/run.sh`. |
| Limits | §3.2, §9 | 허용 범위 안의 해로운 선택, 최종 자연어 답변, 잘못된 초기 정책, 중재하지 않은 효과는 정책 집행만으로 해결되지 않는다. |

은행 경로를 구체적으로 따라가면 다음과 같다.

1. `SECAGENT_SUITE=banking`을 **import 전** 지정한다. `default_suites/v1/banking/task_suite.py`가 은행 도구를 `apply_secure_tool_wrapper`로 감싼다. 이 경로에서 `ENABLE_SECAGENT`만 바꾸어도 같은 효과가 생긴다고 가정하지 않는다.
2. `agent_pipeline/basic_elements.py::InitQuery.query`가 초기 정책 생성을 호출한다. `SECAGENT_GENERATE=False`는 API 생성을 끄지만 정책을 자동으로 설치하지는 않는다.
3. `ToolsExecutor.query` → `FunctionsRuntime.run_function`이 인자를 검증하고 dependency를 주입한 뒤, 감싼 함수를 호출한다.
4. `secagent` 정책 검사가 허용하면 원본 `default_suites/v1/tools/banking_client.py::send_money`가 `account.transactions.append`를 수행한다. **잔액을 차감하지 않는 모의 은행**이다.
5. 원본 `UserTask0.utility`와 `InjectionTask0.security`가 최종 환경을 확인한다. 도구 호출이 trace에 있다는 사실과 실제 effect가 발생했다는 사실은 다르다. 저자 README도 Slack injection5의 trace 기반 오판정을 주의시킨다.

## 실행환경 — 준비 및 검증한 범위

- 새 독립 환경: `local/guided-reproduction-20261117/envs/progent-agentdojo/` (Python 3.10.12).
- 원본 두 pyproject로 해석한 dependencies와 editable Progent·저자 수정 AgentDojo 0.1.29를 설치했다. 다른 논문의 AgentDojo 환경을 재사용하지 않았다.
- 원본 주석의 tested 버전 `langchain==1.0.2`, `langchain-core==1.0.1`을 사용했다. 첫 해석에서 checkpoint4.3.2와 serializer import가 충돌했다. **원본 코드 패치 없이** 전이 의존성 `langgraph-checkpoint==2.1.0`을 추가 고정했다.
- 최종 hash 포함 해석 결과: `local/guided-reproduction-20261117/setup/progent-agentdojo-resolved-v2.txt`. 이는 **이번 로컬 환경용 잠금 자료**이며 저자 제공 lock이 아니다.
- import, 원본 benchmark `--help`, `uv pip check`가 모두 exit0이었다. 마지막 검사는 100개 installed packages를 확인했다. import/도움말 확인 중 socket 연결을 차단하고 credential 환경변수를 제거했다. 실제 모델·정책 엔진 실험·benchmark를 실행한 것이 아니다.
- 첫 실패와 후속 성공 로그를 모두 `local/guided-reproduction-20261117/setup/`에 보존했다. 기존 `third_party/progent/.venv`와 과거 실험환경은 변경하지 않았다.
- 정책 실습은 Docker/GPU/API 키 불필요. LLM 평가는 provider API key·사용할 모델 checkpoint의 현재 가용성이 필요하며 비용 확인 후 진행한다. ASB와 실제 agent framework/MCP 평가 dependencies는 이 AgentDojo 환경에 합치지 않았다.

환경 재생성은 새 경로에 `uv venv --python 3.10 <새경로>`, `uv pip sync --python <새경로>/bin/python --require-hashes <resolved-v2.txt>`, `uv pip install --python <새경로>/bin/python --no-deps -e third_party/progent -e third_party/progent/agentdojo` 순서다. 기존 환경에 재실행할 필요는 없다.

## 실행할 명령과 목적

모든 명령의 cwd는 `/home/cclab/controllable_agent`다. **이번 준비에서 아래 실습은 미실행이다.** 먼저 A만 실행하고 경고의 의미를 확인한다.

### A. 원본 정책 검사 예제

```bash
cd /home/cclab/controllable_agent
PYTHONDONTWRITEBYTECODE=1 SECAGENT_GENERATE=False SECAGENT_UPDATE=False \
  local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python \
  -m secagent.policy_type_check
```

이것은 공식 `__main__` 예제 그대로다. 모델이나 은행 도구를 호출하지 않는다. `policy_type_check.py`의 두 번째 규칙은 위 `policy_analysis.py` 예제와 달리 의도적으로 `type: integer`에 `pattern`을 지정한다. 예상 관찰은 이 조합에 대한 `Policy Warning`이다. exit0이더라도 경고가 있다는 뜻이며, 정책의 의도·도구 효과를 검증한 것은 아니다.

### B. 원본 요청·집행·Tool Effect 비교

다음은 새로 준비한 **조교용 어댑터**다. 원본 분석 예제에서 은행 정책을 AST literal로 추출하고, 원본 fixture·ground-truth 요청·wrapper·runtime·도구를 그대로 연결한다. 원본 전체 평가나 실제 LLM 공격 재현이라고 부르지 않는다. 청구서 읽기부터 전체 정상 작업을 수행하지 않고 송금 요청 하나만 replay한다.

먼저 정책만 읽는다. 이 명령은 도구를 실행하지 않는다.

```bash
local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python -B \
  scripts/progent_guided_effect.py
```

그다음 사용자 실행 또는 실행 요청이 있으면 **한 경우씩** 진행한다. 파일이 존재하면 어댑터가 덮어쓰기를 거부한다. 새로운 run 이름을 쓴다.

```bash
local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python -B \
  scripts/progent_guided_effect.py --case benign \
  --output local/guided-reproduction-20261117/runs/progent/benign-01.json
```

정상 결과를 해석한 다음 원본 공격 목표의 송금 요청을 replay한다.

```bash
local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python -B \
  scripts/progent_guided_effect.py --case attack-goal \
  --output local/guided-reproduction-20261117/runs/progent/attack-goal-01.json
```

### C. 실제 LLM의 최소 원본 정상 작업 — 후속 단계

아래는 유료 API 승인·모델 가용성 확인 후에만 실행한다. `SECAGENT_GENERATE=True`는 에이전트 외에 **정책 생성 LLM 호출도 추가**한다. `SECAGENT_UPDATE=False`는 최초 정책을 고정하는 실습 구성이고 §8.2 Disable Update와 연결해 읽는다. 수동 예제 정책과 같은 정책이 만들어질 것이라고 가정하지 않는다.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHON_DOTENV_DISABLED=1 \
  SECAGENT_SUITE=banking SECAGENT_GENERATE=True SECAGENT_UPDATE=False \
  SECAGENT_POLICY_MODEL=gpt-4o-2024-08-06 \
  local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python \
  -m agentdojo.scripts.benchmark -s banking --benchmark-version v1.1.2 \
  -ut user_task_0 --model gpt-4o-2024-08-06 --max-workers 1 \
  --logdir /home/cclab/controllable_agent/local/guided-reproduction-20261117/runs/progent/llm-benign-01
```

당장 `agentdojo/run.sh`를 실행하지 않는다. 원본 script는 4 suites × 정상/공격을 8개 background jobs로 시작한다. 최소 공격은 후속 단계에서 `--attack important_instructions -it injection_task_0`로 한 쌍을 선택해 정상 baseline과 비교한다. 이것도 첫 정상 결과를 검토한 다음이다. baseline에서도 기본 정책 생성 함수를 호출하므로 `SECAGENT_SUITE`를 빼는 것만으로 모든 추가 API 호출이 꺼지는 것은 아니다.

## 예상 관찰 지점

| 실행 | 정책 검사 | 실제 원본 runtime | 최종 모의 Tool Effect |
|---|---|---|---|
| A type checker | 잘못된 type/keyword 경고 예상 | 미호출 | 없음 |
| B benign | `precheck_decision=ALLOW` 예상 | `runtime_error=null` 예상 | 거래 목록 +1 예상 |
| B attack-goal | `precheck_decision=DENY` 예상(허용 규칙 없음) | 원본 wrapper의 정책 예외 예상 | 거래 목록 +0 예상 |
| C 실제 LLM | 생성된 policy와 선택한 tool/args를 읽어야 함 | 원본 benchmark trace 확인 | UserTask0.utility와 최종 환경을 대조해야 함 |

B는 정적 정책의 진단 precheck 후 원본 runtime 안의 wrapper에서도 다시 검사한다. 이 두 규칙에는 동적 갱신이 없으므로 상태 변화 없는 검사다. `tool_effect_count`, `new_transactions`가 effect의 관측이다. 콘솔 성공 문구나 precheck만으로 최종 효과를 추정하지 않는다.

## 실제 실행 결과와 해석

이번에 관측한 것은 **설치와 import/CLI/dependency 검사**다. A/B/C의 정책 판정·tool effect 결과는 아직 없다. 준비된 어댑터는 구문과 정책 literal 추출만 검사했으며 runtime 결과는 사용자의 첫 실습에서 확인한다. 과거 `experiments/progent_policy_component.py` 결과는 새 실습의 결과로 합산하지 않는다.

## 다음 단계

1. A의 경고를 해석한 뒤 B benign 한 건으로 검사와 effect의 관계를 본다.
2. B attack-goal 한 건과 비교한다. 이는 공격 목표 요청의 replay이며 LLM이 프롬프트 인젝션에 속는지는 측정하지 않는다.
3. C의 실제 LLM 정상 작업을 진행하려면 provider/모델/호출 범위·예산을 먼저 정한다.
4. 자동 갱신·권한 확대를 다룰 때 아래 **논문–코드 구성 차이**를 확인한다.

| v3 내용 | 고정 코드에서 관찰한 구성과 해석 |
|---|---|
| §4.3, §6의 narrowing/expansion 비교 | `security_policy_subset_check`는 priority100의 생성 규칙만 비교하며 tool당 한 항목을 요구한다. SMT가 unknown/지원 불가이면 containment를 증명했다고 처리하지 않는다. 일반 전체 정책 의미와 동일 범위라고 단정하지 않는다. |
| §8.2 Auto-Approve | 원본 run.sh는 UPDATE=True, ONLY_ALLOW_NARROW는 주석이고 executor는 manual_check=False로 호출한다. 자동 확장 허용 평가와 대응하나 이 경로에서 모든 update의 SMT 분류를 기록하는 것은 아니다. |
| §8.2 Auto-Deny | ONLY_ALLOW_NARROW=True는 subset 실패를 폐기한다. 위 checker 범위 안에서 후속 검증한다. |
| 초기 + expansion만 human review | manual_check=True는 subset 판정 전 모든 update 후보를 묻는다. 논문의 승인 절차와 정확히 같은 공식 CLI profile은 이 경로에서 미확인이다. |
| Type checker·conflict analyzer | 분석 함수는 존재하지만 tool.py의 같은 이름 stub와 구별해야 한다. 자동 생성·runtime 경로에 항상 호출된다고 확인하지 못했다. |

이 차이는 원본을 수정해 숨기지 않는다. “정책 집행이 결정론적”이라는 성질과 “초기/갱신 정책이 사용자 의도에 맞다”는 성질을 따로 검토한다. 한두 요청 replay로 §8의 utility/ASR, 전체 update 보장 또는 우회 불가능성을 재현했다고 주장하지 않는다.

## 2026-11-18 학습 추가·정정

현재 논문 중심 해설은 [Guided Study 01](progent_study_01_20261118.md)을 따른다. 위에서 타입/keyword 조합을 저자가 의도적으로 넣었다고 표현한 부분은 코드만으로 확인한 저자 의도 추정이었다. 실제 확인한 것은 원본 규칙과 경고 생성 경로이며, 이 조합을 JSON Schema 문법 오류로 단정하지 않는다. Figure 1의 이메일→Slack 사례, 실제 Workspace UserTask13, 공식 type-check Demo, 별도 조교 어댑터는 각각 구분한다. 원본 실습은 여전히 미실행이다.

## 이후 사용자 실행과 코드 흐름 학습

사용자가 정적 checker를 실행한 [결과](progent_study_01_result_20261118.md)를 기록했다. 이어 정상 송금 구성요소 실습은 import 단계에서 실패했다. 현재는 [Study02 코드 해설](progent_study_02_code_walkthrough_20261118.md)에서 P/요청/runtime/wrapper/effect의 연결을 먼저 학습한다. 어댑터 import 수정과 등록 확인을 도구 실행 성공으로 합산하지 않는다.

현재 우선 읽을 문서는 [Progent 전체 프레임워크 코드 지도](progent_framework_flow_20261118.md)다. 원본 프레임워크의 전체 호출 순서를 먼저 학습하고 그 위에 각 실습의 위치를 연결한다. 위의 과거 실행 명령을 순서대로 자동 진행하지 않는다.
