# C10 독립 oracle의 정책 불일치 노출 대조

2026-11-25 UTC. [사전등록](prereg.md), [코드](run.py), [원시 요청/응답](raw.jsonl), [Cedar CLI·모델 전체 결과](result.json). 공식 AutoCedar `case-101` gold를 `region in assignedGroup`에서 `region == assignedGroup`로 좁힌 연구자 후보를 사용했다. **공식 Cedar CLI+schema**는 gold의 네 요청에서 `ALLOW,ALLOW,ALLOW,DENY`, 후보에서 `ALLOW,DENY,DENY,DENY`를 반환했다. 따라서 정상 자손 승인 두 건은 후보의 과거부 반례다.

| 모델 oracle | Blind (4요청) | 잘못된 후보 결정·불일치 report 노출 (4요청) | 두 자손 정상 승인 label |
|---|---:|---:|---|
| `gpt-4.1-mini-2025-04-14` | 4/4 | 4/4 | 양쪽 모두 ALLOW |
| `gpt-4.1-2025-04-14` | 3/4 | 3/4 | 양쪽 모두 ALLOW |

총 16 calls, mini 입력 3,173/출력 898 tokens·$0.002706, 강한 모델 입력 3,173/출력 880 tokens·$0.013386, 합계 **$0.016092**. 같은 요청의 blind 정답이 후보 결정 노출 후 오답으로 뒤집힌 사례는 **0**이었다. 따라서 이 고정 구성에서 policy-disagreement exposure가 oracle을 후보 쪽으로 오염시킨다는 가설은 **기각**한다. [Reparo §5.2.2](https://arxiv.org/html/2610.41800v1)의 원본 모델·prompt·repository evidence·manual adjudication은 재현하지 않았다.

강한 모델은 `unrelated/south`를 blind·exposed 모두 ALLOW로 판정하며 `root`가 모든 그룹의 상위라고 설명했다. **중요한 입력 한계:** 모델 입력의 `group_parent_edges=[child→root, leaf→child]`가 완전한 그래프라고 명시하지 않았고 `south`의 parent 부재도 적지 않았다. 따라서 이 2건을 확정 모델 오류로 해석할 수 없다. C8의 실제 Cedar entities에는 `south`의 parents가 빈 배열이라 DENY가 정답이다. C10b에서 이 차이를 명시한 최소 반증 실험을 한다. C10은 독립 oracle 생성의 입력 완전성 위험을 보여 주는 점검 사례이며, Reparo 저자 성능이나 새 시스템 Need의 증거가 아니다.
