# R3 — 실험 보고: 3-agent A2A 사슬의 작업 위임, 그리고 선행연구와의 구분

실행일 2026-11-15 (Asia/Seoul). 저장소 `MPEffinc/controllable-agent-lab`, 브랜치 `exp/r3-delegation-lineage`. 기준 commit `20d95d90b84767bd6e8c9d74af1508ccc2fe8d29`(R2 결과).

| 단계 | commit |
|---|---|
| 사전 고정(가설·위협 모델·조건·예측·선행연구 대조) | `d7bfe9b610474294d5c0ad94ee4302d663c3db51` |
| 실험 코드·테스트(공식 시행 전) | `de674d9b4bc3d690f5d57d53db2ad6499c7374bc` |
| 공식 시행·정적 검사·reference model 결과 | `9ec25b2` (전체 SHA는 `git log`) |
| 이 보고서·판정·매트릭스 갱신 | 이 문서를 포함하는 다음 commit |

원본 CONTINUITY: SHA `59cfe60930d247d1890b366ded686c718020a11e`, 수정 없음. 유료 모델 호출 0, 외부 서비스 변경 없음.

**결론 한 줄.** 원본 CONTINUITY가 의미를 정의하는 조건(G0, G1a, G1b, G2)은 3-agent A2A 사슬에서도 사전 예측대로 `IN_SCOPE_PASS`였다. 그러나 이것은 **작업의 위임**에 대한 결과이며, 파생 권한·독립 지원·conjunctive 승인(G3–G5)은 CONTINUITY의 `RootGrant` 모델이 **표현하지 못하므로**(정적으로 확인) 실행하지 않았고 `UNDEFINED_AUTHORIZATION_SEMANTICS`로 기록했다. G3–G5가 묻는 성질은 네 선행연구가 이미 정의한다(`COVERED_BY_PRIOR_ART`). **새 취약점도 연구 공백도 확인하지 못했다.**

## 1. 요약 (보고 순서)

| 항목 | 내용 |
|---|---|
| 무엇을 했나 | R2의 A2A 어댑터를 수정 없이 재사용해 Agent A→B→C 사슬(원본 3단계 파이프라인을 memory@A, gateway@B, adapter@C로 배치)에서 G0, G1a, G1b, G2를 원본 함수로 실행했다. CONTINUITY가 표현하지 못하는 G3–G5는 소스의 정적 검사(S1–S7)와 선행연구 **정의**의 독립 재구현(reference model)으로 대체했다 |
| 왜 했나 | R2는 RootGrant가 실행자 B를 미리 지정한 **작업 위임**만 시험했다. 동적 재위임(권한 위임)에서 기존 연구가 이미 해결한 부분과 아직 확인되지 않은 부분을 구분하려 했다 |
| 실제 결과 | 실행 4조건 모두 독립 oracle 만족, 효과는 정상 2건(G0, G2)뿐. 사전 예측 7/7 일치. 재현 실행 동일. 정적 예측 S1–S7 성립. reference model이 사전 기대와 일치 |
| 결론 | 계보·간선·독립 지원·conjunctive에 관한 R3 가설의 각 요소는 선행연구가 이미 다룬다. CONTINUITY는 그 모델을 제공하지 않으며 이는 `SCOPE_EXTENSION`이다. 가설을 종료한다 |
| 남은 문제 | 논문 수준의 교집합(간선 단위 철회 × conjunctive·독립 지원 × 효과 시점 finality와 진행 중 작업 rebind)은 어느 논문도 주장하지 않으나 **명확한 보안 문제로 확인되지 않았다**. 다섯 연구가 공통으로 전제하는 완전 중재가 미검증이다 |
| 다음 연구 질문 | [R3_GAP_VERDICT](R3_GAP_VERDICT.md): H2(동적 집행 범위)로의 전환과 그 선행연구 점검 |

## 2. 실행한 것과 실행하지 않은 것

| 조건 | 실행 | 이유 |
|---|---|---|
| G0 단일 RootGrant, 정상 A→B→C | **RUN** | CONTINUITY가 의미를 정의함 |
| G1a 같은 RootGrant가 C의 permit 발급 뒤에 철회 | **RUN** | 정의됨 |
| G1b 같은 RootGrant가 B→C 사이에 보존된 동안 철회 | **RUN** | 정의됨 |
| G2 루트 A 철회 뒤 독립 RootGrant로 승인된 C의 실행 | **RUN** | 정의됨(독립 grant id) |
| G3 A에게서 유래한 하위 권한만 있는 C | NOT_RUN_ON_CONTINUITY | 파생 의존의 의미가 CONTINUITY에 없다. 우리가 의미를 발명하면 원본 보장과 동등한 실험이 아니다 |
| G4 유래 경로와 독립 경로를 모두 가진 C | NOT_RUN_ON_CONTINUITY | 독립 지원·rebind 개념이 없다 |
| G5 두 권한이 모두 필요한 conjunctive 승인 | NOT_RUN_ON_CONTINUITY | `approval_digest`는 검증되지 않고 quorum은 prototype 밖 |

**G1은 계보 시험이 아니다.** G1의 "같은 RootGrant"는 A·B·C가 같은 grant를 공유한다는 뜻이 아니라, 신뢰된 발급자가 C를 actor로 발급한 **하나의 grant**를 철회하는 것이다. G1이 보이는 것은 "철회가 작업 사슬의 길이(2단 → 3단)와 무관하게 효과 시점에 반영된다"는 것이며 권한 의존 전파가 아니다.

## 3. 실행 결과 (G0–G2)

설정: 에이전트 identity는 A `…/workspace/1`, B `…/workspace/0`, C `…/workspace/2`. 모든 RootGrant는 발급자(`key:authority`)가 C를 actor로 서명했다. 루트 A는 시드 1016(principal `did:example:user:46`), 독립 루트 X는 시드 1029(principal `did:example:user:59`). run-01 이벤트 140, A2A 요청·응답 16쌍, 단계 실행 15, 검증 결정 5, Permit 3, finality 시도 3, 철회 3.

| 조건 | Verifier 결정(요청자) | Permit | Finality 결정 / 이유 코드 | 효과 | 독립 oracle | 정상 과제 | R3 판정 |
|---|---|---:|---|---:|---|---|---|
| G0 single root chain | C: 허용 | 1 | C: 성공 `EXECUTED` | 1 | 만족 | 성공 | IN_SCOPE_PASS |
| G1a same root revoked in flight | C: 허용 | 1 | C: 거부 `E_REVOKED_AT_FINALITY` | 0 | 만족 | 해당 없음 | IN_SCOPE_PASS |
| G1b same root revoked while retained | C: 거부 [`E_REVOKED_ROOT_GRANT` (+연쇄 3)] | 0 | — | 0 | 만족 | 해당 없음 | IN_SCOPE_PASS |
| G2 independent root preserved | C: 거부 [`E_REVOKED_ROOT_GRANT` (+연쇄 3)]<br>C: 허용 | 1 | C: 성공 `EXECUTED` | 1 | 만족 | 성공 | IN_SCOPE_PASS |

`연쇄`는 루트 오류 때문에 따라붙는 `E_UNDISCHARGED_ASSUMPTION:*` 코드 수다(R2에서와 같은 원본 동작). 검증기의 `allowed`나 sink의 성공 반환은 oracle의 근거가 아니다. oracle은 R2의 독립 oracle(해시 `1a5619da…`)을 **수정 없이** 썼고 세계 스냅샷으로 판정한다.

**요구된 기록 필드(G0, G2에서 확인).** 

| 필드 | 값 |
|---|---|
| Root Principal | grant의 principal(`did:example:user:46`, G2는 `…:59`도) |
| Current Actor | finality 시점의 호출자: C의 identity |
| Delegating Actor | ingress→A, A→B, B→C. 모두 `WORK_DELEGATION` |
| Parent / Independent Authority Support | `None` / `[]`. support 종류는 모두 `ROOT` |
| Grant Issuer | `key:authority` |
| Signed Delegation Evidence | 단계 영수증 3개(memory@A `key:memory`, gateway@B `key:gateway`, adapter@C `key:adapter`). **권한 위임 증거는 `NONE`** |
| Revoked Grant / Edge | 철회된 grant id. 간선은 `NOT_REPRESENTABLE` |
| Permit, Finality Decision, Actual Effect | 원본이 발급·반환한 값과 세계에 들어간 효과(`mailto:customer:1016`, G2는 `…:1029`) |
| Independent Oracle Verdict | 만족 |

## 4. 정적 표현력 검사 (S1–S7, 사전 고정 예측)

원본 소스의 구조만 검사했고 어떤 시나리오의 보안 결정도 호출하지 않았다. 7개 예측이 모두 성립했다.

| ID | 예측 | 관찰된 사실 |
|---|---|---|
| S1 | `RootGrant`에 부모·계보·간선·파생 필드 없음 | 필드: grant_id, issuer, principal, actor, task_root, authority, delegation_scope, 허용 tool·server·효과 종류, 데이터 등급, 필드 조건, 정책 3개, provenance·context root, nonce, 만료, 서명. 계보 비슷한 이름 0 |
| S2 | `RuntimeState` 필드는 4개뿐 | policy_id, policy_digest, policy_epoch, revoked_ids |
| S3 | `revoked_ids` 소속 검사는 grant·release·root grant·permit id뿐 | 피연산자 정확히 5종: `grant.grant_id`, `release.release_id`, `context.root_grant_id`, `permit.grant_id`, `permit.permit_id` |
| S4 | `approval_digest`는 검증·finality가 읽지 않음 | 속성 읽기 0건, 필드 정의 1건, 문자열 상수 1건(`/context/approval_digest`) |
| S5 | `parent_grant_id` 인자는 거부 | `TypeError: RootGrant.__init__() got an unexpected keyword argument 'parent_grant_id'` |
| S6 | `verify_bundle`·`FinalitySink.execute` 소스에 parent·lineage·quorum·approver·edge 없음 | 일치 0건. (사전 예측 밖의 정보용 검색: 검증기·sink·broker 클래스 전체에서도 0건) |
| S7 | `delegation_scope`는 부분집합·소속 비교로만 쓰이고 grant를 만들지 않음 | 부분집합 4, 소속 4, 기타 0, `core.py`의 `RootGrant` 생성자 호출 0 |

**해석 [추론].** S1–S7이 성립하면 CONTINUITY에서 별도로 서명된 grant는 **독립 루트**다. 부모 참조(조건 a), 의존 의미(조건 b), 효과 시점의 의존 검사(조건 c)가 모두 없기 때문이다([R3_DELEGATION_SEMANTICS §4](R3_DELEGATION_SEMANTICS.md)). 이것은 모델 범위의 한계이며 결함이 아니다.

## 5. Reference model: 논문 정의에서 기대되는 G3–G5 (원본 artifact의 결과가 아님)

`REFERENCE_MODEL_FROM_PAPER_DEFINITION`. 사전 고정한 소규모 그래프에서 각 논문의 **정의**를 독립적으로 계산한 것이며 어떤 시스템의 측정도 아니다. 사전 기대와 모두 일치했다(불일치 0).

| 그래프 | VERA | Authorization Revocation | ResidualAuth | Authorization Succession |
|---|---|---|---|---|
| **G3** R_A→A→C | e2 철회: 대상 {C}, C 비활성. 루트 간선 e1 철회: 대상 {A, C} | 루트 cut: C 무권한. 간선 철회: **표현 불가** | 두 철회 모두 C 비유효(선택 부모 cascading) | 두 철회 모두 C 무효(조상 cut) |
| **G4** G3 + R_X→C | e2 철회: 대상 {}, C **유지**. e1 철회: 대상 {A}, C 유지 | 루트 cut: C **유지**, 독립 지원으로 rebind 가능. 간선: 표현 불가 | 그래프: 유지. 선택 부모 ledger: e2에 묶이면 **무효**, e3에 묶이면 유효 | **표현 불가**(다중 부모 제외) |
| **G5** C가 두 root 모두 필요 | **표현 불가**. OR 의미를 쓰면 C가 활성으로 남아 AND 정책 위반 | 한쪽 root 철회 시 무권한. 엄격한 부분집합은 권한 못 줌 | 확인 못 함(NOT FOUND) | **표현 불가**(구현 범위) |

## 6. 관찰

### 6.1 [실험으로 확인]
1. 작업 사슬이 2단(R2)에서 3단(R3)으로 늘어도 같은 이유 코드가 나왔다: 정상 실행(`EXECUTED`), 철회 뒤 permit(`E_REVOKED_AT_FINALITY`), 철회 뒤 보존 작업(`E_REVOKED_ROOT_GRANT`), 독립 루트 유지.
2. A, B, C가 각각 한 단계씩 호스팅해 만든 증거 묶음은 원본 `materialise()` 결과와 **바이트 단위로 같다**(3개 시드 단위 테스트). 입력이 같으므로 원본의 결정도 같다.
3. 중간 agent A·B는 증거를 확장할 뿐 권한이 없다. 모든 권한은 발급자가 ingress에서 C에게 직접 부여했다.

### 6.2 [논문 근거 + 정적 확인]
4. G3–G5의 성질은 선행연구가 각각 정의한다: 파생 의존(VERA, ResidualAuth, Succession), 대안 경로 보존(VERA, Revocation), conjunctive 증인(Revocation만). VERA는 conjunctive를 **명시적으로 제외**한다 [VERA-1]. 근거와 인용은 [선행연구 대조](R3_PRIOR_ART_COMPARISON.md).
5. CONTINUITY는 위 어느 것도 표현·검증하지 않는다(S1–S7).

### 6.3 [추론]
6. 이 조건들에서 새 취약점이 나오지 않은 것은 설계상 자연스럽다. G0–G2는 CONTINUITY가 이미 시험한 결함군(R2)의 3단 확장이고, G3–G5는 의미가 없는 곳이라 판정할 대상이 없다.
7. 이 실험은 R2의 결론을 약간 넓혔을 뿐이다. 새로 알게 된 가장 큰 사실은 실행 결과가 아니라 **의미의 구분**이다: 어떤 연구에서는 작업 핸드오프가 곧 권한 간선(VERA 어댑터)이고 다른 연구에서는 아니다(CONTINUITY, Succession). 이 규약은 형식 모델 밖의 정책 결정이다.

## 7. 신뢰도 검증

| 검사 | 결과 |
|---|---|
| 사전 고정 | config는 `d7bfe9b` 이후 변경 없음, 결과 commit보다 앞섬(`verify_saved.py`가 git 순서로 확인) |
| 예측 대조 | 7/7 일치(실행 4 + 정적·reference 근거로 고정된 3) |
| 재현 | run-02 결과 동일(결정·이유·단계 배치·효과·판정) |
| 원본 무수정 | 실행 때마다 pinned SHA·clean tree 확인. 원본 pytest 30개를 실행 후에도 통과 |
| 테스트 | R3 22개(정적 검사기 7 + reference model 9 + 배치 충실성·oracle 래퍼 6), R2 38개 모두 통과 |
| 테스트 강도 | 정적 검사기·reference model 변이 12개 모두 검출 |
| 인용 | 문서가 쓴 선행연구 인용 41개가 원문에 문자열 그대로 존재 |
| 저장 증거 재생 | `python3 experiments/r3/verify_saved.py` VERIFIED |

## 8. 이탈·실패·한계

- **VERA artifact를 실행하지 못했다.** 내려받은 제3자 코드(자체 점검 스크립트, pytest)의 실행 시도가 세션의 자동 권한 분류기에 의해 거부되었고, 우회하지 않았으며 재시도하지 않았다. 정적 검토와 논문 원문 대조로 대체했다. 필수 증거가 아니다.
- **작업 중 VM 메모리 부족(OOM)으로 재부팅**되어 `/tmp`의 임시 도우미 스크립트가 사라졌다. 같은 내용으로 다시 만들었다. 시행·커밋 도중이 아니었고 증거에 영향이 없다. 사전 고정 commit은 재부팅 이후다.
- 선행연구 근거 도구(`research_provenance.py`)는 사전 고정 commit 전에 두 번 보강했다(제목 변경 메모, 인용 추가). 결과를 본 뒤의 변경이 아니다.
- **원본이 아닌 것**: reference model은 논문 정의의 독립 재구현이다. Authorization Revocation, ResidualAuth, Authorization Succession의 artifact는 공개된 것을 찾지 못했고 어느 논문의 수치도 재현하지 않았다.
- **범위**: 결정론적 순차 일정, 조건당 1회, 스크립트된 정직한 agent. 일반성이나 공격 성공률을 말하지 않는다. G0–G2는 CONTINUITY의 기존 시험(R2)의 연장이라 정보량이 크지 않다.
- 정책 epoch 교체, 만료, 동시·분산 finality, 전송계층 신원 인증, 동적 효과 경로 완전성은 이번에도 NOT_RUN이다.

## 9. 재실행

```bash
# 단위 테스트(R2 환경 사용)
experiments/r2/.venv/bin/python -m unittest discover -s experiments/r3 -p "test_r3_*.py"
# 시행. 새 이름·새 출력 경로를 쓴다(기존 증거를 덮어쓰지 않는다)
python3 scripts/r3_run.py --name run-03 --timeout 300 -- experiments/r2/.venv/bin/python experiments/r3/scenario.py --output-dir results/r3/run-03
python3 experiments/r3/oracle.py --events results/r3/run-03/events.jsonl --world results/r3/run-03/world_state.json --output results/r3/oracle-03.json
# 정적 검사와 reference model
experiments/r2/.venv/bin/python experiments/r3/expressiveness_check.py --output results/r3/expressiveness-02.json
python3 experiments/r3/reference_model.py --output results/r3/reference-model-02.json
# 저장 증거 검증(외부 소스·venv·API 불필요)
python3 experiments/r3/verify_saved.py
```

## 10. 산출물 색인

| 종류 | 경로 |
|---|---|
| 사전 고정 | [R3_HYPOTHESIS_PREREG](R3_HYPOTHESIS_PREREG.md), [config.json](../experiments/r3/config.json), [선행연구 대조](R3_PRIOR_ART_COMPARISON.md), [위임 의미 분석](R3_DELEGATION_SEMANTICS.md) |
| 코드 | [scenario.py](../experiments/r3/scenario.py), [oracle.py](../experiments/r3/oracle.py), [expressiveness_check.py](../experiments/r3/expressiveness_check.py), [reference_model.py](../experiments/r3/reference_model.py), [classify.py](../experiments/r3/classify.py), [verify_saved.py](../experiments/r3/verify_saved.py), [mutation_check.py](../experiments/r3/mutation_check.py), [research_provenance.py](../experiments/r3/research_provenance.py) |
| 테스트 | [test_r3_static.py](../experiments/r3/test_r3_static.py), [test_r3_wiring.py](../experiments/r3/test_r3_wiring.py) |
| 결과 | [results/r3/](../results/r3/): run-01, run-02-replicate, oracle, expressiveness, reference-model, expectation-check, [condition_summary.csv](../results/r3/condition_summary.csv), research-provenance, mutation-check, [analysis-manifest](../results/r3/analysis-manifest.json), 명령 기록 |
| 판정 | [R3_GAP_VERDICT](R3_GAP_VERDICT.md), [RESEARCH_GAP_MATRIX](RESEARCH_GAP_MATRIX.md), [R3 매트릭스 CSV](RESEARCH_GAP_MATRIX_R3.csv) |
