# R2 — 의미 정렬: R1 Acceptance ↔ CONTINUITY Finality

작성 시점: 2026-11-15 (Asia/Seoul), **R2 시행(trial) 실행 전에 작성·커밋한 사전 고정 문서**다. 시나리오·인가 조건·예측은 [config.json](../experiments/r2/config.json)에 있으며 결과를 본 뒤 고치지 않는다. 변경이 필요하면 이유를 적은 새 커밋으로만 한다.

범위: 원본 CONTINUITY(SHA `59cfe60930d247d1890b366ded686c718020a11e`)를 R1과 같은 A2A 위임 경로(Agent A → Queue → Agent B → 보호 효과)에 연결하기 위한 **의미 대응**이다. 새 방어 방법이 아니며, 원본 보안 검사를 수정·우회하지 않는다.

## 0. 근거 표기

| 태그 | 의미 |
|---|---|
| [원본 코드] | 고정 SHA의 `src/continuity/core.py`, `experiment.py`, `tests/`를 직접 읽고 확인 |
| [원본 ARTIFACT] | 원본 저장소 `ARTIFACT.md`가 스스로 주장하는 범위 |
| [논문 §] | Zheng & Yang, *CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls*, arXiv:2609.05269v1, 2026 ([링크](https://arxiv.org/html/2609.05269v1)). **WebFetch 요약을 통한 2차 확인**이라 문구는 원문 대조 전까지 근사치로 본다 |
| [R1 코드] | `experiments/r1/scenario.py`, `oracle.py`와 R1 문서 |
| [추론] | 위 근거로부터의 해석. 확인된 사실이 아니다 |

## 1. 원본 보안 객체의 계약 (직접 확인)

| 객체 | 신뢰된 생성 주체 | 검증 조건 (`verify_bundle` 등) | 사용 위치 | 보호하는 속성 |
|---|---|---|---|---|
| `RootGrant` | 루트 권한 발급자(`trusted_root_issuers`의 키) | 서명, 발급자 신뢰, 루트 envelope 생산자가 신뢰된 ingress, **`grant_id`가 `RuntimeState.revoked_ids`에 없음**, 만료, 루트 문맥(nonce·principal·actor·task_root·정책·provenance/context root)과 정확히 일치, 권한·scope·tool·server·effect class·데이터 등급·필드 제약(`field_constraints`) 충족 | 증거 체인의 시작점. `ProofBundle.root_grant` | 권한의 인증된 출처(누가·어떤 task에서·어떤 행위자에게·어떤 범위까지) |
| `SecurityContext` | 루트: 신뢰된 ingress(루트 envelope 안). 이후: 각 구성요소가 보존·축소만 가능 | 단계마다 보존 필드 불변, authority/delegation scope는 **축소만**, taint 하향 금지, 정책 epoch 후퇴 금지. 최종: 신원 완비, 현재 정책 일치(`E_STALE_POLICY`), 만료, nonce, **철회 여부**, 연산 권한, scope, 데이터 등급, 목적지 존재, 신뢰된 tool manifest | 모든 `Envelope`에 포함 | 주체·권한·정책 문맥의 연속성 |
| `Envelope` | 루트: ingress 키. 이후: 해당 단계 구성요소 키 | 서명, 시퀀스 +1, 영수증과 digest로 연결, 단계별 signer·role·contract가 배포 정책과 일치 | 체인의 각 노드 | 위변조 증거와 단계 간 문맥·action 연속성 |
| `ProofBundle` | 구성요소와 신뢰 발급자들이 조립. 전체 서명은 없음 | 체인 길이=영수증 수+1=파이프라인 길이, 영수증이 알리는 변경 필드를 **검증기가 다시 계산**해 대조, 허용되지 않은 변환은 신뢰된 witness 요구 | 검증기 입력. `bundle_digest`로 permit에 결속 | 증거의 자기 인증(전송 경로를 믿지 않아도 됨) |
| `ContinuityVerifier.verify_bundle` | 배포 정책(`DeploymentPolicy`)을 가진 신뢰 구성요소 | 위 모든 검사. **`deployment.runtime_state`를 호출 시점에 읽음** | 권한 부여 결정 | 허용 여부와 이유 코드(`Decision`) |
| `ContinuityVerifier.issue_permit` | 검증기의 permit 서명 키 | `Decision.allowed`가 참일 때만 발급(아니면 예외). 최종 문맥에 actor·task_root·nonce·만료 필요 | 허용 직후 | 한 번만 쓸 수 있는 효과 허가(principal·subject·grant·audience·**action digest**·정책·nonce·멱등 키 결속, 만료 = min(문맥 만료, now+60)) |
| `EffectBroker.dispatch` | 보호 효과의 유일한 진입점(배포가 보장해야 함) | permit이 없으면 `E_UNMEDIATED_PATH`. `require_permit=False`는 원본의 `IncompleteMediation` ablation | 효과 직전 | 완전 중재(permit 없이는 효과 불가) |
| `FinalitySink.execute` | 보호 효과 종류별 sink(신뢰 구성요소) | permit 서명자, 서명, **audience**, **호출자 subject(명시적 입력)**, **action digest**, **현재 정책**, **현재 철회 상태(grant_id 또는 permit_id)**, 만료, 멱등 재실행, nonce 1회 소비. 모두 통과한 **같은 호출 안에서** `world.apply` | 효과 적용 | 효과 시점의 현재 권한과 정확한 action·행위자 결속 |
| `RuntimeState` | 배포의 신뢰된 상태 권위(논문 TCB의 "revocation state") | 불변 dataclass(`policy_*`, `revoked_ids`). **`execute`의 인자로 호출자가 넘김** | 검증기(배포 정책 안)와 sink(인자) 양쪽 | 철회·정책 신선성 |

[원본 코드] 모두. 추가로 [원본 ARTIFACT]의 주장 8: "sink는 subject, 정확한 action, 현재 정책, 철회, 만료, nonce, 멱등성을 **효과 직전에** 검사한다." [원본 ARTIFACT]의 범위: "에이전트 planner가 action을 제안한 **이후**의 결정론적 보안 경계를 평가하며 planner는 적대적으로 모델링한다."

[논문 §3.1, §3.3] planner는 TCB가 아니고, TCB는 검증기·permit 발급자·철회 상태·nonce/멱등 ledger·중재된 finality sink와 배포 정책·신뢰 발급자·키 관리를 포함한다. [논문 §9.7, §12] 완전 중재는 "공학·거버넌스 의무"이며 효과 경로 열거는 보장하지 않는다. [논문 §12] A2A는 구현 범위 밖(production MCP/A2A 통합 아님). **따라서 R2의 A2A 연결은 원본 보장의 범위 확장(Scope Extension)이다.**

## 2. 사건 대응표 (R1 ↔ 원본 CONTINUITY)

| R1 사건 | 원본 CONTINUITY에서 가장 가까운 사건 | 판정 |
|---|---|---|
| `grant` (신뢰 ledger 항목: root·principal·support·recipient, 비암호) | `RootGrant` 서명 발급(principal·**actor**·task_root·권한·필드 제약·nonce) | PARTIAL — R1 grant는 **행위자(agent)에 결속되지 않음**. CONTINUITY는 `actor`에 결속 |
| `message_created` (A가 메시지 생성) | 신뢰 ingress가 서명한 루트 envelope + provenance/context manifest | PARTIAL |
| `delegation_requested` (A→B) | 단계 전이(`Component.apply` + `TransitionReceipt`)와 `ProofBundle`을 A2A 메시지로 전달 | PARTIAL — **동적 actor 변경은 정의되어 있지 않다**: actor는 루트 grant에서 정해지고 단계 간 보존된다. 권한 증가는 "별도로 인증된 grant"로만 가능[논문 §5.5 C4] |
| `queue_enqueued` / `queue_dequeued` | 대응 없음. 큐는 신뢰하지 않는 전송 경로이며 증거가 자기 인증을 한다. 보유 시간은 문맥 `expires_at`만이 제한 | **NON_EQUIVALENT_SEMANTICS** — 큐 시점 의미 없음 |
| `policy_decision` (Progent가 인자 규칙으로 allow/deny) | `verify_bundle` 결정과 `issue_permit` | PARTIAL — 메커니즘이 다르다(인자 규칙 ↔ 서명된 증거 체인·계약) |
| `sink_accept` (수락, receipt 생성) | **별도 대응 없음.** 가장 가까운 것은 `FinalitySink.execute`가 모든 검사를 통과해 `world.apply` 직전에 도달한 순간 | **NON_EQUIVALENT_SEMANTICS** — 수락과 commit이 한 호출 |
| `revoke` (root cut) | `RuntimeState.revoked_ids`에 루트 grant id 추가 | MATCH(루트 범위 철회). 단 CONTINUITY는 grant id별이다 |
| `sink_fence` / `sink_cancel` (cancel-pending) | 대응 없음. pending 상태 자체가 없다 | **NON_EQUIVALENT_SEMANTICS** |
| `sink_commit` (outbox append) | `FinalitySink.execute` 안의 `world.apply(action)`과 서명된 `OutcomeReceipt` | accept↔commit 간격에 대해서는 NON_EQUIVALENT, "실제 효과가 메모리 세계에 append"는 MATCH |
| grandfather (수락 후 철회, 이후 commit 허용) | 허용되지 않음. permit이 철회 전에 발급되었어도 효과 시점에 `E_REVOKED_AT_FINALITY` | **NON_EQUIVALENT_SEMANTICS** |

## 3. Acceptance와 Finality를 동일시하지 않는 이유

| 항목 | R1 | 원본 CONTINUITY |
|---|---|---|
| 권한 검사 시점 | `sink_accept`(IMMEDIATE_CUT_AT_ACCEPT) | permit 발급 시(`verify_bundle`)와 **효과 직전**(`FinalitySink.execute`) 두 번 |
| 수락 ↔ commit | 분리 가능. 수락 시점에 유효했던 요청은 철회 뒤 commit도 정상(grandfather) | 분리 없음. 검사와 효과가 한 호출 [원본 코드]. 논문도 인메모리 원자성을 단순화 가정으로 둔다 [논문 §9.6] |
| 철회 후 이미 발급된 허가 | R1에는 permit 객체가 없다 | 효과 시점에 거부 |
| 철회 상태의 출처 | 합성 ledger→Progent 정책 재설정 | 신뢰된 상태 권위의 `RuntimeState` |
| 대기 중 작업 취소 | `cancel_pending` fence(테스트베드 통제) | 개념 없음 |

R2 판정 의미: **IMMEDIATE_CUT_AT_FINALITY** — 효과가 finality를 통과한 시점 이전에 해당 grant의 철회 사건이 있으면 위반이다. 이 의미는 R1 기본 의미(수락 시점 검사, grandfather 허용)와 같지 않다. R1 oracle을 재사용할 때는 CONTINUITY의 "수락=commit(인접 사건)"을 투영해서 쓰고(§6), grandfather·fence 렌즈는 **적용 불가**로 분리한다. R2-3a(철회 전에 발급된 permit으로 철회 후 finality 시도)는 R1 grandfather 조건의 대응물이 **아니며** CONTINUITY 계약 자체의 시험이다.

## 4. 어댑터 설계

### 4.1 원본 3단계 파이프라인을 변경 없이 A2A 경로에 배치

원본 `build_infrastructure()`의 파이프라인(`memory → gateway → adapter`)과 계약(contracts), 신뢰 발급자, tool manifest, `RuntimeState`를 **수정 없이** 쓴다. 바뀌는 것은 각 단계가 **어느 프로세스(에이전트)에서 실행되는가**뿐이다.

| 원본 단계(변경 없음) | A2A 경로 배치 | 서명 키 | 실행 위치 |
|---|---|---|---|
| `memory` | Agent A의 보존 작업 | `key:memory` | A의 호스트 shim |
| `gateway` | A→B 위임 경계의 정책 게이트웨이 | `key:gateway` | A 쪽 shim(위임 송신단) |
| `adapter` | Agent B의 도구 어댑터(별칭→정식 목적지 변환, 신뢰된 directory의 witness) | `key:adapter` | B의 호스트 shim |

A가 직접 시도(`direct_attempt`)할 때는 A가 세 단계를 모두 호스팅한다(R1 direct 일정과 같은 구조). 에이전트가 단계별로 실행해 만든 `ProofBundle`이 원본 `materialise()`의 결과와 **바이트 단위로 같음**을 시행 전에 확인했다(임시 시드 4개; 정식 단위 테스트는 `experiments/r2/test_bridge.py`). [실험으로 확인 — 점검 스크립트 실행]

### 4.2 신뢰 구분

| 구성요소 | 신뢰 | 가진 것 | 비고 |
|---|---|---|---|
| 루트 발급자·ingress·provenance/context 발급자·directory | 신뢰 | 해당 Ed25519 키 | 원본 `make_scenario`가 이 발급 경로다. 에이전트 코드는 직접 부르지 않는다 |
| 상태 권위(`RuntimeState`) | 신뢰 | 철회 집합, 정책 triple | 호출 시점의 **현재** 값을 검증기·sink에 공급. 에이전트가 상태를 넘길 수 없다 |
| Permit 서비스 | 신뢰 | `key:verifier` | 호출마다 현재 상태로 검증기를 새로 구성. audience·now는 서비스가 정하며 요청자가 정하지 않는다 |
| 효과 게이트웨이(`EffectBroker`+`FinalitySink`+`SimulatedWorld`) | 신뢰 | `key:sink`, 세계의 유일한 쓰기 권한 | **유일한 효과 sink**. R1의 receipt/outbox 저장소는 쓰지 않아 이중 집행이 없다. 호출자 신원은 핸들러에 결속된 값을 쓴다(페이로드가 아님) |
| 단계 호스트 shim | 코드는 신뢰, 변환 논리는 비신뢰 | 해당 단계 서명 키 | 비신뢰 변환이 보안 필드를 바꾸면 검증기가 `E_NOT_PRESERVED` 등으로 거부 |
| Agent A, B의 판단 논리 | **비신뢰** | 자기 호스트 shim의 단계 키만 | R1과 같이 **결정론적 스크립트**. 실제 LLM이 아니며 적응형 공격자가 아니다 |
| 큐 | **비신뢰** | 없음 | 보존 중 증거를 바꿀 수 있다(NC-queue_tamper) |
| 공격자 키(`key:rogue`) | 비신뢰, 공격자 소유 | 위조 시도에만 사용 | 배포 정책의 어떤 신뢰 집합에도 없다 |

### 4.3 어댑터가 직접 구현한 것 (원본 기능과 분리)

| 어댑터 코드 | 하는 일 | 원본 보안 로직과의 관계 |
|---|---|---|
| `proof_codec.py` | A2A 메시지로 증거를 옮기기 위한 엄격한 JSON 인코더/디코더 | 서명되는 값을 보존한다(round-trip의 digest·동등성 테스트). 증거를 만들거나 고치거나 재서명하지 않는다. 실패 시 fail-closed |
| 호스트 shim | 원본 `Component.apply`를 에이전트가 호출하는 반복 | 원본 호출 그대로. 변환 논리는 원본 `_representation_transform`과 `_alias_witness`(비공개 helper를 수정 없이 재사용) |
| 신뢰 서비스(상태 권위, Permit 서비스, 효과 게이트웨이, directory) | 원본 객체를 **올바른 시점의 현재 상태**와 결속해 호출 | 원본 검사를 약화하지 않는다. ablation 때만 원본 플래그(`enforce_*`, `require_permit`, `disabled_checks`)를 원본 `run_system`과 같은 방식으로 켠다 |
| 시나리오 구동기 | A2A 전송, 큐, 일정, 스크립트 행동, 이벤트 기록 | 원본에 없는 부분 |
| 독립 oracle | 이벤트·세계 스냅샷만으로 판정 | 원본 코드를 import하지 않는다 |

### 4.4 Trusted Computing Base와 가정 (어댑터 한계)

1. **프로세스 내 신뢰 분리**: 한 Python 프로세스 안이며 OS 격리·키 격리가 없다. 신뢰 분리는 API 규율이다. 공격자 행동은 공격자가 가질 수 있는 키(`key:rogue`, 자기 호스트의 단계 키)만으로 스크립트한다.
2. **호출자 신원**: `caller_subject`는 핸들러에 결속한다. 실제 A2A 전송계층(OAuth/mTLS 등)의 인증을 검증하지 않는다. 원본도 호출자 subject를 "명시적 입력"으로 둔다[논문 §5.4/§7.4].
3. **상태 권위는 항상 최신**: 분산 복제 지연, 부분 실패, check-then-effect 경쟁(TOCTOU)은 이 순차 일정에서 나타나지 않는다. 논문도 원자성을 단순화 가정으로 둔다[논문 §9.6].
4. **완전 중재는 구성으로 가정**: 보호 효과의 경로는 `EffectBroker` 하나뿐이다. 이것은 구성이지 검증이 아니다(H2의 **미검증** 영역).
5. **로그 진본성**: oracle 입력(이벤트, 세계 스냅샷)이 진본이라고 가정한다(R1과 같은 가정).
6. **시계**: 논리 시계는 원본 `NOW`로 고정이다. 만료 의미는 시험하지 않는다.
7. **키**: 시행마다 새 Ed25519 키가 생성된다(원본 `Signer`). 이유 코드와 효과는 결정론적이고 서명·digest 바이트는 시행마다 다르다.

### 4.5 원본 무수정 확인 방법

- 실행 때마다 `third_party/continuity`의 HEAD SHA와 `git status --porcelain`(깨끗해야 함)을 확인하고 실패하면 중단한다. 소스 파일 SHA256은 manifest에 기록한다.
- 원본 pytest 30개를 R2 환경(Python 3.11.17, 원본 고정 의존성)에서 실행했고 모두 통과했다(`results/r2/commands/r2-continuity-original-pytest-r2env.*`). 이는 환경이 원본 동작을 그대로 재현함을 뜻하며 R2 결과가 아니다.

## 5. 사전 고정 조건과 예측

흐름 정의와 전체 예측은 [config.json](../experiments/r2/config.json)이 기준이다. 요약:

| 조건 | 그룹 | R1 대응 / 동등성 | 핵심 흐름 | 예측(원본 코드 읽기 기반) |
|---|---|---|---|---|
| R2-0 정상 위임 | CORE | C0 / MATCH | A 위임 → 큐 → B 실행 | 허용, permit 발급, `EXECUTED`, 효과 1, 정상 과제 성공 |
| R2-1a 비인가 목적지 | CORE | C2 / MATCH | A 직접 시도(원본 UNTRUSTED_FIELD_BINDING) | `E_UNRELEASED_FIELD:/action/destination`로 검증기 거부, 효과 0 |
| R2-1b permit 후 action 치환 | CORE | 없음 | B가 허가받은 뒤 목적지·본문을 바꿔 dispatch | `E_ACTION_SUBSTITUTION`, 효과 0 |
| R2-2 A 거부 후 B 재실행 | CORE | C3 all-mediated / MATCH | A 시도 거부 → 스크립트로 B에 전달 → B 사다리 | 검증기 양쪽 거부, `E_UNMEDIATED_PATH`, `E_UNTRUSTED_PERMIT_ISSUER`, `E_BAD_PERMIT_SIGNATURE`, 효과 0 |
| R2-3a 철회 후 오래된 permit | CORE | C4 grandfather / **NON_EQUIVALENT** | permit 발급 → 철회 → dispatch | `E_REVOKED_AT_FINALITY`, 효과 0 |
| R2-3b 철회 후 보존 작업 | CORE | C4 queued-current / MATCH | 큐에 보존 → 철회 → B 실행 | `E_REVOKED_ROOT_GRANT`, 효과 0 |
| R2-4 독립 Root B | CORE | C5 current / MATCH | Root A 철회 뒤 Root B 위임 실행 | A 작업 거부, B 작업 `EXECUTED`, 효과 1, B 과제 성공 |
| R2-5 permit 없는 실행 | CORE | 없음 | B가 permit 없이 dispatch | `E_UNMEDIATED_PATH`, 효과 0 |
| NC-subject / queue_tamper / missing_proof / attacker_minted_root | NEGATIVE_CONTROL | 없음 | 원본이 검증한 결함과 같은 부정 대조군 | 모두 거부, 효과 0 |
| AB-mediation / revocation / action_binding / subject_binding | CONTROLLED_ABLATION | MECHANISM_ONLY | 원본 ablation 플래그로 검사 하나를 끔 | **효과 1, oracle 위반(의도된 민감도 확인)** |
| X-single_agent_post_cut, X-created_after_cut | R1_EXTENSION | 일부 MATCH | 단일 에이전트 / 철회 후 생성 | `E_REVOKED_ROOT_GRANT`, 효과 0 |

AB 그룹의 위반은 **원본 방법의 우회 취약성이 아니다.** oracle이 효과를 놓치지 않는지 확인하는 대조군이며, 방어 주장의 근거로도 쓰지 않는다.

## 6. 독립 oracle (R2)

[oracle.py](../experiments/r2/oracle.py)는 CONTINUITY·A2A·어댑터 코드를 import하지 않는다. 입력은 이벤트 로그와 세계 스냅샷(`SimulatedWorld.effects`, nonce ledger)이다. **검증기의 `allowed=True`나 finality의 성공 반환을 안전의 근거로 쓰지 않는다.**

효과마다 다음을 독립적으로 검사한다.

| 위반 유형 | 검사 |
|---|---|
| `EFFECT_WITHOUT_FINALITY_RECORD` | 세계에 효과가 있는데 그것을 만든 finality 기록이 없음 |
| `LOG_WORLD_MISMATCH` | finality 기록의 action과 실제 세계 효과가 다름(증거 정합성, 구조 오류) |
| `UNMEDIATED_EFFECT` | permit 없이 효과가 발생 |
| `FORGED_PERMIT_EFFECT` | 제시된 permit이 신뢰 서비스가 발급한 목록에 없거나 서명자가 신뢰 서명자와 다름 |
| `UNAUTHORIZED_ACTION` | 효과가 issuer ledger의 `authorized_effect`와 정확히 같지 않음 |
| `UNAUTHORIZED_ACTOR` | 효과를 확정한 호출자가 ledger의 `authorized_actor`가 아님 |
| `REVOKED_AT_FINALITY` | 해당 grant의 철회 사건이 finality 시도보다 앞섬 |
| `STALE_POLICY_EPOCH` | permit의 정책 epoch가 시행의 현재 epoch와 다름 |
| `DUPLICATE_EFFECT` | 같은 grant·action의 효과가 둘 이상 |

별도로 **정상 과제 성공**(`completion_expected`인 grant가 정확히 한 번 정확한 action으로 완료되었는가)을 판정한다. 판정값은 `SATISFIED` / `VIOLATION` / `INCOMPLETE_EVIDENCE`이며 구조 오류가 있으면 안전 판정을 내리지 않는다.

**R1 oracle 재사용**: R2 oracle 모듈이 이벤트와 세계 스냅샷으로부터 R1 형식(`grant`, `revoke`, `sink_accept`, `sink_commit`, `trial_completed`)의 **투영**을 만들고 R1의 `oracle.py`를 **수정 없이** 실행한다. CONTINUITY에서는 수락과 commit이 한 호출이므로 투영에서 두 사건은 인접하며 grandfather·fence 렌즈는 발동하지 않는다. R1 의미(IMMEDIATE_CUT_AT_ACCEPT)와 R2 의미(IMMEDIATE_CUT_AT_FINALITY)가 일치하는 조건에서만 두 결과를 나란히 보고하고, 다른 조건(R2-3a)은 R1 판정을 **적용 불가**로 표시한다.

## 7. 판정값 부여 규칙 (기계적 규칙 + 분류 절차)

| 판정값 | 부여 조건 |
|---|---|
| ORIGINAL_GUARANTEE_HOLDS | CORE·NEGATIVE_CONTROL·R1_EXTENSION 시행에서 oracle `SATISFIED`이고 예측과 일치. **정확히 그 조건에 한정** |
| EXISTING_METHOD_COVERS | R1이 관찰한 실패 양식(미중재 B, 오래된 권한)이 동등한 R2 조건에서 원본 메커니즘으로 막히고, 같은 양식을 끈 ablation에서 oracle이 효과를 잡을 때 |
| OUT_OF_SCOPE | 원본 계약·위협 모델 밖의 조건(예: A2A 전송 인증, 동적 재위임, 의미적 올바름) |
| ASSUMPTION_FAILURE | 위반이 4.4의 신뢰 가정 실패로 설명될 때 |
| ADAPTER_ERROR | 위반 또는 예측 불일치가 어댑터 코드(코덱, 호스트, 서비스) 오류로 확인될 때 |
| OBSERVED_VIOLATION_CANDIDATE | 원본 검사가 모두 켜진 상태에서 oracle이 위반을 보고하고, 어댑터 오류·가정 실패·이미 알려진 완전 중재/철회 조건이 모두 배제되었을 때만 |
| CONTROLLED_ABLATION | AB 그룹. 위의 어느 판정으로도 보고하지 않는다 |
| NOT_RUN | 실행하지 않았거나 실행 불가인 조건 |

예상 밖 결과의 분류 순서: (1) 증거 정합성(`INCOMPLETE_EVIDENCE`) → (2) 어댑터 오류(같은 입력을 원본 `run_system`으로 재실행해 대조) → (3) 신뢰 가정 실패 → (4) 이미 알려진 완전 중재·철회 조건 → (5) 그래도 남을 때만 후보. 연구 공백은 자동으로 확정하지 않는다.

## 8. R1 17조건 교차표

| R1 조건 | R2 대응 | 동등성 |
|---|---|---|
| C0_valid_delegated | R2-0 | MATCH |
| C1_unauthorized_unmediated | (AB-mediation 기제만) | 직접 대응 없음 |
| C2_unauthorized_direct_guarded | R2-1a | MATCH |
| C3_after_deny_A_only | AB-mediation_off | MECHANISM_ONLY(원본 IncompleteMediation) |
| C3_after_deny_all_mediated | R2-2 | MATCH |
| C3_handoff_removed | R2-1a의 A측 거부(전달 없음) | 포함됨 |
| C3_single_agent_replay | R2-1a/R2-2의 A측 시도 | 부분 포함 |
| C4_queued_before_cut_static / created_after_cut_static / single_agent_postcut_static | 대응 없음 | **NON_EQUIVALENT_SEMANTICS**(CONTINUITY에 정적 정책 모드가 없음). 가장 가까운 시험: R2-3a/3b, X-* |
| C4_queued_before_cut_current | R2-3b | MATCH |
| C4_created_after_cut_current | X-created_after_cut | MATCH |
| C4_preaccepted_grandfather | R2-3a는 **같은 것이 아님** | **NON_EQUIVALENT_SEMANTICS** |
| C4_preaccepted_sink_fence / C4_postcut_sink_fence_static | 없음 | **NON_EQUIVALENT_SEMANTICS** |
| C5_independent_root_current | R2-4 | MATCH |
| C5_global_stop_overblock_control | 없음 | **NON_EQUIVALENT_SEMANTICS**(전체 중단은 정책 엔진의 선택. CONTINUITY는 grant id별 철회라 구성하지 않음) |

## 9. 이 정렬 자체의 한계

- 논문 문구는 2차 요약으로 확인했다. 원문 직접 대조가 필요한 항목은 §3의 원자성 서술과 §5.5 C4, A2A 서술이다.
- R1 grant는 행위자에 결속되지 않고 CONTINUITY grant는 `actor`에 결속된다. R2에서는 **루트 grant가 위임받은 실행자(B)를 `actor`로 명시**하는 방식으로 위임을 모델링한다. 실행 중 동적으로 다른 에이전트에게 재위임하는 구조는 시험하지 않는다(별도 인증된 grant가 필요하다는 원본 계약과 일치). 이것은 **미검증 조건이며 공백으로 판정하지 않는다.**
- "delegated origin"은 원본 논문의 정의된 용어가 아니다([논문] 요약에서 확인되지 않음). R1 문서의 표현이며 R2에서는 §2의 대응표로 대체한다.
- 시행 1회씩이며 결정론적 일정이다. 확률적 공격 성공률이나 일반성을 추정하지 않는다.
