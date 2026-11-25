# 추가 소규모 대조 — 위임 범위

원래 3입력 실행·`raw.json` 확인 후 2026-11-25 UTC에 등록. 이것은 **사후 추가 대조**이며 처음 3입력의 사전등록 결과와 분리한다. 원래 `raw.json`은 `raw_preregistered_3case.json`으로 보존한다.

질문: 같은 원저자 `verify_bundle`이 루트의 `payment.transfer:account:111` 위임 범위를 `payment.transfer:*`로 확대한 signed context를 거절하는가? 저자 `ROOT_SCOPE_EXCEEDED` fault를 EUR 120 action에 그대로 적용한다. 예상: `E_ROOT_SCOPE_EXCEEDED` 및 효과 +0. 반증: verifier allow 또는 효과 +1. 추가 case를 원래 N/A와 넓은 root W 사이에 놓아 같은 `SimulatedWorld`/`NonceLedger`의 state delta를 관측한다. 원저자 code 호출, 외부 API/모델 0. 이는 A2A 별도 참여자와 실제 provider를 시험하지 않는다.
