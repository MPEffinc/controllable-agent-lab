# A5 사전등록 — 현행 Agent libOS task authority 대안

2026-11-25 UTC. 공식 [Agent libOS](https://github.com/yingqi-z20/Agent-libOS) 고정 `85e8ff94c1e562bfb1f891714e3bf4bed9795690`, 패키지 v1.6.0. 논문 평가 시점의 판본과 같다고 가정하지 않는다.

- **RQ:** B1에서 제기한 공유 worker와 자식 위임 권한 문제를, 강한 현행 대안이 host-authored manifest와 parent intersection, effect ceiling으로 이미 막는가?
- **검증:** 원저자 `tests/runtime/test_authority_manifest.py`에서 host manifest hash/persistence, child narrow allow/outside deny, child ceiling widening deny, empty effect ceiling deny를 같은 고정 판본에서 실행한다. 정상 허용과 비인가 거부를 함께 확인한다.
- **신뢰/범위:** manifest는 trusted host가 작성하며 실험의 정책 목표는 고정이다. 이 테스트는 runtime 결정·SQLite 상태 테스트이지 외부 provider의 실제 effect까지 입증하지 않는다. 그 부분은 별도 질문/실험으로 분리한다.
- **반증:** 테스트 실패나 effective policy가 명시 ceiling보다 넓게 작동하면 현행 구현 범위의 반례. 모두 통과하면 B1의 넓은 '권한 위임 자체의 미해결' 가설을 기각하되 자연어→manifest 변환과 provider effect 결속은 남긴다.
- **자원/완료:** `uv.lock` 고정 의존성을 별도 `env/`에 설치, 공식 pytest 선택 실행. 유료 API 0, source 수정 0. 명령·버전·exit·원시 로그를 저장하면 완료.
