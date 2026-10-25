# controllable-agent-lab

설치된 관측 도구 1개가 악성인 멀티에이전트 운영 복구 시스템에서, 강한 기존 방어로도 막히지 않는
"허용 범위 내 해로운 행동"이 어디에 남는지 측정하는 연구 저장소다. 반복되는 잔여가 확인될 때만
최종 안전장치(Controllable Agent)를 설계한다. 지금은 방어 설계로 갈 수 있는지 확인하는 1단계(타당성 확인·측정)다.

- 연구 중심 정의·위협 모델·가설: [docs/context/research-context.md](docs/context/research-context.md)
- 환경 조사·판단(SREGym 선택 근거, 사실 정정 목록): [docs/context/env-decision.md](docs/context/env-decision.md)
- 작업 규칙(Claude Code용): [CLAUDE.md](CLAUDE.md)

## 구조
| 경로 | 내용 | 커밋 |
|---|---|---|
| `docs/context/` | 연구 컨텍스트, 환경 결정 문서 | O |
| `docs/reports/` | 사전 점검·실험 보고서(민감 정보 제거본) | O |
| `env/sregym/` | SREGym 용 메모·스크립트와 업스트림 커밋 해시(`UPSTREAM_COMMIT`) | O |
| `legacy/lab-v0/` | 이전 실습(S0~S2, 직접 구축한 소형 환경). **결과의 근거로 쓰지 않는 학습·부품 시험용**이며 게이트·판정기·기록기 이식의 원본. 설명은 [legacy/lab-v0/README.md](legacy/lab-v0/README.md) | O |
| `third_party/` | 업스트림 클론(SREGym 등). 수정 금지 | X (gitignore) |
| `local/` | 원시 출력(점검 로그 등) | X (gitignore) |
| `.venv/` | 파이썬 가상환경(Python 3.12) | X (gitignore) |

정리 전 상태(이전 실습이 최상위에 있던 시점)는 git 태그 `lab-v0` 로 복원할 수 있다.

## 현재 상태
- 단계: 1단계 타당성 확인·측정. 사전 점검과 무공격 기준선 뒤, 한 SREGym 과제의 관측 위조→진단→수리→게이트→실제 상태→복구·피해 판정을 연결했다.
- 최신 파일럿(2026-10-26): `service_wrong_pod_selection_hotel_reservation`, 정상/위조 × G0/G1/G2 × 2회 = 12/12 유효 실행. 위조 G0·G1은 4/4 잘못된 실제 변경과 추가 피해, G2는 2/2 실행 전 차단·추가 피해 없음. 정상 G0·G1·G2는 6/6 복구했다. 이 사례의 거짓 보고는 승인 기준+독립 상태 확인이라는 강한 기존 방어로 해결됐으며 새 방어 기여로 주장하지 않는다.
- 남은 질문: G2가 위조 요청을 막은 뒤에도 원래 장애는 미복구다. 다음 최소 실험은 신뢰된 대체 관측 1회로 안전 복구를 이어 가는 비용 측정이다. 승인 기준이 없는 과제와 정책 작성 부담은 그 다음 후보이다.
- 최신 산출물: [통합 보고서](docs/reports/2026-10-26-sregym-gate-pilot.md), [실행별 CSV](docs/reports/2026-10-26-sregym-gate-pilot-results.csv), [NABC TSV](docs/reports/2026-10-26-nabc.tsv), [사전 고정 계획](env/sregym/pilot/PLAN.md)
- 과거 기록: [야간 실행](docs/reports/2026-10-22-overnight.md), [사전 점검](docs/reports/2026-10-21-precheck.md)
