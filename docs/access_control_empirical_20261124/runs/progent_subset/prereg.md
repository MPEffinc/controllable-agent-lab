# Progent generated-rule 포함관계 검사 — 사전 질문

- 검증 질문: 원본 `security_policy_subset_check`가 같은 도구의 좁힌 인자 집합은 허용하고, 확대 집합 또는 새 도구는 거부하는가?
- 원래 주장: Progent의 **생성된** 정책 갱신을 기존 허용 집합 이하로 제한하는 SMT 검사. 수동 정책/최초 생성 정책의 의미 정확성 주장이 아니다.
- 예상 결과: 동일 정책·좁힌 enum은 `True`; 넓힌 enum·신규 tool은 `False`.
- 반증: 확대 또는 신규 tool이 `True`, 좁힌 집합이 `False`.
- 최소 비용: 기존 Progent venv, z3 로컬, 모델/API 0.
- 완료: 정책과 bool 결과, 원시 stderr, code commit 기록.
