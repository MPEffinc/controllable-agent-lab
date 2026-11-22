# Kata guest launch result: FAILED, host cgroup delegation BLOCKED

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
