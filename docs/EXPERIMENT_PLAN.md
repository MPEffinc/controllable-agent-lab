# 다음 원본 재현 절차 — 계획 상태 NOT_RUN

기준일 2026-11-15 (Asia/Seoul). 이번 작업은 감사와 GitHub 인계이며 새 실험·설치는 시작하지 않는다. 실행 성공, 설치 성공, 논문 재현 성공은 별도 상태다. 현재 완료된 실험은 A2ASecBench 원본 결정론적 ASRF offline 100 attack + 100 matched control뿐이다. 이것은 방어 OFF/ON 실험이나 LLM 공격 재현이 아니다.

## 다음 실행 가능한 한 가지 비교

**Progent 원본 wrapper의 recipient 제한 OFF/ON component check**를 먼저 검토한다. 격리 설치가 성공했고 외부 서비스가 필요 없다. 준비된 [experiments/progent_policy_component.py](../experiments/progent_policy_component.py)는 원본 `secagent.apply_secure_tool_wrapper`와 `update_security_policy`를 호출하고, 모의 도구의 in-memory outbox를 관찰한다. 새 정책 알고리즘은 구현하지 않았다. 실행 증거가 없으므로 현재 **NOT_RUN**이며, 예상 동작은 결과로 취급하지 않는다.

향후 별도 실행 작업에서:

```bash
python3 scripts/bootstrap_run.py --name progent-policy-first --cwd /home/cclab/controllable_agent --timeout 120 -- third_party/progent/.venv/bin/python experiments/progent_policy_component.py --output-dir results/setup/progent-policy-first
```

동일한 task와 수신자 대체 입력에 정책만 OFF/ON으로 바꾸고 benign/attack 2×2를 비교한다. action intent → wrapper 판정 → outbox commit → benign task success를 분리한다. 제약 schema는 고정 synthetic fixture다. 이 결과가 성공하더라도 **원본 라이브러리의 기능 확인**이며 LLM·MAS·논문 전체 재현은 아니다. 이 wrapper의 실제 실행 성공 전에는 ON/OFF 차이를 관찰했다고 보고하지 않는다.

후속 순서는 ORBIT 공식 v1.0.4 wheel 설치 timeout 해결 → 공식 두 agent smoke와 negative control → AgentDojo 원본 benign/attack + 원본 방어 preset 비교다. ORBIT negative control은 행동 없이 성공을 주장하는 scorer 대조군으로, 정책 ON/OFF와 다르다. AgentDojo provider 실험은 자격증명·호출 수·예산 승인이 먼저 필요하다. SASY/FORGE는 공식 구현이 확인됐지만 엔진과 toolchain이 미설치다. MultiAgentDojo는 공식 URL 검증 후 우선 추가한다.

## E1–E4 후보와 대조군

| 후보 | 비교할 보안 속성 / 경계 | 첫 후보 방법·환경 | 필요한 대조군 | 현재 상태 |
|---|---|---|---|---|
| E1 | root task와 현재 권한에 대한 action 정당화, I2/I4 | Progent 기능 확인 후 PAuth·AuthGraph·IntentCap 공식 구현과 비교 | single-agent, handoff 제거, static/revoked 권한 | NOT_RUN |
| E2 | agent 메시지·요약·공유 상태의 provenance 보존, I2/I3 | CaMeL/Multi-CaMeL, SASY/FORGE, MultiAgentDojo | tree/DAG, private/shared state, 상호작용 제거 | NOT_RUN |
| E3 | 정책 대상 effect가 실제 commit 전에 모두 중재되는가, I4/I6 | AgentDojo tool executor, SASY/FORGE, OpenShell | 직접/중첩 도구, queue 유무, sync/async | NOT_RUN |
| E4 | 구성원 변화·공동 결정에서 권한 보존, I1/I5 | ORBIT topology/hooks, A2A protocol 환경 | static/dynamic membership, 단일 결정자/집단 | NOT_RUN |

SoK의 A(공격자 위치), I(경계), R(위반 속성), C(구성), P(경로)는 별개 축이다. 공격 기법을 보안 결과나 인터페이스와 혼동하지 않는다. 이번 관찰의 R은 로컬 ASRF fixture에서 forbidden resource dereference가 기록된 것뿐이다. 기존 방법이 해결하는 사례를 미해결 gap으로 재명명하지 않는다.

## 측정·해석 규칙

- 최소 이벤트: trial/task/root principal, agent/delegation, provenance, action/args, policy/version/decision, effect commit, score, timestamp. 없는 필드는 `missing`으로 남기며 추론해서 채우지 않는다. A2A 원본에는 agent/event/action/monotonic time/scorer가 있으나 root principal·정책 버전·방어 판정은 없다.
- 한 번에 축 하나만 변경한다. same task+attack, single-agent 및 interaction-removed 대조 후 MAS 원인을 논한다. 독립적인 benchmark 수치를 바로 서로 비교하지 않는다.
- original reproduction / faithful reimplementation / conceptual toy / original component check를 구분한다. 현재 A2A는 원본 결정론적 harness 실행, Progent script는 미실행 original component check 준비본이다.
- in-scope 보장 위반 후보 / 보장 가정 실패 / scope extension / implementation bug / measurement issue를 분리한다. 관찰되지 않은 경로는 취약점 증거가 아니다.
- 원본 benchmark와 defense preset, scorer와 실제 효과를 함께 확인한 후에만 원본 실험 재현 완료를 판정한다. 현재 어떠한 논문도 전체 재현 완료로 표시하지 않는다.
