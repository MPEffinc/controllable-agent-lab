# C9 공식 Cedar 의미 제공 후 블라인드 검토

2026-11-25 UTC. [사전등록](prereg.md), [실행 코드](run.py), [원시 요청/응답](raw.jsonl), [전체 판정](result.json). C7 `case-101`의 같은 공식 요구사항·gold 원본/동치 정규화 정책을 사용했다. [Cedar 공식 문서](https://docs.cedarpolicy.com/syntax-operators.html)의 `in` 전이·반사 의미와 `!(true)=false`만 system prompt에 추가했다. C7 verdict, gold 정답, C8 효과는 모델 입력에 주지 않았다.

| 모델 | 원본 gold | 동치 정규화 | 비용 |
|---|---|---|---:|
| `gpt-4.1-mini-2025-04-14` | **거부** | **거부** | 2 calls, $0.000964 |
| `gpt-4.1-2025-04-14` | **거부** | 승인 | 2 calls, $0.004868 |

전체 **1/4 승인**, 4 calls, 추정 **$0.005832**. C7의 같은 case 0/4 승인보다는 1건 개선됐지만 사전등록한 4/4 목표에는 못 미쳤다. 특히 mini 원본은 설명에서 `in`의 올바른 의미와 정책이 요구사항에 맞으며 “should be approved”라고 말하면서도 구조화된 `approve=false`를 냈다. 강한 모델 원본도 설명 마지막에 “Approve”라고 쓰고 `approve=false`였다. **설명과 기계가 소비할 verdict의 불일치 2건**을 원시 응답으로 확인했다. 이는 사후 관찰 지표이며 사전등록 verdict 정확도 1/4를 대체하지 않는다. mini 정규화는 여전히 그룹 방향을 뒤집어 이해했다.

**판정:** 단순한 공식 언어 의미 grounding만으로 이 고정 case의 정상 정책 거짓 거부를 안정적으로 고치지 못했다. C8의 정식 CLI와 스키마 적용 요청은 동일·직접 자손·2단계 자손을 허용하고 무관 그룹을 차단했다. 따라서 독립 **전체 정책** LLM reviewer를 단독 release gate로 쓰면 정상 정책 보류 가능성이 있다. 이 결과를 AutoCedar 원본 atom별 ModelReviewer, 사람 리뷰, 비인가 정책의 false approval 성능으로 일반화하지 않는다. 기존 executable request oracle와 정확 gold 대상 verifier가 직접 대안이며, 그것을 얻기 위한 의도 검토의 실제 효능·비용은 미확정이다.
