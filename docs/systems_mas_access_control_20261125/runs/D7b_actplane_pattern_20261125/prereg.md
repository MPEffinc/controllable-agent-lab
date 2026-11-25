# D7b 사전등록 — 기존 DSL 패턴으로 열린 FD를 막는가

2026-11-25 UTC. D7의 exact-path `/work/forbidden` 정책에서 이미 열린 FD 쓰기가 통과했다. **같은 원본 ActPlane v0.1.8 CLI/정적 C BPF loader, 6.15 BPF-LSM 격리 VM**에 DSL file pattern `"*forbidden"`을 적용한다. Agent가 정책 attach 전에 `/work/forbidden` FD와 정상 별도 경로 `/work/unrelated/forbidden` FD를 열고, attach/seed/ready 후 두 FD의 write를 시도한다. 대상 파일의 새 open과 `/work/allowed` 정상 쓰기도 시험한다.

`*forbidden`이 full path와 basename을 모두 포괄하면 기존 FD도 차단할 수 있지만, 정상 별도 경로의 같은 basename도 차단할 가능성이 있다. 대상 기존 FD가 차단되지 않으면 이 DSL 우회책 가설을 기각한다. 대상은 막고 별도 정상 FD도 막으면 **정상성 비용**을 확인한다. 두 파일을 분리하면서 대상 기존 FD만 막으면 좁은 D7 조건의 기존 해결책으로 인정한다. 모든 경우 syscall errno, 파일 전후·BPF event, loader ready, 정상 파일을 남긴다. 동일 Python adapter/원본 hook 구분, 원본 source 무수정. 이는 실제 policy-delta/revoke API가 아니다.

호스트 커널·서비스 변경 없음, `-net none` 일회용 guest. API 비용 $0, 누적 추정 $0.1211516/$5. 새 Run ID로 기존 D7 원시 증거를 보존한다.
