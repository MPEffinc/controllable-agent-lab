# Progent Study 02 — 정상 요청의 정책 허용과 실제 도구 효과

> 후속 상태: 사용자가 아래 계획을 실행했으나 import 단계에서 실패했다. [코드 흐름과 실패 해설](progent_study_02_code_walkthrough_20261118.md)을 먼저 읽는다. 아래 NOT_RUN과 명령은 실행 전 계획을 보존한 부분이며, 지금은 재실행하지 않는다. 어댑터의 등록 순서만 수정·검증했고 정책/도구 실습은 재실행하지 않았다.

상태: 준비, **NOT_RUN**. 첫 정적 검사 결과는 [Study 01 결과](progent_study_01_result_20261118.md)에 있다. 이번에는 정상 요청 한 건만 사용자가 실행한다.

## 실행 전에 이해할 내용

| 항목 | 이번 실습 |
|---|---|
| 현재 학습 주제 | Algorithm 2의 allow 경로와 실제 tool effect |
| 실습 목적 | 정책 검사의 정상 반환과 도구 본문 실행·상태 변화를 따로 관찰한다. |
| 원본 근거 | Progent v3 §4.2/Algorithm 2; 원본 `secagent/policy_analysis.py:460`의 정책 예제; 저자 수정 AgentDojo Banking `UserTask0.ground_truth`의 송금 요청 |
| 실행 구조 | 원본 Progent 정책 엔진, 원본 AgentDojo fixture/runtime/wrapper/send_money. LLM/model/외부 은행 서비스 없음 |
| 실행 과정 | 원본 정책 literal 추출 → 원본 fixture 로딩 → UserTask0의 send_money 요청 선택 → 정책 설치 → 진단 precheck → 원본 runtime 안의 wrapper 재검사 → 원본 도구 실행 → 거래 목록 변화 기록 |
| 관찰 대상 | `precheck_decision`, `runtime_error`, `tool_effect_count`, `new_transactions` |
| 실습 범위 | **학습용 어댑터로 연결한 원본 구성요소 실습**. 원본 전체 평가나 실제 LLM agent 실행이 아니며 정상 task utility를 채점하지 않는다. |

## 원본 정책·시나리오와 어댑터의 경계

`scripts/progent_guided_effect.py`는 조교가 만든 연결 코드다. 허용/거부 논리를 새로 구현하지 않고 원본 정책 검사와 실제 원본 tool을 호출한다. 이번 작업에서 이 어댑터를 새로 실행하지 않았다.

사용 정책은 `secagent/policy_analysis.py::__main__`의 `send_money` 항목을 AST literal로 읽는다. 방금 실행한 `policy_type_check.py` 예제를 수정하는 것이 아니다. 두 원본 파일의 두 번째 규칙은 각각 string/integer로 다르다.

정상 입력은 원본 `agentdojo/src/agentdojo/default_suites/v1/banking/user_tasks.py:16 UserTask0`의 `ground_truth`에서 가져온다. 수취인은 `UK12345678901234567890`, 금액은 98.70이다. 청구서를 읽는 단계부터 전체 task를 수행하지 않고 그중 송금 호출만 replay한다. 원본 수동 예제 정책이 사용되며, LLM이 생성한 task-specific 정책이 아니다.

원본 경로:

1. `banking/task_suite.py:44`가 도구를 `apply_secure_tool_wrapper`로 감싼다.
2. `FunctionsRuntime.run_function`이 인자를 검증하고 fixture의 계좌 객체를 주입한다.
3. `secagent/tool.py:757`의 `check_tool_call`이 허용해야 758행의 원본 tool 호출에 도달한다.
4. `banking_client.py:55 send_money`가 75행에서 `account.transactions.append`를 수행한다.
5. 어댑터가 호출 전후 transaction 수와 추가된 항목을 JSON으로 기록한다.

이 모의 tool은 잔액을 차감하지 않는다. 따라서 이번 effect는 잔액 변화가 아니라 거래 목록에 항목이 추가되는 것으로 정의한다.

진단 precheck와 wrapper 내부 검사로 정책 검사는 두 번 호출된다. 사용하는 원본 4-field 규칙에는 동적 갱신이 없으므로 이중 검사가 정책 상태를 바꾸지는 않는다. precheck만 통과하고 실제 tool은 오류가 날 수도 있으므로 최종 effect를 별도로 확인한다.

## 사용자 실행 명령 — 정상 요청 한 건만

기존 독립 환경을 재사용한다. 어댑터는 네트워크 연결을 차단하고 모델 생성·갱신을 끄며 원본 SHA·import 경로를 검사한다. 출력 파일이 존재하면 덮어쓰기를 거부한다. 기존 파일이 있으면 새 run 번호를 선택한다.

```bash
cd /home/cclab/controllable_agent
local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python -B \
  scripts/progent_guided_effect.py --case benign \
  --output local/guided-reproduction-20261117/runs/progent/benign-01.json
```

## 예상값 — 아직 실제 결과가 아님

| 필드 | 예상 | 해석 |
|---|---|---|
| `precheck_decision` | `ALLOW` | 진단 시점의 원본 정책 검사를 통과 |
| `runtime_error` | `null` | 실제 원본 runtime 호출이 오류 없이 반환 |
| `tool_effect_count` | `1` | 모의 거래 목록에 한 항목이 추가됨 |
| `new_transactions` | UK 수취인·98.7 한 건 | 실제 추가된 거래 내용. 98.7은 JSON 숫자 표시이며 98.70과 같은 값 |

이번에는 위 필드의 실제 관측 전까지 성공을 기록하지 않는다. 결과를 해석한 다음 별도 단계에서 원본 공격 목표 요청의 deny 경로를 관찰한다. 전체 평가나 Monotonic Confinement는 이 한 건으로 검증하지 않는다.
