# Controllable Agent / MAS 연구 현황

갱신: **2026-11-15 (Asia/Seoul)**. Bootstrap 실행 증거는 2026-11-14 UTC 기록이다. 이번 작업은 기존 결과 감사·문서 정리·GitHub 인계이며 새 설치나 실험은 시작하지 않았다. 시작 시 루트 `CONTEXT.md`는 없었고 `CONTEXT.seed.md`를 출발점으로 작성했다. 기존 파일·과거 연구 기록은 보존했다.

## 연구 배경과 목표

Controllable Agent 및 Multi-Agent System의 **기존 보안 보장을 실행으로 검증**한다. agent 간 메시지, shared state, 위임 권한, 동적 구성, 실제 tool effect를 통과해도 명시된 보장이 성립하는지 확인하고, 기존 방법으로 해결되지 않은 반복 가능한 한계를 찾는다. 새 방어를 먼저 만드는 단계가 아니다.

2026-11-12 지도교수 피드백은 문헌 분류를 늘리기보다 기존 policy-based agent/MAS software를 실행하고 정책 적용 전후의 tool intent, 판정, 실제 효과를 가져오라는 것이었다. 문헌 map·SoK 검토·Key Paper 선정은 연구 배경이며 검증 결과가 아니다. XR/ROS, SREGym, `legacy/`, 기존 `docs/reports/`·`local/`의 결과를 이번 연구 실험으로 합산하지 않는다.

현재 **설치 성공 3환경, 원본 결정론적 harness 1개 실행 성공**을 확인했다. **정책 OFF/ON 비교, LLM 공격 재현, 원본 논문 전체 실험 재현, 신규 method gap 증명은 모두 NOT_RUN**이다.

## SoK 연구 map과 E1–E4

SoK *When Safe Agents Fail Together* (arXiv:2609.00595)는 seed에서 인계한 연구 틀이다. 이번 감사에서 SoK 자체를 새로 검증한 것은 아니다. A=공격자 위치, I=상호작용 경계, R=보안 결과/위반 속성, C=구성, P=공격 경로를 구분한다. I1 admission, I2 messages, I3 state, I4 authority/action, I5 collective decision, I6 intervention. 공격 기법, 전달 인터페이스, 실패 결과를 같은 축으로 취급하지 않는다.

| 후보 | 검증할 속성 | 관련 경계 | 상태 |
|---|---|---|---|
| E1 | 서로 다른 root task의 권한과 delegation/revocation 이후 action 정당화 | I2/I4 | NOT_RUN |
| E2 | 메시지·요약·shared memory에서 provenance/trust 제한 보존 | I2/I3 | NOT_RUN |
| E3 | 중첩 도구·queue·provider·지연 effect의 실제 mediation coverage | I4/I6 | NOT_RUN |
| E4 | 동적 membership·집단 결정에서 권한·안전성 보존 | I1/I5 | NOT_RUN |

이들은 확정된 신규 기여나 네 개의 논문 주제가 아니다. single-agent/상호작용 제거 대조군을 두고 tree/DAG, private/shared state, static/revoked authority, sync/async, membership 축을 하나씩 바꾼다. 보장 범위 내 위반, 가정 실패, scope extension, 구현 오류, 측정 한계를 구분한다.

## Key Papers의 역할

| 분야 | 참조 방법·환경 | 이번 상태 |
|---|---|---|
| control/data 및 provenance | CaMeL, Multi-CaMeL, DRIFT | CaMeL 설치 VERIFIED, DRIFT 소스 확보 VERIFIED, Multi-CaMeL artifact URL PARTIAL |
| fine-grained authorization | Progent, PAuth, AuthGraph, IntentCap | Progent 설치 VERIFIED, IntentCap 논문→repo 확인 VERIFIED/source PARTIAL, PAuth/AuthGraph 코드 연결 PARTIAL |
| history·delegation·revocation | FORGE/SASY, ResidualAuth, Authorization Revocation, SAGA | FORGE/SASY 소스 VERIFIED, 나머지 코드 검증 PARTIAL/실행 NOT_RUN |
| orchestration·runtime | ControlValve, OpenShell | ControlValve 코드 URL PARTIAL, OpenShell 공식 원격 VERIFIED/source PARTIAL |
| 평가 | AgentDojo, MultiAgentDojo, ORBIT, A2ASecBench | A2A offline 실행 VERIFIED; 나머지 benchmark 실행 NOT_RUN |

검증되지 않은 URL을 만들지 않는다. 코드 미확인은 공개 코드 부재의 증명이 아니다. [출처·코드 경로 감사](docs/REPO_AUDIT.md), [미확인 artifact 확인 범위](docs/artifacts/ADDITIONAL.md)를 참조한다. 기존 Related Works sheet는 배경 자료이며 이번 운영 상태의 근거가 아니다.

## 확보한 소스·실제 환경

**VERIFIED/PARTIAL:** 별도 `third_party/`에 10개 pinned source를 확보했다: A2ASecBench, ORBIT, CaMeL, Progent, DRIFT, AgentDojo, IntentCap/agentcap, OpenShell, SASY, FORGE 평가. 정확한 URL·40자리 SHA·라이선스·partial 사유는 [REPO_AUDIT](docs/REPO_AUDIT.md), 기계 판독 목록은 [source-manifest](results/setup/bootstrap-20261114/source-manifest.json)이다. 외부 repo 코드·venv·release wheel·대형 데이터는 Git에서 제외한다.

| 항목 | 상태 | 실제 확인 |
|---|---|---|
| A2ASecBench 격리 설치 | VERIFIED | Python3.10.12, a2asecbench0.1.0, a2a-sdk0.3.26, 43 distributions |
| CaMeL 격리 설치 | VERIFIED | Python3.10.12, camel1.0.0/AgentDojo0.1.34, 원본 uv.lock/no-dev, 121 distributions |
| Progent 최소 격리 설치 | VERIFIED | Python3.10.12, secagent0.1.0, 25 distributions. 내부 benchmark 환경과 별개 |
| ORBIT 공식 release 설치 | FAILED / PARTIAL | v1.0.4 checksum 검증과 Python3.11.17 venv 생성 VERIFIED. 설치 timeout124, packages0 |
| DRIFT·standalone AgentDojo 설치 | NOT_RUN | 원본 소스 감사만, 다른 AgentDojo 환경과 병합하지 않음 |
| IntentCap·OpenShell 설치 | NOT_RUN | sparse source 확장 FAILED timeout124, root cached files 복구/source PARTIAL |
| FORGE/SASY 엔진 설치 | NOT_RUN | 소스 확보/정책·executor 경계 감사만, Rust/Soufflé/Docker daemon 미검증 |

[ENV_SETUP](docs/ENV_SETUP.md), [environment-inventory](results/setup/bootstrap-20261114/environment-inventory.json), requirements snapshots를 참조한다. snapshot은 원본 lockfile 또는 재설치 검증 결과가 아니다.

## 완료한 실행과 증거

**VERIFIED — A2ASecBench 원본 offline ASRF:** `configs/offline/asrf_eval.yaml --trials 1`, exit0, 총200건(attack100 + matched control100). 공격100건 모두 localhost forbidden resource dereference가 관찰되어 attack ASR1.0, control100건 정상 통과하여 control pass1.0/overblock0. 전체200건을 섞은 필드 `asr=0.5`와 공격 ASR을 구분한다.

공식 A2A SDK in-process AgentCard/JSON-RPC와 실제 loopback HTTP trap이 실행됐다. 선택된 SUT는 결정론적 unguarded coordinator이며 LLM/API를 사용하지 않는다. 이 결과는 harness 및 scorer 작동의 증거다. 기존 방어의 보장 위반이나 LLM 보안 성능·MAS 신규 gap은 결론내릴 수 없다. monitor policy ON/OFF 실험도 아니다. 로그에 BrokenPipeError1건이 동반되어 전체 테스트가 깨끗하게 통과한 것으로 표현하지 않는다.

증거 경로:

- [실행 명령·종료코드](results/setup/bootstrap-20261114/a2a-asrf-original.json), [stdout/stderr](results/setup/bootstrap-20261114/a2a-asrf-original.log), [원본 summary](results/setup/bootstrap-20261114/a2a-asrf-original/summary.json).
- [전체200건 sink 이벤트 projection](results/setup/bootstrap-20261114/a2a-asrf-observations.jsonl), [attack/control 전체 이벤트 각1건](results/setup/bootstrap-20261114/a2a-asrf-sample.jsonl), [raw hash·재집계](results/setup/bootstrap-20261114/a2a-verified-counts.json).
- 1,449,552-byte raw `a2a-asrf-original/trials.jsonl`은 로컬 보존/Git 제외. SHA256 `eebabeb64dd42fb88cb6870607649cbc41bb55492aa2474f3607eace9947d52b`.
- [전체28개 기존 명령 index](results/setup/bootstrap-20261114/command-index.json). setup 명령28개를 테스트28개로 세지 않는다.

**FAILED — A2A 전체 pytest 및 release validator:** 둘 다 timeout124. 최종 summary가 없어서 전체 test PASS·정확한 통과 개수를 주장하지 않는다. **NOT_RUN — ORBIT 두 agent example, CaMeL/Progent 동작 test, 정책 ON/OFF, provider model run, 모든 전체 논문 재현.** 실행이 없는 파일이나 upstream의 기존 결과를 성공 증거로 쓰지 않는다.

## 다음 실행 단계와 진입 조건

이번 감사의 범위를 넘어서는 아래 작업은 시작하지 않았다. [EXPERIMENT_PLAN](docs/EXPERIMENT_PLAN.md)과 [BOOTSTRAP_HANDOFF](docs/BOOTSTRAP_HANDOFF.md)에 exact command가 있다.

1. Progent 원본 wrapper를 사용하는 준비된 in-memory 도구 component check를 별도 실행 작업에서 수행한다. 고정 task+recipient substitution에 정책 OFF/ON × benign/attack을 비교하고 판정과 committed effect를 분리한다. 이 파일은 **NOT_RUN**이며 성공하더라도 full reproduction이 아니다.
2. ORBIT release 의존성 설치 timeout을 해결한 후 공식 두 agent example와 negative control을 실행한다. release SHA와 Inspect0.3.263을 유지한다. negative control은 정책 toggle이 아니다.
3. A2A 원본 test를 개별로 좁혀 timeout 위치를 확인한다. deterministic baseline을 LLM 결과와 구분한다.
4. AgentDojo/DRIFT/CaMeL/FORGE의 원본 benchmark·defense preset·scorer·실제 sink를 동일 task/attack에서 비교한다. 모델 호출이 필요하면 호출/토큰 상한·비용·credentials를 사전에 확정하고 승인받는다. 새 방어를 먼저 개발하지 않는다.

## ChatGPT–Codex–GitHub 협업

GitHub 대상은 기존 **[MPEffinc/controllable-agent-lab](https://github.com/MPEffinc/controllable-agent-lab)**, 작업 브랜치는 **`bootstrap/mas-security-keypapers`**, 기반 HEAD는 `baca6088f106d19a226feee84edc0f8cedec24be`이다. 기존 `origin`을 바꾸거나 과거 브랜치를 reset/force-push하지 않는다.

Codex는 로컬 checkout·격리환경·실행·원시로그를 관리하고 검토 가능한 최소 증거·명령·manifest를 커밋한다. ChatGPT는 반드시 **해당 브랜치 또는 보고된 commit SHA**에서 CONTEXT→HANDOFF→audit→JSON/log를 읽는다. main의 예전 연구 문서나 파일 존재만으로 실행 성공을 추론하지 않는다. source/license/SHA와 설치/runtime/full reproduction을 따로 검토하고 다음 한 가지 비교를 정한다.

GitHub fresh clone에서 `python3 scripts/audit_bootstrap.py --verify-saved`로 log hash/exit/metadata, source manifest, 200행 projection 집계, package snapshot 정합성을 검증할 수 있다. 이 감사 명령은 benchmark·모델 호출·설치를 하지 않으며 **저장 증거 검증과 독립 실험 재현을 구분**한다. 로컬의 전체 raw·venv는 GitHub에 포함되지 않는다.

**VERIFIED — 공유 파일만으로 감사:** Git index에서 추출한 별도 디렉터리에서 `--verify-saved` exit0 확인([감사 기록](results/handoff-20261115/verification.json)). 기존 연구 파일 삭제 없음, 커밋 대상의 credential 패턴·제외 경로 점검 완료.
