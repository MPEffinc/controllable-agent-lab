# D7b suffix pattern의 원본 loader attach 실패

2026-11-25 UTC. [사전등록](prereg.md), [원본 DSL](policy.dsl), [원시 guest 결과](result.json), [원본 BPF verifier 로그](loader.log), [console](guest_console.log). ActPlane source SHA `1cbb4d0f40e2bc6042d6883f045fe8e0e838b168`, 원본 CLI v0.1.8, 6.15 BPF-LSM guest. API 비용 $0.

`block write file "*forbidden"`은 원본 CLI에서 1 rule로 컴파일됐다. 그러나 원본 C loader의 `trace_openat_exit` BPF program load가 `-E2BIG`로 실패했고 kernel verifier가 `BPF program is too large. Processed 1000001 insn (limit 1000000)`을 기록했다. `ActPlane: ready`가 없고 `Failed to load BPF skeleton`으로 종료했다. 그러므로 agent의 대상/별도 정상 파일 FD 쓰기와 새 open이 모두 성공한 결과는 **정책이 설치되지 않은 상태**의 데이터이며 PEP 안전성/과거부 비교에 세지 않는다.

이 장애는 D5/D7의 exact-path 정책에서 성공한 동일 kernel/loader 경로와 비교해 suffix rule이 활성화하는 BPF verifier 복잡도 문제다. 다른 kernel·compiler·hook profile에서는 달라질 수 있다. `*forbidden`이 이미 열린 FD를 막거나 정상 파일을 과거부할지 이 run으로는 판정할 수 없다. 원본 코드에서 file_permission은 basename으로 target을 전달하므로, 다음에는 복잡한 suffix glob 대신 exact basename `forbidden`을 별도 Run ID로 시험한다. 호스트 변경 없음, 게스트 종료 확인.
