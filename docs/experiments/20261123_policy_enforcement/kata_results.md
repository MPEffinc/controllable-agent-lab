# Stage D: Kata 실행 시도와 실패 조건

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
