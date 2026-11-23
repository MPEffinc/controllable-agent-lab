# Progent 정책 생성·집행 실험

기록 시작: 2026-11-22 (UTC). 목표는 새 Use Case에서 **적용된 정책, Agent가 제안한 Tool Call, 원본 Progent의 판정, Backend 실행 여부, 최종 상태**를 각각 관찰하는 것이다. 기존 연구의 보장 범위나 새로운 연구 공백을 이 기록만으로 확정하지 않는다.

**2026-11-23 최신 시작점:** [Progent × AgentDojo × Kata 실습 가이드](hands_on_guide.md)에 전체 구조, 원본과 추가 코드의 경계, 실제 실행 명령, 원본 로그의 색 강조 보기, 관찰 결과와 한계를 정리했다. Kata Guest와 Luna Live는 실제 실행했으며 Run ID별 근거는 [Live 기록](e2e_luna_kata.md)에 있다. 예전 문서의 `NOT RUN`·`BLOCKED`는 작성 당시 상태로 보존했다.

## 현재 범위

Phase 0은 환경·소스·과거 기록 조사였다. 이후 사용자의 지시에 따라 Phase 1에서 격리된 Mock VM Tool을 추가했다. 원본 Progent checkout과 이전 로그는 수정하지 않았다.

| 문서 | 내용 |
| --- | --- |
| [environment.md](environment.md) | 저장소, Python, 의존성, 모델/API 설정 인벤토리 |
| [source_audit.md](source_audit.md) | 원본 정책 생성·검사·집행 호출 경로와 코드상 경계 |
| [prior_runs.md](prior_runs.md) | 기존 정상·공격·Auto-Deny·어댑터 실행의 분리 |
| [experiment_matrix.md](experiment_matrix.md) | 다음 단계의 후보 조건과 필요한 관찰 증거. 전부 미실행 |
| [findings.md](findings.md) | Phase 0에서 확인한 사실·한계와 ActPlane 대조 위치 |
| [progress.md](progress.md) | 단계별 진행 상태와 검증 범위 |
| [handoff.md](handoff.md) | 다음 세션에서 유지할 결정·미결정 사항 |
| [phase1.md](phase1.md) | 새 Mock VM Tool과 원본 Wrapper 연결 |
| [phase2.md](phase2.md) | UC01~UC06 실제 수동 정책 실행과 Run ID별 증거 |
| [live_guide.md](live_guide.md) | 연구자 직접 Manual·LLM Live 실행 절차 |
| [hands_on_guide.md](hands_on_guide.md) | 최신 전체 구조와 API 없는/있는 실습, 원본 로그 색 강조 보기 |
| [meeting_summary.md](meeting_summary.md) | 교수님 미팅용 확인 사실과 미검증 경계 |
| [runtime_environment.md](runtime_environment.md) | Stage A Docker·Kata 실행 조건 조사 |
| [custom_suite.md](custom_suite.md) | Stage B AgentDojo Custom Suite |
| [docker_results.md](docker_results.md) | Stage C 실제 Docker 정책 집행·독립 상태 조회 |
| [kata_results.md](kata_results.md) | Stage D 이전 Kata 실패와 이후 실제 Guest·정책 결과 |
| [live_results.md](live_results.md) | Stage E/F Luna Runner의 이전 인증 장애와 이후 Live 결과 |
| [comparison.md](comparison.md) | 정책·Controller·Runtime 경계 비교 |
| [meeting_20261123.md](meeting_20261123.md) | 월요일 미팅용 요약 |

과거 연구 자료는 로컬 `docs/guided_reproduction_20261117/`, 실행기는 `scripts/progent_*`, 원본 checkout은 `third_party/progent/`, 원본 실행 로그는 `local/guided-reproduction-20261119/` 아래에 있다. 앞의 문서·실행기는 루트 Git에서 **미추적**, checkout·로그는 `.gitignore` 대상이다. 이 문서들은 그 내용을 대체하거나 원본 로그를 Git에 포함하지 않는다.
