# C10b 사전등록 — 무관 그룹 입력 완전성 반박

2026-11-25 UTC. C10의 강한 모델은 `south`를 `root`의 자손으로 추정했지만, C10 prompt는 group parent edge 목록의 완전성을 명시하지 않았다. C8의 실제 Cedar entity 파일에서는 `south.parents=[]`다. C10b는 `unrelated` 요청 하나만 동일 모델 두 종×blind/exposed 4회에 재제시한다. 기존 prompt·요구사항·후보 decision은 동일하고 **사실 입력만** `group_parent_edges is the complete list; south has no parent and is not equal to root`로 보충한다. 정답 label은 사전 고정 `DENY`다.

- **RQ:** C10 강한 모델의 두 ALLOW가 정보 누락을 해소하면 DENY로 바뀌는가?
- **반증:** 두 모델/arm 4/4 DENY이면 C10 강한 모델 오답을 사실상 불완전 입력에 따른 것으로 좁히며, 독립 oracle 자체의 새 메커니즘 Need를 주장하지 않는다. strong의 ALLOW가 남으면 이 한 요청에서 완전한 증거를 줘도 label 오류라는 조건부 관찰을 기록한다. 이전 C10 답·gold label은 모델에 주지 않는다.
- **비용·경계:** 4 calls, 목표 <$0.02, temp0/seed20261125, 원시 로그·비용 기록. C10과 같은 독립 fixture이며 Reparo 원본 실행이 아니다. API 오류·잘림은 재시도하지 않는다.
