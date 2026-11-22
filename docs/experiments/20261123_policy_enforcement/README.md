# Progent 정책 생성·집행 실험

기록 시작: 2026-11-22 (UTC). 목표는 새 Use Case에서 **적용된 정책, Agent가 제안한 Tool Call, 원본 Progent의 판정, Backend 실행 여부, 최종 상태**를 각각 관찰하는 것이다. 기존 연구의 보장 범위나 새로운 연구 공백을 이 기록만으로 확정하지 않는다.

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

과거 연구 자료는 로컬 `docs/guided_reproduction_20261117/`, 실행기는 `scripts/progent_*`, 원본 checkout은 `third_party/progent/`, 원본 실행 로그는 `local/guided-reproduction-20261119/` 아래에 있다. 앞의 문서·실행기는 루트 Git에서 **미추적**, checkout·로그는 `.gitignore` 대상이다. 이 문서들은 그 내용을 대체하거나 원본 로그를 Git에 포함하지 않는다.
