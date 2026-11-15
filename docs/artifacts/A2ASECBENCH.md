# A2ASecBench 아티팩트 감사

감사일: 2026-11-15 (Asia/Seoul). 실행은 2026-11-14에 기록되었으며, 이번 완료상태 감사에서 새 설치·실험은 시작하지 않았다.

## 출처와 확보 상태

- **VERIFIED**: [SaFo-Lab/A2ASecBench](https://github.com/SaFo-Lab/A2ASecBench), 로컬 `third_party/a2asecbench`, shallow clone SHA `e02109ebdcce3fe926884fbacbc935eef44e4aa3`.
- **VERIFIED AUTHOR-ASSOCIATED**: GitHub connector로 README를 먼저 읽어 ICLR 2026 논문 *A2ASecBench: A Protocol-Aware Security Benchmark for Agent-to-Agent Multi-Agent Systems*, Tianhao Li 외, [OpenReview LfdFnakqGJ](https://openreview.net/forum?id=LfdFnakqGJ) citation을 확인했다. 저장소가 스스로 연결한 논문/연구실 코드임은 확인했으나, 이 세션의 OpenReview 열기는 browser verification으로 막혀 논문 측의 역방향 링크는 독립 확인하지 못했다. 이를 full paper reproduction으로 표시하지 않는다.
- MIT (`LICENSE`), Python `>=3.10` (`pyproject.toml`), 로컬 Python `3.10.12`. 설치된 핵심 의존성은 `a2a-sdk==0.3.26`, `httpx==0.28.1`, `starlette==0.48.0`, `pytest==9.2.0`; 전체 해결 버전은 설치 로그에 있다.
- 환경: `third_party/a2asecbench/.venv`. 상위 기존 `.venv` 및 다른 연구 환경은 사용하지 않았다. third-party **소스 수정 없음**. pytest가 저장소 `results/summary.json`을 갱신하고 새 `run_20261114*.jsonl`을 생성했다. 원래 체크아웃의 과거 `run_20260508*.jsonl`은 이번 결과에서 제외했다.

## 실제 코드 경로와 Method

아래 경로는 모두 `third_party/a2asecbench/` 기준이다. 이 저장소는 방어기법 자체보다 공격 사례, SUT, 프로토콜 환경, 관찰 가능한 효과와 scorer를 분리한 평가 하네스다.

| 역할 | 코드 경로·심볼 | 확인한 동작 |
| --- | --- | --- |
| 실행 진입점 | `orchestration.py:main`, `run`, `_load_case`, `_build_summary` | config의 case/SUT import path를 로드하고 trial JSONL, config SHA256, summary를 기록한다. |
| 실행 설정 | `configs/offline/asrf_eval.yaml` | 원본 ASRF attack 100개 + matched control 100개, `sut.a2a.reference_env:A2AExecutableSUT`; LLM SUT를 선택하지 않는다. |
| 공개/비공개 데이터 분리 | `attacks/a2a_attack.py:A2AExecutableCase.get_sut_payload`, `run` | SUT에는 public view만 전달하고, scorer에는 환경 event와 private oracle/tag를 사용한다. |
| 결정론적 coordinator | `sut/a2a/reference_env.py:A2AExecutableSUT.run_probe`, `_run_delegation` | peer의 resource를 전부 fetch, artifact를 active render, task를 생성하거나 bounded peer delegation을 수행한다. 선택적 보안 정책은 없다. |
| 프로토콜·peer | `harness/a2a_lab/sdk_protocol.py:OfficialA2APeer`, `OfficialA2AFunctionAgent`, `ScriptedA2AExecutor` | 공식 `a2a-sdk` AgentCard discovery와 JSON-RPC `message/send`; `httpx.ASGITransport`를 쓰는 in-process 서비스다. `.a2a.local` 문자열이 실제 외부 DNS 호출을 뜻하지 않는다. |
| action/effect 경계 | `harness/a2a_lab/env.py:A2AEnvironmentClient.fetch_resource`, `_call_service`, `_handle_resource_service`, `_fetch_resource_direct`, `reject_resource` | fetch/reject를 resource-service A2A message로 전달한다. fetch는 `urlopen`, reject는 `resource_fetch_blocked` event다. 하네스가 일반적인 외부 URL 허용 정책을 강제하는 것은 아니다. |
| 실제 로컬 sink | `harness/a2a_lab/http_trap.py:LocalHTTPTrapServer.start`, `_handle_get` | `127.0.0.1` 임시 포트 HTTP GET을 수신해 `uri_dereference`와 비공개 uri_class/nonce를 기록한다. |
| trial 환경 | `harness/a2a_lab/env.py:LocalA2AProbeEnvironment.__enter__`, `_materialize_asrf_runtime`, `metrics` | 매 trial route/nonce를 만들고 endpoint·SDK 서비스를 종료한다. forbidden/benign GET, A2A message/card fetch 수를 계산한다. |
| scorer | `harness/a2a_lab/scoring.py:score_asrf_environment` | 공격은 forbidden URI class와 request surface에 맞는 실제 trap event로 성공 판정; control은 정상 GET이 있고 forbidden GET이 없어야 통과한다. |
| event·trace | `harness/a2a_lab/events.py:HarnessEvent`, `EventRecorder.record` | case/trial, monotonic timestamp, component, actor, surface, evidence, private_tags를 기록한다. root principal·정책 버전·권한 위임 근거는 자동 제공되지 않는다. |
| 다른 평가 효과 | `artifact_renderer.py:ArtifactRenderer.render`, `delegation.py:DelegationTracker`, `task_store.py:TaskStore`, `scoring.py:score_atsi_environment`, `score_co_environment`, `score_hotf_environment` | ATSI는 active-content callback을 local GET으로 모델링한다(실제 browser/임의 script 실행 아님). CO는 delegation graph/depth, HOTF는 retained task pressure를 측정한다. 이번 full 실행 결과는 ASRF에 한정한다. |
| LLM adapter | `sut/a2a/llm_coordinator.py:LLMA2ACoordinatorSUT._decide`, `_run_peer_response`; `utils/llm_client.py:chat` | LLM이 structured action을 정하면 env를 호출한다. `SUT_API_BASE`, `SUT_API_KEY`, `SUT_MODEL` 필요; `requests.post(.../chat/completions)`. 이번 원본 ASRF 명령은 이 경로를 선택하지 않는다. |
| calibration 주의 | `sut/a2a/reference.py:A2ASUT` | structured-oracle fixture가 자체 event를 구성한다. 이를 실제 sink 관찰 결과와 섞지 않는다. |

AS는 AgentCard 선택, CC whitebox는 card/backend source mismatch, CC blackbox는 정상 A2A 상호작용을 통한 mismatch를 평가한다. AS·두 CC split은 각 100개, executable ASRF/ATSI/CO/HOTF는 attack 및 matched controls다. 이는 소스 구조 감사이며 모든 split을 완주한 주장이 아니다.

## 설치 및 실제 실행 결과

명령은 workspace root 기준이며 `scripts/bootstrap_run.py`가 key/token/secret/password/credential 이름의 환경 변수를 제거하고 command·UTC 시각·exit code를 남겼다. clone의 `.env`는 없음을 확인했다. 이 wrapper는 네트워크 sandbox가 아니므로 실행한 config/코드 경로의 로컬성 확인이 별도로 필요하다.

| 상태 | 명령 | 관찰 및 근거 |
| --- | --- | --- |
| **VERIFIED** | `python3 scripts/bootstrap_run.py --name a2a-clone -- git clone --depth 1 https://github.com/SaFo-Lab/A2ASecBench.git third_party/a2asecbench` | exit 0; `results/setup/bootstrap-20261114/a2a-clone.{json,log}` |
| **VERIFIED** | `python3 scripts/bootstrap_run.py --name a2a-venv -- uv venv third_party/a2asecbench/.venv --python python3.10` | exit 0; `a2a-venv.{json,log}` |
| **VERIFIED** | `python3 scripts/bootstrap_run.py --name a2a-install --timeout 600 -- uv pip install --python third_party/a2asecbench/.venv/bin/python -e 'third_party/a2asecbench[dev]'` | exit 0, 43 packages; `a2a-install.{json,log}` |
| **VERIFIED** | `python3 scripts/bootstrap_run.py --name a2a-asrf-original --cwd /home/cclab/controllable_agent/third_party/a2asecbench --timeout 180 -- .venv/bin/python orchestration.py --config configs/offline/asrf_eval.yaml --trials 1 --out ../../results/setup/bootstrap-20261114/a2a-asrf-original/trials.jsonl` | exit 0, 60.86초; attack 100/100 성공, control 100/100 통과. `a2a-asrf-original.{json,log}`, `a2a-asrf-original/{trials.jsonl,summary.json}` |
| **FAILED** (timeout) / suite **PARTIAL** | 동일 cwd에서 `.venv/bin/python -m pytest -q`, wrapper `--name a2a-pytest --timeout 180` | exit 124, 로그에 53개의 진행 점이 있으나 최종 pytest summary가 없어 suite PASS/정확한 pass 수를 확정하지 않는다. 실제 경과 198.141초. `a2a-pytest.{json,log}` |
| **FAILED** (timeout) | 동일 cwd에서 `.venv/bin/python scripts/validate_release.py`, wrapper `--name a2a-release-validation --timeout 180` | exit 124, 최종 validator 결과 없음. 실제 경과 225.802초. `a2a-release-validation.{json,log}`. 어느 검사에서 오래 걸렸는지 현재 로그만으로 확정 불가. |
| **NOT_RUN** | LLM config, paid API, 선택적 defense ON/OFF, full ATSI/CO/HOTF 및 CC 실행 | 완료로 주장하지 않는다. 추가 실행은 현재 사용자 지시에 따라 수행하지 않았다. |

원본 ASRF raw 200행은 `results/setup/bootstrap-20261114/a2a-asrf-original/trials.jsonl`에 로컬 보존한다(1,449,552 bytes, SHA256 `eebabeb64dd42fb88cb6870607649cbc41bb55492aa2474f3607eace9947d52b`). 공유용 표본은 `a2a-asrf-sample.jsonl`(attack/control 각 1건의 전체 event), 재집계는 `a2a-verified-counts.json`이다. 추가로 전체200건에서 sink event와 score/count 필드만 추출한 `a2a-asrf-observations.jsonl`을 공유한다. fresh clone에서도 `scripts/audit_bootstrap.py --verify-saved`로 summary와 대조할 수 있다. 요약의 **`asr=0.5`는 attack+control 200개를 합친 값**이다. 공격 ASR은 **`a2a_attack_asr=1.0`**, control pass rate는 **1.0**, overblock rate는 **0.0**이다.

## 해석과 다음 검증

이번 VERIFIED 결과는 원본 결정론적 coordinator가 untrusted peer resource를 fetch하고, 실제 localhost trap GET을 scorer가 구분하며, matched control도 정상 처리한다는 하네스 smoke 결과다. LLM의 공격 취약성, 기존 방어의 보장 위반, 새 MAS method gap을 입증하지 않는다. monitor decision 및 selective policy가 없어 defense ON/OFF 결과도 아니다. 공격과 control의 URI class는 scorer의 private metadata이므로 이를 SUT 정책에 노출해 문제를 쉽게 만들어서는 안 된다.

현재 진행 중인 A2A 명령은 없음을 프로세스 목록으로 확인했다. 다음 허용된 검증 시에는 기존 `test_asrf_executable_environment.py`만 별도 제한 시간으로 실행해 sink/scorer 회귀검사를 먼저 좁히고, full pytest/validator timeout은 `-vv` 또는 검사별 진입 로그로 위치를 확인한다. 새 방어를 작성하기 전에 paper-linked 기존 정책의 실제 집행 지점을 동일한 로컬 effect 경계에 연결할 수 있는지 검토한다. 이번 감사에서는 이 후속 명령들을 실행하지 않았다.
