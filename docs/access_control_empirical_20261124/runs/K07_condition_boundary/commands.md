# K07 실행 명령 원장

작업 디렉터리는 별도 표기가 없으면 `/home/cclab/controllable_agent`다. 아래 명령은 실행 시 사용한 경로와 옵션을 보존하기 위한 것이다. `build-attempt1.log`와 `build-attempt2.log`가 각 Maven 원시 출력이다. 비밀정보 또는 외부 모델 호출은 없다.

```bash
mkdir -p env/K07_maven_tool env/K07_m2_cache
curl --proto '=https' --tlsv1.2 -fsS --max-time 45 --retry 2 \
  'https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.8/apache-maven-3.9.8-bin.zip.sha512' \
  -o env/K07_maven_tool/apache-maven-3.9.8-bin.zip.sha512
curl --proto '=https' --tlsv1.2 -fsS --max-time 60 --retry 2 \
  'https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.8/apache-maven-3.9.8-bin.zip' \
  -o env/K07_maven_tool/apache-maven-3.9.8-bin.zip
expected=$(cat env/K07_maven_tool/apache-maven-3.9.8-bin.zip.sha512)
printf '%s  %s\n' "$expected" env/K07_maven_tool/apache-maven-3.9.8-bin.zip | sha512sum -c -
unzip -q env/K07_maven_tool/apache-maven-3.9.8-bin.zip -d env/K07_maven_tool

git -C third_party/K07-nist-policy-machine worktree add --detach \
  /home/cclab/controllable_agent/env/K07_pm_worktree \
  7cc6b615354c871099d84bab8ec6667ef7c3e417
# 실험 test는 worktree의 src/test/java/.../K07ConditionBoundaryTest.java에만 추가.

cd /home/cclab/controllable_agent/env/K07_pm_worktree
MAVEN_SKIP_RC=true MAVEN_OPTS=-Xmx1g \
  timeout --signal=TERM --kill-after=10s 180s \
  /home/cclab/controllable_agent/env/K07_maven_tool/apache-maven-3.9.8/bin/mvn \
  -B -ntp -Dmaven.repo.local=/home/cclab/controllable_agent/env/K07_m2_cache \
  -Dtest=K07ConditionBoundaryTest -Dsurefire.useFile=false test \
  > /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/K07_condition_boundary/build-attempt1.log 2>&1
# exit 1: protos submodule 미초기화로 generated gRPC class 없음.

timeout --signal=TERM --kill-after=10s 90s git submodule update --init protos \
  > /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/K07_condition_boundary/submodule-init.log 2>&1
MAVEN_SKIP_RC=true MAVEN_OPTS=-Xmx1g \
  timeout --signal=TERM --kill-after=10s 180s \
  /home/cclab/controllable_agent/env/K07_maven_tool/apache-maven-3.9.8/bin/mvn \
  -B -ntp -Dmaven.repo.local=/home/cclab/controllable_agent/env/K07_m2_cache \
  -Dtest=K07ConditionBoundaryTest -Dsurefire.useFile=false test \
  > /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/K07_condition_boundary/build-attempt2.log 2>&1
# exit 0: BUILD SUCCESS, 6 K07_RAW case 행.
```

성공 로그에서 `rg '^K07_RAW ' build-attempt2.log | sed 's/^K07_RAW //' > decisions.jsonl`로 여섯 행을 보존했다. Maven 격리 캐시의 `*.jar`/`*.pom`은 정렬된 경로별 `sha256sum`으로 [dependency-sha256.txt](dependency-sha256.txt)에 기록했다. 원본 clone의 tracked 파일은 수정하지 않았고, 새 worktree의 test 소스는 [이 run의 사본](K07ConditionBoundaryTest.java)과 SHA-256이 같다.
