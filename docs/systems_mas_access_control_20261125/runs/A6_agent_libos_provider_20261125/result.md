# A6 결과 — Agent libOS A→B→C Capability와 실제 Provider 파일 효과

2026-11-25 UTC. [사전등록](prereg.md) 원격 SHA `b5695ccd1a3c76f0d148f6d9023a3760e5bdda8e` 이후 실행. 원본 Agent libOS v1.6.0 SHA `85e8ff94c1e562bfb1f891714e3bf4bed9795690`, 소스 수정 없음. A5 고정 Python 환경을 재사용. 유료 API $0, 누적 추정 **$0.0754388 / $5**.

## 구성과 원본/adapter 구분

[연구자 드라이버](run.py)는 원본 `Runtime.open`, `ProcessManager.spawn/spawn_child`, `CapabilityManager.revoke`, `LocalFilesystemProvider.write_text`를 호출했다. 별도 SQLite와 두 파일 `A.txt`/`B.txt`를 사용했다. A는 두 파일 쓰기·`filesystem.*` 효과를 Host manifest로 보유한다. B와 C는 A 파일만 받는 자식·손자이며, 별도 B 자식은 A 파일 Capability와 빈 provider effect ceiling을 받는다. [원시 JSON](raw.json)은 각 API 결과/오류·호출자·파일 전후·시간·manifest 부모 id·capability 부모 id·effect 장부를 기록한다. [SQLite](runtime.sqlite.gz)와 [실제 파일 스냅샷](workspaces.tar.gz)도 보존했다.

| 요청 | 원본 API 결과 | 독립 파일 전후 상태 / effect 장부 |
|---|---|---|
| A의 `B.txt` 정상 쓰기 | 반환 | B 파일 `baseline`→`parent B normal`; 원본 filesystem effect 1건 |
| B의 `A.txt` 정상 쓰기 | 반환 | A 파일 `baseline`→`child A normal`; effect 1건 |
| C의 `A.txt` 정상 쓰기 | 반환 | A 파일 `child A normal`→`grandchild A normal`; effect 1건 |
| B의 `B.txt` 범위 밖 쓰기 | `CapabilityDenied` | B 파일 유지, 새 effect 0 |
| 빈 `permitted_effects`를 가진 자식의 `A.txt` 쓰기 | `CapabilityDenied: ... does not permit effect class filesystem.write_text` | A 파일 유지, 새 effect 0 |
| Host가 A의 A-file Capability를 철회한 뒤 C의 `A.txt` 쓰기 | `CapabilityDenied` | A 파일 유지, 새 effect 0 |

원본 장부에는 `filesystem/write_text`, `state_mutation=true`, `finalized/committed`가 정상 3건만 남았다. B의 `A.txt` Capability는 A의 Capability id를, C의 것은 B의 Capability id를 `parent_cap_id`로 참조한다. A의 부모 Capability 철회 뒤 `active=false`와 C의 파일 무변경을 확인했다. 각 호출 경과 시간은 [원시 JSON](raw.json)에 있으며 성공 `650–674 ms`, 거부 `152–191 ms`였다. 한 번씩 순차 실행한 로컬 Runtime의 초기화·SQLite 비용 등이 섞여 있어 일반 성능 차이로 해석하지 않는다.

처음 두 드라이버 시도는 각각 연구자 구성 오류였다. 첫 시도는 child `max_delegation_depth=1`에서 `delegable=true`를 요청해 원본이 올바르게 `delegated capability cannot be delegable after depth exhaustion`으로 거부했다([stderr](attempt1.stderr), [SQLite](runtime_attempt1.sqlite.gz)). 두 번째는 연구자 JSON 직렬화 코드가 manifest dict를 객체처럼 읽어 `AttributeError`를 냈다([stderr](attempt2.stderr), [SQLite](runtime_attempt2.sqlite.gz)). 두 시도에서는 비교 효과를 실행하지 않았고 원본 실패 사례로 세지 않는다. 코드를 수정한 세 번째 시도가 위 결과다. 원본 [HTTP JSON-RPC 효과 테스트와 부모 철회 테스트](original_pytest.stdout)도 선택 실행해 **2 passed**였다.

## 판정과 한계

이 고정 범위에서 Agent libOS 원본의 Host manifest, child attenuation, Capability 계보 철회 및 Provider effect ceiling은 정상성을 유지하면서 비인가 파일 효과를 막았다. 단순 공유 Worker의 권한 합집합을 독립 신규 메커니즘 문제로 주장할 근거는 더 약해졌다. 다만 A/B/C는 **같은 Python Runtime 안의 `AgentProcess` 객체**이며 OS PID/별도 A2A 네트워크 Agent가 아니다. Host가 올바른 manifest를 작성하고 모든 효과가 원본 Provider를 거친다는 전제가 있다. 이를 ActPlane의 OS 주체·파일 Hook에 결속하거나 독립 서비스 credential/비동기 요청까지 확장한 결과는 아니다.

기존 [R2](../../../R2_CONTINUITY_INTEGRATION_REPORT.md)와 [R3](../../../R3_EXPERIMENT_REPORT.md)는 CONTINUITY 원본으로 A2A **작업 전달**과 최종 효과를 이미 실행했다. R3의 A→B→C 정상·철회 조건 4개는 원본 범위에서 통과했다. 그 시스템은 A→B→C **파생 권한** 계보를 표현하지 않는다고 명시되며, 이를 결함으로 취급하지 않는다. 현재 A6의 추가 증거는 Agent libOS의 파생 Capability가 실제 파일 Provider 효과까지 결속된다는 조건부 관측이다. PAuth·VERA·Authorization Revocation·EffectBound의 동일 실제 service/OS 경계 비교, 재위임·비동기 철회·비용은 남는다. 독립 Research Need는 `UNVERIFIED`다.
