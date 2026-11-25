# C2 원본 verifier와 독립 의미 oracle 결과

2026-11-25 UTC. [사전등록](prereg.md), [실행 코드](run.py), [전체 원시 명령/출력/상태](raw.json). AutoCedar 공식 source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5`; 공식 case-011 `gold.cedar`의 `context.onVpn` 조건 하나만 삭제한 연구자 후보. 모델/API 비용 $0. 원저자 `autocedar.cli verify`와 공식 Cedar CLI v4.12.0을 사용했다. `verification_plan.py` 두 개와 local effect adapter는 **연구자 작성**, 저자 생성 plan·실제 GitHub API가 아니다.

| 동일 후보 `missing_vpn.cedar`의 target | 후보⇒target ceiling | target⇒후보 floor | 원본 verifier exit |
|---|---:|---:|---:|
| 자기 자신(`self_reference`) | PASS | PASS | 0, loss 0 |
| 독립 gold(`independent_gold`) | FAIL: `onVpn=false` 반례 | PASS | 1, loss 1 |

| 정책 | 정상 maintainer·VPN·승인 | 동일 요청·VPN off | 작성자 본인 |
|---|---|---|---|
| 원본 gold | ALLOW, 모의 PR `open→merged` | DENY, `open→open` | DENY, `open→open` |
| VPN 조건 누락 후보 | ALLOW, `open→merged` | **ALLOW, `open→merged`** | DENY, `open→open` |

**판정:** 형식 검증은 주어진 목표에 대해서는 정확히 작동했다. 승인 의미와 다른 목표를 입력하면 self-reference 검사는 의미 오류를 알 수 없었다. 독립 gold를 목표로 주면 원본 verifier가 반례를 찾았고 정상 request도 허용했다. 따라서 이 고정 조건의 **새 정형 검증 메커니즘 Need는 기각**한다. 남는 질문은 실제 조직 승인에서 정확한 독립 target/gold와 검토자를 어떻게 확보하고 오류·정상성·비용을 측정하느냐이다. 이 실험은 C1–C1c 생성 실패나 논문의 19개 불일치 후보를 재현한 것이 아니다.
