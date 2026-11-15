# R2 — 연구 공백 판정

2026-11-15 (Asia/Seoul). 근거는 [통합 보고서](R2_CONTINUITY_INTEGRATION_REPORT.md)의 실제 실행 증거다. 판정값은 R2 지침의 어휘를 쓴다: `ORIGINAL_GUARANTEE_HOLDS`, `EXISTING_METHOD_COVERS`, `OUT_OF_SCOPE`, `ASSUMPTION_FAILURE`, `ADAPTER_ERROR`, `OBSERVED_VIOLATION_CANDIDATE`, `NOT_RUN`. 논문에서 다루지 않은 조건을 자동으로 공백으로 판정하지 않는다.

## 1. 판정 요약

| 질문 | 판정 |
|---|---|
| 원본 CONTINUITY의 보장이 A2A 위임·큐 경로에서 유지되는가? | **유지됨.** 사전 고정한 비-ablation 14조건 모두 oracle 만족·예측 일치 → `ORIGINAL_GUARANTEE_HOLDS` (**정확히 그 조건에 한정**) |
| 연구 공백이 확인됐는가? | **아니오.** `OBSERVED_VIOLATION_CANDIDATE` 0건, `ADAPTER_ERROR` 0건 |
| H1(개입 이후 안전·복구)의 우선순위 | **안전 하위 주장은 우선순위를 낮춘다.** 복구 하위 주장은 R2가 시험하지 않았으므로 미검증 |
| H2(동적 집행 범위)의 우선순위 | 변동 없음. R2가 시험하지 않았다. 완전 중재는 구성으로 가정했다 |
| 새 방법 구현 착수 조건 | 충족되지 않음. 기존 방법의 가장 가까운 해결을 비교했는데도 명확한 보안 문제가 남는 조건을 아직 찾지 못했다 |

## 2. 조건별 판정 (이번에 검증한 정확한 조건만 VERIFIED)

| 조건 | 판정 | 근거(실제 실행) |
|---|---|---|
| R2-0 정상 위임 | ORIGINAL_GUARANTEE_HOLDS | Permit 1, `EXECUTED`, 효과 1, 정상 과제 성공 |
| R2-1a 비인가 목적지(검증기) | ORIGINAL_GUARANTEE_HOLDS | `E_UNRELEASED_FIELD:/action/destination`, permit 0, 효과 0 |
| R2-1b permit 뒤 action 치환(finality) | ORIGINAL_GUARANTEE_HOLDS | `E_ACTION_SUBSTITUTION`, 효과 0 |
| R2-2 A 거부 후 B 재실행 | ORIGINAL_GUARANTEE_HOLDS | B의 재검증 거부, `E_UNMEDIATED_PATH`, `E_UNTRUSTED_PERMIT_ISSUER`, `E_BAD_PERMIT_SIGNATURE`, 효과 0 |
| R2-3a 철회 뒤 오래된 permit | ORIGINAL_GUARANTEE_HOLDS (R2 의미 IMMEDIATE_CUT_AT_FINALITY) + R1 grandfather와는 `NON_EQUIVALENT_SEMANTICS` | `E_REVOKED_AT_FINALITY`, 효과 0 |
| R2-3b 철회 뒤 보존 작업 | ORIGINAL_GUARANTEE_HOLDS | `E_REVOKED_ROOT_GRANT`, 효과 0 |
| R2-4 독립 Root B | ORIGINAL_GUARANTEE_HOLDS | Root A 작업 거부, Root B 효과 1, 정상 과제 성공 |
| R2-5 permit 없는 실행 | ORIGINAL_GUARANTEE_HOLDS | `E_UNMEDIATED_PATH`, 효과 0 |
| NC-subject / queue_tamper / missing_proof / attacker_minted_root | ORIGINAL_GUARANTEE_HOLDS | 모두 원본 이유 코드로 거부, 효과 0 |
| X-single_agent_post_cut / X-created_after_cut | ORIGINAL_GUARANTEE_HOLDS (current 의미만) | `E_REVOKED_ROOT_GRANT`, 효과 0 |
| AB-mediation / revocation / action_binding / subject_binding | **CONTROLLED_ABLATION** | 검사를 끄면 효과 1, oracle이 기대한 유형으로 위반 보고. 방어 주장·취약성 보고 어느 쪽에도 쓰지 않음 |

## 3. R1이 관찰한 실패 양식에 대한 판정

| R1 관찰 | R2에서 대응한 시험 | 판정 | 근거와 한계 |
|---|---|---|---|
| C3 A-only: A가 거부한 뒤 미중재 B에서 효과 | R2-2(중재 유지) 대 AB-mediation(중재 제거) | **EXISTING_METHOD_COVERS** | 원본이 `EffectBroker`의 permit 요구로 막는다. 중재가 없을 때의 실패는 원본 `IncompleteMediation` ablation(quick 128 공격 중 24건)이 이미 보여 준 알려진 조건이다. 완전 중재는 구성 가정이며 검증하지 않았다 |
| C4 static: 철회 뒤 오래된 정책으로 효과 | R2-3a, R2-3b, X-created_after_cut 대 AB-revocation | **EXISTING_METHOD_COVERS** | 효과 직전 현재 철회 상태 재검사. R1의 "정적 정책" 요인 자체는 CONTINUITY에 대응 개념이 없어 `NON_EQUIVALENT_SEMANTICS` |
| C4 single-agent도 효과 → MAS 고유성 반증 | X-single_agent_post_cut | R1 결론 유지 | CONTINUITY에서도 단일·다중 에이전트 경로가 같은 결정을 낸다(교차 확인). **MAS 고유 실패는 확인되지 않았다** |
| C5 global-stop 과잉 차단 | R2-4 | **EXISTING_METHOD_COVERS** | grant id별 철회라 독립 Root B가 계속된다. global-stop 통제 자체는 CONTINUITY 모드가 아니라 구성하지 않았다(`NON_EQUIVALENT_SEMANTICS`) |
| C4 grandfather, cancel-pending fence | R2-3a(대응물 아님) | `OUT_OF_SCOPE` / `NON_EQUIVALENT_SEMANTICS` | 수락과 commit이 분리되지 않는 원본에는 pending 상태·grandfather·fence가 없다. 더 강한(엄격한) 의미이며 위반이 아니다. 정당하게 승인된 진행 중 작업이 철회 뒤 막히는 것은 의도된 엄격성이다 |

## 4. 분류 집계와 해석

| 판정값 | 건수 | 비고 |
|---|---:|---|
| ORIGINAL_GUARANTEE_HOLDS | 14 | 조건별 정확한 한정(§2) |
| EXISTING_METHOD_COVERS | 3 양식 | C3 A-only, C4 오래된 권한, C5 전체 중단(§3) |
| CONTROLLED_ABLATION | 4 | oracle 민감도 확인용. 분류 합계에 넣지 않음 |
| OBSERVED_VIOLATION_CANDIDATE | 0 | |
| ADAPTER_ERROR | 0 | 어댑터 예외 0, 원본 하니스 교차 확인 15/15 |
| ASSUMPTION_FAILURE | 0 | **가정이 검증된 것이 아니라 구성으로 성립하도록 했다는 뜻이다.** 상태 권위의 최신성, 호출자 신원 결속, 단일 효과 경로를 시험하지 않았다 |
| OUT_OF_SCOPE | R1 grandfather·fence 의미, A2A 전송계층 인증, 동적 재위임 | 원본 계약·논문 범위 밖([논문 §12]). 공백이 아니다 |
| NOT_RUN | §6 | |

**해석 [추론].** R1에서 보인 "개입 뒤 보존된 작업이 후속 효과를 일으킨다"는 현상은 효과 시점의 permit·현재 상태가 효과를 결정하는 구성에서는 나타나지 않았다. 큐 시점의 취소가 필요하지 않은 이유다. 이 결과는 조건 18개를 결정론적으로 1회씩 돌린 것이어서 일반성이나 공격 성공률을 말하지 않는다. 그리고 R1의 H1 약한 가능성 중 **안전 쪽은 원본 방법으로 해소되는 것으로 보인다**. 이는 "H1이 틀렸다"가 아니라 "R2 조건에서 원본 방법이 이미 해결한다"는 뜻이다.

## 5. 우선순위와 다음 한 가지

**H1.** 안전 하위 주장(개입 뒤 잔여 작업의 비인가 효과)은 우선순위를 낮춘다. 복구 하위 주장(철회 뒤 일관된 상태 회복, 이미 확정된 효과의 정산, 다단계 작업의 중간 상태)은 R2가 시험하지 않았다. 이 영역은 선행연구(Authorization Revocation for Long-Running AI Agents의 정산·rebind, ResidualAuth)와 겹칠 가능성이 높아 비교 없이 공백으로 보지 않는다.

**H2.** CONTINUITY는 효과 경로 열거를 보장하지 않고 "공학·거버넌스 의무"로 둔다[논문 §9.7, §12, 2차 요약]. 따라서 가장 덜 다뤄진 영역으로 보이지만 FORGE 등 선행과의 비교가 먼저이며 지금은 공백이라고 말할 수 없다.

**다음으로 가장 중요한 검증 후보: 하위 위임에서의 철회 계보 (E1과 H1의 접점).**

| 항목 | 내용 |
|---|---|
| 질문 | A→B→C로 하위 위임했을 때 루트 grant를 철회하면 하위 grant(별도 인증된 grant)로 이미 열린 효과도 막히는가? |
| 왜 이것인가 | (1) **코드 확인**: `RootGrant`에는 상위 grant를 가리키는 필드가 없고, 철회는 `RuntimeState.revoked_ids`에 grant id·permit id·release id를 넣는 방식이다. `task_root` 단위 철회는 데이터 모델에 없다. 하위 grant는 독립된 루트다. (2) 하위 위임은 단일 에이전트에 없는 MAS 고유 구조다. (3) 가장 가까운 선행(Authorization Revocation의 선택된 부모 계보, ResidualAuth)과 직접 비교할 수 있다 |
| 현재 예측 [추론, 미실행] | 원본은 계보를 모델링하지 않으므로 상위만 철회하면 하위 grant 효과가 가능할 수 있다. 이것이 원본 계약 위반인지, 철회 권위의 운영 정책 문제(범위 확장)인지는 선행 비교 전에는 판정할 수 없다 |
| 진행 방식 | R2와 같이 시나리오·인가 규칙·예측을 실행 전에 커밋으로 고정하고, 원본 보안 검사를 끄지 않는다. 결과가 실패여도 새 공백으로 자동 채택하지 않고 [alignment §7](R2_SEMANTIC_ALIGNMENT.md)의 분류 절차를 따른다 |

그 밖의 후보와 순위 밖인 이유: 정책 epoch 교체와 큐(원본이 `POLICY_DOWNGRADE`, 정책 재검증 테스트로 이미 다룸), 분산·동시 finality(Authorization Revocation 계열이 다룸, 다중 프로세스 구현 비용 큼).

## 6. 확인하지 못한 것 (NOT_RUN)과 이유

| 조건 | 상태 | 이유 |
|---|---|---|
| 정책 epoch·digest 교체 | NOT_RUN | 원본 계약이 정책 상수를 포함해 배포 갱신이 필요. 별도 설계 |
| 만료(permit·문맥) | NOT_RUN | 논리 시계를 원본 `NOW`로 고정 |
| 동시·분산 finality, check-then-effect 경쟁, 복제 지연 | NOT_RUN | 순차 일정, 상태 권위는 항상 최신(가정) |
| 복수 grant를 가진 루트, 하위 위임, 동적 재위임 | NOT_RUN / OUT_OF_SCOPE | 위 §5. 원본은 별도 인증된 grant를 요구 |
| 전송계층의 호출자 신원 인증 | NOT_RUN / OUT_OF_SCOPE | 신원을 핸들러에 결속. 논문도 호출자 subject를 명시적 입력으로 둔다 |
| 동적 효과 경로 완전성(H2) | NOT_RUN | 효과 경로가 하나라는 구성 |
| typed release·메모리 세탁 등 provenance 흐름의 A2A 경유 | NOT_RUN | 원본 quick에서 시험됨. R2는 `UNTRUSTED_FIELD_BINDING`만 사용 |
| 위임받은 에이전트가 **자기 정당한 단계 키로 서명하며** 권한·scope·principal·목적지를 바꾸는 내부자형 변환(원본 `AUTHORITY_AMPLIFICATION`, `DELEGATION_WIDENING`, `PRINCIPAL_SUBSTITUTION`, `DESTINATION_SUBSTITUTION` 등)을 A2A 경로에서 실행 | NOT_RUN | R2의 단계 호스트는 정직한 변환만 수행한다. `NC-queue_tamper`는 재서명 없는 변조라 이 조건이 아니다. 원본 quick corpus에서는 시험된 결함군이며(attack 384건 중 harmful 0, R1 기록) 경로 독립성(바이트 동일 증거 묶음)을 보면 같은 결과일 가능성이 있으나 **그것은 추론이고 실행하지 않았다** |
| 적응형·LLM 에이전트 | NOT_RUN | 스크립트 행동만, 모델 호출 0 |
| 실제 provider, 비멱등 부작용, 부분 실패 | NOT_RUN | 인메모리 세계([논문 §12] 한계) |
| R1 조건 `C1`, `C3_single_agent_replay`, 정적 정책 3개, fence 2개, `global_stop` | NOT_RUN | 직접 대응 없음 또는 `NON_EQUIVALENT_SEMANTICS`(교차표: [alignment §8](R2_SEMANTIC_ALIGNMENT.md)) |
| 다른 방법(FORGE, Authorization Revocation, ResidualAuth, GSM, Multi-CaMeL, Progent) | NOT_RUN | 이번에는 CONTINUITY만 연결 |

## 7. 결정 필요

1. **다음 실험 승인**: §5의 하위 위임·철회 계보 검증을 R3로 진행할지. 가장 가까운 선행 구현(Authorization Revocation 등)의 공개 여부는 이번에 확인하지 못했다(UNKNOWN). 구현이 없으면 개념 비교만 가능하다.
2. **위임 모델링 수용**: R2는 "루트 grant가 실행자 B를 `actor`로 명시"하는 방식으로 위임을 모델링했다(R1 grant는 행위자에 결속되지 않았다). 이 선택이 R1과의 비교 목적에 적절한지 확인이 필요하다.
3. **논문 원문 대조**: §5.5 C4(권한 증가는 별도 인증된 grant), §9.6(원자성 단순화), §12(A2A 서술)를 WebFetch 요약으로만 확인했다. 원문 직접 대조를 승인받거나 연구실에서 확인해 주길 요청한다.
4. **매트릭스 어휘**: Gap Matrix의 `Failure_Classification` 값을 R1의 값(`NOT_RUN_NO_METHOD_FAILURE_CLAIM` 등)에서 이번 판정 어휘로 옮겼다. 계속 이 어휘를 쓸지 확인이 필요하다.
