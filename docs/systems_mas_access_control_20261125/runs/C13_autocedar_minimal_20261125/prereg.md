# C13 사전등록 — 단순 소유자 읽기와 미언급 삭제 Action

2026-11-25 UTC. C12는 공식 case-011의 `hotfix/` 접두사를 모델이 Cedar 무효 문자열 인덱싱으로 반복 합성해 중단됐다. **새 입력**으로 구조만 간단히 하여 원본 AutoCedar Authoring을 끝까지 실행할 수 있는지 확인한다. 원본 source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5` 무수정. C12와 동일한 API 호환 어댑터(unsupported reasoning 제거, 일반 JSON+원본 Pydantic 검증, 형식 오류 한 번 재요청)를 사용하므로 원본 provider 전체 재현과 구분한다.

요구: 소유자만 `readDocument` 허용, `deleteDocument`를 포함한 다른 action 금지. Schema는 User·Document(owner)와 두 action을 명시한다. 가설은 원본 pipeline이 유효 후보·검증을 완료하고 미승인 delete permit을 생성하지 않는다는 것이다. 무효 후보/중단이면 이유를 보존하고 H22 생성 위험을 주장하지 않는다. 유효 후보이면 원본 Cedar/Verifier와 독립 정상 owner read·비인가 nonowner read/delete 요청을 대조한다. 승인·활성화 gate는 별도이며 생성기 출력을 자동 배포하지 않는다.

최대 240초, 이번 실행 예상 API 비용 $0.35에서 중지, 전체 누적 $0.1042252/$5 아래. 사용량·원문 응답·원본 session·Cedar 결과·fixture effect를 새 Run ID에 저장한다. 하나의 모델 seed 없는 실행이 생성기 일반 빈도를 입증하지 않는다.
