# C7 사전등록 — 공식 gold의 표기 민감성 교차 사례

2026-11-25 UTC. 읽기 전용으로 고정된 AutoCedar 공식 gold-reference-dataset 200 case 중 `(!(true) ||`가 들어 있는 파일은 184개였다(`third_party/K06-autocedar` SHA `a0cf180977d799cf943514b67ffc260fc579b9a5`). 이는 표현 빈도이며 정책 오류·리뷰어 실패율이 아니다. 각 50-case 구간에서 **첫 번째 해당 파일**을 사전 선택한다: `case-001`, `case-052`, `case-101`, `case-151`. 선택 규칙·네 case는 모델 결과를 보기 전에 고정했다.

- **RQ:** case-011 이외 공식 gold에서도 독립 자연어 정책 reviewer의 거짓 거부가 재현되는가? `(!(true) || X)`만 제거한 동치 정책에서 거짓 거부가 줄어드는가?
- **입력:** 각 case의 공식 `requirement.md`와 `gold/gold.cedar`. `(!(true) || X)`의 바깥 괄호를 포함하는 식만 `(X)`로 바꾸며 `>=0` 등 다른 조건은 건드리지 않는다. 원본/정규화의 양방향 포함을 원본 AutoCedar verifier로 먼저 확인한다. 원본과 정규화 모두 공식 gold와 의미가 같으므로 reviewer 정답은 8개 전부 승인이다.
- **모델:** C4와 동일 system prompt, `gpt-4.1-mini-2025-04-14`와 `gpt-4.1-2025-04-14`, temperature 0, seed 20261125. 각 모델 8 calls. 순서는 `001 original, normalized; 052 normalized, original; 101 original, normalized; 151 normalized, original`. 각 호출은 독립 stateless. 원시 요청/응답·토큰·비용 저장.
- **반증:** 원본 4/4 승인이라면 C4/C5 실패를 다른 case에 일반화하지 않는다. 원본 거짓 거부가 정규화 뒤 그대로면 이 한 가지 표기 제거만으로 해결된다는 가설을 기각한다. 개선되더라도 4-case 편의 표본의 정상성 결과이며 저자 ModelReviewer, 인간 검토, 비인가 정책 승인율로 확대하지 않는다. 정형 동치가 실패하면 API 호출 없이 멈춘다.
- **비용·효과:** 최대 16 calls, 예상 <$0.10, 누적 $5 이하. 보안 effect는 C4에서 별도 확인했으며 C7은 **decision-only** 정상 gold 리뷰 정확성이다. 실제 provider effect 없음. 결과를 보고 case/prompt를 바꾸지 않는다.
