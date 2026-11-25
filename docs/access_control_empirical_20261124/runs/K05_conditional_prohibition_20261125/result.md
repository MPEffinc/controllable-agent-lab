# Cedar 조건부 prohibition의 기존 대안 결과

[사전 등록](prereg.md) 뒤 [공식 Cedar CLI v4.12.0](https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.12.0)로 같은 `read(doc)` 요청을 평가했다. [정책](policy.cedar)은 무조건 permit과 `when { !context.registration_open }`인 forbid를 함께 둔다. [raw.json](raw.json)에 binary/policy/context SHA-256, 정확 argv, CLI stdout/stderr/exit, 로컬 ledger 전후를 보존했다. 재현 명령은 저장소 루트에서 `python3 docs/access_control_empirical_20261124/runs/K05_conditional_prohibition_20261125/run.py`; 기존 raw를 보존하려면 새 run 사본에서 실행한다. 모델/API/실서비스 0, seed 해당 없음, 비용 USD 0.

| 조건 | Cedar 결정 | 근거 정책 | ledger 전→후 |
|---|---|---|---:|
| `registration_open=false` | `DENY`/exit 2 | 조건부 `forbid` `policy1` | 0→0 |
| `registration_open=true` | `ALLOW`/exit 0 | 무조건 `permit` `policy0` | 0→1 |

두 조건은 각각 한 요청과 독립 wrapper의 **인메모리 효과**다. 신뢰된 조건값과 PDP 결과를 효과 전에 적용하면 이 단순 조건부 금지는 기존 Cedar로 안전·정상 완료를 동시에 만족한다. [NGAC-IR §5.1](https://arxiv.org/html/2611.26941v1)이 기술한 strict graph의 조건부 prohibition 항상 적용은 정상 거부 가능성을 남기지만, 이번 실행은 NGAC-IR 저자 export·실제 서비스·동시 상태 전환을 재현하지 않는다. 실제 상태 출처와 commit 시점 원자성은 `UNVERIFIED`다.
