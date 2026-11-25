# C4 사전등록 — AutoCedar gold 조건 변이의 블라인드 모델 검토

2026-11-25 UTC. 공식 K06 `case-011/requirement.md`, `gold.cedar`, `schema.cedarschema`에서 시작. 원문 gold와 연구자가 고정한 여섯 단일 조건 변이를 모델 리뷰어에게 **정답/변이 이름 없이** 제시한다. 원저자 생성 후보나 인간 reviewer 평가가 아니다.

- **RQ:** 블라인드 `gpt-4.1-mini-2025-04-14` 정책 검토자가 원문과 정책의 의미 차이를 발견하는가? 원본 AutoCedar verifier에 독립 gold target을 주면 같은 오류를 찾는가? 각 오류의 정상·비인가 모의 효과는 무엇인가?
- **고정 변이:** `p0` gold; `p1` VPN 조건 삭제; `p2` Maintainer 조건 삭제; `p3` 작성자 본인 금지 삭제; `p4` `hotfix/` branch 조건 삭제; `p5` 최소 approval 1 조건 삭제; `p6` 최소 approval을 2로 과강화. 모델에는 ID·gold·예상 정답을 알리지 않고 같은 자연어 requirement+후보 Cedar만 제공한다. 검토 순서는 `p4,p0,p6,p2,p5,p1,p3`으로 고정한다.
- **정답:** p0만 approve, p1–p6 reject. 각 변이의 구별 요청을 공식 Cedar CLI로 평가해 local SQLite PR `open→merged` 또는 그대로를 관측한다. 정상 p0/변이 요청 및 누락 조건의 비인가 요청을 구별한다. gold reference를 가진 원본 verifier는 candidate⇒gold ceiling와 gold⇒candidate floor를 검사한다.
- **반증:** 리뷰어가 7/7 정확하고 oracle 효과도 모두 예상과 일치하면 이 쉬운 단일 조건 세트의 자동 검토 실패 가설 기각. 놓친 오류가 있어도 독립 gold/verifier가 해결하면 새 메커니즘 Need로 판정하지 않는다. 이 결과를 사람 atom review의 성능으로 환산하지 않는다.
- **비용/범위:** 7 API calls, temperature 0, seed 20261125, 목표 <$0.05/전체 $5; 원시 요청·응답·토큰 기록. 모델은 정책 파일을 실행하지 않는다. 정책 비교/효과는 공식 Cedar CLI와 독립 SQLite adapter. 실제 GitHub effect 0. API 오류는 기록하고 같은 run에서 반복하지 않는다.
