# K07 조건부 권한에 대한 Cedar 대안 — 사전 등록

2026-11-24 UTC. **질문:** K07의 조건부 허용과 같은 `read(doc)` 의도를 Cedar의 요청 `context`와 `when`으로 표현할 때, `registration_open=false`에서는 로컬 effect 0이고 `true`에서는 정상 effect 1인가?

- **원래 주장/대안:** [NGAC-IR §5.1](https://arxiv.org/html/2611.26941v1)는 NGAC Policy Machine graph가 조건을 검사하지 못한다고 인정한다. [공식 Cedar authorization 문서](https://docs.cedarpolicy.com/auth/authorization.html)는 요청 context와 `when` 조건을 지원한다. 이는 K07 저자 코드 재현이 아니라 기존 직접 대안의 독립 컴포넌트 시험이다.
- **정책 의도:** `User::"student"`가 `Action::"read"`를 `Document::"doc"`에 수행하는 것은 신뢰된 `registration_open=true`일 때만. 거짓 상태의 effect 0/참 상태의 effect 1이 안전·정상 완료 조건이다.
- **예상/반증:** Cedar 동일 정책에 두 context를 넣어 각각 Deny/Allow가 나오고, 결정에 연결한 독립 로컬 ledger가 각각 0/1이면 직접 조건 PDP가 이 단순 조건을 해결한다. 동일 정책에서 거짓 상태 Allow나 참 상태 Deny가 나오면 코드/입력/버전을 점검하고 대안을 재평가한다.
- **범위/비용:** 공식 Cedar CLI v4.12.0 실험 binary를 사용하며 원본 소스를 수정하지 않는다. 새 `runs/`에 정책·entities·context와 결과만 저장한다. 모델/API 0, 실서비스·네트워크 0, seed 해당 없음. app이 condition 값을 정확히 공급하고 PEP가 결정을 실제 효과 앞에 적용한다는 신뢰 가정을 명시한다.
- **완료:** binary/policy SHA-256, 정확 명령, CLI stdout/stderr, 결정, effect 전후 및 정상/비인가 분모 저장. 이 결과가 시간 경합·서비스 원자성·자연어 생성 정확성을 증명하지 않음을 표시한다.
