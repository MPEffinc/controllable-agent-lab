# Stage D: Kata 실행 시도와 실패 조건

> 이 제목과 첫 절은 2026-11-22 상태다. **2026-11-23 실제 Kata + Progent 6/6 결과**는 문서 끝의 후속 결과 절을 참조한다.

2026-11-22 UTC, **Kata workload NOT RUN**. Host는 KVM 장치 읽기·쓰기 가능, nested virtualization=`Y`, QEMU와 `/dev/vhost-vsock`이 있다. 그러나 Kata shim/guest kernel/image가 설치되어 있지 않고 기존 Docker daemon에는 `kata` runtime이 등록되지 않았다.

| 방법 | 실제 명령 | 결과·원인 |
| --- | --- | --- |
| 기존 Docker에 Kata 요청 | `docker create --name cclab-progent-exp-kata-probe --runtime kata --network none --memory 128m --pids-limit 64 busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662 sleep 1` | exit 1, `unknown or invalid runtime name: kata`; 컨테이너 생성 안 됨 |
| 별도 rootless Docker 검사 | `dockerd-rootless-setuptool.sh check --force` | exit 1, `Missing system requirements`, `newuidmap`/`newgidmap` 및 `uidmap` 패키지 필요 |
| 사용자 namespace 가능성 | `unshare -Ur true` | exit 0. 단일 사용자 namespace 가능만 확인; rootless Docker/Kata 기동 증거 아님 |
| 시스템 패키지 권한 | `sudo -n true` | exit 1, `a password is required` |
| 시스템 containerd | `ctr namespaces ls` | exit 1, socket permission denied |

공식 [설치 안내](https://github.com/kata-containers/kata-containers/blob/main/docs/installation.md)에 따르면 Docker에서 Kata runtime-rs를 사용하려면 공식 tarball의 shim·guest artifact를 설치하고 Docker daemon에 runtime을 등록해야 한다. 현재 daemon은 기존 SREGym 워크로드 4개를 호스팅한다. 전역 daemon 설정 변경·재시작이나 보안 권한 우회는 허용 범위 밖이므로 시도하지 않았다. rootless 경로는 `uidmap` setuid 바이너리 부재로 진행하지 못했고 비대화형 sudo도 불가능했다. tarball 다운로드·압축 해제만으로 실험 가능한 runtime이 생기는 상황이 아니어서 대규모 artifact 설치는 하지 않았다.

두 대안을 검토했다: (1) 기존 Docker 등록은 daemon 전역 변경이 필요, (2) 독립 rootless daemon은 필수 uidmap 설치 권한이 필요. 독립 containerd도 현재 socket 접근 권한과 rootless 준비가 없으며, 기존 kind cluster에 Kata Deploy를 적용하면 공유 워크로드에 영향을 줄 수 있어 제외했다. 실제 Kata guest kernel·VMM 프로세스·워크로드 상태는 모두 **미관찰**이다.

Docker 실험은 [별도 기록](docker_results.md)대로 완료했다. 그 결과는 runc 기반 컨테이너 제어의 Progent Wrapper 효과이며 Kata 격리·집행과 비교 측정한 결과가 아니다. 별도 전용 VM/호스트에서 Kata를 검증하려면 관리자가 제공하는 설치 권한, 등록 가능한 독립 runtime, guest artifact, 작동하는 KVM 및 테스트 전용 리소스가 필요하다.

## 2026-11-23 후속 결과 — 실제 Kata Runtime + 수동 Progent 정책

위 **NOT RUN**은 2026-11-22 당시의 결과로 보존한다. 사용자가 2026-11-23 Root 설치 스크립트를 실행한 뒤 Docker `kata` Runtime 등록과 Guest 기동이 성공했다. 원본 Progent checkout은 수정하지 않았다. Controller는 `runc`/`kata` 선택, Runtime별 자원 제한, Run ID·Docker ID·Label·Runtime 소유 확인을 추가했다. 실제 실행 명령은 `bash scripts/progent_vm.sh kata`다. Tool Call은 **Harness 직접 입력**이고 정책은 원본 `update_security_policy()`, Tool 중재는 `apply_secure_tool_wrapper()`/`check_tool_call()`을 사용한다. LLM 정책 생성과 Agent 자율 호출은 이 Run에 없다.

최종 Run ID `kata-20261123T004347Z-aa1064`, 실행 코드 `fb8a3bb2f52601864ec71d25cb3b2290dc5bb3de`, `source_dirty=false`. [전체 실행 JSON](runs/kata/kata-20261123T004347Z-aa1064.json)에 적용 정책 전문, 입력, 원본 Wrapper 예외, Controller 진입, Docker 명령, 독립 `docker inspect` 상태, Guest/Host 증거, 정리 결과를 기록했다. 대상은 Run ID와 Label을 가진 전용 Kata 컨테이너 `...-01`이며 다른 전용 컨테이너 `...-02`는 범위 밖 요청 확인용이다.

| Case | 정책 핵심과 직접 입력 | Progent/Controller/Docker | 독립 상태 | 기대 대비 |
| --- | --- | --- | --- | --- |
| UC-A | 대상 `get_resource_status` priority 10 Allow | SUCCESS / Controller 1 / mutation 0 | running→running | 일치 |
| UC-B | 대상 `stop_resource` priority 10 Allow | SUCCESS / Controller 1 / `docker stop` 1 | running→exited | 일치 |
| UC-D | 대상 `start_resource` priority 10 Allow | SUCCESS / Controller 1 / `docker start` 1 | exited→running | 일치 |
| UC-C | 같은 대상 `stop_resource` priority 1 **Deny**와 priority 10 Allow 동시 적용 | **POLICY_DENIED** / Controller **0** / Docker 명령 **0** | running→running | 일치 |
| UC-E | 첫 대상만 status Allow, 둘째 대상 조회 | **POLICY_DENIED** / Controller **0** / Docker 명령 **0** | 둘째 running→running | 일치 |
| Backend 오류 비교 | `get_resource_status`를 넓게 Allow, 존재하지 않는 ID 입력 | **BACKEND_EXECUTION_FAILED** / Controller 1 / Docker 명령 0 | 첫 대상 running→running | 일치 |

6/6 기대와 일치했고, 실행 후 전용 컨테이너 2개만 정리했다. UC-C의 첫 일치 규칙은 정책 전문과 원본 우선순위 처리에서 **설명용으로 추론**했다. 원본 Progent API가 규칙 ID를 반환하지 않으므로 별도 추적 ID라고 주장하지 않는다. Backend 오류는 Controller 소유 목록 검증에서 발생했으며 Docker daemon의 거부가 아니다. 이 결과는 **Tool Wrapper가 감싼 호출**의 집행과 Kata Guest에서의 작업 효과를 각각 관측한 것이다. Kata가 Progent 정책을 OS 수준에서 강제했다는 뜻은 아니다.

`runc` 회귀 Run `docker-20261123T004057Z-9468ce`도 [실행 JSON](runs/docker/docker-20261123T004057Z-9468ce.json)에서 같은 6/6 결과를 기록했다. AgentDojo `TaskSuite`의 Kata 오프라인 GroundTruth A/B는 [조회 로그](runs/agentdojo/dojo-20261123T004109Z-482f27.json), [종료 로그](runs/agentdojo/dojo-20261123T004138Z-d56345.json)에서 Utility `True`와 실제 Runtime 상태를 확인했다. 이 둘은 모델 호출이 아니며 Prompt Injection 평가도 아니다.
