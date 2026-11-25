# B4 사전등록 — 같은 요청의 집행 시점과 최종 SQLite 효과

2026-11-25 UTC, 실행 전. Track B/H18–H19. D5 원본 ActPlane 6.15 게스트 경로를 재사용한다. ARES 원본 LAM은 공개 구현이 없어 이번 결과에 귀속하지 않는다. API 비용 $0, 누적 $0.0754388 / $5.

## 질문·위협 모델

작업 A가 로컬 서비스의 같은 `POST /write` 경로를 통해 A/B row를 변경할 수 있을 때, 사전 호출·dispatch·OS BPF-LSM·최종 SQLite transaction 시점 PEP는 **동일 승인, 동일 요청 형식, 동일 효과 경계**에서 안전/정상/비용이 어떻게 다른가? 승인 oracle은 `task=A → key=A`만 허용하고 `task=A → key=B`를 금지한다. Agent 요청 본문은 비신뢰이며 서비스는 별도 프로세스다. 승인 규칙은 연구자 fixture에 고정하고 원저자 시스템의 주장으로 대체하지 않는다.

## Arm·예측·기각

1. 무집행: 정상 A와 비인가 B 모두 SQLite 효과가 발생해 oracle 민감도를 확인한다.
2. 정적 preflight: 가능한 B 경로가 있다는 이유로 전체 호출을 거부하면 비인가 효과 0이지만 정상 A 과거부 1이다. 이는 ARES LAM의 행동 예측이 아니다.
3. Dispatch PEP: 본문 key/task를 확인해 정상 A만 전달한다. 요청이 큐에 들어간 뒤 철회되면 dispatch 결정만으로는 이전 결정을 보존할 수 있으므로 최신 grant 확인이 없을 때의 결과를 별도 기록한다.
4. OS PEP: **원본 ActPlane** 정적 BPF-LSM `block write file` 정책으로 Agent의 DB 직접 쓰기를 막는다. 동일 TCP endpoint를 통해 서비스가 B row를 쓸 수 있으면 OS의 파일 경계만으로 업무 row 의미를 알 수 없음을 확인한다. 서비스 프로세스의 label 전파·정상 거부가 발생하면 그것을 실제 결과로 기록한다. loader attach 실패 시 `NOT_RUN`.
5. 최종 서비스 PEP 및 OS+서비스 조합: SQLite transaction 직전에 현재 task/key/grant를 확인해 정상 A는 적용하고 비인가 B 또는 철회 후 요청은 거부할 것으로 예측한다. 기존 효과 시점 PEP가 조건을 해결하면 새로운 집행 메커니즘 Need는 기각한다.

각 arm의 정상·비인가 입력을 분리된 초기 `A=0, B=0` DB에 적용한다. 응답, 접수/적용 시각, row 전후, direct DB 쓰기, eBPF 위반 로그, 실행 시간과 프로세스 상태를 남긴다. 서비스 PEP는 연구자 fixture, OS Hook은 원본 ActPlane임을 구분한다. 로컬 loopback·일회용 QEMU guest만 사용하고 호스트 보안 설정/서비스는 바꾸지 않는다. 정책의 실제 효과가 예측과 다르면 기각하고 설명을 수정한다.
