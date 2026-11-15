# Bootstrap artifact audit

**R1 추가 상태(2026-11-15):** 기존10개 snapshot은 아래 Bootstrap 기록으로 보존한다. CONTINUITY 공식 source를 추가 확보(SHA `59cfe60930d247d1890b366ded686c718020a11e`, MIT)하고 원본 tests/quick을 실행했다. Progent component, A2A 원본5tests, 합성17조건도 실행했다. 현재 상태는 [R1 보고](R1_EXPERIMENT_REPORT.md)와 [CONTINUITY artifact 감사](r1_continuity_artifact.md)를 기준으로 읽는다. 아래의 NOT_RUN은 Bootstrap 시점 기록이다.

감사일: **2026-11-15 (Asia/Seoul)**. 실행 로그의 날짜는 **2026-11-14 UTC**이며 이번 인계 작업에서 새로운 설치·실험은 하지 않았다. 과거 SREGym/XR/ROS 기록은 현재 연구 검증에 포함하지 않는다.

상태: `VERIFIED` = 해당 사실에 직접 증거 있음, `PARTIAL` = 일부만 확보·확인, `FAILED` = 시도했으나 실패/timeout, `NOT_RUN` = 실행 기록 없음. 출처 등급의 `VERIFIED OFFICIAL` / `VERIFIED AUTHOR-ASSOCIATED`는 실행 상태와 별개다. **설치와 원본 논문 실험 재현은 다르며, 전체 논문 재현은 모두 NOT_RUN이다.**

## 소스 URL·고정 revision·라이선스

| 프로젝트 / 역할 | 출처 등급 | 원격 URL | 확보 SHA | 라이선스 | 소스 확보 |
|---|---|---|---|---|---|
| A2ASecBench / A2A 평가 | VERIFIED AUTHOR-ASSOCIATED | https://github.com/SaFo-Lab/A2ASecBench | `e02109ebdcce3fe926884fbacbc935eef44e4aa3` | MIT | VERIFIED |
| ORBIT / MAS 평가 | VERIFIED OFFICIAL | https://github.com/wlanderson0/orbit | `887a0415e0ded15406de0f1e14259099b595d443` | Apache-2.0 | VERIFIED |
| CaMeL / control-data 분리·capabilities | VERIFIED OFFICIAL | https://github.com/google-research/camel-prompt-injection | `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8` | Apache-2.0 | VERIFIED |
| Progent / tool argument 정책 | VERIFIED AUTHOR-ASSOCIATED | https://github.com/sunblaze-ucb/progent | `b02783b896d4bf01a2adf24738015e258db8d35b` | MIT | VERIFIED |
| DRIFT / 계획·검증·격리 | VERIFIED OFFICIAL | https://github.com/SaFo-Lab/DRIFT | `6fd3df4763fad77398c3c273c2a4fe14dd50f7ea` | MIT | VERIFIED |
| AgentDojo / stateful tool benchmark | VERIFIED OFFICIAL | https://github.com/sequrity-ai/agentdojo | `357c80dea9af34323f709c3505d9e6d224654c7e` | MIT | VERIFIED |
| IntentCap / task-scoped field authority | VERIFIED OFFICIAL | https://github.com/yunwei37/agentcap | `1886fd50dbd51344c62acd1d224375054ac076e9` | PARTIAL: 라이선스 미확인 | PARTIAL: source sparse timeout |
| OpenShell / OS·network runtime | VERIFIED OFFICIAL | https://github.com/NVIDIA/OpenShell | `2e5589b2180dd432320adda124c4f7bcede119b5` | Apache-2.0 | PARTIAL: source sparse timeout |
| SASY / FORGE 구현 | VERIFIED OFFICIAL | https://github.com/sasy-labs/sasy | `7dc9e524c5b1979b91d16b9d573219e358a6c332` | Apache-2.0 | VERIFIED |
| FORGE / 평가 harness | VERIFIED OFFICIAL | https://github.com/sasy-labs/forge | `ecc5ff9f7576f2669249609d9002c07674947913` | Apache-2.0 | VERIFIED: 평가 소스만 sparse |

A2ASecBench 등의 author-associated 등급은 README 논문 citation과 해당 저자/조직 원격을 확인한 수준이다. 역방향 논문→repo 연결을 독립 확인하지 못한 항목은 공식 등급으로 올리지 않았다. IntentCap은 논문 §3, FORGE는 논문 첫 각주에서 실제 URL을 확인했다. OpenShell은 공식 NVIDIA 프로젝트이며 특정 논문 재현으로 분류하지 않는다.

ORBIT 실행 준비는 위 HEAD가 아닌 공식 **v1.0.4 release** 기준이다. release manifest source SHA는 `076104ae2479595b4c973df7758131401e684c7d`. wheel SHA256은 `95a7cbda584b22dd5250ce05c144286bce624814596aa59928f66beb24f29afc`. HEAD·release를 혼합하지 않는다.

원격·SHA·sparse·dirty 상태의 기계 판독 근거: [source-manifest.json](../results/setup/bootstrap-20261114/source-manifest.json). 제3자 코드는 Git에 넣지 않았고 원본 source 수정은 없다. A2A 테스트가 해당 checkout의 `results/summary.json`과 run JSONL을 생성/변경한 사실은 manifest에 남겼다. 이는 코드 patch가 아니다.

## 설치·실행·실패

| 대상 | 설치 | 실제 실행 | 결과 / 한계 | 근거 |
|---|---|---|---|---|
| A2ASecBench `.venv` | VERIFIED | VERIFIED: 원본 `configs/offline/asrf_eval.yaml`, trial 1/case | exit 0, 100 attack + 100 matched control. attack ASR 1.0, control pass 1.0, 전체 `asr` 0.5 | [ASRF 로그](../results/setup/bootstrap-20261114/a2a-asrf-original.log), [summary](../results/setup/bootstrap-20261114/a2a-asrf-original/summary.json), [대표 이벤트](../results/setup/bootstrap-20261114/a2a-asrf-sample.jsonl) |
| A2A 전체 pytest | VERIFIED: 의존성 | FAILED: timeout 124 | progress dots는 suite pass 증거가 아님 | [pytest 로그](../results/setup/bootstrap-20261114/a2a-pytest.log) |
| A2A release validator | VERIFIED: 의존성 | FAILED: timeout 124 | 완료 출력 없음 | [validator 로그](../results/setup/bootstrap-20261114/a2a-release-validation.log) |
| ORBIT release `.venv` | FAILED: install timeout 124 | NOT_RUN | Python 3.11.17/venv만 존재, 설치 패키지 0개. checksum/download 성공과 구분 | [install 로그](../results/setup/bootstrap-20261114/orbit-release-install.log) |
| CaMeL `.venv` | VERIFIED: `uv sync --frozen --no-dev` | NOT_RUN | 원본 lock 기준 설치 distributions121개. unit test/full benchmark 없음 | [sync 로그](../results/setup/bootstrap-20261114/defenses-camel-sync.log) |
| Progent `.venv` | VERIFIED: editable package install | NOT_RUN | 설치 distributions25개. ON/OFF script는 준비본만 있음 | [install 로그](../results/setup/bootstrap-20261114/defenses-progent-install.log) |
| DRIFT / standalone AgentDojo | NOT_RUN | NOT_RUN | clone과 코드 감사만 완료. CaMeL에 포함된 PyPI AgentDojo와 standalone checkout 구분 | [방어 상세](artifacts/DEFENSES.md) |
| IntentCap / OpenShell / SASY / FORGE | NOT_RUN | NOT_RUN | 일부 소스·코드 경로 감사, 엔진·OS enforcement 미검증 | [추가 상세](artifacts/ADDITIONAL.md) |

A2A ASRF에서는 공식 SDK의 로컬 ASGI transport와 loopback HTTP trap에 실제 요청이 있었다. 모델·외부 공격 대상은 사용하지 않았다. 결정론적 unguarded SUT에서 fixture의 이벤트·scorer가 작동함을 보일 뿐이다. `BrokenPipeError` 1건이 성공 로그에 동반되어 있어 깨끗한 전체 테스트 통과로 표현하지 않는다. 방어 ON/OFF 결과는 **NOT_RUN**이다.

## 실제 method·중재·effect·scorer 경로

아래 문서는 각 repo-relative 파일·함수·class를 연결한다. 본문을 읽지 못한 부분은 명시적으로 PARTIAL이다.

| 범위 | entry/config/model | 정책·집행 경계·effect | benchmark/scorer/trace |
|---|---|---|---|
| [A2ASecBench](artifacts/A2ASECBENCH.md) | `orchestration.py`, `configs/offline/asrf_eval.yaml`, deterministic/LLM adapter 구분 | SDK local peers → resource service → `harness/a2a_lab/http_trap.py`; unguarded policy | ASRF scorer, raw events, matched control 판정 |
| [ORBIT](artifacts/ORBIT.md) | release `first_benchmark.py`, `multi_agent_task`, activation/scheduler | `DefenseBoundary.wrap_tool`, channel ACL, tool wrapper; `reserve_units` shared inventory commit | `inventory_score`, Inspect sample/epoch log. 모두 코드 감사, 실행 NOT_RUN |
| [CaMeL·Progent·DRIFT·AgentDojo](artifacts/DEFENSES.md) | 각 원본 CLI/config/model adapter | capability check / JSON-schema tool wrapper / DRIFT guard / stateful function runtime | AgentDojo benign·attack task success; source 감사와 설치만, scores 없음 |
| [SASY/FORGE·IntentCap·OpenShell](artifacts/ADDITIONAL.md) | SDK/runner/toolchain 및 미확보 범위 | `check_tool_call` → `check_authorization`; executor pre-effect gate; mock send sink | FORGE AgentDojo effect audit 코드. runtime·scorer execution NOT_RUN |

공식 URL 미확인: ControlValve, Multi-CaMeL/MultiAgentDojo, PAuth, AuthGraph, ResidualAuth, Authorization Revocation, SAGA. 모두 실행 NOT_RUN이며 공개 코드 부재 확정이 아니다. [확인 범위·원문 링크](artifacts/ADDITIONAL.md#아직-공식-코드-url이-확인되지-않은-항목).
