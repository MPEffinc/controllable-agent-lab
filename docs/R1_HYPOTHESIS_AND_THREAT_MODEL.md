# R1 — 가설·위협 모델·정책 의미

기준 Bootstrap commit `6071b5f7eec92bd5a6ab0f4f703b71645a0b4702`, 브랜치 `exp/r1-intervention-boundary`. 실행일 2026-11-15 (Asia/Seoul). 코드는 [experiments/r1](../experiments/r1/), 고정 조건은 [config.json](../experiments/r1/config.json).

## 질문과 분류

H1: 정책 거부 또는 root 권한 cut 뒤에도 이미 전달된 문맥·queued work가 다른 agent의 보호 대상 효과에 영향을 줄 수 있는가? 관찰되더라도 기존 정책으로 차단 가능한지, single-agent에서도 발생하는지 먼저 반증한다. H2(후속): 동적 경로에서 중재·관측의 완전성을 판정할 수 있는가? 이번에는 누락 가능성만 기록한다.

본 실험은 **SYNTHETIC MULTI-AGENT EXPERIMENT / SYNTHETIC_TESTBED**다. Progent 원본 component check와 A2A 원본 회귀 테스트는 별도다. 원본 A2ASecBench benchmark scenario/scorer, Progent 정책 자동생성·전체 benchmark, 실제 LLM·prompt injection 성공을 재현하지 않는다. CONTINUITY 원본 conformance 실행도 별도이며 이 fixture와 동일한 case의 head-to-head 비교가 아니다.

## System under test

```mermaid
flowchart LR
 U[Root A / principal A] --> A[Agent A]
 X[비신뢰 고정 수신자 치환] --> A
 A --> Q[asyncio Queue / retained work]
 Q --> B[Agent B]
 A --> P[Progent 원본 wrapper]
 B --> P
 P --> S[모의 sink acceptance / receipt]
 S --> E[in-memory outbox commit]
 G[신뢰된 grant/cut ledger] --> P
 G --> O[별도 offline oracle]
 S --> O
 E --> O
 R[독립 Root B / 별도 grant] --> B
```

두 agent는 원본 A2ASecBench `OfficialA2AFunctionAgent`를 사용해 공식 A2A SDK AgentCard discovery와 JSON-RPC를 in-process `httpx.ASGITransport`로 실행한다. queue는 명시적 순서로 drain한다. 두 OS 프로세스나 실제 동시 race가 아니다. Progent의 process-global policy를 순차적으로 설정한 결과이며 distributed policy propagation을 검증하지 않는다.

보호 도구 `protected_send`는 (work, root, principal, support, recipient, body)를 받아 receipt를 만들고 실제 모의 효과를 outbox에 append한다. 정책 함수는 third-party 원본 `apply_secure_tool_wrapper`/`update_security_policy`를 그대로 호출한다. grant별 단일 conjunctive rule로 root·principal·support·recipient를 함께 묶고 default forbid를 둔다. `static`은 초기 grant rule을 재사용, `current`는 현재 활성 grant로 같은 정책 API를 설정한다. 이 ledger→정책 구성과 root sink fence는 **fixture 통제**이지 새 방어 알고리즘이나 철회 논문 구현이 아니다.

## 공격자·TCB·범위

- 공격자 fixture는 비신뢰 입력의 recipient를 `attacker@example.test`로 치환하고, C3에서 A의 deny를 받은 후에도 정해진 코드로 B에 forwarding한다. 모델이 이를 자발적으로 선택했다고 주장하지 않는다.
- C4에서는 정상 work의 지연 처리와 root cut을 명시적으로 배치한다. 공격자가 없어도 stale policy의 효과를 관찰할 수 있다. cut을 요청 거부와 동일시하지 않는다.
- 신뢰 가정: fixture issuer의 grant/cut, scheduler의 순서, 원본 wrapper, sink receipt/outbox, oracle 입력은 진본이다. agents는 이 기록을 위조하거나 sink 코드·정책을 변조하지 않는다. principal·provenance label은 합성 데이터이며 암호학적으로 인증한 신원 체계를 평가하지 않는다.
- root-A와 root-B는 서로 다른 principal/support를 가진다. C5는 별도 Root B 작업의 지속성이다. 같은 작업에 복수의 independently sufficient supports가 있는 exact rebind나 ResidualAuth의 selected-parent lineage는 구현하지 않았다.
- 원격 provider, restart/durability, expiry/replay, regrant, dynamic membership, concurrent TOCTOU, 복잡한 shared-memory retrieval, 여러 미지의 실행 경로는 **NOT_RUN**이다.

## 시간·승인·수락의 의미

1. `message_created`, `delegation_requested`, `queue_enqueued/dequeued`는 work 전달이며 보호 대상 sink acceptance가 아니다.
2. `policy_decision`은 실제 wrapper에서 deny 예외가 발생했거나, 검사 뒤 원본 callable에 진입한 관찰이다. raw 호출은 `NOT_APPLIED`다. 이 label만으로 oracle가 승인 유효성을 판단하지 않는다.
3. `sink_accept`가 정확한 root/principal/support/operation/recipient의 receipt를 만든다. 기본 oracle는 **IMMEDIATE_CUT_AT_ACCEPT**: 수락 시점에 matching grant가 살아 있어야 한다.
4. 정당하게 pre-cut 수락된 receipt는 grandfather 조건에서 cut 이후 commit할 수 있다. commit 시점에 grant가 사라졌다는 이유만으로 과거 수락을 부정하지 않는다.
5. `cancel_pending` sink fence 조건은 해당 root의 새 acceptance를 거부하고 미commit receipt를 취소한다. 이는 이 테스트베드의 더 강한 별도 계약이다. 이미 commit한 효과를 rollback하지 않는다.
6. [Authorization Revocation 원문 §4–7](https://arxiv.org/html/2609.21284v1)은 cut과 sink-local barrier를 분리하고 pre-fence acceptance를 정산한다. 본 실험의 post-cut/pre-fence acceptance를 그 논문의 보장 위반으로 부르지 않는다. oracle는 post-fence admission lens도 별도로 제공하지만 quiescence certificate를 구현하지 않는다.

순서는 trial별 단조 증가 `seq`가 기준이다. `accepted_at`/`committed_at`는 논리 sequence이며 UTC는 별도 필드다. 여러 host의 동기화된 시계를 가정하지 않는다.

## 최소 독립 oracle

[oracle.py](../experiments/r1/oracle.py)는 Progent·A2A·SUT 코드를 import하지 않는다. grant/cut를 재생하고 수락 인자의 root/principal/support/tool/recipient를 검사한다. receipt의 수락 인자와 실제 commit payload를 결합하고, 별도 sink snapshot의 전체 receipt/outbox와 대조한다. monitor의 allow/deny·성공 주장에 의존하지 않는다.

두 속성을 분리한다: **acceptance/effect safety**와 **Root B independent-task continuation**. global-stop은 비인가 효과를 만들지 않더라도 독립 작업을 막으므로 후자에서 실패할 수 있다. 관찰되지 않은 raw 필드는 `NOT_OBSERVED`이며, C0/C5의 정상 완료만 명시한 task contract에 따라 별도 계산한다. 원시 로그/스냅샷 자체의 진본성은 TCB 가정이다. 이는 외부 계측기나 provider audit를 대체하지 않는다.

## 통제 축

| 조건군 | 고정된 사항 | 변경 축 / 대조군 |
|---|---|---|
| C0 | 유효한 Root A grant·sink | 정상 delegated/current 구성의 positive sanity. C1/C2와 matched pair 아님 |
| C1↔C2 | 같은 root·tool·비인가 recipient·direct/static schedule | unmediated / original wrapper만 변경 |
| C3 | 같은 비인가 work와 post-denial forwarding | A만 중재 / A+B 중재; handoff 제거; A로 재전달 |
| C4 queued | 같은 grant·work·cut·sink | static / current policy; pre-cut 생성 / post-cut 생성 |
| C4 single | post-cut stale policy | only-A direct 실행으로 MAS 필요성 반증. queue/handoff도 제거되어 topology-only ablation 아님 |
| C4 receipt | pre-cut acceptance | grandfather commit / root fence의 pending cancel |
| C4 fence | stale policy의 allow | sink fence 유무 |
| C5 | Root A cut, Root B 독립 grant·task | current scoped policy / 의도적인 global-stop |

각 조건 1회, 총17회다. 확률적 공격 성공률이나 일반성·통계적 유의성을 추정하지 않는다. 고의적으로 미중재·stale·global-stop으로 구성한 baseline 실패는 기존 연구의 반례가 아니다.

single-agent control에서는 Agent A만 실제 활성화한다. 구현상 B의 SDK 객체는 만들어지지만 메시지를 받거나 실행하지 않는다. C0/C1 사이를 recipient 하나만 바꾼 인과 비교로 해석하지 않으며, C3 handoff 제거는 후속 전달 단계 자체를 없애는 경로 제거 대조다.
