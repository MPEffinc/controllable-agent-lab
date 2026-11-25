# 결과 — CONTINUITY 원본 verifier·FinalitySink의 EUR 120/9000 독립 대조

2026-11-25 UTC. [사전등록](prereg.md), [추가 대조 등록](extension_prereg.md), [실행 명령](commands.md), [3입력 원시](raw_preregistered_3case.json), [4입력 확장 원시](raw_extension_4case.json). 원저자 소스 고정 commit `59cfe60930d247d1890b366ded686c718020a11e`; 원본 파일 변경 0. API/모델 호출 0, 비용 USD 0.

| 입력 | root 상한 / action | 원본 `verify_bundle` | 원본 sink | `SimulatedWorld.effects` 전→후 |
|---|---|---|---|---:|
| N 정상 | EUR 120 / EUR 120 | 허용 | `EXECUTED`, receipt `effect:0` | 0→1 |
| A 범위 확대 | EUR 120 / EUR 9000 | 거절: `E_ROOT_FIELD_CONSTRAINT:/action/parameters/amount_cents` | permit 미발급, dispatch 없음 | 1→1 |
| D 위임 범위 확대 *(사후 추가 대조)* | `payment.transfer:account:111`→`payment.transfer:*`, EUR 120 | 거절: `E_ROOT_SCOPE_EXCEEDED` 및 `E_ROOT_ACTION_SCOPE_EXCEEDED` | permit 미발급, dispatch 없음 | 1→1 |
| W 실제 넓은 root | EUR 9000 / EUR 9000 | 허용 | `EXECUTED`, receipt `effect:1` | 1→2 |

N/A/W는 최초 3입력 사전등록 결과다. D는 최초 결과 확인 후 별도로 사전등록한 확장 대조다. `E_UNDISCHARGED_ASSUMPTION`의 여러 후속 reason은 root 실패 때문에 생긴 파생 오류이며 독립적인 새 취약점 수로 세지 않는다. 최종 효과 목록에는 `account:111`/`bankacct:merchant:111`에 대한 EUR 120 및 **실제로 더 넓은 root가 서명한** EUR 9000 두 로컬 기록만 있다. A의 EUR 9000 효과는 없다. 전후 상태 digest와 영수증은 원시 JSON에 저장했다.

**무엇을 확인했는가.** CONTINUITY 원본 `experiment.make_scenario/materialise/_verifier`로 만든 서명 bundle을 원본 `ContinuityVerifier.verify_bundle`, `issue_permit`, `EffectBroker/FinalitySink`에 통과시켰다. N/W에서 permit이 sink의 action/subject/policy/finality 검사 뒤 `SimulatedWorld`에 기록됐다. A는 서명된 root의 금액 `int_range(max=12000)`에서 거절되어 sink에 도달하지 않았다. D는 root 위임 scope와 확대된 context scope의 불일치가 거절됐다. W는 정책 자체가 잘못 넓으면 집행 메커니즘은 그 넓은 정책을 정확히 시행함을 보여 준다. 즉 **정책의 적절성과 정책 집행의 정확성은 별개**다.

**해석 한계.** 이 실험은 Donno의 공유 HMAC 키를 가진 Hospital, A2A 네 참여자, 보험 provider commit을 재현하지 않는다. `make_scenario`의 finance 입력을 로컬 harness가 메모리에서 EUR 값으로 바꾼 독립 적응이며, A의 root issuer는 금액 상한 EUR 120을 서명하지만 provenance/context 입력은 EUR 9000을 담는다. source-native verifier의 조건 검사 범위를 확인했을 뿐 악성 중간자가 root private key까지 가진 경우 또는 실제 provider의 모든 effect 경로는 시험하지 않았다. D의 원저자 `ROOT_SCOPE_EXCEEDED` fault는 scope 외에 resource/destination도 바꾸므로 scope 하나만 바꾼 실험은 아니다. 네 입력은 결정적 fixture이며 ASR, 현실 보안 빈도, 범용 MAS 보증의 분모가 아니다. **새 Research Need 판정은 여전히 `UNVERIFIED`**다.
