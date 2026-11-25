# D7 ActPlane pre-open FD와 정책 attach 이후 효과

2026-11-25 UTC. [사전등록](prereg.md), [정책](policy.dsl), [격리 guest init](guest_init.sh), [agent](agent.py), [orchestrator](orchestrate.py), [원시 결과](result.json), [원본 BPF event](loader.log), [guest console](guest_console.log). 원본 ActPlane source SHA `1cbb4d0f40e2bc6042d6883f045fe8e0e838b168`, 원본 CLI v0.1.8/정적 C BPF loader 무수정. D5와 같은 Ubuntu 6.15 BPF-LSM guest, `-net none`; 호스트 커널 상태·서비스 변경 없음. API 비용 $0, 누적 추정 $0.1211516/$5.

Python agent PID 100이 `/work/forbidden`을 append 쓰기 FD로 **정책 attach 전에** 열었다. 별도 unlabelled orchestrator가 원본 loader에 `--seed-pid 100 --seed-label 1`을 주고 `ActPlane: ready`, `enforce mode (BPF LSM is active)`를 확인한 다음 agent를 재개했다.

| 정책 활성 후 agent 동작 | syscall 관측 | 독립 파일 효과 |
|---|---|---|
| 이미 열린 forbidden FD에 `os.write` | **10 bytes 성공** | `baseline` 뒤 `preopened` 추가 |
| 같은 forbidden 파일을 `os.open(O_WRONLY|O_APPEND)` | `EPERM`(errno 1) | 추가 변화 없음; 원본 `TAINT_VIOLATION`/`blocked=true` 1건 |
| allowed 파일 쓰기 | 성공 | `normal`로 변경 |

따라서 이 **exact-path 규칙과 attach 순서**에서는 새 open을 막는 것만으로 이미 열린 FD의 후속 효과가 차단되지 않았다. 원본 loader는 file_permission Hook을 켜는 조건을 충족하며, 원본 BPF 코드의 `te_handle_file_permission`은 verifier 제약 때문에 file basename을 target match에 사용한다고 주석/구현에 명시한다(`local` 복제본 `bpf/process.bpf.c`, 2125–2155행). 이것은 관측과 일치하는 가능한 원인이지만 D7 단독으로 유일 원인이라고 확정하지 않는다. BPF event는 새 open 차단 1건이고 pre-open write 차단 event는 없다.

이 결과는 **런타임 정책 attach**이지 원본 동적 policy-delta API나 grant revoke가 아니다. 기존 파일 핸들이 없는 D5의 정적 파일 차단 결과와 모순되지 않는다. 기존 파일 객체/FD를 추적하는 다른 OS PEP·효과 시점 서비스 PEP나 더 넓은 rule pattern이 해결할 수 있는지 직접 대조하기 전에는 새로운 메커니즘 Need를 주장하지 않는다. 일단 `IMPLEMENTATION_CONDITION_SUPPORTED`는 “이 버전의 exact-path rule을 파일 open 뒤 붙이면 후속 FD 쓰기가 남는다”라는 좁은 조건에 한정한다.
