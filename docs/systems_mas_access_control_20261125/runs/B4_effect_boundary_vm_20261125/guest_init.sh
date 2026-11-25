#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
mkdir -p /sys/fs/bpf /sys/kernel/security /sys/kernel/tracing /sys/kernel/debug /work
mount -t bpf bpf /sys/fs/bpf
mount -t securityfs securityfs /sys/kernel/security
mount -t tracefs tracefs /sys/kernel/tracing
mount -t debugfs debugfs /sys/kernel/debug
/usr/sbin/ip link set lo up
echo B4_GUEST_READY
cat /sys/kernel/security/lsm
python /work/fixture.py all >/work/run.stdout 2>/work/run.stderr
echo "B4_RUN_EXIT:$?"
sync
echo o >/proc/sysrq-trigger
sleep 10000
