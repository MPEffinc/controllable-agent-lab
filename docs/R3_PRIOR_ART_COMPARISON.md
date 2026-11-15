# R3 — 선행연구 대조: 위임 권한 계보·철회·독립 지원

작성: 2026-11-15 (Asia/Seoul). R3 실험 조건을 고정하기 **전에** 작성했다. 목적은 새 방어를 만드는 것이 아니라, 동적 권한 위임과 철회에서 **기존 연구가 이미 해결한 부분과 아직 확인되지 않은 부분을 구분**하는 것이다. 새 연구 공백을 가정하지 않는다.

## 0. 근거 표기와 대상 논문

| 태그 | 의미 |
|---|---|
| **[원문]** | arXiv HTML을 로컬에 저장한 사본에서 **문자열 그대로** 확인한 인용. 인용 ID는 [research-provenance.json](../results/r3/research-provenance.json)의 `quotes`에 있고 `found_verbatim`이 모두 참이다(41건). 같은 arXiv 버전을 받으면 같은 해시·결과를 재확인할 수 있다 |
| **[요약]** | WebFetch(작은 모델의 요약)로만 확인. 절 번호와 의미는 신뢰하되 원문 대조 전까지 근사치로 본다 |
| **[artifact 정적]** | 내려받은 VERA artifact 소스를 **읽기만** 했다. 실행하지 않았다(§4) |
| **[추론]** | 위 근거로부터의 해석. 확인된 사실이 아니다 |

| 약칭 | 서지 | 링크 | 비고 |
|---|---|---|---|
| CONTINUITY | Zheng, Yang. *CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls.* arXiv:2609.05269v1, 2026-09-04 | [abs](https://arxiv.org/abs/2609.05269) | R1·R2에서 원본 artifact 실행 |
| VERA | Liu, Yu, Jiang. *VERA: Authority-Preserving Edge Revocation for Federated AI-Agent Workflows.* arXiv:2608.30091v1, 2026-08-30 (cs.AI) | [abs](https://arxiv.org/abs/2608.30091) | 서명된 위임 DAG의 간선 철회 |
| Authorization Revocation | Zhu, Wang. *Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution.* arXiv:2609.21284v1, 2026-09-18 | [abs](https://arxiv.org/abs/2609.21284) | 루트 cut·fence·독립 지원·rebind |
| ResidualAuth | Choi, Jeong, Choi, Lee. *ResidualAuth: What Authorization State Must … Preserve under Revocable Delegation?* arXiv:2609.08062 (v1 2026-09-08, v2 2026-09-30) | [abs](https://arxiv.org/abs/2609.08062) | 잔여 상태 이론. abs 페이지 제목은 "Language Agents", v2 HTML 제목은 "Agent Systems"(버전 간 변경) |
| Authorization Succession | Zhu, Wang. *Authorization for Self-Modifying AI Agent Populations: Conserving Authority across Replacement, Forking, and Rollback.* arXiv:2610.00347v1, 2026-09-29 | [abs](https://arxiv.org/abs/2610.00347) | "authorization succession"는 이 논문의 개념 이름이다 |

학회 게재 정보(journal-ref)는 어느 논문에서도 확인되지 않았다(NOT FOUND). 모두 arXiv 프리프린트다.

## 1. 한눈에 보는 결론

- R3 가설의 각 요소는 **선행연구가 이미 다룬다**: 간선 철회와 대안 경로 보존은 VERA, 독립 충분 지원·conjunctive 증인·atomic rebind는 Authorization Revocation, 선택된 부모 계보와 cascading effectiveness는 ResidualAuth, 단일 부모 계보의 ancestor cut은 Authorization Succession이다.
- **CONTINUITY는 위임된 grant, grant 계보, 간선 철회, 독립 지원, conjunctive 승인을 모델링하지 않는다.** 이것은 원본의 결함이 아니라 모델 범위 밖이다(`SCOPE_EXTENSION` / `POLICY_MODEL_MISMATCH`).
- VERA는 보호 효과·finality·진행 중 작업을 다루지 않고 stale 철회 상태는 범위 밖으로 둔다. Authorization Revocation은 효과·fence·진행 중 작업을 다루지만 **간선 철회를 프로토콜 연산으로 다루지 않는다**(자신의 Table 1이 정확한 간선 철회가 확립하는 것은 "권한 결과"이고 남는 문제는 "이미 방출된 obligation과 carrier effect"라고 적는다 [REV-9, REV-13]).
- 다섯 연구는 모두 **완전 중재 또는 완전 매니페스트를 전제**한다(§6). 이 공통 전제가 H2의 출발점이다.

## 2. 아홉 차원 비교

| 차원 | CONTINUITY | VERA | Authorization Revocation | ResidualAuth | Authorization Succession |
|---|---|---|---|---|---|
| **Root Grant 의미** | 서명된 `RootGrant`: principal, 행위자(actor), task root, 권한 집합, delegation scope, tool·server·효과 종류, 필드 조건, 정책, nonce, 만료. 신뢰된 root issuer가 발급 [요약 §5.1; R2 코드] | root = 검증자가 out-of-band로 아는 신뢰 앵커(노드) [요약 §III-A] | root-epoch atom ⟨root, epoch, grant digest⟩. root ledger가 같은 grant·epoch를 ACTIVE로 가질 때 current [요약 §4.1] | 소유자 root는 항상 권한 있음. 소유자 발급 grant는 부모가 없음 [요약 §3; RES-1] | root grant = 수명 envelope. 별도의 population 상한(ceiling)이 현재 노출을 제한 [요약 §4.3] |
| **Delegated Grant 의미** | **정의 없음.** 권한 증가는 "별도로 인증된 grant"로만 [CON-1]. "verified grant edge"는 정리에서만 쓰이고 객체로 정의되지 않음 [CON-2] | 서명된 위임 간선 e=(p,c), 부모 deployer가 서명 [요약 Def. 1]. 별도 grant 유형은 없음 | 위임 grant를 별도 객체로 정의하지 않음. 인증된 derivation edge는 있으나 support는 root atom만 [요약] | grant g = (issuer, subject, 좌표, **optional immutable selected parent**) [RES-1] | successor 세대: par(g)=p, 권한은 부모 잔여 이내 [요약 eq. 9–10] |
| **Authority Lineage** | grant 간 계보 **없음**. envelope·receipt 사슬은 문맥·action 계보(작업 전달 증거)이며 권한은 단조 비증가만 검증 [R2 코드; CON-1] | 서명된 DAG의 root→노드 경로 [요약 §III] | 인증된 부모→자식 provenance(가정 A4)와 obligation graph. support는 root atom만 [요약; REV-5 표] | selected parent 사슬. 부모가 effective여야 effective [RES-1, RES-2] | lineage atom: 부모의 atom 집합에 자기 atom을 더함. 단일 부모 forest [SUC-6; 요약 eq. 1] |
| **Edge / Root Revocation** | grant·permit·release **id 단위** 철회(코드). 간선·계보 철회 없음. 검증 시와 finality 시 두 번 검사 [CON-5; R2 코드] | **간선 철회가 핵심**: 목표 T(e,G)=reach(G)∖reach(G∖{e}). 배치 철회는 합집합이 아님 [VERA-8; 요약 Def. 4]. 루트 철회는 정의 안 됨 | **루트 cut 중심**. 간선 철회는 프로토콜 연산이 아니라 비교 대상 [REV-9; 요약]. fence·quiescence 인증서 | persistent-edge, cascading, Δ-parent 규칙 비교. 루트 grant 철회는 벤치마크에서 사용 [요약] | ancestor cut: 조상 atom을 cut set에 넣으면 모든 후손이 무효 [SUC-7; 요약 Thm 9]. 루트 단위는 re-root |
| **Independent Authorization Support** | 개념 없음. 서로 다른 grant는 무관한 독립 root | 대안 부모 경로가 독립 승인. "alternate authorizing root path must stay active" [VERA-2], 320/320 보존 [VERA-6] | **독립 충분 지원의 antichain**, Theorem 12 [REV-7, REV-11, REV-2] | 다중 incoming grant가 독립 경로(disjunctive) [요약 §4]. 단 ledger는 record당 선택 부모 1개 [RES-6] | **미지원.** 효과는 "하나의 현재 authority witness 또는 새로 발급된 독립 root"에 대해서만 허용 [SUC-3] |
| **Single- / Multi-Parent DAG** | 해당 없음 | **다중 부모 DAG**. APS는 단일 부모 트리라고 대비 [VERA-7, VERA-5] | DAG를 명시하지 않음. 다중 root support는 명시 [요약; REV-11] | principal 단위는 일반 그래프, ledger는 단일 선택 부모 [RES-6] | **단일 부모만.** 다중 부모 병합은 제외 [SUC-1, SUC-2, SUC-6] |
| **Exact Rebind** | 없음. permit은 grant id·action digest에 결속되고, 철회되면 새 bundle로 새 permit이 필요 [코드; 추론] | 없음. 대안 경로가 있으면 노드가 active일 뿐 재결속 절차는 없음 [요약] | **atomic independent rebind**: W′∈Σ, 퇴역 atom∉W′, W′ current. 연산·효과 envelope 보존, 1회용 영수증. 후손은 조상 때문에 rebind를 상속하지 않음 [REV-7, REV-12] | reparent 금지: "an idempotent grant never reparents an authorized target" [RES-5] | 같은 이름의 연산 없음. exact 사후 상태 검사(BindsExact)와 atomic handoff [요약] |
| **Protected Effect / Finality** | `EffectBroker`+`FinalitySink`. 효과 직전 현재 철회·정책 재검사. 인메모리 원자 [CON-5; R2 코드] | **정의 없음.** hot-path는 cached verified revocation state [VERA-3]. 갱신 전파 지연은 범위 밖 [요약 Table II] | protected sink fence/barrier, commitment-admission 사건, pre-fence 수락의 typed receipt, 인증서 [요약 §3.2, §4.4] | hard gate: proposal을 trusted ledger와 대조한 뒤 실행 [RES-3] | protected-effect broker가 직렬화된 ledger 연산 안에서 검사. typed receipt, 멱등성 [요약 §3.2, §5.9] |
| **Trust Assumptions** | 신뢰 발급자·검증기·sink·키 관리. 완전 중재는 "engineering and governance obligation" [CON-4, CON-6, CON-7] | 배포자 공개키를 out-of-band로 고정, 인증된 prefix. 지연·억제 업데이트·Byzantine deployer는 범위 밖 [요약 §III-D] | A1 issuer mediation, A2 authentic evidence, A3 durable linearization, A4 support-provenance completeness, A5 per-sink fence soundness, **A6 registry and manifest completeness**, A7 channel accounting … [REV-5, REV-6] | 인증된 principal·event, trusted ledger. LLM은 보안 경계가 아님 [요약] | **A1 complete mediation**, A2 canonical identity, A3 durable state, A4 complete lineage accounting …, A9 complete revocation fencing. 호출자 인증·공개키 서명은 reference prototype에 없음 [SUC-5; 요약 Table 2] |
| **평가 환경·공개 코드** | 결정론적 코퍼스(위임 도메인 포함) 2,560 attack. 공개 artifact(github.com/zast-ai/continuity, SHA 고정). R1·R2에서 실행 | LangGraph 실행 trace 500개, A2A·AutoGen·CrewAI **형태** artifact, CrewAI 5 workflow. 논문이 밝힌 **익명 artifact** [VERA-4]. E17은 완전한 A2A 스택이 아님 [artifact 정적] | provider-free 17 case(독립 충분 지원 rebind, **conjunctive witness**, A2A delegated task endpoint 범주 포함), 별도 checker 44 mutation. artifact 존재, **공개 URL 없음** [REV-10, REV-4] | 쌍대 합성 벤치마크 + LLM. "experiment repository" 언급, **공개 URL 없음** [RES-4] | 32 registered decision + 외부 runtime 2개(OurArk, Darwin Gödel Machine). 실행 artifact는 **공개 archive 밖** [SUC-4] |

## 3. R3 조건별 선행연구 중복 판정

기호: ✓ = 원문이 명시적으로 다룸, ◐ = 부분적, ✗ = 다루지 않음 또는 명시적 제외, — = 확인 못 함(NOT FOUND).

| R3 조건 | CONTINUITY | VERA | Revocation | ResidualAuth | Succession | 판정 |
|---|---|---|---|---|---|---|
| **G0** 단일 RootGrant, 정상 A→B→C 작업 전달 | ✓ (정상 경로, R2-0의 3단 확장) | 해당 없음 | 해당 없음 | 해당 없음 | 해당 없음 | 신규성 논의 대상 아님. CONTINUITY 범위 안 |
| **G1** 같은 RootGrant 철회 뒤 C의 효과 | ✓ finality 재검사 [CON-5] | ✗ 효과 경계 없음 | ✓ 루트 cut·fence(의미는 다름: pre-fence 수락 정산 허용) | ✓ hard gate + cascading | ✓ cut을 효과마다 검사(A9) | **COVERED_BY_PRIOR_ART**. CONTINUITY는 R2-3a/3b로 이미 확인 |
| **G2** 별도 독립 RootGrant로 승인된 C의 정상 실행 | ✓ 독립 grant id | ✓ 별도 root 경로 | ✓ unrelated-root locality [REV-8, REV-3] | ✓ 그래프 | ◐ 독립 re-root, 단 Thm 9 결론에서 제외 [요약] | **COVERED_BY_PRIOR_ART** |
| **G3** A에게서 유래한 하위 권한만 있는 C | ✗ 표현 불가 | ✓ 간선 철회·root 경로 [VERA-2, VERA-8] | ◐ root 수준만. 중간 간선은 atom이 아님 [REV-9] | ✓ 선택 부모 cascading [RES-1, RES-2] | ✓ 단일 부모 ancestor cut [SUC-7] | **COVERED_BY_PRIOR_ART** (VERA, ResidualAuth, Succession). CONTINUITY는 `SCOPE_EXTENSION` |
| **G4** A에게서 유래한 경로와 독립 경로를 동시에 가진 C | ✗ | ✓ 대안 경로 보존, 320/320 [VERA-2, VERA-6] | ✓ Thm 12 + atomic rebind [REV-7] | ◐ 그래프는 가능, selected-parent ledger 정밀화는 감사된 생성 부분군에 한정 [RES-6] | ✗ 단일 부모 [SUC-1] | **COVERED_BY_PRIOR_ART** (VERA, Revocation). 효과 시점 보존은 Revocation만 |
| **G5** 두 권한이 모두 필요한 conjunctive 승인 | ✗ approval은 미검증, quorum은 prototype 밖 [CON-3] | ✗ **명시적 제외** [VERA-1] | ✓ conjunctive witness, 부분 집합은 효과 불가, 17 case 중 1 [REV-1, REV-4, REV-11] | — 가시 범위에서 확인 못 함(disjunctive 모델) | ◐ 추상 profile만, 참조 구현은 단일 digest [요약]. 형제의 grant를 합치지 않음 [SUC-3] | **COVERED_BY_PRIOR_ART** (Authorization Revocation, 루트 수준·논문과 등록 사례 한정). **VERA는 포함하지 않는다** |

**VERA의 정확한 보장 범위(G5 질문에 대한 답).** VERA의 권한은 "유효한 root→노드 경로가 하나라도 있으면 active"이며(disjunctive), threshold·all-parent 승인은 "다른 target 함수가 필요하다"며 명시적으로 제외한다 [VERA-1]. 따라서 G5의 conjunctive 정책은 VERA의 보장에 **들어가지 않는다**. 이것은 VERA의 결함이 아니라 선언된 비목표다.

**교집합 [추론, 논문 수준만].** 어느 논문도 다음 셋을 동시에 주장하지 않는다: (a) 중간 위임 **간선** 단위의 정확한 철회(VERA), (b) conjunctive와 대안 지원의 조합(Revocation), (c) 보호 효과 시점의 finality와 진행 중 작업의 rebind(CONTINUITY, Revocation). Revocation은 atom이 root-epoch이고 "중간 위임 간선과 agent는 atom이 아니다"(요약)라 간선을 atom으로 확장하는 것이 자명한지는 논문으로 판정할 수 없다. 이것은 **논문 대조로만 보이는 약한 후보**이며 실험으로 확인된 문제가 아니다. 자세한 판정은 [R3_GAP_VERDICT](R3_GAP_VERDICT.md).

## 4. 공식 구현·artifact 확인

확인 방법: 논문 본문의 artifact·코드 서술(원문 검색), arXiv abs 페이지의 링크, 웹 검색 4회(논문마다 1회, 저자·제목·"github/code/artifact" 키워드), VERA가 밝힌 링크의 실제 조회. **논문이 링크하지 않은 URL은 만들지 않았다.**

| 논문 | 논문이 밝힌 것 | 웹 검색 | R3에서의 상태 |
|---|---|---|---|
| CONTINUITY | 공개 artifact `github.com/zast-ai/continuity` | — | SHA `59cfe60…` 고정, R1·R2에서 **실행** |
| VERA | "The artifact is available at …" 익명 호스트 링크 [VERA-4]. 포함: Python API·CLI, E16–E19 trace·스크립트, artifact 점검 | GitHub 저장소 없음 | 링크가 **실제로 존재**한다. 호스트의 파일 API로 목록(73개)과 zip(sha256 `5e7ee1be…`)을 받았다. **소스를 정적으로 검토만 했고 실행하지 않았다.** 아래 참조 |
| Authorization Revocation | "executable durable-ledger artifact"를 평가했다고만 서술 [REV-10]. URL 없음 | 없음 | 공개 여부 **UNKNOWN** |
| ResidualAuth | "experiment repository" 언급, 논문 번들은 end-to-end 재현이 아님 [RES-4]. URL 없음 | 없음 | 공개 여부 **UNKNOWN** |
| Authorization Succession | 실행 artifact·adapter·checker trace는 공개 archive **밖**이라고 명시 [SUC-4]. 외부 runtime(OurArk Genesis v0.1.1·Enoch v0.3.1 Apache-2.0, Darwin Gödel Machine commit a565fd2)은 제3자 코드 [요약] | 없음 | 논문 artifact **비공개**. 제3자 runtime을 이 논문의 artifact로 취급하지 않는다 |

### VERA artifact에 대한 정적 검토 결과 [artifact 정적]

- 소스는 `src/revocation/`(dag, granularity, revocation, prototype, api, crypto, envelope, trace_gen, damage_harness)와 단위 테스트, 실험 E4–E19로 구성된다. 위험 호출(네트워크, 하위 프로세스, `eval`, `pickle` 등)은 `src/`에 없었다.
- `target_set_l2`는 **도달 가능 집합의 차이**(`reachable_with − reachable_without`)로 구현되어 논문의 간선 철회 목표 정의와 일치한다.
- 어댑터는 caller→callee **핸드오프를 후보 간선으로 기록**하고 callee 쪽이 수락하면 서명된 위임 그래프의 간선이 된다. 즉 VERA는 어댑터 규약으로 **작업 전달과 권한 위임 간선을 연결**한다. R3의 "Delegation of Work vs Authority" 구분이 필요한 이유다([R3_DELEGATION_SEMANTICS](R3_DELEGATION_SEMANTICS.md)).
- E17의 "A2A"는 **A2A 형태의 이벤트 스키마**이며 artifact 스스로 "완전한 A2A 프로토콜 스택을 구현했다고 주장하지 않는다"고 적었다.
- conjunctive·threshold·all-parent 구현은 없다. `envelope.py`에 "no M-of-N"이라는 주석만 있다(논문 [VERA-1]과 일치).

### 실행하지 않은 이유

VERA artifact의 자체 점검 스크립트와 단위 테스트를 격리 환경에서 실행하려 했으나, 세션의 자동 권한 분류기가 **내려받은 제3자 코드의 실행을 거부**했다. 우회하지 않았고 재시도하지 않았다. R3의 결론에 필수적이지 않아 정적 검토와 논문 원문 대조로 대체했다. 실행하면 추가로 얻는 것은 "artifact가 논문의 정의대로 소규모 그래프에서 같은 목표 집합을 낸다"는 확인뿐이다. 사용자가 실행을 승인하면 [VERA 격리 환경](../results/r3/commands/r3-vera-install.stdout.txt)(원본 고정 의존성, 전역 설치 없음)이 준비되어 있다.

## 5. 아직 읽지 않은 관련 선행연구 (NOT_READ)

검색 결과와 참고문헌에서 발견했을 뿐 **읽지 않았다**. 다음 선행연구 점검의 출발점이다.

| 항목 | 출처 | 왜 중요할 수 있나 [추론] |
|---|---|---|
| Santos-Grueiro, *When Does Authorization End? Effect Closure at Provider Boundaries.* arXiv:2609.02866 | Authorization Succession의 참고문헌 [원문 확인: 인용] | 효과 시점·provider 경계의 권한 종료. H2와 겹칠 수 있음 |
| *Temporary Authority, Permanent Effects: Commit-Time Authorization* arXiv:2607.10487 | 웹 검색 결과 | finality·commit 시점 인가 |
| *AID-Guard: Stateful Authorization for Delegated …* arXiv:2608.21159 | 웹 검색 결과 | 상태 있는 위임 인가 |
| *Authorization Architectures for Tool-Using AI Agents* arXiv:2609.15906 | 웹 검색 결과 | 인가 아키텍처 개관 |
| *Are You Still the Agent I Authorized? Earned Authority under a Fixed Ceiling for Evolving Agents* arXiv:2607.23586 | Authorization Revocation의 참고문헌 | 진화하는 agent의 권한 상한 |
| IETF draft `draft-watts-oauth-agent-revocation-closure-02` | 웹 검색 결과 | 철회 closure의 표준화 논의 |

## 6. 이 대조의 한계

- **[요약]으로 표시한 항목**(예: Revocation의 support가 root atom만이라는 서술, Succession의 정리 번호와 조건, ResidualAuth의 §4 대안 경로)은 원문 문자열로 확인하지 못했다. 원문 대조가 필요하다.
- 논문 전체를 정독하지 않았다. 부록 일부(ResidualAuth Appendix M·O 등)는 HTML 페이지에서 읽히지 않았다. "확인 못 함(—)"은 **없다는 뜻이 아니라** 읽은 범위에 없다는 뜻이다.
- 어느 논문의 artifact도 이번에 **실행하지 않았다**. 논문 수치(예: VERA 320/320, Revocation 17/17과 44/44)는 저자의 주장이며 우리가 재현하지 않았다.
- 같은 저자(Zhu, Wang)의 두 논문(Revocation, Succession)은 서로의 비교 대상이라 독립 평가로 읽으면 안 된다.
- 완전 중재 전제: Succession은 "our protocol assumes such complete mediation"이라 적고 [SUC-5], CONTINUITY는 "The proof protects only sinks that require a valid permit"이라 적는다 [CON-6]. Revocation의 A6은 "frozen manifest covers every runtime, provider, effect sink, and channel class reachable"를 요구한다 [REV-5]. VERA는 보호 효과 경계를 정의하지 않는다 [VERA-3]. ResidualAuth의 hard gate는 gate를 거치는 proposal만 막는다 [RES-3]. 이 공통 전제는 [R3_GAP_VERDICT](R3_GAP_VERDICT.md)의 H2 전환 근거로 쓴다.
