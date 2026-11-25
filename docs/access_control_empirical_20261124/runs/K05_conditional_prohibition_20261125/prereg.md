# 기존 Cedar 조건부 금지 대안 — 사전 등록

등록일 2026-11-25 UTC. **질문:** 무조건 `read(doc)` 허용과 `registration_open=false`일 때만 적용되는 금지가 함께 있을 때, 공식 Cedar CLI는 false의 비인가 effect를 0으로 만들고 true 정상 effect를 1로 유지하는가? 이는 K07 strict export가 조건부 prohibition을 항상 적용한다고 인정한 [§5.1](https://arxiv.org/html/2611.26941v1)의 안전·정상 경계를 직접 대조한다.

- **정책/신뢰:** principal `User::"student"`, action `Action::"read"`, resource `Document::"doc"`, 신뢰된 request context Boolean. `permit`은 무조건, `forbid`은 `!context.registration_open` 조건. 동일한 요청 facts에서 context만 변경한다.
- **예상/반증:** false는 Cedar Deny/로컬 ledger 0→0, true는 Allow/ledger 0→1. true에서도 거부되거나 false에서 허용되면 정책·CLI·wrapper 입력을 먼저 감사한다. 기존 조건식 PDP가 고정 bool case를 해결하면 “조건부 금지에는 신규 메커니즘 필수”라는 주장은 기각한다.
- **실행/비용:** 공식 Cedar CLI v4.12.0 실험 binary를 K06 격리 env에서 재사용하고 새 `runs/`에만 정책/원시 로그를 쓴다. 원본 코드는 수정하지 않는다. 모델/API/실서비스 0, seed 해당 없음.
- **완료/제한:** 정책·binary hash, 정확 argv, CLI 결정/exit, in-memory ledger 전후 및 조건별 1요청을 기록한다. trust in context, 동시 전환, 실제 provider finality, K07 생성기/strict export 자체는 시험하지 않는다.
