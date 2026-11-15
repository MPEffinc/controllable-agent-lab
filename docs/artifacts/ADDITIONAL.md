# 추가 artifact 검증 — 2026-11-15 (Asia/Seoul)

이번 인계 작업에서는 설치·실험을 추가하지 않았다. 아래는 이전 부트스트랩에서 받은 소스와 읽은 코드의 감사 결과다. `VERIFIED`는 해당 항목만 확인했다는 뜻이며 논문 재현 완료를 뜻하지 않는다.

| 프로젝트 | 출처 검증 | 확보 상태 | 설치 / 실행 | 라이선스 |
|---|---|---|---|---|
| IntentCap / agentcap | VERIFIED OFFICIAL: [논문 §3](https://arxiv.org/html/2609.14631v1)이 정확히 `yunwei37/agentcap` 연결 | PARTIAL: shallow/filter clone 성공, sparse source 확장 timeout 124. root 논문 파일은 캐시에서 복구, 소스 디렉터리는 미확보 | NOT_RUN / NOT_RUN | PARTIAL: HEAD tree에 루트 LICENSE/COPYING 없음. 공개 접근과 오픈소스 라이선스 부여를 동일시하지 않음 |
| OpenShell | VERIFIED OFFICIAL: [NVIDIA 원격](https://github.com/NVIDIA/OpenShell), 연구 논문 artifact가 아닌 runtime 프로젝트 | PARTIAL: shallow/filter clone 성공, sparse source 확장 timeout 124. 캐시된 루트 원본 복구, 런타임 소스 미확보 | NOT_RUN / NOT_RUN | Apache-2.0 |
| FORGE 구현 SASY | VERIFIED OFFICIAL: [논문 첫 각주](https://arxiv.org/html/2602.16708v4) → `sasy-labs/sasy` | VERIFIED: shallow source checkout | NOT_RUN / NOT_RUN | Apache-2.0 |
| FORGE 평가 | VERIFIED OFFICIAL: 같은 논문 → `sasy-labs/forge` | VERIFIED: shallow/filter + sparse `experiments`, `scripts`; 전체 데이터·기존 결과는 받지 않음 | NOT_RUN / NOT_RUN | Apache-2.0 |

정확한 URL·40자리 SHA·트리 상태: [source-manifest.json](../../results/setup/bootstrap-20261114/source-manifest.json). clone/sparse 각각의 종료코드는 [command-index.json](../../results/setup/bootstrap-20261114/command-index.json). sparse 확장 중 제거된 **이번에 받은** 루트 파일은 Git 캐시에서 원문 바이트와 실행 모드로 복구했다([복구 기록](../../results/setup/bootstrap-20261114/sparse-recovery.json)). 기존 프로젝트 자료는 삭제하지 않았다.

## 읽어서 확인한 실행 경계

SASY `sdk/python/sasy/observability/record.py::record`가 이벤트와 입력 의존성을 기록하고, `sdk/python/sasy/reference_monitor/api.py::check_tool_call`이 proposed tool action을 reference monitor로 보낸다. `crates/sasy-refmon/src/service.rs::check_tool_call`은 policy checker의 `check_authorization`을 호출한다. 실제 효과 전 interception 및 이벤트·주체의 정확성이 보장 가정이다. 소스 감사이며 엔진 실행을 검증한 것은 아니다.

원본 no-model 예제 `examples/message-flow/demo.py::dispatch`는 `sasy.check_tool_call`을 먼저 호출하고 authorized일 때만 `sent.append`로 모의 발송한다. `run_scenario`는 결정론적 문장 연결과 정규식으로 수신자를 고른다. `policy.dl::Unauthorized`는 sensitive와 untrusted 양쪽에 의존하는 `send_summary`를 차단한다. 이 예제는 sensitive-only / sensitive+untrusted 입력 비교이며 **policy OFF/ON 비교가 아니다**. 실행하려면 별도 로컬 엔진과 Python SDK가 필요하다. Rust·Soufflé·엔진 설치 및 Docker daemon은 이번에 검증하지 않았다. SDK 기본 CLI가 `~/.sasy`를 사용하므로 후속 실행에서는 프로젝트 내부 설정과 소유한 엔진으로 경로를 명시해야 한다.

FORGE `experiments/agentdojo/sasy_agentdojo/pipeline.py::build_pipeline`은 AgentDojo의 `ToolsExecutor`를 `monitor.py::SasyToolsExecutor`로 바꾼다. monitor가 기록 → 정책 판정 → 허용 시 도구 실행 순서를 담당한다. `PolicyDecision`에는 allow/deny 외 `asked`가 있다. 현 코드의 ASK는 실제로 진행될 수 있고 security/utility에서 서로 다른 가정으로 집계되므로 deny와 섞어 해석하면 안 된다. 점수 분석 경로는 `scripts/evaluation/agentdojo_effect.py`, `audit_agentdojo_effect_asr.py`, `summarize_agentdojo.py`. 모델 provider 설정은 `experiments/agentdojo/sasy_agentdojo/providers.py`, 실제 runner는 `runner.py`. 이 경로의 연구 결과나 효과를 새로 재현하지 않았다.

IntentCap 논문의 task-scoped lease/field ownership/deterministic checker는 문헌상 방법이다. Git tree에서 `src/intentcap/checker.py`, `gateway.py`, `boundary_gateway.py`, `live_gateway.py` 존재는 확인했지만 파일 본문을 확보·분석하지 못했으므로 함수·실제 mediation coverage는 **PARTIAL**이다. repo 루트 `main.tex` 제목은 논문과 일치한다. README가 없어서 처음 README URL 요청은 404였으며 repo가 없는 것으로 판단하지 않았다.

OpenShell README와 `rust-toolchain.toml`에서 kernel/filesystem/syscall/network 정책, provider credential 경계, Rust 1.95.0 pin을 확인했다. 트리에는 `crates/openshell-sandbox/src/sandbox/linux/{landlock,seccomp}.rs`, `crates/openshell-supervisor-network/src/proxy.rs`, `crates/openshell-policy/src/lib.rs`가 있다. 본문 미확보이므로 enforcement 함수나 적용 범위를 검증했다고 주장하지 않는다. `install.sh` 실행, gateway/container 생성, 호스트 정책 변경은 하지 않았다.

## 아직 공식 코드 URL이 확인되지 않은 항목

다음은 모두 코드 출처 `NOT VERIFIED`, 로컬 설치·실행 `NOT_RUN`이다. **공개 코드가 없다는 확정이 아니다.** 논문/저자 페이지를 읽고 검색한 범위에서 인증 가능한 다운로드 URL을 확보하지 못했다.

| 항목 | 확인한 원문·저자 출처 | 이번에 확인된 범위 |
|---|---|---|
| Multi-CaMeL / MultiAgentDojo | [arXiv §VIII](https://arxiv.org/html/2610.05640v1) | release 문장은 있으나 읽은 HTML에 artifact URL 없음. 임의 URL 생성·clone 안 함 |
| ControlValve | [저자 페이지](https://rishijha.com/pubs/breaking_and_fixing.html) | `[code]` 텍스트에 실제 연결 URL 없음 |
| PAuth | [arXiv](https://arxiv.org/html/2603.17170) | 원문 확인, 특정 공식 runnable repo 미확인 |
| AuthGraph | [arXiv](https://arxiv.org/html/2605.26497) | 원문 확인, 특정 공식 runnable repo 미확인 |
| ResidualAuth | 이름 검색 | 공식 원문·repo 연결 검증 미완료 |
| Authorization Revocation | [arXiv](https://arxiv.org/abs/2609.21284) | 논문 식별, 코드 연결 미확인 |
| SAGA | seed의 이름 | 추가 출처 검증 NOT_RUN. 동명 프로젝트를 임의 채택하지 않음 |

다음 검증은 저자 페이지·논문 최신 버전·공식 artifact metadata에서 URL을 확인한 뒤 진행한다. FORGE와 IntentCap은 이번 조사에서 직접 연결을 찾았으므로 미확인 목록에서 제외했다.
