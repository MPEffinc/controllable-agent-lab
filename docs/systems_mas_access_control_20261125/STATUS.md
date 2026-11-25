# 상태 — 2026-11-25 UTC

## 현재 검증 질문

시스템 PEP의 자원·호출 단위 권한과 MAS의 원천 승인·위임·작업 범위가 동일 효과에 결속되는가? KubeAegis의 다중 정책 검증, ALPS의 SDK PEP, K04/K15의 서버·효과 PEP 및 기존 교차 계층 방법을 직접 비교한다.

## 기준 감사와 완료

- 기준 브랜치 `exp/20261123-progent-enforcement-usecase`는 지시서 SHA `ce8f62f41d462d62b56352454c6ee151aaa49430`와 일치했고 작업 트리는 깨끗했다. 원격 해당 브랜치 SHA도 같았다. 원격 기본 HEAD `a13622f...`는 다른 참조로, 기준 브랜치에 임의 병합하지 않았다.
- 후속 브랜치 `exp/20261125-systems-mas-access-control` 생성. 기존 R1–R3와 2026-11-24 조사 파일은 수정하지 않는다.
- 기존 STATUS의 `H14 IN_PROGRESS`는 저장된 [H11_context_path 결과](../access_control_empirical_20261124/runs/H11_context_path_20261125/result.md)와 불일치한다. 원본 공개 보조 코드 메서드+shim/결정적 fixture 8 effect row는 완료됐고, 전체 저자 workflow/LLM/원시 41행 인과 재현은 미완료다. 새 표에서는 `H14 narrow implementation observation`과 `broader Need UNVERIFIED`로 분리한다.
- 연구실 [Publications](https://www.cclab.info/publications)와 읽기 전용 [Backlog](https://docs.google.com/spreadsheets/d/1XW5u4aPcshHSyL7Z8cSQZoILxQhWkMRBKb903_aBD3Q/edit)의 메타데이터 및 관련 범위를 확인했다. Backlog `O`는 일정, `S`는 논문 읽기 기록이며 ARES 등의 원문 증거를 대체하지 않는다.
- 연구실 공식 저장소 ALPS SHA `ace0fd2cabdc100bf5491bad3389e47bce6a37f9`, KubeAegis SHA `79845cbcca83f12cab5cc7f6097a68dc2cb1fc5e`, KubeTeus SHA `d484afbfca924e68f5436a425ea0893c5346b7c0`를 격리 checkout했다. ALPS Apache-2.0, 다른 두 저장소의 최상위 LICENSE 미발견.
- [H1–H14 네 축 재평가표](hypothesis_reassessment.md) 초안을 작성했다. H14 결과 존재와 전체 LLM workflow 미검증을 분리했다. [연구실 시스템 대조](systems_comparison.md)에는 KubeAegis §VII-C의 의미 충돌, ALPS 원본 verifier, KubeTeus/Bambda 원문, K04/K15/Agent libOS/다중-target DSL의 강한 반박을 기록했다. 출판 목록만 확인한 POLARIS/ARES 세부는 `UNKNOWN`으로 보존한다.
- [ALPS 공식 Python verifier 12-test 실행](runs/A3_alps_runtime_20261125/result.md): exit 0, 결정 전용. `context`는 decision 키가 아니라 violation 기록에만 사용. 실제 클라우드/Agent effect는 미시험.
- [상위 3개 반증 후보](research_candidates.md)를 H15 공유 worker, H13/H14 event·출처, H16 교차 계층 충돌로 선정했다. H15/H16은 **Gap 판정 아님**. B1 실제 LLM·공식 ALPS+독립 task/service PEP 실험을 [사전등록](runs/B1_shared_worker_llm_20261125/prereg.md)하고 실행 코드를 작성·문법 확인했다.
- `local/progent-vm/.env`에 비어 있지 않은 `OPENAI_API_KEY` 항목이 있고 값은 출력하지 않았다. 이번 후속 연구의 유료 API 사용액 **USD 0 / 총 상한 USD 5**. 실제 서비스 effect 0.

## 다음 실행

1. B1 `python3 docs/systems_mas_access_control_20261125/runs/B1_shared_worker_llm_20261125/run.py`를 **1회** 실행하고 summary/raw·비용을 확인한다.
2. H13/H14를 동일 입력의 실제 LLM+service PEP로 시험할지 B1 결과를 보고 결정한다.
3. POLARIS/ARES 원문 OCR 또는 저자 자료, KubeAegis cross-policy conflict 기존 대안을 더 확인한다. A1 표의 원문 링크를 행별 보강한다.

Git: 초기 체크포인트 `3545acb` push 성공. 이번 A1–A4 문서·B1 사전등록은 별도 commit/push 후 실행한다.
