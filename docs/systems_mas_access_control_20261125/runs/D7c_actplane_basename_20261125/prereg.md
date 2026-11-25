# D7c 사전등록 — basename 정책의 기존 FD와 신규 open 비교

2026-11-25 UTC. D7 exact full path는 정책 attach 전 열린 FD 후속 쓰기를 통과시켰다. D7b `*forbidden`은 BPF verifier `-E2BIG`로 설치 실패했다. 이번에는 원본 ActPlane DSL의 단순 `block write file "forbidden"`을 동일 6.15 BPF-LSM 격리 guest에 설치한다. 같은 pre-open target `/work/forbidden` 및 정상 별도 `/work/unrelated/forbidden` FD의 후속 write, target 새 open, `/work/allowed` 정상 쓰기를 대조한다.

원본 `file_permission`은 basename `forbidden`을 전달하므로 target 기존 FD가 차단될 가능성이 있다. 하지만 동일 basename 정상 파일도 과거부하거나, 전체 경로를 전달하는 `file_open`에는 규칙이 맞지 않을 수 있다. **loader ready와 BPF block event** 없이는 어떤 보안 결과도 세지 않는다. target 기존 FD/새 open 모두 차단되고 정상 둘 다 허용되면 D7 좁은 문제는 기존 DSL로 해결됐다고 판정한다. 한 조건이라도 실패하면 경로/시점 tradeoff로 기록하되 다른 OS PEP의 해결 가능성을 남긴다. 파일 전후와 errno를 독립 관찰한다.

원본 source 무수정, 실제 policy-delta/revoke API 미시험, `-net none` guest, 호스트 설정/서비스 변경 없음. API 비용 $0, 누적 추정 $0.1211516/$5. 새 Run ID 보존.
