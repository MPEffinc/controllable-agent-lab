# B3 사전등록: ARES ARP의 가능 경로와 invocation별 실제 효과

2026-11-25 UTC. 이 실험은 [ARES 원문 §III.2–3](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf)의 **명시된 관계식만 구현하는 독립 fixture**다. ARES 원저자 코드/LLM 재현이 아니다.

- **질문:** `User Invoke(U,F)`, `User Deny(U,DB1)`, `Service Reach(F,DB1)`이 모두 참일 때, F의 이번 호출이 DB1을 사용하지 않는 정상 branch까지 정적 reach 관계만으로 선제 거부되는가?
- **원래 주장:** ARES는 함수 호출 시 ARP를 조회해 우회 가능 경로가 있으면 함수 실행 전 차단한다. 논문 §IV는 4개 cloud의 우회 예시와 warm start 시간을 보여준다. 정상 분기 완료/false denial 분모는 확인되지 않는다.
- **설정/신뢰:** U는 F 호출 가능, U의 DB1 write는 거부, F의 service role은 DB1 write 가능. F의 `read_public` branch는 공개 DB2만 읽고, `write_db1` branch만 DB1을 변경한다. actor, branch 입력, 정책·서비스 상태는 fixture에서 신뢰한다. 실제 클라우드/ARES LAM은 사용하지 않는다.
- **비교 arm:** (1) 원천 권한 검사 없는 baseline, (2) 원문 ARP 관계식만 적용한 호출 전 gate, (3) 강한 대안인 origin-aware service effect PEP. 두 요청을 세 arm에 동일하게 replay한다.
- **예상/반증:** 관계식만 적용하면 두 요청 모두 차단되어 비인가 write 0이나 정상 완료 0. effect PEP가 정상 read 1/1, 비인가 write 0이면 정적 관계 gate의 utility 한계가 드러나지만 **새 메커니즘 Need는 기각**된다. ARES 실제 LAM이 입력 branch를 정확히 구별하거나 원문 ARP가 그 구별을 포함한다는 근거가 나오면 ARES 적용 한계 가설을 버린다.
- **최소 비용/완료:** 표준 Python sqlite3, API USD 0, 합성 row 2개, 각 arm 전후 DB1/DB2 상태·decision·정상 완료·비인가 효과를 JSONL에 남기면 종료한다. 서비스 effect는 로컬 SQLite이며 클라우드 효과가 아니다.
