# C1c 일반 JSON 호환성 어댑터 결과

2026-11-25 UTC. [사전등록](prereg.md). 원본 source는 무수정이나 `compat_adapter.py`는 모델 prompting/출력 방식을 바꾸므로 **논문 재현이 아니다**.

CLI exit 1 (10.6초). `IntentMapResponse`, `MapReviewResponse`, `PropertyAtomsResponse` 모델 요청 3회 성공. `adapter_usage.jsonl`의 총 입력 5,440 토큰, 출력 681 토큰, 추정 $0.0032656. 첫 policy property atom의 필수 `rationale` 필드를 모델이 빠뜨려 원본 Pydantic 검증에서 종료. 원본 자동 재시도 판정은 이 ValidationError를 recoverable malformed output으로 취급하지 않았다. Stage0/1 schema 작성과 context packet까지 진행했으나 **검증 가능한 후보·정상/비인가 effect 없음**. 이 누락은 모델 출력 형식 오류이며 승인 의미의 오류 증거가 아니다.

사전등록 재시도 한도에 따라 같은 full author 경로는 중단한다. C1–C1c 전체 추정 비용 $0.0032656, 기존 B1/B2 포함 연구 누적 추정 **$0.0043872 / $5**. 다음 Track C 검증은 고정 gold policy와 원본 validator의 독립 요청/후보 대조로 별도 사전등록해야 하며 C1을 성공 재현이라고 부르지 않는다.
