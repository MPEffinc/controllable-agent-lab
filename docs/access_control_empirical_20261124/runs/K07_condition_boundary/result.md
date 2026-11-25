# K07 독립 실험: NIST Policy Machine 3.3.0의 정적 association 경계

**실행일:** 2026-11-24 UTC. [사전 등록](prereg.md)을 먼저 작성했다. **성격:** NGAC-IR 논문 저자 생성기/390건 replay의 재현이 아니라, [공식 NIST Policy Machine core `3.3.0`](https://github.com/usnistgov/policy-machine-core/tree/3.3.0)의 실제 in-memory PAP/PDP를 이용한 독립 최소 사례. 원본 `third_party/K07-nist-policy-machine/`은 고정 tag `7cc6b615354c871099d84bab8ec6667ef7c3e417`에서 clean이며 수정하지 않았다. 실험 test는 `/home/cclab/controllable_agent/env/K07_pm_worktree/`의 별도 detached worktree에만 추가하고 [동일 소스 사본](K07ConditionBoundaryTest.java)을 이 run에 보존했다.

## 검증 질문과 PEP

정책 의도는 `read(doc)`가 `registration_open=true`일 때만 effect를 내는 것이다. 각 case마다 새 `MemoryPAP`와 0에서 시작하는 `AtomicInteger` ledger를 만든다. `pc`→`members`/`docs` graph와 `alice`/`doc`을 만들고, 원본 `PAP.query().access().computePrivileges`로 **PM 결정**을 조회한다. 그 뒤 원본 `PDP.adjudicateOperation`이 `RequiredPrivilegeOnParameter(name, read)`를 통과하면 custom `ResourceOperation.execute`가 ledger를 1 올린다. `APP_PM`은 **broad association에 독립 app preguard를 더한 이 실험만의 조합**이다. 이는 NGAC-IR 저자가 제안한 *strict export에서 조건부 permission을 PM 밖 목록으로 남기고 app이 별도로 처리하는 경로*의 구현이 아니다. `APP_PM`의 false에서는 app이 PDP 호출을 막는다. 따라서 그 행의 `pm_allow=true`는 *별도 graph 질의값*이고 실제 `PDP` 실행 허가는 아니다. 전체 구현은 [보존한 test 소스](K07ConditionBoundaryTest.java), 원시 출력은 [decisions.jsonl](decisions.jsonl)/[Maven 로그](build-attempt2.log)에 있다.

| export/집행 | `registration_open` | PM graph 결정 | app 검사 및 PDP 호출 | 실제 최종 결정 | ledger 전→후 | 해석 |
|---|---:|---|---|---|---|---|
| broad: 무조건 `read` association | false | ALLOW | app 없음, PDP 호출 | ALLOW | 0→1 | 정의된 의도 대비 비인가 효과 1. 정적 broad export가 조건을 잃은 결과. |
| broad | true | ALLOW | app 없음, PDP 호출 | ALLOW | 0→1 | 정상 요청 성공. |
| strict: 조건부 association 제외 | false | DENY | app 없음, PDP 호출 | DENY_PM | 0→0 | 비인가 효과 차단. |
| strict | true | DENY | app 없음, PDP 호출 | DENY_PM | 0→0 | PM 단독이면 정상 요청도 1건 거부. **저자 제안 배포의 최종 app 결정은 이 행에서 시험하지 않음.** |
| broad + app condition PEP | false | graph 질의 ALLOW | app DENY, PDP 미호출 | DENY_APP | 0→0 | 같은 조건에서 비인가 효과 차단. |
| broad + app condition PEP | true | ALLOW | app PASS, PDP 호출 | ALLOW | 0→1 | 정상 요청 성공. |

원시 6행 모두 test assertions와 맞았고 Surefire `Tests run: 1, Failures: 0, Errors: 0, Skipped: 0`; 한 테스트 메서드가 **6개 하위 조건**을 순차 실행했다. `registration_open`은 신뢰된 로컬 bool이며 동시 변경·철회·원격 service finality는 실험하지 않았다. 따라서 effect는 **in-memory ledger 증가**이고 실제 서비스 API의 커밋은 아니다. 모델, temperature, random seed는 사용하지 않았다. 외부 LLM/API 비용 0.

## 환경·의존성·정확한 명령

- OS Ubuntu 22.04, 커널 `6.8.0-149-generic`, Java `21.0.13.1`; [POM](https://github.com/usnistgov/policy-machine-core/blob/7cc6b615354c871099d84bab8ec6667ef7c3e417/pom.xml)은 Java 21, ANTLR, protobuf/gRPC, Neo4j 등을 요구한다. POM SHA-256 `010e27516c69d5e2520ff346194c330fa04dc00778447f8367d151a60dd08584`.
- 호스트 Maven이 없어 [공식 Maven Central 3.9.8 binary zip](https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.8/apache-maven-3.9.8-bin.zip)을 `env/K07_maven_tool/`에 받았다. [공식 SHA-512 파일](https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.8/apache-maven-3.9.8-bin.zip.sha512)과 대조 통과: `e5a034a255b5f940d2baa0db1b64bed6ccbc1f568da6b79e37acd92817809c273158f52b2e0e2b942020efc203202f1338f2580590c8fd0ee4fca9bc08679577`. Repo `mvnw`는 검사했지만 실행하지 않았다.
- Maven 로컬 의존성은 **전용** `/home/cclab/controllable_agent/env/K07_m2_cache/`(최종 약 230 MB)에만 받았다. JAR/POM 1,037개별 SHA-256은 [dependency-sha256.txt](dependency-sha256.txt), 이 목록의 SHA-256은 `cd2a0dfa862c90a189262e2b9df1f80d30d576fbd75c2cb845910f0d500bb644`다. 실험 test 소스 SHA-256 `35a2109749dfd7b0deffdc001f8437ecdb8ccd8fcda6ca6a00bd1a41b7c6a44c`.
- 공식 tag의 `protos` submodule은 [NIST 소유 저장소](https://github.com/usnistgov/policy-machine-protos) 고정 commit `c24a420b5f06ad31af2994980e15784bbeac7a90`; 첫 build 때 미초기화였고, [submodule-init.log](submodule-init.log)처럼 `git submodule update --init protos`로 준비했다. 임의 내용으로 proto를 채우지 않았다.
- `env/.gitignore`는 이 세 실험 디렉터리만 무시한다. root에서 이 경로들은 최초 untracked였고 기존 `env/sregym` 등은 보존했다. 문서의 test 소스/원시 로그는 무시되지 않는다. 원본 NIST checkout은 끝까지 clean, worktree 변경은 새 test 파일 하나다. root에는 실험 기록/ignore 외 기존 자료를 수정하지 않았다.

실제 build 명령은 worktree를 작업 디렉터리로 하여 동일하게 **두 번** 실행했다. 각 시도는 `timeout 180s`, 메모리 `-Xmx1g`, 전용 Maven 캐시였다.

```bash
cd /home/cclab/controllable_agent/env/K07_pm_worktree
MAVEN_SKIP_RC=true MAVEN_OPTS=-Xmx1g \
  timeout --signal=TERM --kill-after=10s 180s \
  /home/cclab/controllable_agent/env/K07_maven_tool/apache-maven-3.9.8/bin/mvn \
  -B -ntp -Dmaven.repo.local=/home/cclab/controllable_agent/env/K07_m2_cache \
  -Dtest=K07ConditionBoundaryTest -Dsurefire.useFile=false test
```

[첫 시도](build-attempt1.log)는 1:00, exit 1. protobuf plugin의 `No proto files to compile` 뒤 gRPC package 누락으로 Java compile이 실패했다. 원인은 submodule이 `-c24a...`로 미초기화된 것이며 **정책 Deny/보안 실패가 아니다**. [두 번째 시도](build-attempt2.log)는 submodule 초기화 뒤 20.009초, exit 0, `BUILD SUCCESS`. 세 번째 재시도는 하지 않았다. `decisions.jsonl`은 성공 로그의 `K07_RAW` 6행만 추출한 파일이며 SHA-256 `00d8de6e0cfe77ebf2c20fa76e13aa09ea22bf08458ef85e84164a6f941c61c7`.

## 해석과 가장 강한 반박

[NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1)은 저자 데이터에서 broad export가 **조건부 허용 98/715개를 무조건 허용**하고 strict export가 390건 graph-decision replay 중 23건을 더 거부한다고 보고한다. 저자 390건은 컴파일된 graph에 상대적인 결정이고, 이 6조건 실험과 분모·생성기가 다르다. 여기서는 **정적 association만** 놓고 같은 의미적 tradeoff를 작은 독립 사례에서 관측했다. PM이 자신에게 주어진 graph를 충실히 집행했으므로 broad false의 효과는 PM 구현 버그가 아니라 조건을 누락한 export/PEP 경계에서 생긴다.

이 실험의 **broad association + app preguard**로 고정 로컬 조건의 보안과 정상 완료를 함께 회복했다. 저자 제안의 **strict export + app 조건 처리**는 저자의 설계로 따로 기록하며 여기서 실행하지 않았다. [Cedar의 `when`과 request context](https://docs.cedarpolicy.com/policies/syntax-policy.html), [OASIS XACML 3.0의 environment attributes](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)도 조건을 **정책 PDP 내부**에서 표현·평가할 수 있는 기존 대안이다. 이 대안들의 trusted/fresh context 공급과 effect 시점 원자성은 별도 검증 대상이지만, “조건을 다룰 기존 방법 자체가 없다”는 일반 주장에는 직접 반박이다. **판정:** 정적 NGAC-only broad/strict export의 조건 경계는 이번 여섯 조건에서 관측한 **구체 구현 범위의 한계**다. 이 로컬 app 조합은 `RESOLVED_IN_SCOPE`; 저자 strict+app 경로의 실제 효과는 `UNVERIFIED`; 독립적인 새 Research Need는 `UNVERIFIED`이고 “기존 조건부 PDP 방법 부재” 가설은 `REJECTED_HYPOTHESIS`다.
