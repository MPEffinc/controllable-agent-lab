# H1 최종 좁은 판정: 생성된 정책 target의 의미 오류와 사람 검토

2026-11-24. **가장 좁게 지지되는 것은 K06 AutoCedar의 사람 검토 효과에 관한 평가 지식 공백**이다. 이를 `GAP_SUPPORTED`라고 부를 때 범위는 **“모델이 승인한 target의 관측된 오류를 실제 사람이 원문을 보고 얼마나, 어떤 비용으로 고치는가가 K06의 동일 200-case 조건에서 측정되지 않았다”**뿐이다. [ECOOP 2026 `pick` §4.3/Table 4](https://drops.dagstuhl.de/storage/00lipics/lipics-vol372-ecoop2026/html/LIPIcs.ECOOP.2026.22/LIPIcs.ECOOP.2026.22.html)는 이미 접근정책의 의미 검토를 실제 사람에게 시험했으므로 **분야 전반의 사람 검토 연구 부재 가설은 `REJECTED_HYPOTHESIS`**다. K06만의 미평가를 새 프레임워크의 필요성, 기존 사람 검토의 실패, 일반 MAS 배포의 비인가 효과로 확대하지 않는다. 그 더 강한 명제와 독립 Research Need는 `UNVERIFIED`다.

## 1. 원래 조건과 관측된 차이

- [AutoCedar v2 §V-A, §V-D2/Table VI](https://arxiv.org/html/2607.03656v2): typed gold schema와 자연어 요구를 같은 GPT-6-Luna medium 조건에 제공하고 gold policy는 숨긴 200-case 실험이다. 197개 정책이 완성되어 **197/197 자체 생성 plan 통과**, 178/200은 독립 gold와 동치였다. 남은 19개는 plan의 `L ⊆ G ⊆ U`가 성립하지 않았다. floor가 gold-금지 요청을 포함한 **16 case**, ceiling이 gold-허용 요청을 제외한 **2 case**, 양쪽 **1 case**다. 따라서 gold를 기준으로 적어도 **17 case에는 과허용**, **3 case에는 정상 허용 누락**이 있다(한 case 중복). 이는 case 수이며 실제 서비스 효과·요청 수가 아니다.
- 같은 논문 §V-D3의 14명/98답변 결과는 두 완성 artifact 중 선호 판단이다. 저자는 **AutoCedar human-review mode를 아직 평가하지 않았다**고 명시한다. §VI는 잘못 승인된 atom/누락된 요구가 잘못된 검증 경계를 만든다고 인정한다. 그러므로 19건은 *형식 도구의 오류*도, *사람 검토 실패*도 아니다.
- [공식 AutoCedar source](https://github.com/neselab/cedar-synthesis-engine/tree/a0cf180977d799cf943514b67ffc260fc579b9a5)의 200 gold case는 구조화 입력·gold·NL 요구를 공개하지만 19건 각각의 생성 candidate/plan/trace와 case ID는 연결해 주지 않는다. [별도 trace 감사](deep_h1_trace.md)와 [gold 컴파일 확인](runs/K06_gold_integrity_20261124/result.md)을 구분한다.

## 2. 가장 강한 기존 반박을 **같은 조건 여부**로 대조

| 기존 연구/자료 | 직접 확인된 결과 | 왜 K06 사람 검토의 19건을 해결했다고 판정할 수 없는가 |
|---|---|---|
| **독립 gold + Cedar 동치/포함** | K06의 gold 비교가 19건을 실제로 발견했다. 정확한 승인 원본이 있다면 가장 강한 반박이다. | 평가 때 숨겨둔 gold는 실제 정책 작성 시 자동으로 주어지지 않는다. gold 자체의 독립 승인·정확성은 별도 전제다. **gold가 있는 같은 200 case의 사후 판정**과 운영 중 검토자의 사전 판정을 구별해야 한다. |
| **ECOOP 2026 `pick` 인간 의미 검토** | [원문 §2·§4.3.1–2/Table 4](https://drops.dagstuhl.de/storage/00lipics/lipics-vol372-ecoop2026/html/LIPIcs.ECOOP.2026.22/LIPIcs.ECOOP.2026.22.html): ABAC 후보의 차이를 SAT가 구별 요청으로 보여주고 참가자가 허용/거부를 분류해 후보를 고른다. Control(후보 목록), With List(구별 요청+후보 목록), Without List(구별 요청만) **각 50명, 총 150명**이 Accounting/Grading/Technology 세 문제씩 수행. Table 4는 *조건별·문제별 정답 참가자 비율*: 40/66/70%, 46/68/66%, 46/60/64%. Control 대비 유의 개선은 Accounting의 두 조건, Grading의 With List다. [공식 DARTS artifact](https://drops.dagstuhl.de/entities/document/10.4230/DARTS.12.1.7)는 승인된 0.89GB 자료로 regex VS Code 확장과 익명화 사용자 연구 자료·Docker UI/통계 재현을 포함한다. | 가장 직접적인 **기존 인간 의미 검토**로서 넓은 H1을 기각한다. 다만 작은 3개 문제의 GenAI 초안을 저자가 검토해 gold로 삼고 subset/superset/overlap 오답을 인위 구성했다. 사람은 AutoCedar의 atom/intent-map을 수정한 게 아니라 **구별 요청을 판단하고 후보를 선택**했다. K06의 실제 생성 오류 19건에 대한 검출·수정률과 검토 시간은 여전히 미측정. Artifact 설명의 editor는 regex용이며 ABAC 배포 editor로 해석하지 않는다. |
| **K06 별도 CedarBench** | [고정 commit `26539202f02af19466002cecc3db42fbada40702`의 README](https://github.com/neselab/cedarbench/tree/26539202f02af19466002cecc3db42fbada40702)와 [BENCHMARK_LEVELS](https://github.com/neselab/cedarbench/blob/26539202f02af19466002cecc3db42fbada40702/BENCHMARK_LEVELS.md)는 226 scenario(79 mutation+147 realworld)와 Level 1 fixed-target/Level 2 intent formalization을 나눈다. IBM `21/21` plan·`76/76` semantic request, CyberChair `20/20`·`68/68` HITL case study도 표기한다. | 이는 v2 논문 221-task와 **다른 snapshot**이고 gold 200/19도 아니다. 공식 [IBM TRACE](https://github.com/neselab/cedarbench/blob/26539202f02af19466002cecc3db42fbada40702/scenarios/realworld/ultra_ibm_course_registration/TRACE.md)와 [CyberChair TRACE](https://github.com/neselab/cedarbench/blob/26539202f02af19466002cecc3db42fbada40702/scenarios/realworld/ultra_cyberchair/TRACE.md)는 **Codex가 reviewer oracle 역할을 한 수동 AITL trace**, 당시 broken Stage 1 schema-packet 경로 우회라고 명시한다. 실제 사람 참가자의 K06 review mode 성능과 혼동할 수 없다. 이 2 case는 원문→target 수동 작업 가능성을 보이는 강한 대조다. |
| **Reparo** | [§1, §7/Table 8–9, §9](https://arxiv.org/html/2610.41800v1): 다른 모델이 같은 코드·주석·문서 근거에서 행동 oracle을 만든다. 228 저장소, Cedar decision agreement 82.0–86.5% (generated oracle 상대), Cedar rule coverage 모델별 56.3–70.2%, 결합 70.6–75.3%. 390개 oracle test case를 사람 2명이 30–60초/건, 총 약 3.25–6.5시간 검토했고 Cedar 93.1%가 그 검토에서 정확했다. | 정책과 oracle은 **같은 근거를 공유**하므로 저자도 correlated error와 근거 누락·유한 coverage를 인정한다. 사람은 oracle의 표본 품질을 평가했지 K06의 19 Cedar target을 고치지 않았다. 입력도 repo 증거 vs K06 자연어+gold schema라 동일 조건 수치 비교 불가. 그럼에도 `사람 검토/별도 oracle이 없다`는 넓은 주장을 강하게 반박한다. |
| **NGAC-IR와 Text2NGAC** | [NGAC-IR §5 Table 3·§5.3](https://arxiv.org/html/2611.26941v1)은 **동일 714문장/동일 blind faithfulness 채점**에서 NGAC-IR 95.7%(오류 31)와 Text2NGAC 산출물 90.2%를 직접 비교한다. NGAC-IR는 75/714(10.5%)를 review로 보내 오류 26/31을 찾았고, 다른 family judge와 병합해도 **4/31 오류를 놓쳤다**. 5개 단일 judge 미검출은 조건 누락 3, 잘못된 객체 1, 앞 문장에 걸친 권한 1이다. 출처 재확인 비용은 broader-resource probe에서 문장 15.7% 재독으로 측정했다. [Text2NGAC §9](https://arxiv.org/html/2611.12572v1)는 추출+구조 검사 뒤 전문가 검토를 intended workflow로 둔다. | 이 동일 조건은 **두 NGAC 방법끼리의 비교**이지 K06 Cedar target/19건 평가가 아니다. review로 *보내는 것*과 실제 사람이 오류를 수정한 최종 정책 결과는 다르다. Text2NGAC의 915/918 post-patch 구조 mutant 탐지는 원문 의미 완전성 수치가 아니다. 단, source-relative 자동 triage가 실제 문장 오류를 놓칠 수 있음은 직접 관측이며 K06의 target review 필요성을 반박 없이 강화한다. |

## 3. 라벨을 붙일 수 있는 정확한 범위

**`GAP_SUPPORTED` — K06 한정 평가 지식 공백.** K06은 모델 검토된 target의 독립 gold 불일치 19/197을 관측했다. 정작 이를 막는다고 제시한 *실제 사람의 atom/intent-map 검토*가 같은 gold 조건에서 얼마나 오류를 발견하고 정상 허용을 유지하는지 시험하지 않았다. 공식 CedarBench의 `HITL` 수치도 Codex 수동 oracle·다른 snapshot이라 이 빈칸을 채우지 않는다. `pick`은 실험적 인간 ABAC 검토를 이미 보였지만 인위적 후보·3개 문제에서의 **구별 요청에 따른 후보 선택**이므로 K06 실제 target 오류의 atom 검토·수정 성능은 밝히지 않는다. Reparo의 oracle 품질 표본과 NGAC-IR의 flagging 성능 역시 대상·언어·review 단계가 달라 빈칸을 채우지 않는다. 이는 **후속 검증할 K06 특정 지식**의 공백이며, 선행연구의 `pick` 방식이 같은 오류를 더 잘 해결하는지도 확인해야 한다.

**`UNVERIFIED` — 독립 메커니즘 Gap/새 프레임워크 Need.** 독립 gold와 정형 동치, 권한자 전수 검토, `pick`식 구별 요청 판단, 다른 모델 행동 oracle, 출처 역번역은 이미 있는 강한 해법이다. 이들이 *같은* K06 오류를 허용 가능한 비용과 정상 성공률로 놓친다는 자료가 없다. K06의 19건은 **모델 review/자체 target 평가의 한계**일 뿐 사람 검토가 불충분하다는 실험이 아니다. NGAC-IR의 unflagged 4–5건도 독립 gold 또는 전수 사람 검토의 실패 증거는 아니다. 의도 원본 자체에 정보가 빠진 경우는 입력 결손이며 별도 권한자 확인/기본 거부로 다룬다.

**Research Need:** 잘못된 target이 결정 수준에서 gold-금지 허용과 정상 허용 누락을 낼 수 있고, 검토의 비용·정상 업무 영향이 측정되지 않아 **사람 검토와 독립 oracle을 같은 조건에서 비교하는 평가**는 필요하다. 그러나 지금은 신규 보안 메커니즘의 필요성·배포 서비스 효과가 `UNVERIFIED`; 독립 신규 Framework Need **0건**이다. 평가 필요성과 새로운 해법 필요성을 혼동하지 않는다.

## 4. 바로 기각할 수 있는 검증 설계

1. K06 공식 200 gold 입력에서 생성된 `candidate/plan/atom/intent map`을 고정한다. 원저자 19건의 trace가 공개되지 않았으므로 재생성 run은 **새 run**이라고 표기하고 model/seed/version·prompt·비용을 저장한다. gold는 reviewer에게 숨긴다.
2. 같은 case를 사람 source-aware atom review, **`pick`식 구별 요청 분류**, model review, 독립 gold-derived behavioral tests, Reparo식 별도 모델 oracle, NGAC-IR식 역번역/flagging에 가능한 범위에서 배정한다. 다른 언어로의 단순 이식은 공정 비교가 아니므로 변환 오류를 별도 측정한다. `검토 없음/전체 검토/flag만 검토`를 분리한다.
3. 최종 target과 policy를 gold에 Cedar 포함·동치로 비교해 과허용 case/요청, 과거부 case/요청, benign task completion, review 시간·수정률·누락률을 함께 기록한다. 서비스 효과가 없으면 `DECISION_ONLY`다.
4. **기각 조건:** 사람 검토나 현실적 기존 조합이 같은 target 오류를 충분히 발견하면서 정상 업무·비용 목표를 만족하면 이 평가 공백이 닫히고 신규 Need 주장을 버린다. 반대로 모두 실패해도 정보 결손·잘못된 gold·구현/설정 오류를 먼저 분리한 뒤에만 독립 `GAP_SUPPORTED`로 확대한다.

이번 조사에서 추가 LLM/API 호출과 신규 효과 실험은 0건이다.
