# D6 사전등록 — OpenShell 원본 파일 집행과 ActPlane D5 대조

2026-11-25 UTC. 공식 OpenShell v0.1.9 릴리스 CLI/Gateway/Sandbox binary를 별도 로컬 Gateway 포트 `18084`, 고유 SQLite/TLS와 `d6file01` 일회용 sandbox에서 실행한다. 기존 `oslab-*`, `sregym-*` 컨테이너나 호스트 커널 보안 설정은 건드리지 않는다. D5 원본 ActPlane의 정상 파일 쓰기와 금지된 직접·자식 쓰기와 같은 **파일 효과 범주**를 본다. 실제 경로와 메커니즘은 다르다: OpenShell은 `/sandbox` read-write·`/tmp` read-only의 Landlock 정책, ActPlane D5는 `/work/forbidden` BPF-LSM write block이다.

## 가설·대조·기각

1. 정책 로드와 원본 Landlock 적용 로그를 확인한다. `/sandbox/allowed` 정상 쓰기는 성공·내용 변경, `/tmp/forbidden` 직접 및 자식 프로세스 쓰기는 실패·파일 부재로 예상한다. 정상 쓰기도 막히거나 금지 쓰기가 성공하면 가설 기각.
2. `sandbox exec` 도구를 거치지 않은 내부 자식 셸이 동일 Landlock 범위를 유지하는지 확인한다. 이 결과는 MAS task identity/철회까지 입증하지 않는다.
3. CLI exit/status, 파일 내용/존재, supervisor 정책 적용 이벤트, 파일 요청 경과 시간 각 1회와 정리 후 전용 프로세스·컨테이너 부재를 기록한다. 한 번의 latency를 일반 overhead로 해석하지 않는다. 실패 시 구체적 원인과 마지막 실행 단계를 저장한다.

API 비용 $0, 누적 추정 $0.1211516/$5. 원본 정책 집행과 연구자 입력/관측 코드를 구분한다. CLI/Gateway는 실험 전용 인스턴스로만 실행한다.
