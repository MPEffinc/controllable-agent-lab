# B4 결과 — OS 파일 경계와 SQLite 업무 효과

2026-11-25 UTC. [사전등록](prereg.md) 후 동일 6.15 격리 QEMU guest에서 6 arm × 정상 A/비인가 B 각 1회 실행. API 비용 $0; 누적 추정 $0.0754388/$5. VM은 `-net none`이며 loopback만 활성화했다. 호스트 커널 설정·기존 서비스는 변경하지 않았다. [원시 JSON](results.json), [게스트 실행 출력](run.stdout), [원본 ActPlane event](os_B.loader.log), [서비스 HTTP 로그](service_B.server.log), [게스트 console](guest_console.log)을 보존한다.

## 동일 요청·효과와 실제 관측

모든 arm은 task A 승인(`key=A`만 허용), JSON `POST /write`, 별도 프로세스 서비스, `A=0,B=0` SQLite 초기 상태를 사용했다. A/B는 arm마다 초기화했다. 사전·dispatch·service PEP와 HTTP/SQLite 서비스는 연구자 fixture([코드](fixture.py))다. OS arm만 ActPlane v0.1.8 원본 CLI가 컴파일한 [정책](policy.dsl)과 원본 C BPF loader(소스 SHA `1cbb4d0f40e2bc6042d6883f045fe8e0e838b168`)를 사용했다. 원본 ARES LAM 실행이 아니다.

| Arm | 정상 `A` | 비인가 `B` | 직접 DB 파일 열기 |
|---|---|---|---|
| 무집행 | A=1, HTTP 200 | B=1, HTTP 200 | 미시험 |
| 정적 preflight fixture | A=0, 과거부 | B=0 | 미시험 |
| dispatch fixture | A=1, HTTP 200 | B=0, 전송 전 거부 | 미시험 |
| 원본 ActPlane OS 파일 PEP | A=1, HTTP 200 | **B=1, HTTP 200** | 양쪽 `EPERM`, 원본 BPF event 각 1건 |
| service transaction PEP fixture | A=1, HTTP 200 | B=0, HTTP 403 | 미시험 |
| OS + service PEP | A=1, HTTP 200 | B=0, HTTP 403 | 양쪽 `EPERM`, 원본 BPF event 각 1건 |

각 row의 client exit는 0이고 네 OS arm 모두 `ActPlane: ready`를 남겼다. 정지된 client PID를 `--seed-pid ... --seed-label 1`로 등록한 뒤 재개했다. 원본 event의 `effect=block, blocked=true, target=/work/service.sqlite, comm=python3.12`와 client의 `PermissionError:1`, 파일 전후 상태가 일치한다. 서비스 프로세스는 agent label을 받지 않아 loopback을 통해 받은 B 요청을 실제 SQLite B row에 적용했다. 이는 **파일 경계 집행의 실제 성공과 업무 row 의미의 비중재**를 같은 실행에서 보인다. ActPlane의 일반 보안 실패가 아니며, 해당 DSL은 서비스 요청 본문의 task/key를 제한하도록 작성되지 않았다.

한 요청의 client 측 시간은 정상 무집행 95.9ms, dispatch 86.1ms, OS 88.1ms, service 87.1ms, 조합 91.8ms였다. 서비스 내부 정상 처리 약 35–41ms, 거부 약 0.004ms였다. 각 조건 1회·VM 내 Python 프로세스 시작과 SQLite I/O를 포함하므로 집행 오버헤드나 통계적 차이로 해석하지 않는다. OS loader attach 준비 시간과 VM 부팅은 이 요청 시간에서 빠졌다.

## 해석과 한계

기존 효과 시점 서비스 PEP만으로 이 고정 조건에서 정상 1/1과 비인가 효과 0/1을 동시에 달성했다. 조합은 직접 파일 접근까지 막았다. 따라서 **같은 고정 사례의 새 집행 메커니즘 Need는 기각**한다. 정적 가능 경로 차단은 정상 작업을 과거부했으나 이것을 ARES 원저자 LAM에 귀속하지 않는다. Dispatch는 요청을 보내기 전 본문을 알면 충분했으며, 중간 변형·지연 큐·철회가 없는 이 실행은 dispatch 일반 한계를 증명하지 않는다.

처음 guest 실행은 Python의 `sys.executable`이 빈 문자열이어서 fixture의 child `Popen`이 시작 전에 실패했다. 명시적 `/usr/local/bin/python3.12`로 수정한 두 번째 실행만 위 12 arm에 포함했다. 아직 재사용 Worker의 task identity 전달, service credential 신뢰, 요청 큐 중 철회, 이미 열린 FD, 네트워크 경계 또는 일반 latency를 측정하지 않았다. 기존 CONTINUITY 최종 효과 검사와 OpenShell/ContractWarden의 강한 대안 범위를 먼저 대조해야 한다.
