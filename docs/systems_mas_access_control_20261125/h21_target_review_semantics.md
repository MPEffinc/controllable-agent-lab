# H21 — 승인 의도 target을 검토하는 모델의 정책 언어 의미·판정 일관성

2026-11-25 UTC. **보안 속성:** 정상 요청을 허용하면서 승인하지 않은 요청을 거부하는 target을 정확히 잡고, 최종 policy가 그 target을 충족한다. **정상 업무:** maintainer의 조건부 PR merge와 자손 지역 escrow 승인. **가정:** 요구사항과 Cedar 정책을 전체로 읽는 독립 LLM reviewer가 target의 적절성을 승인/거부한다. 공격자는 필요하지 않다. 생성된 정책의 복잡한 표기와 Cedar 연산자 의미가 오류를 유발할 수 있다.

## 직접 관측

| 증거 | 관측 | 한계 |
|---|---|---|
| [C4/C5](runs/C5_stronger_review_20261125/result.md) 공식 `case-011` gold+여섯 변이 | 두 모델 모두 6/7, 정확 gold를 거짓 거부. 설명의 `!(true) || X` 논리 오류 | 원본 AutoCedar atom별 reviewer나 저자 후보가 아닌 독립 전체 정책 reviewer |
| [C6](runs/C6_normalized_review_20261125/result.md) | 정형 동치 7/7 뒤 두 모델 7/7. 표기 오류는 기존 verifier+정규화로 해결 | 한 case, 고정 규칙 |
| [C7](runs/C7_cross_case_review_20261125/result.md) 네 공식 gold | `001` 강한 모델 표기 오거부는 정규화로 해결. `101` 두 모델은 원본·정규화 모두 거짓 거부하며 `in` 계층 의미를 오해 | 4-case 선택 표본. `052` 한 응답 출력 잘림. 비인가 정책 검출력은 C7에서 미시험 |
| [C8](runs/C8_cedar_hierarchy_effect_20261125/result.md) | 공식 gold/동치 정규화 × 4 group 요청, 정식 Cedar schema decision 8/8. 직접·2단계 자손 허용, 무관 그룹 거부, 모의 효과도 일치 | 실제 escrow 서비스 아님 |
| [C9](runs/C9_grounded_review_20261125/result.md) | 공식 `in`/`!(true)` 의미 제공 뒤 승인 1/4. 두 응답은 설명에서 승인하라고 하면서 `approve=false` | 2 모델×2 정책, 간단 grounding. 실제 atom reviewer 미시험 |

## 기존 연구와 가장 강한 반박

- [AutoCedar v2 §V-D2/Table VI](https://arxiv.org/html/2607.03656v2)는 완료 197/200 중 **178 gold-equivalent**, **19는 생성된 검증 plan은 통과했으나 gold와 다른 target**이라고 보고한다. §V-D3의 14명/98 probe는 artifact 선호도 실험이고 **실제 human atom review의 오류 검출률은 평가하지 않았다고 명시**한다. 따라서 target review 정확성은 저자도 인정하는 평가 공백이다. 그러나 C4–C9의 모델 오류가 그 19건의 원인이라는 증거는 없다.
- **정확한 독립 target이 있으면** 기존 AutoCedar/Cedar 양방향 포함이 C2·C4·C6·C7에서 오류·동치를 정확히 검사했다. [Cedar 공식 문서](https://docs.cedarpolicy.com/syntax-operators.html)와 C8의 실제 실행도 `in` 의미를 제공한다. 이 조건의 새 정형 검증 메커니즘 Need는 기각한다.
- [Reparo v1 §5.2, §7](https://arxiv.org/html/2610.41800v1)는 별도 LLM이 repository code/comment/doc에서 구체 요청과 기대 결정을 만들고 공식 정책 엔진으로 검사한다. 390 oracle 사례를 사람이 평가해 91.5–96.9%의 정답률을 보고한다. **가장 강한 직접 대안**이지만 같은 연구의 §5.2.2는 정책과 불일치한 oracle case를 재해석·정정하기도 한다. 그 운영 방식과 AutoCedar의 human atom 검토를 동일 조건에서 비교한 결과는 없다. 논문 수치를 C4–C9와 직접 비교하지 않는다.

## 판정과 반증 조건

1. **`GAP_SUPPORTED` (좁은 구현·평가 조건):** 독립 전체 정책 LLM reviewer 단독의 정상 정책 보류와 설명/구조화 verdict 불일치. C8의 정상 서비스 효과를 승인 단계에서 막을 수 있다. 정상 완료율의 실제 저하는 이 실험의 독립 게이트 구성에서만 주장한다.
2. **`REJECTED_HYPOTHESIS` (정확 target 존재):** 새로운 Cedar 의미 검증기 필요. 기존 verifier+정확 gold가 해결했다.
3. **`UNVERIFIED` (독립 Research Need):** 신뢰 가능한 target이 아직 없을 때, 자연어/조직 승인에서 얻은 **독립 요청 oracle 또는 사람 atom review**가 과권한·과거부를 어떤 비용과 정상 업무 영향으로 찾아내는가. 저자 19 plan 오류와 실제 human review 성능을 연결한 직접 자료가 없다.

**기각 조건:** Reparo식 독립 요청 oracle, 전문 사람 review, 또는 원본 AutoCedar atom reviewer가 같은 source-only 요구사항·공식 semantics·정상/비인가 요청에서 높은 오류 검출력과 낮은 정상 과거부를 비용 상한 내 보이고, 오류를 고친 target hash가 실제 활성 PEP에 결속된다면 새로운 Need를 기각한다. 반대로 실제 저자 target 오류 19종 또는 독립 실서비스 사례에서 그런 대안이 실패하는 paired 결과와 보안·정상 업무 영향을 보여야 Need를 승격한다. 현재 C4–C9만으로 일반 MAS 보장을 주장하지 않는다.

**다음 질문:** 정책과 불일치한 oracle의 기대 label을 사후 재해석하는 평가가 알려진 gold 오류를 놓칠 수 있는가? 원본 Reparo artifact·저자 지표를 먼저 확인하고, 없으면 **독립 통제 실험**임을 명시해 모델에 정책 불일치 정보를 주는 arm과 blind arm을 비교한다.
