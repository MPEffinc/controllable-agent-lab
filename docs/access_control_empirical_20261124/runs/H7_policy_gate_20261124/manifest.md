# H7 전체 effective policy 검증 대조: 사전 등록

- 질문: OpenShell v0.1.9에서 provider 부착 전 base policy를 승인 상한으로 둔 경우, 같은 base 후보는 공식 prover `within_boundary`인가? provider 부착 뒤의 **전체 effective policy** 후보는 network 확대를 `exceeds_boundary`로 검출하는가?
- 원래 주장: [공식 prover 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover)는 provider 규칙을 포함하는 전체 effective policy를 후보로 넣어야 하며, `within_boundary`는 지원 도메인의 포함만 말한다고 명시한다.
- 입력: 동일 공식 v0.1.9 실행의 `runs/K14_effective_20261124/base-after.json`과 `full-after.json`에서 `policy` 객체만 추출. Base를 승인 상한·base 후보로, full을 확장 후보로 사용. 비밀정보·서비스 데이터 없음.
- 예상: base↔base `within_boundary`, full↔base `exceeds_boundary`와 network counterexample. `unsupported` 또는 `inconclusive`는 해결 확인으로 세지 않는다.
- 반증: 전체 effective에서 확대를 탐지 못하고 `within_boundary`가 나오면 이 정책 형상에 대한 상한 검사 주장에 반례. 단, 이것만으로 런타임 부착 gate가 자동 실행됨을 보장하지 않는다.
- 비용·완료: offline prover 2회, API/GPU/Docker 0. 양쪽 raw JSON·exit code와 입력 SHA를 기록한 뒤 종료. 기존 K14 Gateway/컨테이너는 재기동하지 않는다.
