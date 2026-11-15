# ORBIT 아티팩트 감사

상태 감사: 2026-11-15 (Asia/Seoul). 아래 실행 증거는 2026-11-14 UTC 로그이며 기존 연구 기록에서 가져온 결과가 아니다. 설치 재시작이나 새 실험은 수행하지 않았다.

## 판정과 획득한 버전

- **VERIFIED — 공식 연결:** [논문 arXiv:2609.33102](https://arxiv.org/abs/2609.33102)의 공개 코드 링크가 [wlanderson0/orbit](https://github.com/wlanderson0/orbit)로 연결됨을 웹에서 확인했다. GitHub 연결 도구로 저장소 메타데이터, README, v1.0.4 release를 읽었다. 분류: `VERIFIED OFFICIAL`.
- **VERIFIED — source checkout:** `third_party/orbit/`, shallow clone HEAD `887a0415e0ded15406de0f1e14259099b595d443`. `git status --short` 출력 없음. Apache-2.0 (`LICENSE`), Python >=3.11.
- **VERIFIED — 별도 release:** `third_party/orbit-release-v1.0.4/`의 공식 wheel/sdist, `SHA256SUMS`, `release-manifest.json` 다운로드 및 checksum 검사 exit 0. manifest의 release source revision은 **`076104ae2479595b4c973df7758131401e684c7d`**이며 현재 HEAD와 다르다. 실행 준비 대상은 이 release wheel이다.
- **PARTIAL — 환경:** workspace `.cache/bootstrap-python/`에 Python 3.11.17을 받아 `experiments/orbit-release/.venv/`를 생성했다(exit 0). 시스템 Python/기존 프로젝트 `.venv`는 사용하지 않았다.
- **FAILED — dependency installation:** `orbit-release-install`은 exit **124**, 로그 `TIMEOUT`. 88개 패키지 resolve 후 다운로드 도중 끝났다. 환경 inventory의 설치 package 수는 0으로 확인되어 **설치 완료로 볼 수 없다**. timeout의 상세 네트워크 원인은 입증되지 않았다. 기록된 전체 경과 538.417초는 wrapper의 예정 timeout(360초)을 초과하므로 정확한 시간 제한 성능도 보장하지 않는다.
- **NOT_RUN — smoke / negative control / unit test / policy ON/OFF:** 실행 로그, Inspect `.eval`, scorer 결과가 없다. `first_benchmark.py`가 존재하는 것은 실행 증거가 아니다. README 예상 score 1/0을 관측값으로 사용하지 않는다.

## 무결성과 실행 기록

wheel SHA256: `95a7cbda584b22dd5250ce05c144286bce624814596aa59928f66beb24f29afc`.
sdist SHA256: `c667d742a5eec7b16a4790e0a404f807664279d410f6fd353229f670806e6c20`.

모든 아래 basename은 `results/setup/bootstrap-20261114/`의 `.json`(명령·cwd·UTC·exit) 및 `.log`(stdout/stderr) 쌍이다.

| 항목 | 증거 basename | exit | 판정 |
| --- | --- | ---: | --- |
| shallow clone | `orbit-clone` | 0 | VERIFIED |
| 공식 4개 release asset 다운로드 | `orbit-release-download` | 0 | VERIFIED |
| `sha256sum -c SHA256SUMS` | `orbit-release-checksums` | 0 | wheel/sdist 모두 OK |
| sdist 추출 | `orbit-release-source-extract` | 0 | VERIFIED |
| Python 3.11 설치 | `orbit-python311` | 0 | VERIFIED |
| 격리 venv 생성 | `orbit-release-venv` | 0 | VERIFIED |
| Inspect + local wheel 의존성 설치 | `orbit-release-install` | 124 | FAILED / TIMEOUT |

실제 실패 명령(workspace root):

```bash
uv pip install --python experiments/orbit-release/.venv/bin/python \
  inspect-ai==0.3.263 \
  ./third_party/orbit-release-v1.0.4/orbit-1.0.4-py3-none-any.whl
```

## 실제 Method와 코드 경로: source audit만 완료

이 절의 상대 경로 기준은 **release sdist** `third_party/orbit-release-v1.0.4/orbit-1.0.4/`이다. 현재 HEAD와 섞어 재현성을 주장하지 않는다.

| 구간 | 실제 파일과 심볼 | 확인한 동작 |
| --- | --- | --- |
| 예제 entrypoint | `examples/first_benchmark.py:main`, `run_smoke`, `first_benchmark` | native Inspect task/eval, 2 sample × 2 epoch, max_retries=0; 실행 준비용 원본 사본 `experiments/orbit-release/first_benchmark.py` |
| 일반 entrypoint | `orbit/tasks/multi_agent.py:multi_agent_task`; `orbit/wrapper/cli.py:cli` | Inspect `Task`를 만들고 `mas_orchestrator`를 solver에 연결; CLI/YAML도 존재 |
| 설정 | `orbit/configs/{setup,execution,scheduler,communication,defense}.py` | 독립 agent 사양/실행순서/채널/방어 설정. `DefenseConfig.enabled`가 toggle이며 `automatic`/`scheduler` 경계 집행만 지원; reserved consultation 모드는 거부 |
| 실행 | `orbit/solvers/orchestrator.py:mas_orchestrator`; `orbit/agents/turn_react.py:turn_react`; `orbit/agents/topologies.py:build_turn_react_agents` | Inspect agent 대화/도구와 Orbit scheduling을 연결. 예제 schedule은 Alice→Alice→Bob→Bob이며 메시지가 agent를 임의로 깨우지 않음 |
| 모델 | `examples/first_benchmark.py:offline_model` | `mockllm/first-benchmark`, `custom_outputs`가 tool intent를 결정. 로컬 token estimate를 override하여 tokenizer 다운로드 회피. 실 모델은 별도 opt-in이며 이번에 실행 안 함 |
| 채널 정책/집행 | `orbit/communication/runtime.py:send_message`, `read_messages`; `orbit/communication/delivery.py:CommunicationDeliveryFilter` | writer/reader/edge 권한을 검사 후 메시지 기록/전달. 예제 team channel은 Alice만 writer, Alice/Bob reader |
| 정책 method | `orbit/defenses/monitor.py:MonitorDefense`; `orbit/defenses/tool_wrapper.py:SecureToolWrapper` | regex 메시지·tool 검사, tool 이름/인자 blocklist. 이 두 구현 자체는 LLM 호출 불필요. LLM monitor/guardian/dual-LLM도 별도로 존재하나 실행하지 않음 |
| 방어 집행 위치 | `orbit/solvers/orchestrator.py:_build_attacks_and_defenses`; `orbit/defenses/boundaries.py:DefenseBoundary.wrap_tool`, `input_filter`, `wrap_model` | tool wrapper의 `check(kwargs)`가 `definition.tool(**kwargs)` **전에** 실행됨. 거부 시 `ToolError`로 callable 실행 차단. model input 사본 redaction/output refusal 경계도 구현되어 있음. 원본 기록·과거 side effect rollback은 아님 |
| 실제 mock effect | `examples/first_benchmark.py:reserve_units`, `reservation_tool`, `InventoryState` | trusted Python closure에 owner를 고정하고 quantity 검사 후 `available` 감소 및 owner별 reservations 갱신. 외부 서비스 효과가 아닌 per-sample/epoch Inspect store 변경 |
| scorer | `examples/first_benchmark.py:inventory_score` | completion 문구 대신 store의 owner별 예약값과 남은 수량을 target과 비교. negative control은 Bob이 reserve하지 않고 완료 주장하는 경우 |
| trace | `orbit/communication/state.py:CommunicationMessage`, `CommunicationEvent`; `orbit/defenses/boundaries.py:DefenseBoundary._record`; `orbit/solvers/runtime_state.py:DefenseLog` | agent/session/invocation/message sequence 및 defense decision 정보와 Inspect transcript 기록 코드. 아직 실제 trace는 없음 |
| security scorer | `orbit/scorers/security_scorer.py:security_scorer` | explicit attack attempt ID 등 가용 증거를 사용하는 별도 security scorer. inventory 예제의 scorer와 구분해야 함 |

ORBIT은 MAS 평가 infrastructure이며 단일 보편적 authorization 방어가 아니다. topology/communication/memory/scheduling과 attack/defense를 설정하고 Inspect가 model/tool/sandbox/scoring/log를 담당한다. release source에는 coding, desktop, browser, customer-service, cooperative-allocation adapter가 있지만 이 감사에서는 무거운 환경·dataset·Docker를 설치하거나 실행하지 않았다. 채널 ACL은 공유 파일/Python 도구의 OS 격리를 의미하지 않는다.

## 다음 실행 절차 — 현재 NOT_RUN, 실행 승인 후 별도 작업

현재 사용자의 handoff/상태 감사 범위를 지키기 위해 아래 명령은 **실행하지 않았다**. 우선 동일한 wheel/Inspect pin으로 설치를 재시도하고 성공 여부·package origin을 확인한 다음 두 예제를 실행해야 한다. PyPI의 `pip install orbit`은 다른 프로젝트이므로 사용하면 안 된다. 최신 checkout 개발 의존성은 Inspect Git commit `c060c201c5681dd09dbe3edb5f01e5947218bfb9` 및 swarm Git pin이므로 release용 venv와 혼합하지 않는다.

```bash
# workspace root, 설치 성공 후에만 smoke로 진행
python3 scripts/bootstrap_run.py --name orbit-release-install-retry \
  --timeout 600 -- uv pip install \
  --python experiments/orbit-release/.venv/bin/python \
  inspect-ai==0.3.263 \
  ./third_party/orbit-release-v1.0.4/orbit-1.0.4-py3-none-any.whl

cp third_party/orbit-release-v1.0.4/orbit-1.0.4/examples/first_benchmark.py experiments/orbit-release/first_benchmark.py

python3 scripts/bootstrap_run.py --name orbit-positive \
  --cwd /home/cclab/controllable_agent/experiments/orbit-release \
  -- .venv/bin/python first_benchmark.py \
  --log-dir ../../results/setup/bootstrap-20261114/orbit-positive-inspect

python3 scripts/bootstrap_run.py --name orbit-negative \
  --cwd /home/cclab/controllable_agent/experiments/orbit-release \
  -- .venv/bin/python first_benchmark.py --negative-control \
  --log-dir ../../results/setup/bootstrap-20261114/orbit-negative-inspect
```

성공 시 `.eval`에서 두 agent의 도구 intent, team 메시지 전달, store 변경, scorer 및 4/4 sample-epoch 완료를 직접 확인한다. 기대값은 positive 1, negative 0이지만 **현 시점 관측값은 없음**. 이것은 deterministic scripted execution/scoring 검증이며 LLM 취약성 재현이나 policy ON/OFF 비교가 아니다. 다음 policy 비교는 원본의 `tests/test_intervention_boundaries.py`와 `examples/security_extensions.py`를 먼저 읽고 기존 방어 toggle과 실제 mock effect가 포함된 원본 테스트를 선택해야 한다. 현재는 그 비교도 NOT_RUN이다.
