# C8 사전등록 — case-101 Cedar 계층 의미와 로컬 효과

2026-11-25 UTC. C7에서 두 블라인드 모델은 공식 gold `case-101`의 `resource.region in principal.assignedGroup`가 직접 일치만 검사해 자손 지역을 놓친다고 판정했다. [Cedar 공식 연산자 문서](https://docs.cedarpolicy.com/syntax-operators.html)는 `in`이 자손 관계에 대해 **전이적이고 자기 자신에 대해 참**이라고 명시한다. C8은 같은 공식 정책으로 독립 요청을 실행한다.

- **RQ:** 지정 `Group`과 같은 지역, 1단계 자손, 2단계 자손, 무관한 지역의 실제 Cedar decision·로컬 승인 효과는 무엇인가?
- **입력/정답:** 공식 `case-101/gold.cedar`, C7의 동치 정규화 정책, 고정 `User` TitleOfficer·funded EscrowFile·모든 다른 조건 만족. `region=root`, `child`, `leaf`, `south` 네 요청의 기대는 차례대로 `ALLOW, ALLOW, ALLOW, DENY`다. `child→root`, `leaf→child→root`의 parent edge는 코드가 제공한다. 정상 효과는 독립 SQLite `clear_to_close` row 추가로 관측한다.
- **반증:** 2단계 자손이 DENY면 C7 모델의 과거부 지적을 다시 검토한다. 공식 정책이 기대와 일치하면 C7 모델 설명은 Cedar 의미 오해이며 gold 자체 오류라고 주장하지 않는다. CLI 오류는 `UNKNOWN`으로 보존하고 성공으로 세지 않는다.
- **비용/범위:** API 호출 $0, 공식 Cedar CLI 4 request×2 policy, 독립 모의 서비스. 실제 escrow provider effect 없음. 원본 AutoCedar reviewer/사람 검토 재현이 아니다.
