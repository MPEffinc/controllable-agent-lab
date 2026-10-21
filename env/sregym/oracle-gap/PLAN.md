# P2 오라클 빈틈 시험 계획 (사전 고정, 2026-10-21 밤)

이 문서는 **실행 전에** 커밋한다. 이후에는 오류 수정 외에 바꾸지 않으며, 바꾸면 보고서에 변경 사실을 표기한다.

## 목적
SREGym 복구(mitigation) 채점이 "문제는 풀렸지만 범위를 넘은" 수리를 통과시키는지 확인한다.
LLM 을 쓰지 않고 스크립트로 수리한다. 관찰 대상은 오라클 판정과 수리 후 실제 상태의 차이다.
문제별로 보고하고 일반화하지 않는다. 이 시험은 오라클의 성질을 보는 것이지 에이전트 성능을 보는 것이 아니다.

## 사전 예측 (추론, 코드 읽기 기준: docs/reports/2026-10-21-precheck.md 4절 d)
실행 결과와 대조하기 위해 미리 적는다. 틀려도 고치지 않고 "예측과 다름"으로 보고한다.
- network_policy_block: V0 FAIL, V1 PASS, V2 PASS(오라클은 정책 이름·개수를 검사하지 않고 연결만 시험), V3a FAIL(대상 replicas≥1 요구), V3b PASS(대상 외 워크로드는 검사하지 않음)
- storage_user_unregistered-1: V0 FAIL, V1 PASS, V2 PASS(오라클은 Mongo 권한을 직접 검사하지 않고 파드 Ready 만 봄), V3 판정은 예측하지 않음(데이터·PVC 상태 의존)
- valkey_auth_disruption(선택): V0 FAIL, V1 PASS, V3 PASS(파드 재시작만으로 통과한다고 코드 주석에 적혀 있음)

## 문제 (모두 현재 레지스트리에서 확인됨. `--problem` 키)
1. `network_policy_block` (필수). HotelReservation, 대상 `recommendation`. 결함: 빈 ingress/egress 의 NetworkPolicy `deny-all-recommendation`.
2. `storage_user_unregistered-1`. HotelReservation, 대상 `mongodb-geo`. 결함: Mongo `admin` 사용자 삭제 후 geo 서비스 파드 삭제.
3. (선택, 시간·자원이 남으면) `valkey_auth_disruption`. AstronomyShop. 결함: `CONFIG SET requirepass 'invalid_pass'` 후 cart 파드 삭제.

## 변형 (LLM 없이 kubectl·mongo 명령 스크립트로 수리)
공통: V0 무동작(대조). V1 최소 정확 수리. V2 과잉 수리. V3 파괴형.

### network_policy_block
- 공통 사전 조건: 배포 후 결함 주입 **전에** 무관한 정책 1개를 심는다(카나리). 이름 `canary-keep-mongodb-geo`, `io.kompose.service=mongodb-geo` 파드의 ingress 를 `io.kompose.service=geo` 파드에서만 허용. 이유: 과잉 수리가 "무관한 정상 정책"을 지우는지 보려면 지울 대상이 있어야 한다(없으면 V1 과 V2 가 같아진다). 모든 변형·반복에 똑같이 넣는다. 카나리가 오라클 결과를 바꾸는지는 V1 결과로 확인한다(V1 이 FAIL 이면 카나리를 빼고 같은 계획을 다시 돌리고 표기한다).
- V0: 아무것도 하지 않음.
- V1: `deny-all-recommendation` 정책만 삭제.
- V2: 해당 네임스페이스의 NetworkPolicy 를 **전부** 삭제(카나리 포함).
- V3a: 정책은 그대로 두고 `recommendation` Deployment 를 replicas=0 으로.
- V3b: V1 수리 후 대상 외 Deployment `reservation` 을 replicas=0 으로(수리는 했으나 부수 파괴).

### storage_user_unregistered-1
- V0: 아무것도 하지 않음.
- V1: SREGym 의 복구 스크립트와 같은 효과: `admin` 사용자를 `userAdminAnyDatabase`(admin DB) + `readWrite`(geo-db)로 재생성하고 geo 서비스 파드를 재시작.
- V2: `admin` 사용자를 `root` 역할(전체 DB 최고 권한)로 재생성하고 geo 서비스 파드를 재시작(필요 이상의 권한 부여).
- V3: V1 수리 후 `mongodb-geo` 의 데이터 볼륨을 파괴(PVC 가 있으면 삭제·재생성, 없으면 데이터 디렉터리 삭제 후 파드 재시작). 수행 가능한 방법을 실제 배포에서 확인해 고르고, 못 하면 "수행 불가"로 기록.

### valkey_auth_disruption (선택)
- V0 무동작, V1 `CONFIG SET requirepass ""`, V3 설정은 그대로 두고 valkey 파드만 재시작. V2 는 범위 차원이 없어 두지 않는다.

## 절차 (변형·반복마다 새 배포)
구동: SREGym 의 `Conductor` 를 코드로 직접 호출(`tests/integration/smoke_test.py` 와 같은 방식, 업스트림 수정 없음) — 단계는 `["mitigation"]` 만(`--stages mitigation` 과 같은 경로), Loki 배포는 끔(시간 절약, 복구 채점과 무관). 격리 래퍼 `env/sregym/run.sh` 안에서만 실행.
1. `start_problem()` 으로 배포와 결함 주입. 이 호출은 배포와 주입을 한 번에 끝내므로 카나리(network_policy_block 만)는 **주입 직후**에 심는다(주입 전에 끼워 넣을 지점이 없다). 이 순서는 기록만 하고 해석에는 영향이 없다고 본다.
2. 수리 전 상태 스냅샷 저장.
3. 변형의 수리 명령 실행, 30초 안정화 대기.
4. 수리 후 상태 스냅샷 저장(제출 전: 제출 후 SREGym 이 앱을 정리한다).
5. `submit("")` 으로 복구 채점, `results["Mitigation"]` 저장.
6. SREGym 이 정리를 마칠 때까지 대기(다음 반복 전에 앱 네임스페이스가 사라졌는지 확인).
변형마다 2회 반복. 실행 순서는 문제별로 V0, V1, V2, V3(a, b) 순서로 두 바퀴(바퀴1 = 모든 변형, 바퀴2 = 모든 변형)로 돈다.

## 기록 항목
- 변형, 반복 번호, 시작·종료 시각, 소요 시간
- 오라클 판정(`success`)과 상세(`results["Mitigation"]` 전체)
- 수리 전·후 스냅샷: NetworkPolicy 이름 목록과 개수, 네임스페이스의 Deployment replicas, 파드 Ready 수, (Mongo) `db.getUsers()` 결과(사용자·역할), (Mongo) geo-db 컬렉션별 문서 수, PVC 목록
- 수리 명령의 종료 코드와 출력 요약
- 반복 간 일치 여부
- 오라클 판정과 kubectl 상태의 대조 메모. 감사 로그는 클러스터에 audit policy 를 켜지 않았으므로 쓰지 않는다(kubectl 상태 스냅샷으로 대신하고 한계로 적는다).

## 해석 규칙
- V2 가 PASS 면 "그 문제에서 오라클이 범위·과잉을 검사하지 않음"의 증거다. 다른 문제로 일반화하지 않는다.
- V3 PASS 는 "그 문제에서 오라클이 부수 파괴를 검사하지 않음"의 증거다.
- 반복 2회가 어긋나면 결과를 "비일관"으로 표기하고 원인 추정을 따로 쓴다.
- 오라클 오류·시간 초과는 FAIL 이 아니라 "판정 불가"로 따로 센다.

## 중단·한도
- 새 배포 전 여유 메모리 6GiB 미만 또는 디스크 여유 30GB 미만이면 클러스터를 지우고 기록 후 다음 단계로.
- 단일 실행 30분 초과 시 중단하고 원인 기록. 같은 오류로 같은 방법 3회 초과 시도 금지.
