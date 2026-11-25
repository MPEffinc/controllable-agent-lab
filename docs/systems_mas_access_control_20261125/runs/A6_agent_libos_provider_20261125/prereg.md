# A6 사전등록 — Agent libOS 위임 계보와 실제 로컬 Provider 효과

2026-11-25 UTC, 실행 전. 원본 `third_party/ALT_Agent_libOS` SHA `85e8ff94c1e562bfb1f891714e3bf4bed9795690`, v1.6.0. 기존 A5는 내부 결정만 확인했다. 기존 R2/R3는 CONTINUITY 원본으로 A→B 및 A→B→C **작업 전달**과 최종 효과를 이미 시험했으며, R3는 파생 권한을 CONTINUITY에 부여하지 않았다. 동일 실험을 반복하지 않는다.

## 질문·범위

원본 Agent libOS의 Host-authored manifest와 Capability 계보를 A→B→C `AgentProcess` 사슬에 적용할 때, 로컬 `LocalFilesystemProvider`의 실제 파일 효과가 정상 작업에서 발생하고 작업 밖 파일 쓰기, `permitted_effects=[]`, 부모 Capability 철회 뒤 쓰기는 억제되는가? 같은 Python Runtime의 프로세스 객체를 사용한다. 네트워크 A2A, OS PID 격리, 실제 LLM, 외부 HTTP 서비스는 포함하지 않는다.

## 사전 고정 입력과 예측

- 부모 A: `A.txt`, `B.txt` 쓰기 권한과 `filesystem.*` 효과를 명시한 manifest. A의 정상 B 쓰기는 성공한다.
- 자식 B 및 손자 C: A 파일만 허용하는 더 좁은 manifest. B/C의 정상 A 쓰기는 성공하고 B 파일 쓰기는 거부되어 파일이 바뀌지 않는다.
- B에서 `permitted_effects=[]`를 명시한 별도 자식: A 파일 Capability가 있더라도 실제 파일 쓰기는 거부된다.
- 부모의 A 파일 Capability를 Host가 철회한 뒤 C의 A 쓰기는 거부되고 기존 내용이 유지된다. 효과가 발생하면 예측 기각. 원본의 실제 기능에 따라 child launch 자체가 추가 권한/ceiling에서 거부되면 실패 원인과 마지막 상태를 기록한다.

## 기록·판정

원본 `Runtime`, `ProcessManager`, `CapabilityManager`, `LocalFilesystemProvider`는 수정하지 않는다. 연구자 드라이버는 독립 디렉터리의 SQLite와 A/B 파일을 생성하고 원본 API를 호출한다. 각 호출의 반환·오류, 파일 전후 내용, manifest parent id/허용 범위, Capability id·철회 상태, 경과 시간, Runtime 원본 SHA와 의존성, 원시 JSON을 남긴다. 실제 provider 파일 효과와 내부 결정, Host 정책 구성의 신뢰 가정을 분리한다. 기존 방법이 안전·정상을 유지하면 그 조건의 신규 메커니즘 Need는 기각한다. 비용 $0, 누적 $0.0754388 / $5 유지.
