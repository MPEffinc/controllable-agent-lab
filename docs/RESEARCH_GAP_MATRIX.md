# Research Gap Matrix (R1, R2 갱신)

**R2 갱신(2026-11-15):** CONTINUITY 행을 원본 방법의 실제 A2A 위임 경로 실행(18조건)으로 갱신했다. 아래 R1 서술은 보존했고 갱신 내용은 마지막 [R2 갱신](#r2-갱신--continuity--a2a-위임-경로) 절과 CSV의 CONTINUITY 6개 행에 있다. 다른 방법의 행은 이번에 실행하지 않았으므로 바꾸지 않았다.

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
| [CONTINUITY](https://arxiv.org/html/2609.05269v1): witness/permit의 finality 검증 | D3/D4/D5 | 신뢰 issuer/verifier/sink, 완전 context·중재, atomic in-memory finality prototype | deterministic faults, delegated origin/revocation/alternate path | 원본 tests30 + quick 실행(R1). **R2: 원본을 A2A 위임 경로에 연결한 18조건 VERIFIED**(14 `ORIGINAL_GUARANTEE_HOLDS`, 4 `CONTROLLED_ABLATION`). R1 17조건 전체 adapter는 아님 | `ORIGINAL_GUARANTEE_HOLDS`(정확한 조건 한정), R1 C3/C4/C5 실패 양식은 `EXISTING_METHOD_COVERS`. 남은 질문: 하위 위임의 철회 계보([R2 판정](R2_GAP_VERDICT.md)) |
| [Authorization Revocation](https://arxiv.org/html/2609.21284v1): root cut + local fence + exact accounting/rebind | D3/D4/D5 | durable linearization, manifest/channel 완전성, authenticated evidence | provider-free17-case, semantic mutations, pre-fence accounting·독립 지원 | NOT_RUN | cut 후 commit 자체 반례 아님. 원본 fence 의미를 유지한 실제 A2A/provider 통합은? |
| [ResidualAuth](https://arxiv.org/html/2609.08062v2): history-sufficient residual state / hard gate | D3/D4/D5 | 인증 사건·principal, 특정 selected-parent ledger family | paired authorization episodes와 memory/gate 구분 | NOT_RUN | 현재 두 root 단일 support fixture는 lineage sufficiency 재현 아님. 어떤 history가 필요한가? |
| [Governed Shared Memory](https://arxiv.org/html/2606.24535v1#S3.SS2): scoped retrieval·supersession·provenance | D2/D4/D5 | governance/scope/tenant 및 retrieval 경계 | live memory probes, GET-by-id 누락 수정·재측정 | NOT_RUN | 누락 경계 문제는 선행에서 다룸. memory 철회와 sink action 권한의 접점은? |
| [Progent](https://github.com/sunblaze-ucb/progent): programmable tool argument wrapper | D3 | 배치한 정책과 적용한 wrapper의 호출 범위 | 원본 AgentDojo/ASB 등의 논문 평가; R1 cut/fence UNKNOWN | 원본 component4 + synthetic17조건에서 원본 wrapper 재사용 | 정책은 주어진 static rule대로 동작. 현재 grant 반영으로 차단 가능; 신규 method gap 아님 |
| [Multi-CaMeL](https://arxiv.org/html/2610.05640v1#S4): trusted message/opaque variables + capability 보존 | D2/D5 | unique-parent hierarchical tree, instrumented protocol, policy S | AssetOpsBench/MultiAgentDojo; 실제 평가 trivial policy | NOT_RUN | async retained state/root revoke 직접 평가 UNKNOWN. tree CFI를 revocation 보장으로 확대하지 않음 |

기계 판독용 [RESEARCH_GAP_MATRIX.csv](RESEARCH_GAP_MATRIX.csv)는 방법×6조건 축별로 요청된10개 차원을 분리한다. 모든 방법을 같은 실험으로 실행했다는 뜻은 아니다.

## 좁혀진 연구 판단

**Observation:** 미중재 B와 stale policy에서 효과가 남고, 완전한 알려진 경계 적용·현재 권한 정책으로 차단됐다. broad stop은 독립 작업을 막았다. **Interpretation:** 현재 fixture의 실패는 이미 알려진 mediation/권한 신선성/철회 의미 문제로 설명된다. **Established Finding:** 이 구성의 조건 의존성은 재실행 가능한 증거가 있지만 기존 방법 전체의 미해결 gap은 확정하지 않았다. **Open Question:** 가장 가까운 원본 CONTINUITY artifact를 A2A 실행 경로에 연결했을 때 context·현재 정책·receipt binding을 완전히 중재할 수 있는가? 원본 quick 성공은 이 integration의 답이 아니다.

## R2 갱신 — CONTINUITY × A2A 위임 경로

2026-11-15. 원본 CONTINUITY(SHA `59cfe60930d247d1890b366ded686c718020a11e`, 무수정)를 R1의 A2A 위임 경로에 연결해 사전 고정한 18조건을 1회씩 실행했다([통합 보고서](R2_CONTINUITY_INTEGRATION_REPORT.md), [판정](R2_GAP_VERDICT.md), [의미 정렬](R2_SEMANTIC_ALIGNMENT.md)). 기존 D1–D6 분류(CONTINUITY는 D3/D4/D5)와 SoK A/I/R 축을 유지했고 새 번호 체계를 만들지 않았다. 판정값은 `ORIGINAL_GUARANTEE_HOLDS`, `EXISTING_METHOD_COVERS`, `OUT_OF_SCOPE`, `ASSUMPTION_FAILURE`, `ADAPTER_ERROR`, `OBSERVED_VIOLATION_CANDIDATE`, `NOT_RUN`을 쓴다. `VERIFIED`는 이번에 실제로 실행한 **정확한 조건**에만 쓴다.

공통 항목(6개 축 모두): **Trust Assumptions** = 신뢰된 발급자·검증기·sink·상태 권위, 호출자 신원의 결속, 완전 중재, 원자적 인메모리 finality(원본의 단순화 가정). **Evaluation Coverage(원본)** = 결정론적 결함 corpus이며 A2A 전송 결합은 논문 구현 범위 밖. **Existing Mechanism** = 서명된 RootGrant·증거 체인·Permit·Finality.

| 축 | Security Property | Enforcement Point | Our Experiment (R2) | Observed Failure | Failure Classification | Closest Prior Solution | Remaining Research Question |
|---|---|---|---|---|---|---|---|
| direct_tool | 인가된 root·principal·목적지만 효과 | `verify_bundle` → `issue_permit` → `FinalitySink` | R2-1a, X-single_agent_post_cut | 없음 | ORIGINAL_GUARANTEE_HOLDS | CONTINUITY(시험 대상 자체) | 이 조건에는 없음 |
| delegated_tool | 모든 실제 효과 진입에서 같은 인가, 행위자·action 결속 | `EffectBroker.dispatch`, `FinalitySink.execute`의 subject/action/audience | R2-0, R2-1b, R2-2, R2-5, NC-subject, NC-queue_tamper, NC-missing_proof, NC-attacker_minted_root. 대조군 AB-mediation/action_binding/subject_binding | 비인가 효과 0(대조군 제외) | ORIGINAL_GUARANTEE_HOLDS; R1 C3 A-only는 EXISTING_METHOD_COVERS | CONTINUITY. 위임 provenance는 Multi-CaMeL, 완전 중재는 FORGE(둘 다 NOT_RUN) | 하위 위임, 복수 grant, 전송계층 신원 인증(NOT_RUN) |
| post_intervention_state | 효과 시점의 현재 인가 | `FinalitySink`의 철회·정책 재검사, `verify_bundle`의 현재 상태 | R2-3a, R2-3b, X-created_after_cut. 대조군 AB-revocation | 비인가 효과 0(대조군 제외) | ORIGINAL_GUARANTEE_HOLDS; R1 C4 오래된 권한은 EXISTING_METHOD_COVERS; 정적 정책 요인은 NON_EQUIVALENT_SEMANTICS | CONTINUITY, 정산은 Authorization Revocation(NOT_RUN) | 확정된 효과의 정산·복구, 정책 epoch 교체(NOT_RUN) |
| post_revocation_async | cut·수락·commit의 분리 의미 | 원본에는 pending 상태가 없음(검사와 효과가 한 호출) | R2-3a(IMMEDIATE_CUT_AT_FINALITY). R1 grandfather의 대응물이 아님 | 없음 | OUT_OF_SCOPE(NON_EQUIVALENT_SEMANTICS) | Authorization Revocation의 cut·fence·정산(NOT_RUN) | 원자적이지 않은 sink에서 진행 중 인가 작업의 정산 |
| independent_root_continuation | 별도 승인된 작업 보존 | grant id별 철회(`RuntimeState.revoked_ids`) | R2-4 | 과잉 차단 없음 | ORIGINAL_GUARANTEE_HOLDS; R1 C5 전체 중단은 EXISTING_METHOD_COVERS; global-stop 통제는 NON_EQUIVALENT_SEMANTICS | CONTINUITY. 필요한 이력은 ResidualAuth(NOT_RUN) | 철회 단위가 grant/permit/release id뿐이고 task_root 단위·계보가 없다. 루트 철회가 하위 위임 grant를 막는가(NOT_RUN) |
| dynamic_mediation_completeness | 모든 관련 효과가 중재되고 진본으로 관측됨 | 중재(`EffectBroker`) | **NOT_RUN**(효과 경로 1개로 구성). 대조군 AB-mediation만 | — | NOT_RUN | FORGE의 이력 인지 완전 중재(NOT_RUN). 원본은 의무로 둔다 | 동적으로 추가되는 에이전트·도구에서 중재 완전성을 검증할 수 있는가(H2) |

**Observation:** 사전 고정한 14개 비-ablation 조건에서 비인가 효과는 0건이었고(독립 oracle), 검사를 하나씩 끈 대조군 4건에서는 효과가 발생해 oracle이 기대한 유형으로 위반을 보고했다. 원본 하니스만으로 같은 시드를 돌린 결과(15건 비교)와 A2A 경로 결과가 모두 같았다. **Interpretation:** R1의 미중재 B와 오래된 권한 실패는 원본이 이미 다루는 조건으로 설명된다. 개입 뒤 보존된 작업이 효과를 일으키지 않는 이유는 큐 시점이 아니라 효과 시점의 permit과 현재 상태가 효과를 결정하기 때문이다[추론]. **Established Finding:** 이 18개 조건의 결정론적 시행에 한정해 원본 보장이 유지된다. 연구 공백은 확정하지 않았고 `OBSERVED_VIOLATION_CANDIDATE`와 `ADAPTER_ERROR`는 0건이다. **Open Question:** 하위 위임(A→B→C)에서 루트 grant 철회가 하위 grant의 효과를 막는가. 원본 데이터 모델에는 grant 계보와 task_root 단위 철회가 없다(코드 확인). 이것이 원본 계약 위반인지 철회 권위의 운영 정책인지는 Authorization Revocation, ResidualAuth와 비교하기 전에는 판정할 수 없다.

H1의 안전 하위 주장은 우선순위를 낮췄고(원본으로 해소되는 것으로 보임), 복구 하위 주장과 H2는 R2가 시험하지 않았다.
