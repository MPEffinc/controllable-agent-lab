# D7 사전등록 — ActPlane 정책 attach 전 열린 FD의 후속 쓰기

2026-11-25 UTC. D5와 같은 ActPlane 원본 정적 C BPF loader/CLI 정책, 6.15 BPF-LSM 활성 격리 QEMU guest를 사용한다. 실험 전용 Python agent 프로세스가 `/work/forbidden`을 **정책 attach 전에** `O_WRONLY|O_APPEND`로 연다. 그 PID를 원본 loader `--seed-pid ... --seed-label 1`로 정책 대상에 넣고 `ActPlane: ready`를 확인한 후, 같은 agent가 (1) 열린 FD에 write, (2) 같은 파일을 새로 open/write, (3) `/work/allowed` 정상 쓰기를 시도한다. baseline 파일 내용, 각 syscall 결과/errno, 원본 BPF event와 정책 상태를 저장한다.

## 가설·반증

D5의 신규 open은 파일 전체 경로 검사로 차단됐다. 원본 BPF `file_permission` 구현 주석은 일부 커널의 verifier 제약으로 열린 FD의 후속 permission hook에서 basename으로 target match한다고 명시한다. 따라서 exact-path 규칙 `/work/forbidden`이 이미 열린 FD의 `write`에는 적용되지 않을 가능성이 있다. 실제 write가 차단되면 이 가능성을 기각한다. 열린 FD 쓰기가 허용돼도 다른 rule 형태나 다른 커널·정책이 해결할 수 있는지 검토해야 하며 ActPlane 일반 보안 실패나 새로운 Research Need를 곧바로 주장하지 않는다. 파일 write가 허용되면 **정책 적용 전 열린 FD가 남는 조건**의 좁은 구현/의미 차이를 기록한다.

정책 활성화/subject seed는 런타임 attach이지 원본의 동적 policy-delta API나 grant revocation이 아니다. 정상 파일 쓰기 성공, 금지 파일 새 open 거부, pre-open FD 결과의 세 대조를 모두 요구한다. 기존 호스트 보안 상태나 서비스는 건드리지 않고 `-net none` VM만 사용한다. API 비용 $0, 누적 추정 $0.1211516/$5.
