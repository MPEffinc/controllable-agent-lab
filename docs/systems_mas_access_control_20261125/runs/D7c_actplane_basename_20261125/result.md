# D7c basename rule의 원본 loader attach 실패

2026-11-25 UTC. [사전등록](prereg.md), [원본 DSL](policy.dsl), [원시 결과](result.json), [원본 loader/verifier 로그](loader.log), [guest console](guest_console.log). ActPlane 원본 SHA `1cbb4d0f40e2bc6042d6883f045fe8e0e838b168`, 6.15 BPF-LSM 격리 VM, API 비용 $0.

`block write file "forbidden"`은 원본 CLI에서 1 rule로 컴파일됐으나 D7b와 동일하게 원본 C loader의 `trace_openat_exit`가 kernel verifier 100만 instruction 제한 `-E2BIG`로 실패했다. `ActPlane: ready` 없음. 따라서 대상 기존 FD/신규 open 및 별도 정상 파일이 모두 써진 상태는 **집행 미설치 조건**이며 보안·정상성 대조 결과가 아니다. D7의 exact-path `/work/forbidden`에서는 같은 kernel/loader가 ready로 설치됐으므로 이 실패를 guest의 BPF-LSM 비활성으로 설명할 수는 없다. 파일 matcher 형식이 verifier 경로에 영향을 준다는 관측까지만 가능하며, 모든 커널/빌드의 보장은 아니다.

Guest script의 SysRq poweroff 뒤 PID1 종료가 kernel panic 문구를 남겨 QEMU를 호스트에서 전용 PID에 `SIGTERM`으로 정리했다. 그 전에 fixture는 `D7C_RUN_EXIT:0`으로 마쳤고 결과 파일을 추출했다. 이 init 정리 오류와 BPF verifier 거부는 분리한다. 다른 패턴의 반복 시도는 중단한다. 현재 **원본 ActPlane의 열린 FD 차단 대안은 미확인**이며, 이전 D7의 좁은 현상만 증거로 남긴다. 기존 서비스 PEP/사전 sandbox화/다른 FD-aware OS PEP가 해결할 가능성을 유지한다.
