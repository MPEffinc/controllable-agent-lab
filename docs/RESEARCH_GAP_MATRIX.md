# R1 Research Gap Matrix

2026-11-15 (Asia/Seoul). 목적은 기존 방법의 보장과 **관찰한 조건**을 분리하는 것이다. `NOT_RUN`은 그 방법의 해당 시나리오를 실행하지 않았다는 뜻이며, `UNKNOWN`은 명시적 원본 평가 범위를 확인하지 못했다는 뜻이다. 미실행 조건을 `NOT_SUPPORTED`, `VULNERABLE`, `GAP`으로 채우지 않는다.

## 기존 D1–D6 분류 보존

[기존 Related Works](https://docs.google.com/spreadsheets/d/1abFjTBcpDAYTZFAVOTUtYH28jKw3xhKg6JCjCGX5Tjg/edit#gid=2045979736)의 정의를 읽기 전용으로 확인했다. [범위·행 기록](../results/r1/taxonomy-source.json). SoK 자체의 D1–D4 번호와 합치지 않는다.

| 기존 분류 | 의미 | 이번 관계 |
|---|---|---|
| D1 | 입력 모델 수준 방어 | LLM/탐지율 검증 NOT_RUN |
| D2 | 정보흐름 및 신뢰경계 보호 | retained work의 출처를 기록했지만 full IFC/retrieval 검증 NOT_RUN |
| D3 | 도구 호출 인가 및 최소 권한 통제 | Progent 원본 wrapper component와 현재/static rule 비교 |
| D4 | 계획 및 동적 실행 흐름 검증 | cut/accept/commit 순서·state freshness 대조 |
| D5 | Multi-Agent 통신/위임/신원 보호 | 공식 A2A local handoff, principal/root 기록. 신원 암호 검증 NOT_RUN |
| D6 | 실행환경 격리 및 실제 자원 접근제어 | in-memory sink, OS sandbox 보장 검증 NOT_RUN |

## 조건 축 — 공격·경계·구성·속성

R의 이름은 본 실험의 설명용 security property이며 새 SoK risk 번호를 만들지 않는다. A는 합성 adversary 위치를 뜻한다.

| 문제 축 | Attack Mechanism | SoK A / I / R | System Configuration | Security Property | Our Validation / Failure Classification |
|---|---|---|---|---|---|
| 직접 tool 실행 | 고정 recipient substitution | 외부 입력 / I4 / 비인가 효과 | single-agent, wrapper OFF/ON | 정확한 root/principal/grant/destination 승인 | C1 효과, C2 차단. deliberate unmediated baseline |
| 위임된 tool 실행 | deny 이후 scripted forwarding | member-agent continuation / I2,I4,I6 / 비인가 효과 | A→queue→B, A-only/all mediation | 모든 실제 sink 진입 경계의 동일 정책 적용 | C3 A-only 효과, all mediation 차단. complete-mediation assumption failure |
| 개입 이후 상태 재사용 | retained work + stale grant snapshot | 실행 상태 / I3,I4,I6 / 현재 승인 상실 | static/current policy, 같은 work | 수락 시 현재 승인. single-agent 대조 | C4 stale 효과, current 차단; single-agent도 효과. policy/scope mismatch |
| 철회 이후 비동기 실행 | delayed dispatch/acceptance | scheduler/queue / I3,I4,I6 / cut·fence 의미 | 생성/queue/수락/commit 순서를 고정 | immediate-cut acceptance와 grandfather/cancel-pending을 분리 | C4 관찰. fence-paper 반례 아님; deterministic schedule only |
| 독립 작업 정상 지속 | global-stop으로 collateral denial | intervention control / I4,I6 / 정상 작업 과잉 차단 | 독립 Root B grant, Root A cut | root별 정상 continuation 보존 | C5 current는 완료, global-stop은 차단. deliberate overblocking |
| 동적 경로 완전성 | 누락될 수 있는 effect path | infrastructure/member / I2,I3,I4,I6 / 미중재 효과 | 알려진 두 callable 경로만 | 모든 정책 대상 효과 사전 중재와 진본 관측 | H2 NOT_RUN. known-path 누락 탐지는 보였지만 discovery/증명 아님 |

## 기존 방법·보장·원본 평가와 우리 검증

아래 문헌의 버전·절·직접 링크는 [권한 상태 노트](r1_prior_authorization.md), [상태·경계 노트](r1_prior_state.md)에 있다. 분류 태그는 기존 D1–D6의 범위 표시이며 원문의 새 분류로 제시하지 않는다.

| Existing Method / mechanism | D | Assumptions / Original Guarantee | Original Evaluation Coverage | Our Validation | Failure Classification / Follow-up Question |
|---|---|---|---|---|---|
| [FORGE](https://arxiv.org/html/2602.16708v4#S4.SS4): event graph + Datalog pre-action monitor | D2/D3/D4 | faithful events/identity, complete mediation, 올바른 deployed policy | 여러 agent/tool benchmark; R1 root cut/fence matched 평가 UNKNOWN | source audit; engine R1 NOT_RUN | R1 미중재 B는 가정 실패. 실제 executor가 queue/provider의 필요한 사실을 중재하는가? |
| [CONTINUITY](https://arxiv.org/html/2609.05269v1): witness/permit의 finality 검증 | D3/D4/D5 | 신뢰 issuer/verifier/sink, 완전 context·중재, atomic in-memory finality prototype | deterministic faults, delegated origin/revocation/alternate path | **원본 tests30 + quick 실행**. R1 A2A17조건 adapter NOT_RUN | 기존 해결과 직접 중첩. 원본 sink가 A2A retained work에서도 동일 조건을 중재하는가? |
| [Authorization Revocation](https://arxiv.org/html/2609.21284v1): root cut + local fence + exact accounting/rebind | D3/D4/D5 | durable linearization, manifest/channel 완전성, authenticated evidence | provider-free17-case, semantic mutations, pre-fence accounting·독립 지원 | NOT_RUN | cut 후 commit 자체 반례 아님. 원본 fence 의미를 유지한 실제 A2A/provider 통합은? |
| [ResidualAuth](https://arxiv.org/html/2609.08062v2): history-sufficient residual state / hard gate | D3/D4/D5 | 인증 사건·principal, 특정 selected-parent ledger family | paired authorization episodes와 memory/gate 구분 | NOT_RUN | 현재 두 root 단일 support fixture는 lineage sufficiency 재현 아님. 어떤 history가 필요한가? |
| [Governed Shared Memory](https://arxiv.org/html/2606.24535v1#S3.SS2): scoped retrieval·supersession·provenance | D2/D4/D5 | governance/scope/tenant 및 retrieval 경계 | live memory probes, GET-by-id 누락 수정·재측정 | NOT_RUN | 누락 경계 문제는 선행에서 다룸. memory 철회와 sink action 권한의 접점은? |
| [Progent](https://github.com/sunblaze-ucb/progent): programmable tool argument wrapper | D3 | 배치한 정책과 적용한 wrapper의 호출 범위 | 원본 AgentDojo/ASB 등의 논문 평가; R1 cut/fence UNKNOWN | 원본 component4 + synthetic17조건에서 원본 wrapper 재사용 | 정책은 주어진 static rule대로 동작. 현재 grant 반영으로 차단 가능; 신규 method gap 아님 |
| [Multi-CaMeL](https://arxiv.org/html/2610.05640v1#S4): trusted message/opaque variables + capability 보존 | D2/D5 | unique-parent hierarchical tree, instrumented protocol, policy S | AssetOpsBench/MultiAgentDojo; 실제 평가 trivial policy | NOT_RUN | async retained state/root revoke 직접 평가 UNKNOWN. tree CFI를 revocation 보장으로 확대하지 않음 |

기계 판독용 [RESEARCH_GAP_MATRIX.csv](RESEARCH_GAP_MATRIX.csv)는 방법×6조건 축별로 요청된10개 차원을 분리한다. 모든 방법을 같은 실험으로 실행했다는 뜻은 아니다.

## 좁혀진 연구 판단

**Observation:** 미중재 B와 stale policy에서 효과가 남고, 완전한 알려진 경계 적용·현재 권한 정책으로 차단됐다. broad stop은 독립 작업을 막았다. **Interpretation:** 현재 fixture의 실패는 이미 알려진 mediation/권한 신선성/철회 의미 문제로 설명된다. **Established Finding:** 이 구성의 조건 의존성은 재실행 가능한 증거가 있지만 기존 방법 전체의 미해결 gap은 확정하지 않았다. **Open Question:** 가장 가까운 원본 CONTINUITY artifact를 A2A 실행 경로에 연결했을 때 context·현재 정책·receipt binding을 완전히 중재할 수 있는가? 원본 quick 성공은 이 integration의 답이 아니다.
