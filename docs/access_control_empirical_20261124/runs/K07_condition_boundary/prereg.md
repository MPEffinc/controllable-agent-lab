# K07 조건부 권한의 NGAC-only 집행 경계 — 사전 등록

등록일: 2026-11-24 UTC. **질문:** 같은 `read(doc)` 요청에 대해 `registration_open=true`일 때만 허용해야 할 때, NIST Policy Machine 3.3.0에 (a) 무조건 association만 export, (b) 조건부 association 제외(strict), (c) 무조건 association+독립 app condition PEP를 적용하면 실제 로컬 effect와 정상 완료가 각각 어떻게 달라지는가?

- **원래 주장/근거:** [NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1)은 PM이 조건을 검사하지 못해 broad export에서 조건부 허용 98/715가 무조건 허용되고, strict export는 390 replay 중 23 요청을 PM에서 거부한 뒤 app check에 맡긴다고 보고한다. [NIST Policy Machine core 3.3.0](https://github.com/usnistgov/policy-machine-core/tree/3.3.0)을 원본 코드로 사용하되, NGAC-IR 생성기 자체는 공개 코드 미확보라 **논문 재현이 아닌 독립 PM 경계 시험**이다.
- **고정 보안/정상 속성:** `registration_open=false`의 read effect 0, `true`의 read effect 1. 실제 effect는 별도 인메모리 ledger 증가. 공격자 제어는 요청 시점의 상태 변화만; 신뢰된 PM 코드·app condition 값·PEP 연결을 바꾸지 않는다.
- **예상:** broad association은 상태와 무관하게 두 요청 모두 effect 1(거짓 허용 1). strict export는 둘 다 effect 0(정상 거부 1). app condition+PM은 false 0/true 1. 이 정상 대조가 성공하면 **NGAC-only 고정 구조의 조건 표현/집행 한계**를 지지하고, app PEP 또는 조건 지원 PDP라는 기존 대안이 같은 조건을 해결함도 확인한다.
- **반증:** 공식 PM이 association 이외의 상태 predicate 없이도 두 상태를 구별하거나, app+PM이 false를 허용/true를 거부하면 예상이 뒤집힌다. Java 테스트/adapter 버그, API 오해, 의존성 빌드 실패는 K07/NGAC의 보안 실패로 분류하지 않는다.
- **비용/안전:** 공식 NIST tag `7cc6b615354c871099d84bab8ec6667ef7c3e417`을 읽기 전용 보존하고 별도 `env/K07_pm_worktree` 복사본에서 테스트 추가. Maven wrapper/POM 검토 후 Maven Central 의존성만 격리 캐시에 다운로드. 모델/API/실서비스 0, CPU와 디스크 작은 단위, 180초 build 상한, 실패 2회 이내.
- **완료:** 원본 tag·도구/의존성 hash·실행 명령·네 조건의 PM 결정/실제 ledger 전후 상태·정상/비인가 분모와 해석을 `result.md`/원시 로그에 저장. 생성기 원본이나 98/715 저자 수치를 로컬 재현으로 부르지 않는다.
