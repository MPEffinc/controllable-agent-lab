# R3 — 위임 의미 분석: 작업의 위임과 권한의 위임

작성: 2026-11-15 (Asia/Seoul), R3 조건을 고정하기 전. 근거 태그와 인용 ID(`[VERA-1]` 등)는 [R3_PRIOR_ART_COMPARISON](R3_PRIOR_ART_COMPARISON.md) §0과 같다. CONTINUITY에 관한 사실은 R2에서 원본 소스를 정독한 결과이며, R3의 [expressiveness_check.py](../experiments/r3/expressiveness_check.py)가 같은 사실을 기계적으로 다시 확인한다(결과는 [R3_EXPERIMENT_REPORT](R3_EXPERIMENT_REPORT.md)).

## 1. 용어 (이 문서와 R3 전체에서 쓰는 정의)

| 용어 | 정의 | 무엇이 증거인가 |
|---|---|---|
| **작업의 위임(Delegation of Work)** | A가 작업 단위(메시지·task)를 B에게 넘긴다. B는 효과를 내려면 **이미 B에게 귀속된 독립 권한**이 필요하다. 넘김 자체는 B의 권한을 새로 만들지 않는다 | 전송 기록, 단계 영수증(작업·문맥이 이동한 증거) |
| **권한의 위임(Delegation of Authority)** | A가 자신의 권한 α의 일부(β ⊑ α)를 B에게 **새로 부여**한다. β의 유효성은 α와 위임 간선에 **의존**한다 | 부모를 가리키는 서명된 위임 증거(간선 또는 하위 grant) |
| **Root Grant** | 신뢰된 발급자가 부여한 신뢰 앵커 권한. 다른 권한에 의존하지 않는다 | 발급자 서명 |
| **Delegated Grant(하위 grant)** | 유효성이 부모 권한과 위임 간선에 의존하는 권한 | 부모 참조 + 의존 의미 + 효과 시점 검사(§4) |
| **Authority Lineage(권한 계보)** | grant들 사이의 "누가 누구에게서 파생됐는가" 관계 | 부모 참조의 사슬 |
| **Independent Authorization Support(독립 지원)** | 같은 효과를 별개로 정당화할 수 있는 다른 권한 경로. 하나가 철회돼도 다른 하나가 남으면 권한이 유지된다 | 서로 의존하지 않는 grant 또는 경로 |
| **Edge / Root Revocation** | 위임 **간선** 하나 / **루트** 권한 하나를 철회 | 철회 기록 |
| **Exact Rebind** | 진행 중인 작업을 같은 연산·효과 범위로 **다른 독립 지원**에 원자적으로 다시 결속 | 단일 사용 영수증([REV-7]) |
| **Protected Effect / Finality** | 보호 대상 효과와, 그 효과가 확정되는 지점의 마지막 검사 | 효과 sink의 검사 기록 |

## 2. R2가 시험한 것과 시험하지 않은 것

R2에서는 `RootGrant`가 **B를 행위자(actor)로 발급 시점에 미리 지정**했다. A는 신뢰된 발급자가 만든 증거를 B에게 넘기는 전달자였다.

| 질문 | R2 | 이유 |
|---|---|---|
| A→B로 작업이 전달돼도 서명된 증거가 보존되고 변조가 거부되는가 | **시험함** | 단계 호스트가 원본 `Component.apply`로 증거를 확장하고 검증기가 사슬을 검사 |
| 철회 뒤 보존된 작업과 오래된 permit이 효과를 내는가 | **시험함** | R2-3a, R2-3b |
| 독립 root의 작업이 철회에 영향을 받지 않는가 | **시험함** | R2-4 |
| **A가 B에게 새 권한을 발급**하는가 | **시험하지 않음** | B의 권한은 A가 아니라 발급자가 ingress에서 직접 부여 |
| A의 권한 철회가 B의 **파생** 권한에 반영되는가 | **시험하지 않음** | 파생 관계가 존재하지 않음 |
| 독립 경로·conjunctive 승인·rebind | **시험하지 않음** | 표현할 객체가 없음 |

따라서 R2의 `ORIGINAL_GUARANTEE_HOLDS`는 **작업의 위임**에 한정된다. R2는 동적 재위임(권한의 위임)에 대해 아무것도 말하지 않으며, R2 보고서의 NOT_RUN 목록(동적 재위임, 복수 grant, 하위 위임)이 그 뜻이다. `NC-subject`(위임자가 위임받은 자의 permit을 쓰는 시도)는 행위자 결속의 시험이지 권한 위임의 시험이 아니다.

## 3. CONTINUITY의 `RootGrant` 모델이 표현하는 범위

| 표현 | 가능 | 근거 |
|---|---|---|
| 신뢰된 발급자가 서명한 루트 권한 | ✓ | `RootGrant`: principal, actor, task root, 권한 집합, delegation scope, tool·server·효과 종류, 필드 조건, 정책, nonce, 만료, 서명 |
| 효과를 낼 수 있는 행위자의 결속 | ✓ | grant의 actor, finality의 caller subject 검사 |
| 단계 사이의 권한 **단조 비증가**(attenuation) | ✓ | 권한·delegation scope·taint 단조 검사 |
| 권한 **증가** | 새 grant로만 | "Authority and delegation can increase only through a separately authenticated grant" [CON-1] |
| 작업 전달 경로의 서명된 증거 | ✓ | envelope·영수증 사슬(문맥·action의 계보이지 권한의 계보가 아님) |
| 부모 grant를 가리키는 필드 | **✗** | `RootGrant`에 부모·계보·간선 필드가 없음. 논문도 하위 grant·계보 객체를 정의하지 않음("grant edge"는 정리에서만 언급 [CON-2]) |
| 부모·간선에 의존하는 철회 | **✗** | 철회는 `RuntimeState.revoked_ids`에 grant·permit·release id를 넣는 방식. task_root·계보 단위 철회가 없음 |
| 독립·대안 지원 | **✗** | 서로 다른 grant는 서로 무관한 독립 root |
| conjunctive 승인 | **✗** | `approval_digest`는 문맥 필드로 존재하지만 검증 로직이 참조하지 않는다. quorum 승인은 prototype 밖 [CON-3] |
| rebind | **✗** | permit은 grant id·action digest에 결속. 철회되면 새 bundle로 새 permit이 필요 |

**CONTINUITY에서 "위임"은 두 가지로만 나타난다.** (1) `delegation_scope`: 한 task 문맥 안에서 **더 넘겨줄 수 있는 범위**를 나타내는 문자열 집합이며 단계마다 좁아지는지만 검사한다. 새 grant를 만들지 않는다. (2) 원본의 `multiagent` 도메인: `agent.delegate`는 **보호 효과**(STATE_MUTATION, tool `urn:a2a:delegation`, resource `task`, destination `agent:worker`)로 모델링된 작업 위임이다. 위임 자체를 효과로 승인할 뿐 권한 파생을 표현하지 않는다.

## 4. 별도로 서명된 RootGrant가 있다고 하위 grant가 되는 것은 아니다

신뢰된 발급자가 C 앞으로 새 `RootGrant`를 서명했고 사람이 "A가 C에게 위임했다"고 이해한다고 해도, 그것만으로 그 grant를 A의 grant의 하위 grant로 판정하지 않는다. 하위 grant로 인정하려면 다음 **세 조건이 모두** 필요하다.

| 조건 | CONTINUITY | VERA | Revocation | ResidualAuth | Succession |
|---|---|---|---|---|---|
| (a) 부모를 가리키는 **인증된 참조**가 증거 안에 있다 | ✗ | ✓ 서명된 간선 | ◐ 인증된 derivation edge, 단 support는 root atom | ✓ selected parent | ✓ `par(g)`와 lineage atom |
| (b) 부모 철회가 자식에 **영향을 주는 의미**가 정의돼 있다 | ✗ | ✓ 도달 가능성 | ◐ root cut이 root atom을 포함하는 witness에 영향 | ✓ cascading effectiveness | ✓ ancestor cut closure |
| (c) 효과 시점에 그 의존을 **검사하는 지점**이 있다 | ✗ (id 철회만 검사) | ✗ 효과 경계 없음 | ✓ sink fence | ✓ hard gate | ✓ protected-effect broker |

CONTINUITY는 세 조건이 모두 없으므로 별도 grant는 **독립 루트**다. 발급자의 머릿속이나 외부 장부에 있는 "유래"는 검증기와 sink가 볼 수 없는 정보다. 이 의미로 판정하면 A의 grant를 철회해도 C의 grant가 남는 것은 **정책 불일치**이지 취약점이 아니다.

## 5. 핸드오프와 권한 위임을 잇는 규약은 연구마다 다르다

| 연구 | 작업 핸드오프(A→B)가 권한 위임인가 | 근거 |
|---|---|---|
| CONTINUITY | **아니다.** 핸드오프는 grant를 만들지 않고 증거가 이동할 뿐이다 | 원본 소스, [CON-1] |
| VERA | **어댑터 규약으로 그렇다.** caller→callee 핸드오프를 후보 간선으로 기록하고, callee 쪽이 수락하면 서명된 위임 그래프의 간선이 된다 | [artifact 정적], "An adapter needs four hooks: emit caller-to-callee edges, …"(논문 §VII) |
| Authorization Revocation | **아니다(작업).** "A2A delegated task"는 보호 sink·fence 계약의 endpoint 범주이고, 권한 의존은 root support로 표현한다 | [요약; 원문 표의 endpoint 행] |
| Authorization Succession | **아니다.** 형제 협업은 authorization parent edge를 만들지 않고 grant를 합치지 않는다 | [SUC-3] |
| ResidualAuth | 작업 핸드오프를 다루지 않는다. 권한은 grant 그래프에서만 정의 | [RES-1] |

[추론] 같은 "A2A 작업 전달"이 어떤 모델에서는 권한 간선이고 어떤 모델에서는 아니다. 따라서 **"이 핸드오프가 권한을 위임하는가"는 형식 모델 밖의 정책 결정**이며, R3는 이를 임의로 가정하지 않는다. 핸드오프가 권한을 위임했는지는 **신뢰된 발급자의 서명으로만** 인정한다.

## 6. R3에 대한 함의

- **G0, G1, G2**는 CONTINUITY가 의미를 정의하는 조건이다(작업의 위임, 루트 철회, 독립 grant). CONTINUITY 원본 함수로 실행한다.
- **G3, G4, G5**는 CONTINUITY가 의미를 정의하지 않는다 → CONTINUITY 기준 판정은 `UNDEFINED_AUTHORIZATION_SEMANTICS`이며 원인은 `SCOPE_EXTENSION` / `POLICY_MODEL_MISMATCH`다. 이 조건을 CONTINUITY 위에서 **실행해 PASS/FAIL을 내지 않는다**:
  1. 파생 의존의 생성·철회 의미를 우리가 발명해야 하고, 그러면 원본 보장과 동등한 실험이 아니다.
  2. 신뢰된 발급자가 새 권한을 발급한 뒤 관찰한 효과를 원본의 취약점으로 주장하는 것은 금지되어 있다.
- 선행연구가 정의한 의미에서 기대되는 결과는 **논문 정의를 독립적으로 재구현한 reference model**로 계산한다. 이것은 원본 artifact의 결과가 아니라 **정의의 계산**이다([reference_model.py](../experiments/r3/reference_model.py), 모든 출력에 `REFERENCE_MODEL_FROM_PAPER_DEFINITION`을 표기).

## 7. 판정 어휘

| 값 | 정의 | 사용 규칙 |
|---|---|---|
| `IN_SCOPE_PASS` | 원본이 의미를 정의한 조건에서 기대한 결과가 나왔고 독립 oracle이 만족 | 정확한 조건에 한정 |
| `EXISTING_METHOD_COVERS` | 가장 가까운 기존 방법이 그 문제를 직접 다룸 | 근거 인용 필수 |
| `COVERED_BY_PRIOR_ART` | 선행연구의 정리·정의·등록 사례가 조건을 직접 다룸 | 논문 수준의 중복 표시. 실행 결과가 아님 |
| `SCOPE_EXTENSION` | 원본 모델의 범위를 넘는 조건 | 원본 결함이 아님 |
| `POLICY_MODEL_MISMATCH` | 기대하는 정책 의미가 원본 모델에 표현되지 않음 | 효과가 관찰돼도 취약점이 아님 |
| `UNDEFINED_AUTHORIZATION_SEMANTICS` | 정책 의미가 정의되지 않아 PASS/FAIL을 내지 않음 | 이 값에서는 효과 유무를 판정하지 않음 |
| `ASSUMPTION_FAILURE` | 신뢰 가정 실패로 설명되는 위반 | 가정이 구성으로 성립했는지 구분 |
| `IMPLEMENTATION_ERROR` | 우리 어댑터·하니스 오류 | 원본 방법의 결과로 보고하지 않음 |
| `EVALUATION_LIMITATION` | 평가 도구의 한계(예: oracle이 못 보는 속성) | 방법의 결함이 아님 |
| `UNRESOLVED_GAP_CANDIDATE` | 가장 가까운 선행연구까지 비교했는데 명확한 문제가 남음 | 자동 확정 금지, 근거와 약점을 함께 기록 |
| `NOT_RUN` | 실행하지 않음 | 이유를 적는다 |
