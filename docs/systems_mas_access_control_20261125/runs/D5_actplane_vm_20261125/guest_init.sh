#!/bin/sh
# Isolated QEMU guest PID 1. The image is disposable and has no network device.
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
mkdir -p /sys/fs/bpf /sys/kernel/security /sys/kernel/tracing /sys/kernel/debug /work
mount -t bpf bpf /sys/fs/bpf
mount -t securityfs securityfs /sys/kernel/security
mount -t tracefs tracefs /sys/kernel/tracing
mount -t debugfs debugfs /sys/kernel/debug
echo D5_GUEST_READY
cat /sys/kernel/security/lsm 2>/dev/null
exec /bin/bash -i </dev/console >/dev/console 2>&1
