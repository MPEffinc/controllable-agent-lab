# Controllable Agent / MAS 연구 현황

갱신: **2026-11-15 (Asia/Seoul), R1 실행 완료**. 기준 Bootstrap commit `6071b5f7eec92bd5a6ab0f4f703b71645a0b4702`, R1 브랜치 `exp/r1-intervention-boundary`. 기존 [Bootstrap CONTEXT](docs/history/CONTEXT.bootstrap-6071b5f.md)와 실행 기록을 보존했다. SREGym/XR/ROS/legacy 기록은 현재 검증 결과에 합산하지 않는다.

## 연구 목표와 판단

Controllable Agent / MAS의 **기존 보안 보장을 실제 실행으로 검증**한다. 메시지·shared state·위임·비동기 실행·효과 경계를 통과해도 명시한 속성이 유지되는지 확인하고 기존 방법으로 해결되지 않는 반복 가능한 한계를 찾는다. 지도교수의 2026-11-12 요청대로 공개 정책 코드를 실행하고 intent·판정·실제 효과를 분리한다. 새 방어 알고리즘이나 통합 프레임워크를 먼저 만드는 단계가 아니다.

**VERIFIED:** Progent 원본 component, 결정론적 R1 17조건, 독립 oracle/회귀, CONTINUITY 원본 quick conformance를 실제 실행했다. **전체 논문 재현·LLM 공격 성공·새 method gap은 확정하지 않았다.**

H1의 약한 가능성—개입 후 retained work가 후속 효과로 이어짐—은 미중재/stale-policy 구성에서 관찰됐다. 모든 알려진 경계에 wrapper를 적용하거나 현재 grant를 반영하면 차단됐고 single-agent stale-policy 조건에서도 효과가 발생했다. MAS 고유 실패나 기존 방법으로 해결 불가능하다는 강한 주장은 성립하지 않는다.

## SoK map·E1–E4

SoK [2609.00595v1](https://arxiv.org/html/2609.00595v1)의 관련 원문을 확인했다. A=공격자 위치, I=경계, R=위반 속성, C=구성, P=경로를 분리한다. I1 admission, I2 messages, I3 state, I4 authority/action, I5 collective decisions, I6 intervention. local block과 path closure, containment와 recovery의 차이는 이미 SoK가 제시한다.

| 후보 | 속성 / 경계 | 현재 상태 |
|---|---|---|
| E1 | task/root 권한·delegation/revocation, I2/I4 | PARTIAL: R1 독립 root와 단일 support/cut. 복수 support·lineage·rebind NOT_RUN |
| E2 | message/summary/shared memory provenance, I2/I3 | PARTIAL: retained work label 기록. full IFC/요약·retrieval NOT_RUN |
| E3 | 실제 effect 중재·관측 범위, I4/I6 | PARTIAL: 알려진 A/B와 sink 대조. H2 동적 완전성 판정 NOT_RUN |
| E4 | membership·collective decisions, I1/I5 | NOT_RUN |

기존 Related Works의 **D1 입력·모델, D2 정보흐름·신뢰경계, D3 tool 인가·최소권한, D4 계획·동적 흐름, D5 MAS 통신·위임·신원, D6 실행환경 격리**를 sheet에서 읽어 유지했다. SoK 자체 D1–D4와 혼합하지 않는다. [Gap Matrix](docs/RESEARCH_GAP_MATRIX.md), [출처 행](results/r1/taxonomy-source.json).

## 분야별 Key Papers

| 분야 | 참조 방법 | 실제 검증 범위 |
|---|---|---|
| tool 인가 | Progent, PAuth, AuthGraph, IntentCap | Progent component VERIFIED; 나머지 runtime NOT_RUN |
| control/data·provenance | CaMeL, DRIFT, Multi-CaMeL | source/일부 설치. R1 runtime NOT_RUN |
| history·finality·revocation | FORGE/SASY, CONTINUITY, ResidualAuth, Authorization Revocation | CONTINUITY 원본 tests/quick VERIFIED. 다른 방법 R1 runtime NOT_RUN |
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

이전 Bootstrap A2A deterministic ASRF100attack+100control/exit0은 [별도 기록](results/setup/bootstrap-20261114/a2a-asrf-original/summary.json)으로 보존하며 R1와 합산하지 않는다.

## 미완료·실패·다음 검증

CONTINUITY cache-only install은 미캐시 pinned package로 exit1, 이후 같은 requirements 설치exit0. 실패 로그를 보존했다. ORBIT install/full A2A tests의 이전 timeout은 해결하지 않았다. 전체 논문 재현·dynamic complete mediation 판정은 NOT_RUN이다.

가장 가까운 기존 해결은 CONTINUITY의 current-bound finality, Revocation의 fence/accounting, FORGE의 history-aware complete mediation, ResidualAuth의 필요한 history다. 현재 관찰은 이들로 설명 가능하여 새 gap을 확정하지 않는다. **다음 한 가지는 원본 CONTINUITY의 witness/permit/finality를 동일 R1 A2A17조건에 좁게 연결하고 cut/accept/fence 의미를 일치시켜 원본 control과 비교하는 것**이다. 아직 NOT_RUN이며 새 방어를 먼저 만들지 않는다.

## ChatGPT–Codex–GitHub 협업

대상 [MPEffinc/controllable-agent-lab](https://github.com/MPEffinc/controllable-agent-lab), R1 브랜치 `exp/r1-intervention-boundary`. Bootstrap/과거 연구 이력을 보존하고 origin 변경/reset/force-push를 하지 않는다. Codex는 실행·로그·의존성·코드 hashes를 남기고 ChatGPT는 **고정 commit**에서 CONTEXT→R1 report→raw/manifest/oracle 순으로 관찰·해석·원본 보장 범위를 검토한다.

Git에는 key/`.env`/venv/외부 source/대형 원본 conformance CSV를 넣지 않는다. CONTINUITY raw CSV는 로컬 보존+hash, 모든 trial의 최소 score projection은 공유한다. R1 raw333events와 sink snapshot도 공유한다.

`python3 experiments/r1/verify_saved.py`는 외부 source/venv/API 없이 저장 증거의 hashes·oracle replay·conformance 집계를 검증한다. 저장 증거 정합성과 새 runtime 재현을 구분한다. 기존 `scripts/audit_bootstrap.py --verify-saved`도 유지한다.
