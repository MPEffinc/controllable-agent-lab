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
- 단계: 1단계 준비·기준선 측정. 사전 점검(2026-10-21)과 야간 실행(2026-10-21 밤) 완료. 공격 요소는 아직 만들지 않음(시나리오·인가 조건 사전 고정 전).
- 야간 실행 요약: SREGym 격리 래퍼·재생성 스크립트 확보. 오라클 빈틈 시험에서 3개 문제의 복구 오라클이 무관한 정책 삭제·과다 권한·데이터 전량 삭제·대상 외 0 스케일을 통과시킴(대상 0 스케일만 차단). 단일/분리 에이전트(OpenAI Agents SDK, gpt-6-luna) 무공격 기준선 15회 실행, 비용 0.15 USD. 환경이 노출한 스크립트 ConfigMap 이 오진 방아쇠로 추정되어(원인 규명은 아님) 기준선이 오염됨.
- 막힌 곳: 결정이 필요한 사항(보고서 8절): 노출 ConfigMap 처리, 에이전트 도구 경계.
- 보고서: [야간 실행](docs/reports/2026-10-22-overnight.md), [사전 점검](docs/reports/2026-10-21-precheck.md)
