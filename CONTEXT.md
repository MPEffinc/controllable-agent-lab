# Controllable Agent / MAS 연구 현황

갱신: **2026-11-15 (Asia/Seoul), R2 실행 완료**(원본 CONTINUITY × A2A 위임 경로, 브랜치 `exp/r2-continuity-a2a`, 사전 고정 commit `75870a95fc0161176e108c03d7c0f5c6e5344bb5`). 기준 Bootstrap commit `6071b5f7eec92bd5a6ab0f4f703b71645a0b4702`, R1 브랜치 `exp/r1-intervention-boundary`(R1 증거는 수정하지 않았다). 기존 [Bootstrap CONTEXT](docs/history/CONTEXT.bootstrap-6071b5f.md)와 실행 기록을 보존했다. SREGym/XR/ROS/legacy 기록은 현재 검증 결과에 합산하지 않는다.

## 연구 목표와 판단

Controllable Agent / MAS의 **기존 보안 보장을 실제 실행으로 검증**한다. 메시지·shared state·위임·비동기 실행·효과 경계를 통과해도 명시한 속성이 유지되는지 확인하고 기존 방법으로 해결되지 않는 반복 가능한 한계를 찾는다. 지도교수의 2026-11-12 요청대로 공개 정책 코드를 실행하고 intent·판정·실제 효과를 분리한다. 새 방어 알고리즘이나 통합 프레임워크를 먼저 만드는 단계가 아니다.

**VERIFIED:** Progent 원본 component, 결정론적 R1 17조건, 독립 oracle/회귀, CONTINUITY 원본 quick conformance, **R2: 원본 CONTINUITY를 A2A 위임 경로에 연결한 사전 고정 18조건(독립 oracle 14 만족 / 4 CONTROLLED_ABLATION 위반 / 증거 불완전 0)**을 실제 실행했다. **전체 논문 재현·LLM 공격 성공·새 method gap은 확정하지 않았다.**

H1의 약한 가능성—개입 후 retained work가 후속 효과로 이어짐—은 미중재/stale-policy 구성에서 관찰됐다. 모든 알려진 경계에 wrapper를 적용하거나 현재 grant를 반영하면 차단됐고 single-agent stale-policy 조건에서도 효과가 발생했다. MAS 고유 실패나 기존 방법으로 해결 불가능하다는 강한 주장은 성립하지 않는다.

**R2 판정(우선순위 조정):** 원본 CONTINUITY를 켠 구성에서는 미중재 경로·효과 시점의 오래된 권한·전체 중단 같은 R1 실패 양식이 A2A 위임·큐 경로에서도 막혔다(`EXISTING_METHOD_COVERS`). **H1의 안전 하위 주장은 우선순위를 낮춘다.** 복구(정산·일관된 상태 회복) 하위 주장과 H2는 R2가 시험하지 않았다(NOT_RUN). 연구 공백은 확정하지 않았다(`OBSERVED_VIOLATION_CANDIDATE` 0, `ADAPTER_ERROR` 0). [판정](docs/R2_GAP_VERDICT.md).

## SoK map·E1–E4

SoK [2609.00595v1](https://arxiv.org/html/2609.00595v1)의 관련 원문을 확인했다. A=공격자 위치, I=경계, R=위반 속성, C=구성, P=경로를 분리한다. I1 admission, I2 messages, I3 state, I4 authority/action, I5 collective decisions, I6 intervention. local block과 path closure, containment와 recovery의 차이는 이미 SoK가 제시한다.

| 후보 | 속성 / 경계 | 현재 상태 |
|---|---|---|
| E1 | task/root 권한·delegation/revocation, I2/I4 | PARTIAL: R1·R2 독립 root(R2: 원본 CONTINUITY의 grant id별 철회로 유지). 복수 grant·하위 위임 계보·rebind NOT_RUN(원본 데이터 모델에 계보 필드 없음) |
| E2 | message/summary/shared memory provenance, I2/I3 | PARTIAL: retained work label 기록. full IFC/요약·retrieval NOT_RUN |
| E3 | 실제 effect 중재·관측 범위, I4/I6 | PARTIAL: 알려진 A/B와 sink 대조. H2 동적 완전성 판정 NOT_RUN |
| E4 | membership·collective decisions, I1/I5 | NOT_RUN |

기존 Related Works의 **D1 입력·모델, D2 정보흐름·신뢰경계, D3 tool 인가·최소권한, D4 계획·동적 흐름, D5 MAS 통신·위임·신원, D6 실행환경 격리**를 sheet에서 읽어 유지했다. SoK 자체 D1–D4와 혼합하지 않는다. [Gap Matrix](docs/RESEARCH_GAP_MATRIX.md), [출처 행](results/r1/taxonomy-source.json).

## 분야별 Key Papers

| 분야 | 참조 방법 | 실제 검증 범위 |
|---|---|---|
| tool 인가 | Progent, PAuth, AuthGraph, IntentCap | Progent component VERIFIED; 나머지 runtime NOT_RUN |
| control/data·provenance | CaMeL, DRIFT, Multi-CaMeL | source/일부 설치. R1 runtime NOT_RUN |
| history·finality·revocation | FORGE/SASY, CONTINUITY, ResidualAuth, Authorization Revocation | CONTINUITY 원본 tests/quick VERIFIED, **R2 A2A 위임 경로 18조건 VERIFIED**. 다른 방법 runtime NOT_RUN |
| shared state | Governed Shared Memory | 관련 원문 확인; runtime NOT_RUN |
| orchestration·runtime | ControlValve, SAGA, OpenShell | source/연결 일부 감사; runtime NOT_RUN |
| 평가 | AgentDojo, MultiAgentDojo, ORBIT, A2ASecBench | A2A offline/회귀·SDK 재사용 VERIFIED; 다른 full benchmark NOT_RUN |

[권한 상태 원문 대조](docs/r1_prior_authorization.md), [상태·경계 대조](docs/r1_prior_state.md)는 직접 관련 보장·전제·평가만 기록한다. 코드 URL 미확인을 코드 부재로 단정하지 않는다.

## 소스와 환경

Bootstrap source10개 URL/license/40자리SHA는 [REPO_AUDIT](docs/REPO_AUDIT.md)와 [source-manifest](results/setup/bootstrap-20261114/source-manifest.json)에 보존했다. 추가 공식 source는 `https://github.com/zast-ai/continuity`, SHA `59cfe60930d247d1890b366ded686c718020a11e`, MIT, clean. 총11개 remote snapshot이며 agentcap/OpenShell은 이전 partial 상태다.

| 환경 | 상태 | 실제 설치·용도 |
|---|---|---|
| A2ASecBench `.venv` | VERIFIED | Python3.10.12/a2a-sdk0.3.26; 기존 ASRF200건, 이번 원본 tests5 |
| Progent `.venv` | VERIFIED | Python3.10.12/secagent0.1.0; component4조건 |
| `experiments/r1/.venv` | VERIFIED | Python3.10.12, 별도 offline dependency union; SDK+wrapper17조건 |
| CONTINUITY `.venv` | VERIFIED | Python3.11.17, 원본 pinned requirements20distributions; tests30/quick |
| `experiments/r2/.venv` | VERIFIED | Python3.11.17, 원본 CONTINUITY pinned requirements + a2a-sdk0.3.26 snapshot(cryptography는 원본 pin 우선). 기존 venv 변경 없음. 원본 tests30 재통과, R2 단위 테스트38 |
| CaMeL `.venv` | VERIFIED 설치 / NOT_RUN 동작 | 원본 frozen lock/no-dev121distributions |
| ORBIT release `.venv` | FAILED 설치 / NOT_RUN 실행 | 이전 timeout124/packages0. 이번 재시도 안 함 |
| DRIFT·standalone AgentDojo·SASY/FORGE·IntentCap·OpenShell | NOT_RUN 설치/실행 | 기존 source audit 수준 유지 |

전역 설치/sudo/기존 venv 변경과 원본 보안 로직 수정은 없다. R1 dependency snapshot을 upstream lock으로 부르지 않는다. 정확한 source/runtime/code/config/output hashes는 [R1 manifest](results/r1/fixture-run-01/manifest.json), [CONTINUITY metadata](results/r1/continuity-source-runtime.json), [ENV_SETUP](docs/ENV_SETUP.md).

## 실제 실행과 증거

**SYNTHETIC MULTI-AGENT EXPERIMENT — VERIFIED:** 공식 A2A AgentCard/JSON-RPC in-process ASGI, A→asyncio queue→B, 원본 Progent wrapper, in-memory receipt/outbox.17조건·333이벤트·각1회·exit0. 실제 모델·race·원본 benchmark scenario 재현이 아니다.

독립 oracle02는 grant/cut를 재생하고 수락 인자↔commit binding과 별도 sink snapshot을 검사했다. receipt9/commit8, 실험의 immediate-cut 의미에서 비인가 acceptance/commit5개. safety12만족/5위반, Root B continuation1만족/1과잉차단, 결합11만족/6위반. 고의적 baseline 실패를 전체 보안 PASS나 기존 메서드 취약점으로 표현하지 않는다.

- C3 A-only: A deny 뒤 B 미중재 효과1. A+B 적용은0. handoff 제거/동일-agent 재시도도 차단.
- C4 static grant: cut 후 효과. current grant는 차단. single-agent static도 효과여서 MAS 고유성 반증.
- pre-cut 정당한 acceptance의 post-cut commit은 grandfather 의미에서 정상이다. pending-cancel fence는 별도 강한 테스트베드 통제이며 원본 철회 논문의 구현이 아니다. post-fence acceptance0건.
- C5 current scoped policy는 독립 Root B 완료, global-stop은 과잉차단. safety와 정상지속 판정을 분리한다.

[보고서](docs/R1_EXPERIMENT_REPORT.md), [threat model](docs/R1_HYPOTHESIS_AND_THREAT_MODEL.md), [raw333events](results/r1/fixture-run-01/events.jsonl), [sink snapshot](results/r1/fixture-run-01/sink_state.json), [canonical oracle02](results/r1/oracle-02.json), [17조건 CSV](results/r1/condition_summary.csv). 초기 safety-only oracle01은 보존했다. analyzer에 effect binding·독립 root 지속성 검사를 보강했으며 실제8개 commit의 인자 불일치는0건이었다.

**ORIGINAL METHOD COMPONENT CHECK — VERIFIED:** Progent OFF 정상·치환 모두 outbox commit, ON 정상 commit·치환 deny/no effect.4조건/exit0([로그](results/r1/commands/progent-component-first.stdout.txt)). full paper/LLM/MAS 결과가 아니다.

**회귀 VERIFIED:** independent oracle15tests, A2A 원본 ASRF5tests exit0. 효과+outbox 동시 치환, 누락/중복·principal·순서·overblocking을 검사했다. 이전 full A2A pytest/validator timeout124는 미해결이다.

**ORIGINAL ARTIFACT CONFORMANCE / PARTIAL PAPER EVALUATION — VERIFIED:** CONTINUITY 원본 tests30와 quick main488scenarios/3416system-runs, ablation2304행·performance exit0. CONTINUITY harmful0/384attack, benign80/80, ambiguous24/24, lifecycle488/488. [artifact 보고](docs/r1_continuity_artifact.md), [summary](results/r1/continuity-quick-01/summary.csv), [score projection](results/r1/continuity-quick-01/score_projection.csv). 원본 runner는 full receipt trace를 저장하지 않으므로 독립 sink oracle 결과로 대체하지 않는다. R1와 직접 ASR 크기 비교 금지. full2,560attack/R1adapter NOT_RUN.

**ORIGINAL METHOD INTEGRATION (R2) — VERIFIED:** 공식 a2a-sdk(in-process ASGI)의 A→큐→B 경로에서 원본 CONTINUITY(SHA `59cfe60930d247d1890b366ded686c718020a11e`, 무수정)의 `verify_bundle`·`issue_permit`·`EffectBroker`·`FinalitySink`를 호출했다. 사전 고정 18조건(CORE 8, NEGATIVE_CONTROL 4, CONTROLLED_ABLATION 4, R1_EXTENSION 2)을 1회씩(run-01)과 동일 코드 재현(run-02). 이벤트322, Permit8, finality 시도13, 효과6(정상 2 + 대조군 4), exit0, 어댑터 오류0, 모델 호출0. 독립 oracle(CONTINUITY를 import하지 않음, 세계 스냅샷 기준) 14 만족 / 4 위반(전부 검사를 끈 CONTROLLED_ABLATION, 원본 방법의 취약성이 아님) / 증거 불완전 0. 사전 예측 18/18 일치, 재현 결과 동일, 원본 하니스만으로 같은 시드를 돌린 교차 확인 15/15 일치(사후·확인용). 에이전트가 단계별로 조립한 증거 묶음은 원본 `materialise()`와 바이트 단위로 같다. **R1 acceptance와 CONTINUITY finality는 같지 않다**(수락·commit이 한 호출): R2-3a는 R1 grandfather의 대응물이 아니며 `NON_EQUIVALENT_SEMANTICS`로 분리했다. 수정 없는 R1 oracle은 행위자 대체(AB-subject_binding_off)를 놓친다(R1 grant에 행위자 필드가 없음; R1 평가의 한계, CONTINUITY의 결함이 아님). 범위는 이 18개 결정론적 조건이며 일반성·공격 성공률·분산/동시 finality·정책 epoch 교체·하위 위임·전송계층 신원 인증·위임받은 에이전트의 내부자형 단계 변환(자기 키로 서명한 권한·목적지 변경)·동적 효과 경로 완전성은 NOT_RUN이다. [통합 보고](docs/R2_CONTINUITY_INTEGRATION_REPORT.md), [의미 정렬](docs/R2_SEMANTIC_ALIGNMENT.md), [판정](docs/R2_GAP_VERDICT.md), [요약 CSV](results/r2/condition_summary.csv).

이전 Bootstrap A2A deterministic ASRF100attack+100control/exit0은 [별도 기록](results/setup/bootstrap-20261114/a2a-asrf-original/summary.json)으로 보존하며 R1와 합산하지 않는다.

## 미완료·실패·다음 검증

CONTINUITY cache-only install은 미캐시 pinned package로 exit1, 이후 같은 requirements 설치exit0. 실패 로그를 보존했다. ORBIT install/full A2A tests의 이전 timeout은 해결하지 않았다. 전체 논문 재현·dynamic complete mediation 판정은 NOT_RUN이다.

가장 가까운 기존 해결은 CONTINUITY의 current-bound finality, Revocation의 fence/accounting, FORGE의 history-aware complete mediation, ResidualAuth의 필요한 history다. 현재 관찰은 이들로 설명 가능하여 새 gap을 확정하지 않는다. 이전에 "다음 한 가지"로 둔 원본 CONTINUITY의 A2A 연결은 R2에서 수행했다(R1 17조건 전부가 아니라 의미가 일치하는 조건 + 사전 고정 18조건; 일치하지 않는 R1 조건은 `NON_EQUIVALENT_SEMANTICS`로 분리). 결과는 기존 방법이 해당 조건을 해결한다는 것이다. **다음으로 가장 중요한 검증 후보는 하위 위임(A→B→C)에서 루트 grant 철회가 하위 grant의 효과를 막는가이다.** 원본 데이터 모델에는 grant 계보와 task_root 단위 철회가 없다(코드 확인). 아직 NOT_RUN이며 새 방어를 먼저 만들지 않는다. 먼저 시나리오와 예측을 실행 전에 고정하고 Authorization Revocation·ResidualAuth와 비교한다([판정 §5](docs/R2_GAP_VERDICT.md)). 결정이 필요한 사항은 [판정 §7](docs/R2_GAP_VERDICT.md)에 모았다.

## ChatGPT–Codex–GitHub 협업

대상 [MPEffinc/controllable-agent-lab](https://github.com/MPEffinc/controllable-agent-lab), R1 브랜치 `exp/r1-intervention-boundary`. Bootstrap/과거 연구 이력을 보존하고 origin 변경/reset/force-push를 하지 않는다. Codex는 실행·로그·의존성·코드 hashes를 남기고 ChatGPT는 **고정 commit**에서 CONTEXT→R1 report→raw/manifest/oracle 순으로 관찰·해석·원본 보장 범위를 검토한다.

Git에는 key/`.env`/venv/외부 source/대형 원본 conformance CSV를 넣지 않는다. CONTINUITY raw CSV는 로컬 보존+hash, 모든 trial의 최소 score projection은 공유한다. R1 raw333events와 sink snapshot도 공유한다.

R2는 브랜치 `exp/r2-continuity-a2a`에서 사전 고정 commit(`75870a9`) → 코드 commit(`a297090`) → 결과 commit 순서로 진행했고 `python3 experiments/r2/verify_saved.py`가 해시, oracle·R1 투영·예측 대조의 재생, 재현 일치, 사전 고정이 결과보다 앞섬(git 순서), 민감 패턴 0건을 외부 source/venv/API 없이 검증한다.

`python3 experiments/r1/verify_saved.py`는 외부 source/venv/API 없이 저장 증거의 hashes·oracle replay·conformance 집계를 검증한다. 저장 증거 정합성과 새 runtime 재현을 구분한다. 기존 `scripts/audit_bootstrap.py --verify-saved`도 유지한다.
