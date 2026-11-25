# A3 ALPS 공식 Python verifier 최소 실행 — 사전등록

- 질문: 연구실 ALPS의 공개 런타임 verifier가 정적 function allowlist에 대한 정상 SDK action/resource를 허용하고 다른 action/resource를 거부하는가? monitor는 block과 구별되는가?
- 원래 주장: [ALPS 원문 §IV–V](https://cclab.info/papers/2026_shin_infocom.pdf)은 소스 코드에서 최소 권한을 추출하고 SDK 호출 전 런타임 검사를 수행한다. 본 실행은 추출기·실제 클라우드·LLM을 재현하지 않는다.
- 입력·예상: 공식 `runtime/python/test_runtime.py`의 `prod-Orders` PutItem 허용, `prod-Customers` PutItem 및 DeleteTable 차단, monitor violation의 decision/log 관측. official suite 그대로 1회 실행.
- 반증 관찰: 공식 테스트 실패 또는 정상/비인가 경계가 뒤집힘.
- 최소 비용: Python stdlib, 외부 API/서비스/컨테이너 0, USD 0.
- 완료 조건: SHA, 명령, exit, 원시 stdout/stderr, 모드·PEP 위치, 본 결과의 한계 기록.
