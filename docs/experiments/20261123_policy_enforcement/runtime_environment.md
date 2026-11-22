# Stage A: runtime 환경 조사 (2026-11-22 UTC)

시작 HEAD `f3bfa72dd9f1c5cdc50d2fa9cb6d95b9163a7031`, 원본 Progent `b02783b896d4bf01a2adf24738015e258db8d35b` clean. 루트 추적 파일 변경 없음; 기존 미추적 연구 문서·스크립트 보존.

| 항목 | 관찰 |
| --- | --- |
| Host | Ubuntu 22.04.5, Linux 5.15.0-203-generic, 8 CPU, RAM 31 GiB(가용 약 22 GiB), 디스크 가용 89 GiB |
| 권한 | 일반 사용자 `cclab`, `docker`·`kvm` 그룹. `sudo -n true` exit 1: `a password is required` |
| Docker | Engine 28.3.2, containerd 1.7.27, runc 1.2.5. CLI/daemon 사용 가능 |
| 기존 워크로드 | `sregym-lab` kind 컨테이너 4개 모두 실행 중. 이들은 실험 대상에서 제외 |
| 이미지 | 기존 이미지 3개는 SREGym/kind/mitmproxy용. 실험 전용 이미지는 별도 확보 필요 |
| KVM | `/dev/kvm` 읽기·쓰기 가능, `kvm_intel` nested=`Y`, `systemd-detect-virt`=`kvm`, `/dev/vhost-vsock` 존재 |
| Kata | `kata-runtime`·`/opt/kata` 미설치, Docker 등록 runtime에는 `runc`만 있음. `/run/containerd/containerd.sock` 직접 접근은 permission denied |
| 기타 | QEMU 설치. Podman, nerdctl, Cloud Hypervisor는 PATH에서 확인되지 않음. rootless Docker 도구는 존재 |

현재 실제 컨테이너 실험에는 이미 동작하는 Docker를 사용한다. 새 리소스는 생성 시 Label·이름·ID를 기록하고, 모든 관리 작업 전 소유 범위를 재검증한다. 네트워크를 끄고 자원 제한을 적용한다. 기존 4개 컨테이너는 중단·삭제·변경하지 않는다.

Kata의 공식 [설치 문서](https://github.com/kata-containers/kata-containers/blob/main/docs/installation.md)는 Docker 26+와 공식 tarball, daemon runtime 등록을 안내한다. 이 호스트의 Docker 버전과 KVM 조건은 일부 충족하지만, **현재 daemon 설정 변경은 기존 워크로드에 영향을 줄 수 있어 하지 않는다**. 별도 rootless daemon 또는 격리 containerd 구성이 가능한지 Stage D에서 살펴본다. `sudo -n` 실패와 시스템 containerd socket 거부는 기록된 장애 조건이다. 패키지 설치·Kata 워크로드 기동은 아직 시도하지 않았다.
