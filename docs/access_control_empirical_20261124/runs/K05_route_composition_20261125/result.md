# Cedar의 허용 경로별 조건·금지 우선순위 대안 결과

[사전 등록](prereg.md)한 여섯 요청에 [공식 Cedar CLI v4.12.0](https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.12.0)을 적용했다. [정책](policy.cedar)은 조건부 permit (`registration_open`), 별도 조건부 permit (`alternate_allow`), 조건부 forbid (`embargo_active`)를 동일 요청에 둔다. `python3 docs/access_control_empirical_20261124/runs/K05_route_composition_20261125/run.py`를 저장소 루트에서 실행했다. [raw.json](raw.json)에 binary/정책/context SHA-256, 정확 argv, stdout/stderr/exit, 각 case의 로컬 effect 전후를 보존했다. 모델/API/실서비스 0, 비용 USD 0, seed 해당 없음.

| 요청 상태 | CLI 결정 | 로컬 effect 전→후 | 의도와 일치 |
|---|---|---:|---|
| closed, 다른 허용 없음, embargo 없음 | Deny | 0→0 | 예 |
| open, 조건부 허용 | Allow | 0→1 | 예 |
| closed, 독립 허용 | Allow | 0→1 | 예 |
| open, 두 허용 | Allow | 0→1 | 예 |
| closed, 독립 허용, embargo 활성 | Deny | 0→0 | 예 |
| open, 두 허용, embargo 활성 | Deny | 0→0 | 예 |

6/6은 **서로 다른 고정 입력의 결정**이며 독립 통계 trial이 아니다. effect는 CLI 결정에 따른 Python wrapper의 인메모리 기록으로서 실제 서비스 커밋이 아니다. 이 작은 같은 조건에서 기존 Cedar는 단순한 전역 `registration_open` gate의 독립 경로 과거부와 정적 금지 상시 적용의 과거부를 피하고 활성 금지는 우선시한다. 신뢰된 context 공급, 상태 변경과 effect의 원자성, 자연어→정책 정확성은 시험하지 않았다. K07 NGAC-IR 저자 생성기나 원저자 `strict+앱` adapter의 재현이 아니다.
