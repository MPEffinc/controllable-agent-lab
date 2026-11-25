# Cedar 조건부 허용 대안의 로컬 결정·효과

[사전 등록](prereg.md)에 따라 [공식 Cedar CLI v4.12.0](https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.12.0) 실험 binary를 사용했다. 입력은 [정책](policy.cedar)의 `when { context.registration_open }`, 같은 principal/action/resource, false/true [context](context_false.json) 두 개다. 정확 명령, binary/input SHA-256, stdout/stderr, 로컬 ledger 전후 상태는 [raw.json](raw.json)에 있다. 실행 명령은 저장소 루트의 `python3 docs/access_control_empirical_20261124/runs/K05_conditional_alternative_20261124/run.py`다. 모델/API/실서비스 0, seed 해당 없음, 비용 USD 0.

| context | CLI 결정/exit | 로컬 read effect 전→후 | 평가 |
|---|---:|---:|---|
| `registration_open=false` | `DENY`, exit 2 | 0→0 | 비인가 조건 차단 1/1 |
| `registration_open=true` | `ALLOW`, exit 0 | 0→1 | 정상 조건 완료 1/1 |

CLI 결정 뒤 독립 wrapper가 인메모리 ledger를 바꾼 **로컬 효과**다. 이는 Cedar가 요청 context 조건을 표현·판정할 수 있고 애플리케이션 PEP가 그 결정을 따를 때 이 단순 조건의 안전성과 정상 완료가 함께 가능하다는 **기존 대안의 구성적 반례**다. 조건 값을 공급하는 애플리케이션을 신뢰하며, 상태 변화와 실제 provider commit 사이의 원자성·정보 출처·자연어 정책 생성·서비스 효과는 시험하지 않았다. 이 결과를 K07 NGAC-IR 생성기 또는 K05 OOPSLA 논문 평가의 재현으로 부르지 않는다.
