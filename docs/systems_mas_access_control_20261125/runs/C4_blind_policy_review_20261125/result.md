# C4 블라인드 모델 리뷰와 원본 verifier 대조

2026-11-25 UTC. [사전등록](prereg.md), [실행 코드](run.py), [모델 원시 요청/응답](raw.jsonl), [검증·효과 전체 결과](result.json), `service_state.sqlite`. 공식 AutoCedar source/`case-011` gold 고정 `a0cf180977d799cf943514b67ffc260fc579b9a5`. `p0`만 원본 gold, `p1–p6`은 연구자가 조건 하나씩 삭제하거나 approval 하한을 높인 변이. 저자 생성 오류 19건이나 사람/원본 ModelReviewer 평가가 아니다. 모델 `gpt-4.1-mini-2025-04-14`, temperature 0, seed 20261125. 7 calls, 입력 1,770/출력 844 토큰, 추정 $0.0020584. 외부 서비스 0.

| 정책 | Gold 정답 | 블라인드 모델 verdict | 원본 verifier (독립 gold target) | 로컬 Cedar effect |
|---|---|---|---|---|
| `p0` 원본 gold | 승인 | **거부** | 2/2 PASS | 정상 merge 허용·off-VPN 차단 |
| `p1–p5` 각 한 조건 삭제 | 거부 | 모두 거부 | 각 과권한 반례 | 정상 merge 허용·해당 비인가 witness merge 허용 |
| `p6` 최소 approval 2로 강화 | 거부 | 거부 | 과거부 반례 | approval 1의 정상 merge 차단 |

Verdict 정확도는 **6/7**. 원본 verifier는 독립 gold를 주었을 때 **7/7** 정확했다. 모델의 `p0` 거부 이유는 `approvalCount>=0`이 다른 `>=1` 조건을 무력화하고 `!(true) || principal != author`가 항상 true라는 주장이었으나, 두 주장은 Cedar/불 논리상 틀렸다. 따라서 이 고정 입력에서는 **정확한 정책의 거짓 거부 1건**이 관측된다. `p6`의 verdict는 거부로 맞았지만 설명은 'too broad'라고 하여 과거부 방향을 잘못 말했다. 사전등록한 평가지표는 verdict였으므로 설명의 방향 오류를 새 비율로 계산하지 않는다.

**판정:** 저가 모델을 독립 의미 리뷰어로 쓰는 이 단일 세트는 정상 policy를 불필요하게 보류할 수 있다. 그러나 `p1–p6` 오류를 모두 잡았고, gold가 있는 원본 verifier는 전부 정확히 대조했다. 인간 atom review 성능이나 조직 승인 의도 평가를 이 결과로 주장하지 않는다. 더 강한 reviewer·독립 요청 oracle가 같은 세트의 정상·안전을 달성하면 새 메커니즘 Need 기각. 사람 검토 efficacy/cost는 여전히 `UNVERIFIED`.
