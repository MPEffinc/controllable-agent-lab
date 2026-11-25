# 정확한 실행 명령과 환경

실행일 2026-11-25 UTC. 사전 등록 `prereg.md` 생성 시각 00:30:31, Maven 로그 종료 00:31:45. 로컬 디렉터리는 `/home/cclab/controllable_agent`; worktree는 `/home/cclab/controllable_agent/env/K07_pm_worktree`. Worktree 원본 commit `7cc6b615354c871099d84bab8ec6667ef7c3e417`, `protos` submodule `c24a420b5f06ad31af2994980e15784bbeac7a90`. 공식 원본 `third_party/K07-nist-policy-machine/`은 clean. Worktree에서 새 test만 추가했으며 기존 `K07ConditionBoundaryTest.java`는 변경하지 않았다. `env/.gitignore`가 worktree·Maven 도구·캐시를 제외한다. 사용자 파일/기존 실험 기록 수정 없음.

Java `21.0.13.1`; Ubuntu 22.04, Linux `6.8.0-149-generic`, x86_64. Maven 3.9.8 도구는 이전 K07 실행에서 공식 SHA-512로 검증된 `env/K07_maven_tool/`; 전용 기존 의존성 cache `env/K07_m2_cache/` 사용. 명령의 `-o`는 Maven offline 모드이며 모델·외부 API 호출 없음. 테스트에 인증정보/실데이터/원격 서비스가 없다. 외부 API 비용 0.

준비/보존: 새 JUnit 소스를 **사전 등록 후**, 실행 전에 `env/K07_pm_worktree/src/test/java/gov/nist/csd/pm/core/example/K07RouteCompositionTest.java`에 작성했다. 같은 소스를 run 디렉터리에 복사하고 SHA-256을 확인했다.

```bash
cd /home/cclab/controllable_agent
test -f docs/access_control_empirical_20261124/runs/K07_route_composition_20261125/prereg.md
cp env/K07_pm_worktree/src/test/java/gov/nist/csd/pm/core/example/K07RouteCompositionTest.java docs/access_control_empirical_20261124/runs/K07_route_composition_20261125/K07RouteCompositionTest.java
sha256sum env/K07_pm_worktree/src/test/java/gov/nist/csd/pm/core/example/K07RouteCompositionTest.java docs/access_control_empirical_20261124/runs/K07_route_composition_20261125/K07RouteCompositionTest.java
```

실제 실행(argv 보존, 시도 1/최대 2):

```bash
cd /home/cclab/controllable_agent/env/K07_pm_worktree
set -o pipefail
MAVEN_SKIP_RC=true MAVEN_OPTS=-Xmx1g timeout --signal=TERM --kill-after=10s 180s /home/cclab/controllable_agent/env/K07_maven_tool/apache-maven-3.9.8/bin/mvn -B -ntp -o -Dmaven.repo.local=/home/cclab/controllable_agent/env/K07_m2_cache -Dtest=K07RouteCompositionTest -Dsurefire.useFile=false test 2>&1 | tee /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/K07_route_composition_20261125/build-attempt1.log
```

Exit 0, BUILD SUCCESS, Maven total 16.809 s; JUnit tests run 1 method, 7 scenario rows, failures/errors/skips 0. 재시도 없음. JSONL은 성공 로그의 접두어 `K07_ROUTE_RAW `를 제거해 추출했다:

```bash
cd /home/cclab/controllable_agent
rg '^K07_ROUTE_RAW ' docs/access_control_empirical_20261124/runs/K07_route_composition_20261125/build-attempt1.log | sed 's/^K07_ROUTE_RAW //' > docs/access_control_empirical_20261124/runs/K07_route_composition_20261125/decisions.jsonl
```

SHA-256: test source `e13521f8e25fb38cd7a8803949d6f4b034005ff90ae2d4fe85c892abb6690a36`; raw build log `6d3066c96371161aeee01043b1c3d17e0c22f9ea269565a18855a8fc32a89310`; decisions JSONL `fafbbd10b0fda80484476325fd2805e9c9f3d6e2b5933e06a51f660143f57ec7`.
