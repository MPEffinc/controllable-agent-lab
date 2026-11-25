# Progent Study 01 — 사용자가 실행한 원본 정적 검사

기록일: 2026-11-18, Asia/Seoul. 근거는 사용자가 대화에 붙여 넣은 터미널 출력이다. 조교가 명령을 다시 실행한 결과가 아니다. 정확한 실행 시각과 exit code는 제공되지 않았다.

## 실행 명령과 실제 전달된 출력

cwd는 사용자 프롬프트 기준 `/home/cclab/controllable_agent`다. HTML 공백 표현과 셸 줄 연속 표기를 정리해 저장했다.

```bash
PYTHONDONTWRITEBYTECODE=1 SECAGENT_GENERATE=False SECAGENT_UPDATE=False \
  local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python \
  -m secagent.policy_type_check
```

```text
Policy Model: gpt-4o-2024-08-06
["Policy Warning at send_money.recipient: 'pattern' is not allowed for type integer."]
```

정규화한 명령·전달 출력·출처와 한계·hash는 `local/guided-reproduction-20261118/user-runs/progent-typecheck-01/`에 새로 보존했다. stdout/stderr는 사용자가 붙여 넣은 화면에서 분리되지 않았고, 모델 이름 출력이 stderr라는 점은 소스에서 확인했다. 분석 시점의 원본 HEAD는 `b02783b896d4bf01a2adf24738015e258db8d35b`, working tree는 clean이다. 사용자 실행 순간의 SHA를 별도 계측한 것은 아니다.

## 관찰과 코드 해석

| 관찰한 출력 | 소스에서 확인한 생성 경로 | 해석 |
|---|---|---|
| Policy Model | `secagent/tool.py:41–42`의 module-level print | 설정 모델 이름 출력이다. 이 Demo 실행 경로에는 LLM 요청 함수 호출이 없다. |
| 경고 목록 한 건 | `secagent/policy_type_check.py:101` → `security_policy_type_check:79` → `check_type_specific_keys:15` → `print:113` | `type: integer`에 문자열 제약인 `pattern`을 지정한 규칙을 독자적인 타입 검사기가 보고했다. |

원본 두 번째 규칙은 `policy_type_check.py:106`이다. effect=1은 forbid, priority=2, fallback=0이다. 이번에는 이 규칙을 **호출 인자에 적용한 것이 아니라 정책 자료구조로 검사**했다. 출력의 “not allowed”를 송금 거부로 읽지 않는다.

`validator.check_schema`의 오류 경고와 독자적인 keyword/type 경고는 코드에서 별도 경로다. 관찰한 메시지는 후자이며 JSON Schema 문법 오류라고 단정하지 않는다. 경고가 없더라도 정책과 사용자 의도의 일치가 증명되는 것은 아니다.

## 논문과 연결되는 범위

- §4.1/Figure 2의 인자 조건과 §7의 JSON Schema 구현을 이해하기 위한 **공식 Repository Demo**다.
- 관찰된 경고는 코드에서 예상한 것과 일치했다.
- 확인한 것: 이번 원본 예제에 포함된 타입/keyword 조합에 대한 경고 출력.
- 아직 확인하지 않은 것: Algorithm 2의 실제 Allow/Deny, 원본 tool effect, 정책 자동 생성/갱신, SMT subset 검사, Monotonic Confinement, 원본 평가 utility/ASR.
- 정확한 exit code는 미제공이다. 셸 프롬프트 복귀만으로 exit0을 기록하지 않았다.

이전 학습 노트의 NOT_RUN은 실행 전 상태를 보존한 기록이다. 이번 사용자 실행 보고는 그 이후의 별도 관찰로 추가한다. 기존 로그·원본 소스는 수정하지 않았다.

## 다음 단일 학습 목표

[Study 02](progent_study_02_enforcement_20261118.md)에서 정상 요청 한 건에 대해 **정책 허용 → 원본 wrapper 통과 → 실제 모의 거래 추가**를 구분한다. 다음 실습은 준비만 했으며 미실행이다. 공격 목표 요청과 정책 갱신은 아직 실행하지 않는다.
