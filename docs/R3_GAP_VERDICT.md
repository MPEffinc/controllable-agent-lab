# R3 — 연구 공백 판정

2026-11-15 (Asia/Seoul). 근거: [선행연구 대조](R3_PRIOR_ART_COMPARISON.md), [위임 의미 분석](R3_DELEGATION_SEMANTICS.md), [사전 고정](R3_HYPOTHESIS_PREREG.md), [실험 보고](R3_EXPERIMENT_REPORT.md). 인용 ID(`[VERA-1]` 등)는 [research-provenance.json](../results/r3/research-provenance.json). 새 연구 공백을 가정하지 않으며, 공백을 찾는 것이 이 작업의 성공 조건이 아니다.

## 1. 판정 요약

| 질문 | 판정 |
|---|---|
| 원본 CONTINUITY가 의미를 정의한 조건(G0, G1a, G1b, G2)이 3-agent A2A 사슬에서 유지되는가 | **유지됨.** 4/4 `IN_SCOPE_PASS`(조건에 한정) |
| 파생 권한·독립 지원·conjunctive 승인(G3–G5)을 CONTINUITY가 표현하는가 | **아니오.** 정적 검사 S1–S7 모두 성립. `SCOPE_EXTENSION` / `POLICY_MODEL_MISMATCH`, 판정은 `UNDEFINED_AUTHORIZATION_SEMANTICS` |
| G3–G5가 묻는 성질을 기존 연구가 이미 다루는가 | **예.** G3: VERA, ResidualAuth, Succession. G4: VERA, Authorization Revocation. G5: Authorization Revocation만(VERA는 명시적 제외) → `COVERED_BY_PRIOR_ART` |
| R3 가설(권한 의존 철회의 정확한 반영과 독립 경로 보존)의 연구 공백 여부 | **확인하지 못했다.** `UNRESOLVED_GAP_CANDIDATE` 0건. **간선·계보 가설은 종료한다** |
| 다음 방향 | **H2(동적 집행 범위)로 전환을 권고**한다. 단 H2의 선행연구 점검을 먼저 한다(§5) |

## 2. 조건별 판정

두 열을 분리한다. **CONTINUITY 기준**은 원본 방법의 모델 안에서의 판정, **선행연구 기준**은 가장 가까운 기존 방법이 그 문제를 직접 다루는지다. Gap Status는 두 열을 합친 최종 표기다.

| 조건 | CONTINUITY 기준 | 선행연구 기준(가장 가까운 해결) | Gap Status |
|---|---|---|---|
| G0 단일 RootGrant 사슬 | `IN_SCOPE_PASS` (EXECUTED, 효과 1, 정상 과제 성공) | 신규성 논의 대상 아님 | 해당 없음 |
| G1a 같은 RootGrant 철회, permit 발급 뒤 | `IN_SCOPE_PASS` (`E_REVOKED_AT_FINALITY`, 효과 0) | CONTINUITY 자신[CON-5], Authorization Revocation(루트 cut·fence, pre-fence 수락 정산은 의미가 다름), Succession, ResidualAuth hard gate | `EXISTING_METHOD_COVERS` |
| G1b 같은 RootGrant 철회, 작업 보존 중 | `IN_SCOPE_PASS` (`E_REVOKED_ROOT_GRANT`, 효과 0) | 위와 같음. R2-3b의 3단 확장 | `EXISTING_METHOD_COVERS` |
| G2 독립 RootGrant 보존 | `IN_SCOPE_PASS` (A 작업 거부, X 작업 실행, 효과 1) | Authorization Revocation unrelated-root locality [REV-8, REV-3] | `EXISTING_METHOD_COVERS` |
| G3 A에게서 유래한 하위 권한만 있는 C | `SCOPE_EXTENSION`, `UNDEFINED_AUTHORIZATION_SEMANTICS` | VERA(간선 철회), ResidualAuth(선택 부모 cascading), Succession(단일 부모 조상 cut). Revocation은 루트 수준만 [REV-9] | `COVERED_BY_PRIOR_ART` |
| G4 유래 경로 + 독립 경로 | `SCOPE_EXTENSION`, `UNDEFINED_AUTHORIZATION_SEMANTICS` | VERA(대안 경로 보존 [VERA-2, VERA-6]), Authorization Revocation(Thm 12, rebind [REV-7]). ResidualAuth는 그래프 수준만, Succession은 제외 [SUC-1] | `COVERED_BY_PRIOR_ART` |
| G5 conjunctive 승인 | `SCOPE_EXTENSION`, `UNDEFINED_AUTHORIZATION_SEMANTICS` | Authorization Revocation(conjunctive witness [REV-1, REV-4]). **VERA는 명시적 제외 [VERA-1]**, ResidualAuth는 확인 못 함, Succession은 추상 profile만 | `COVERED_BY_PRIOR_ART` (Revocation, 루트 수준·논문과 등록 사례 한정) |

### G4, G5와 VERA의 정확한 보장 범위

- VERA의 권한은 "유효한 root→노드 경로가 하나라도 있으면 active"(disjunctive)다. G4의 "대안 경로가 있으면 유지"는 **VERA의 보장 범위 안**이다 [VERA-2]. 논문은 대안 부모 경로가 있는 320개 단일 간선 철회 모두에서 공유 agent가 유지된다고 보고한다(저자 주장) [VERA-6].
- G5의 conjunctive 정책은 VERA의 보장에 **들어가지 않는다.** 논문이 "threshold approval이나 all-parent approval은 다른 target 함수가 필요하다"고 명시적으로 제외한다 [VERA-1]. reference model에서 OR 의미를 쓰면 AND 정책을 위반하는 것이 확인된다. 이것은 VERA의 결함이 아니라 선언된 비목표이며 `SCOPE_EXTENSION`이다.
- Authorization Revocation과의 비교(G4): VERA는 **어떤 노드가 권한을 잃는가**(목표 집합)를 정확히 정의하지만 진행 중인 작업과 효과는 다루지 않는다. Authorization Revocation은 같은 정밀도 목표를 공유하면서 "퇴역한 root 아래에서 선택된 진행 중 carrier가 여전히 commit할 수 있는가"를 묻고(관련 연구 절의 서술 [요약]), 독립 충분 지원에 대한 atomic rebind를 정의한다 [REV-7, REV-12]. 두 논문은 서로 다른 층을 다루며 **둘 다 G4의 해당 층을 직접 다룬다**.

## 3. 기존 연구가 이미 해결한 내용

| 연구 | 이미 해결한 것 | 근거 |
|---|---|---|
| VERA | 서명된 다중 부모 DAG에서 간선 하나의 철회가 권한을 잃는 노드 집합 정확히 결정, 대안 경로 보존, 배치 철회의 비합성, 검증자 독립 증명 | [VERA-2, VERA-5, VERA-8] |
| Authorization Revocation | 루트 cut과 protected sink fence, 독립 충분 지원의 antichain, conjunctive 증인, atomic independent rebind, 관련 없는 root 보존, 진행 중 carrier의 정산 | [REV-1, REV-2, REV-4, REV-7, REV-8] |
| ResidualAuth | 철회 뒤에도 같은 현재 권한을 가진 이력들이 다른 결정을 요구할 수 있다는 잔여 상태 이론, 선택 부모 cascading effectiveness, hard gate로 효과 차단 | [RES-1, RES-2, RES-3] |
| Authorization Succession | 단일 부모 세대 forest에서 조상 cut의 후손 무효화, 포크 보존, 원자적 인계, 독립 re-root, 효과 broker | [SUC-6, SUC-7] |
| CONTINUITY | 서명된 루트 grant와 증거 사슬, 효과 직전 현재 철회·정책 재검사(permit), 행위자·action 결속 | [CON-1, CON-5], R2 |

## 4. 현재 Method가 지원하지 않지만 기존 연구로 해결 가능한 조건

CONTINUITY는 아래 조건을 **모델링하지 않는다.** 원본 취약점이 아니라 모델 범위 밖이다([위임 의미 분석 §3–4](R3_DELEGATION_SEMANTICS.md)).

| 조건 | CONTINUITY에 없는 것 | 해결할 수 있는 기존 연구 |
|---|---|---|
| 파생 grant의 부모 참조와 의존 철회 | 부모 필드, 계보, 간선 철회, 효과 시점 의존 검사 (S1, S3, S6) | VERA(간선), ResidualAuth, Succession(단일 부모) |
| 독립·대안 지원과 rebind | 개념 자체가 없음 | VERA(보존), Authorization Revocation(보존과 atomic rebind) |
| conjunctive 승인 | `approval_digest` 미검증, quorum은 prototype 밖 (S4, [CON-3]) | Authorization Revocation(루트 수준) |

[추론, 미실행] 부수 귀결: CONTINUITY에서 서로 다른 task root를 가진 grant 둘이 같은 action을 승인하면 각각 한 번씩 확정될 수 있다(멱등 키가 `task_root`와 action digest). "대안 지원이 하나의 효과를 정당화한다"는 의미를 표현할 수 없으므로 지원 사이의 exactly-once는 정의되지 않는다. 이는 정책 불일치의 한 면이며 실행으로 확인하지 않았다.

## 5. 독립적으로 남은 검증 질문과 H2 전환

### 5.1 남은 질문 (공백 후보가 아님)

| 질문 | 상태 | 왜 후보가 아닌가 |
|---|---|---|
| (a) 간선 단위 정확 철회 × conjunctive·독립 지원 × 효과 시점 finality와 진행 중 작업의 rebind를 **한 모델**이 다루는가 | 어느 논문도 주장하지 않음(논문 수준). Revocation의 atom은 root-epoch이고 중간 위임 간선·agent는 atom이 아니다 [요약; 간선 철회는 연산이 아님 REV-9] | **명확한 보안 문제가 제시되지 않았다.** 간선을 atom으로 확장하는 것이 자명한지 논문으로 판정할 수 없고, 효과를 낼 수 있는 구체적 실패 조건이 없다. `UNRESOLVED_GAP_CANDIDATE`로 올리면 신규성을 성급히 긍정하는 것이다 |
| (b) VERA의 캐시된 철회 상태 위에서 효과 시점의 낡은 권한 상한 | VERA는 전파 지연을 범위 밖으로 둔다 [VERA-3] | 효과 시점 재검사는 CONTINUITY·Revocation이 정의한 층이다. 합성의 공학 문제에 가깝다 |
| (c) 핸드오프가 권한을 위임하는가의 규약 | 연구마다 다름(VERA 어댑터는 간선, CONTINUITY·Succession은 아님) | 형식 모델 밖의 정책·상호운용 결정이며 실험 대상으로 정의되지 않았다 |

`UNRESOLVED_GAP_CANDIDATE`: **0건**. `ASSUMPTION_FAILURE` 0건(가정이 검증된 것이 아니라 구성으로 성립하도록 했다는 뜻), `IMPLEMENTATION_ERROR` 0건.

### 5.2 H2 전환의 근거: 다섯 연구가 공통으로 전제하는 것

각 연구가 보장을 주려면 **효과 경로가 모두 열거되고 중재된다**는 전제가 필요하다. 이것은 연구마다 이름만 다르다.

| 연구 | 전제 | 근거 |
|---|---|---|
| CONTINUITY | 증명은 permit을 요구하는 sink만 보호한다. 배포는 보호 효과 종류를 열거해야 한다. 완전 중재는 공학·거버넌스 의무다 | [CON-6, CON-7, CON-4] |
| Authorization Revocation | A6 "Registry and manifest completeness": 동결된 매니페스트가 철회 root의 작업이 닿을 수 있는 모든 runtime, provider, effect sink, channel을 덮어야 한다. A1 "Issuer mediation": 권한을 발급·위임·확대하는 모든 전이가 매니페스트된 발급자를 거친다 | [REV-5, REV-6] |
| Authorization Succession | "Our protocol assumes such complete mediation"; 가정 A1 complete mediation, A4 complete lineage accounting [요약, Table 2] | [SUC-5] |
| ResidualAuth | hard gate는 gate를 거치는 proposal만 신뢰된 ledger와 대조한다 | [RES-3] |
| VERA | 어댑터가 caller→callee 간선을 **보고**해야 하고, 누락된 in-edge·노드는 서명된 roster와의 대조로만 잡는다. 보호 효과 경계는 정의하지 않는다 | [VERA-3], 논문 §VII, Table II |

[추론] 이 공통 전제는 동적 환경에서 가장 약하다. 에이전트·도구·위임 경로가 **실행 중에 추가되거나 바뀌면** 매니페스트와 효과 클래스 목록이 낡을 수 있다. 위의 연구들은 이 가정이 성립한다고 보고 그 위에서 철회·finality·계보를 정확히 만든다. 가정 자체를 **검증**하는 것은 어느 것도 목표로 삼지 않는다. 이것이 H2("동적으로 추가·변경되는 Agent·Tool·위임 경로에서 모든 보호 대상 효과가 집행 경계를 통과한다는 사실을 검증할 수 있는가")의 질문이다.

### 5.3 전환 전에 해야 할 것 (H2도 선행연구와 겹칠 수 있다)

- **읽지 않은 선행연구**([비교 문서 §5](R3_PRIOR_ART_COMPARISON.md)): Santos-Grueiro, *When Does Authorization End? Effect Closure at Provider Boundaries* (arXiv:2609.02866), *Temporary Authority, Permanent Effects: Commit-Time Authorization* (2607.10487), AID-Guard (2608.21159) 등. 효과 경계·provider 경계를 직접 다룰 수 있다.
- R1에서 정리한 FORGE의 이력 인지 완전 중재와 한계 서술(미계측 channel은 보장하지 않음), OpenShell·ControlValve의 집행 경계.
- 같은 방식(사전 고정 → 코드 → 결과 → 문서)으로 H2의 선행연구 구분 문서를 먼저 만든다. 신규 방어를 먼저 만들지 않는다.

**권고하는 다음 연구 방향.** H2를 **측정 우선**으로 재구성한다. 실제 A2A와 MCP 구성에서 보호 효과를 낼 수 있는 인터페이스를 열거하고 그것이 집행 매니페스트와 얼마나 일치하는지, 동적 추가 시 불일치가 생기는지를 기존 방법(CONTINUITY broker, Revocation의 매니페스트 가정, FORGE 모니터)에 대해 확인한다. 이것은 방법의 취약점 주장이 아니라 **가정의 검증 가능성**을 묻는 질문이다. 결과가 "기존 연구가 이미 해결"로 끝나도 의미 있는 판정이다.

## 6. 판정 어휘 집계

| 값 | 건수 | 비고 |
|---|---:|---|
| IN_SCOPE_PASS | 4 | G0, G1a, G1b, G2 (CONTINUITY 기준, 정확한 조건 한정) |
| EXISTING_METHOD_COVERS / COVERED_BY_PRIOR_ART | 5 조건 | G1, G2는 CONTINUITY를 포함한 기존 방법이, G3–G5는 선행연구가 직접 다룸 |
| SCOPE_EXTENSION | 3 | G3, G4, G5 (CONTINUITY 기준). 원본 결함이 아님 |
| UNDEFINED_AUTHORIZATION_SEMANTICS | 3 | G3, G4, G5. PASS/FAIL을 내지 않음 |
| ASSUMPTION_FAILURE | 0 | 시험하지 않음(가정은 구성으로 성립) |
| IMPLEMENTATION_ERROR | 0 | 어댑터 예외 0, 3-host 증거 묶음의 원본 일치 |
| EVALUATION_LIMITATION | 2 | reference model은 정의 수준 재구현이며 artifact 결과가 아니다. VERA artifact는 실행하지 못했다. 다른 세 artifact는 공개되지 않았다 |
| UNRESOLVED_GAP_CANDIDATE | 0 | §5.1 |
| NOT_RUN | 다수 | G3–G5의 CONTINUITY 실행, 어느 선행연구 artifact의 실행, 정책 epoch 교체·만료·동시·분산 finality·전송계층 신원 인증 |

## 7. 결정 필요

1. **H2 전환 승인**과 선행연구 점검 범위(읽지 않은 6건 + FORGE·OpenShell·ControlValve 재검토).
2. **VERA artifact 실행 승인 여부.** 내려받은 제3자 코드의 실행이 세션의 자동 권한 분류기에 의해 거부되어 정적 검토만 했다. 실행을 원하면 허용 규칙을 추가해 주어야 한다. 격리 환경(원본 고정 의존성, 전역 설치 없음)은 준비되어 있다. 실행으로 추가되는 정보는 "artifact가 소규모 그래프에서 논문 정의대로 같은 목표 집합을 낸다"는 확인뿐이라 R3 결론에는 필수가 아니다.
3. **논문 원문 직접 대조.** [요약]으로 표시한 항목(Revocation의 support가 root atom뿐이라는 서술, Succession의 정리 조건, ResidualAuth §4)은 원문 문자열로 확인하지 못했다.
4. **다른 세 연구의 artifact.** 공개 여부를 확인하지 못했다(UNKNOWN). 저자에게 문의할지, reference model(정의 수준)로 만족할지.
5. **매트릭스 스키마.** 요청한 11개 필드는 기존 CSV와 열이 달라 **새 파일**([RESEARCH_GAP_MATRIX_R3.csv](RESEARCH_GAP_MATRIX_R3.csv))로 분리했다. 기존 CSV는 그대로다. 이 분리를 유지할지 확인이 필요하다.
