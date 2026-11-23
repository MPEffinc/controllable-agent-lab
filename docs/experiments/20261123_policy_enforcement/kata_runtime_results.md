# Kata guest launch result: FAILED, host cgroup delegation BLOCKED

> 이 제목과 아래 실패 분석은 2026-11-22 Rootless 시도 기록이다. **2026-11-23 Docker Kata Guest 기동 성공**은 문서 끝의 후속 실행 절을 참조한다.

2026-11-22 UTC. Dedicated namespace: `cclab-progent-exp` on a dedicated containerd socket under ignored `local/progent-vm/kata-4.4.0/`. Host kernel `5.15`, guest image kernel artifact `6.18.62-211`. **No Kata guest actually booted; guest kernel was not observed executing.**

| Probe | Actual command/variant | Exit | Observed failure |
| --- | --- | ---: | --- |
| Official BusyBox image | `ctr -a <dedicated socket> -n cclab-progent-exp run --rm --snapshotter native --runtime io.containerd.kata.v2 --runtime-config-path /opt/kata/share/defaults/kata-containers/runtime-rs/configuration-qemu-runtime-rs.toml docker.io/library/busybox:1.36.1 cclab-progent-kata-probe uname -r` | 1 | Image layer extraction could not `lchown .../home` to UID/GID 65534: `invalid argument`. The one-ID `unshare -Ur` map cannot represent that owner. |
| Owner-normalized rootfs, first try | Same `ctr run` with `--rootfs --fifo-dir <local fifo> --cgroup ''` and an isolated rootfs from the pinned BusyBox 1.36.1 layer extracted as current user | 1 | Shim start `bind address: Permission denied`; attempted socket path was under host-owned `/run/containerd`. |
| Owner-normalized rootfs, private `/run` | Relaunched dedicated containerd inside a mount namespace with private `/run` tmpfs, then repeated rootfs `ctr run` | 1 | Kata shim initialized but failed at `add runtime to sandbox cgroup`: writing `/sys/fs/cgroup/cgroup.procs` returned `Permission denied (os error 13)`. |
| Independent runc comparison | Same dedicated containerd/rootfs with `--runtime io.containerd.runc.v2` | 1 | `rootless needs no limits + no cgrouppath ... mkdir /sys/fs/cgroup/user.slice/user-1000.slice/...: permission denied`. This shows lack of cgroup delegation affects even the alternate runtime. |

The rootfs workaround is only a diagnostic to pass the UID mapping error. It is not a Kata boot or a reproduction of the official BusyBox image layout. `unshare -Ur -m -C` could mount cgroup2, but `mkdir` below that mount returned `Permission denied`; its root was owned by unmapped UID/GID 65534. The user session cgroup is host-root-owned (mode 755), so this user cannot delegate a writable subtree. Disabling shared host security or using the Docker group to obtain host root was outside the approved scope.

After tests, `ctr ... tasks ls` and `ctr ... containers ls` were empty, the dedicated daemon was terminated, and `docker ps` still listed only the original four SREGym/kind containers. No QEMU/Kata workload remains. Detailed stderr is in ignored `local/progent-vm/kata-4.4.0/{probe,rootfs-probe,rootfs-probe2,runc-probe}.stderr`.

**State:** artifact installation **DONE**; Kata guest boot **FAILED** in attempted rootless configuration and **BLOCKED** on writable cgroup delegation or an approved dedicated privileged runtime. Minimum safe external action: provide a research-only host/VM with a delegated writable cgroup and working UID/GID mapping helpers, or activate sudo for a dedicated runtime setup. Do not change the shared Docker/containerd daemon. Luna + Kata policy experiment is **BLOCKED** by both guest boot and missing API key.

## 2026-11-23 후속 실행 — Docker Kata Guest 기동 성공

위 실패는 **2026-11-22의 별도 rootless containerd 시도**다. 사용자가 승인된 Root 설치 스크립트를 실행해 Docker에 Kata 4.4.0을 등록한 뒤, 일반 사용자 Docker CLI로 아래 전용 리소스만 조작했다. 설치 로그는 `/var/log/cclab-progent-kata-setup/setup-20261123T003621Z-jYb5io.log`다. 기존 SREGym 컨테이너는 조작하지 않았다.

| 관측 | 실제 결과 |
| --- | --- |
| Docker Runtime | `docker info`에 `kata` 등록, 기본 Runtime은 계속 `runc` |
| 전용 Probe | `docker run -d --runtime kata --name cclab-progent-exp-kata-probe-20261123 --label org.cclab.progent.experiment=kata-probe-20261123 --network none --memory 1g --cpus 1 --pids-limit 64 --read-only busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662 sleep 600` → exit 0, ID `bfea2b6298ae...` |
| Host/Guest | Host `uname -r` = `5.15.0-203-generic`; `docker exec <probe> uname -r` = `6.18.62` |
| Host 프로세스 | 해당 Docker ID를 인자로 가진 `/opt/kata/runtime-rs/bin/containerd-shim-kata-v2`, `/opt/kata/bin/qemu-system-x86_64`, `virtiofsd` 확인. QEMU 인자에 `accel=kvm` 포함 |
| Probe lifecycle | `docker stop --time 2` → `exited`; `docker start` → `running`; `docker restart --time 2` → `running`; 재시작 후 Guest `uname -r` = `6.18.62`. Docker CLI는 `--time` 폐기 경고를 출력하여 Controller에서는 `--timeout`으로 변경 |
| Probe 정리 | ID·Label·Runtime 재확인 후 이 Probe만 `docker rm -f`; 해당 Label 컨테이너 0개 |

커밋된 Controller `fb8a3bb2f52601864ec71d25cb3b2290dc5bb3de`에서 수행한 최종 Progent Run `kata-20261123T004347Z-aa1064`는 [실행 JSON](runs/kata/kata-20261123T004347Z-aa1064.json)에 Host Kernel `5.15.0-203-generic`, Guest Kernel `6.18.62`, 소유 컨테이너 Runtime `kata`, Kata Shim PID `2127769`, QEMU PID `2127784`를 독립 관측으로 기록했다. 해당 Run의 `source_dirty=false`, `guest_boot_verified=true`다. PID는 실행 중 일시적인 값이며 로그 재생으로 Guest 실행을 증명하는 값이 아니다. **현재 시점에는 실험용 Kata 컨테이너가 모두 정리됐다.**

이 결과는 Kata Guest가 실제 부팅했고 Docker 컨테이너 생명주기 명령이 동작했다는 증거다. Guest 격리 강도, 모든 Host 시스템 호출의 정책 중재, Proxmox VM 전원 제어는 이 실험으로 측정하지 않았다. LLM 정책 생성 및 Agent Tool Call은 이번 Run에서 사용하지 않았다.
