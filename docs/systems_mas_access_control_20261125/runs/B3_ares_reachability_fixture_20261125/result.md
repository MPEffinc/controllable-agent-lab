# B3: ARES 명시 ARP 관계식의 분기별 정상성 조건

2026-11-25 UTC. [사전등록](prereg.md)은 `273b541`로 실행 전 push했다. [ARES 원문 §III.2–3](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf)의 `User Invoke(U,F) ∧ User Deny(U,DB1) ∧ Service Reach(F,DB1)`을 **관계식 그대로** 반영한 독립 fixture다. 원저자 LAM·agent·proxy·cloud 배포를 재현한 것이 아니다.

표준 Python `sqlite3`, 호출/API 비용 USD 0. 실행 명령: `PYTHONDONTWRITEBYTECODE=1 python3 -B docs/systems_mas_access_control_20261125/runs/B3_ares_reachability_fixture_20261125/run.py` (exit 0). [코드](run.py), [요청별 원시 decision·서비스 전후 상태](raw.jsonl)를 보존했다. 각 case는 격리된 임시 SQLite DB에서 시작한다. 사용자는 함수 F 호출이 허용되지만 DB1 write는 금지된다. F의 `read_public` branch는 DB2만 읽고 `write_db1`만 DB1을 변경한다.

| Arm | 정상 `read_public` | 금지 `write_db1` | DB1 금지 효과 | 정상 완료 |
|---|---|---|---:|---:|
| origin 검사 없음 | ALLOW | ALLOW | 1 | 1/1 |
| 논문 ARP **관계식만** 호출 전 적용 | BLOCK_PRE_INVOKE | BLOCK_PRE_INVOKE | 0 | **0/1** |
| origin-aware **서비스 effect PEP** | ALLOW | BLOCK_AT_EFFECT | 0 | **1/1** |

서비스 `private.value`는 무방어 금지 요청에서 `before→after`로 바뀌었고, 다른 arm에서는 `before`로 남았다. 정상 read는 effect PEP에서 공개 DB2 `public_ok`를 읽었다. 따라서 **정적 reach relation만** invocation 전체에 적용하면 실제 수행하지 않는 금지 branch의 가능성 때문에 정상 branch도 차단된다. 강한 서비스 PEP는 이 고정 조건의 안전성과 정상성을 모두 달성했다.

**엄격한 한계:** ARES 원문은 LAM이 호출 이벤트를 받아 ARP를 동적으로 조회한다고 하므로, 실제 LAM이 이벤트 인자/branch를 추가로 판단해 정상 요청을 허용할 수도 있다. 공식 코드가 공개되지 않아 이를 확인하지 못했다. 논문 §IV는 네 cloud의 차단 로그와 warm start 평균을 제시하지만 같은 함수의 안전/금지 branch에 대한 false denial 분모·DB 전후 상태는 제시하지 않는다. 따라서 관계식 한정 utility 손실은 fixture에서 `GAP_SUPPORTED`, **ARES 실제 false denial 및 독립적인 새로운 Need는 `UNVERIFIED`**. 실제 ARES가 branch를 구별하거나 PAuth/CONTINUITY 같은 현재 effect PEP를 붙여 정상·안전을 함께 유지하면 이 가설을 기각한다.
