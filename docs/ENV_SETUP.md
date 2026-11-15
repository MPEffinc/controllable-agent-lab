# 설치·실행 증거와 재생성

**R1 갱신(2026-11-15):** 아래 본문은 Bootstrap 감사 시점 기록이다. 이후 별도 `experiments/r1/.venv`(Python3.10.12)를 기존 cache의 A2A/Progent snapshot으로 offline 구성해17조건을 실행했다. 기존 venv를 변경하지 않았다. 별도 `third_party/continuity/.venv`(Python3.11.17)는 공식 원본 requirements를 설치해 tests30/quick을 실행했다. cache-only 실패(exit1) 뒤 같은 requirements 설치성공(exit0)도 보존했다. 정확한 재생성은 [R1 README](../experiments/r1/README.md), [CONTINUITY 설치](r1_continuity_artifact.md), [source/runtime](../results/r1/continuity-source-runtime.json), [원본 실행 manifest](../results/r1/fixture-run-01/manifest.json) 참조. 원본 full paper 재현은 아니다.

감사일 2026-11-15 (Asia/Seoul). **아래 재개 명령은 이번 감사에서 실행하지 않았다.** 실제 수행 명령·cwd·UTC 시작/종료·exit code·log hash는 [command-index.json](../results/setup/bootstrap-20261114/command-index.json)에 있다. 기존 성공/실패 기록은 재작성하지 않았다.

## 확인된 호스트·격리 환경

호스트: Linux x86_64, Python 3.10.12, uv 0.13.3, Git 2.34.1, Docker client 28.3.2. 부트스트랩 당시 RAM31GiB, 디스크 여유93GiB. Docker daemon·GPU·컨테이너 실행은 검증하지 않았다. 전역 pip/sudo를 사용하지 않았고 기존 `.venv`는 건드리지 않았다. [host doctor](../results/setup/bootstrap-20261114/host-doctor.log).

| 환경 경로 | Python | 주요 설치 버전 | 설치 / 실행 |
|---|---|---|---|
| `third_party/a2asecbench/.venv` | 3.10.12 | a2asecbench0.1.0, a2a-sdk0.3.26, pytest9.2.0, pydantic2.14.3 | VERIFIED / ASRF VERIFIED, 전체 tests FAILED timeout |
| `third_party/camel/.venv` | 3.10.12 | camel1.0.0, agentdojo0.1.34, pydantic2.11.5, openai1.82.1, anthropic0.52.2 | VERIFIED / NOT_RUN |
| `third_party/progent/.venv` | 3.10.12 | secagent0.1.0, pydantic2.14.3, openai3.51.0, anthropic2.8.0, z3-solver5.4.1.0 | VERIFIED / NOT_RUN |
| `experiments/orbit-release/.venv` | 3.11.17 | 0 packages | PARTIAL: interpreter만 / install FAILED, smoke NOT_RUN |

[environment-inventory.json](../results/setup/bootstrap-20261114/environment-inventory.json)과 `requirements-{a2asecbench,camel,progent}.txt`는 설치된 distribution metadata를 읽어 만든 snapshot이다. CaMeL은 원본 `uv.lock`으로 설치했다. 나머지는 snapshot을 원본 lockfile이라고 부르지 않는다. Progent의 느슨한 dependency 조건으로 설치된 최신 SDK와 artifact 간 실행 호환성은 NOT_RUN이다. API package가 설치되었다는 사실은 API 호출을 했다는 의미가 아니다.

## 소스 복구와 의존성

각 repo URL·고정 SHA는 [source-manifest.json](../results/setup/bootstrap-20261114/source-manifest.json)에 있다. 새 위치에서는 shallow clone 후 그 SHA로 checkout한다. 기존 checkout을 reset/삭제하지 말고 manifest와 다른 SHA라면 별도 경로를 쓴다. filter/sparse 상태인 repo의 미다운로드 blob은 full source 확보와 구분한다. 원격에서 고정 commit을 얻을 수 없다면 그 사실을 보고하고 최신 HEAD로 대체하지 않는다.

아래는 **미래 재생성용** 예시이며 이미 설치된 환경을 자동 변경하는 스크립트가 아니다. 프로젝트 root에서 실행한다.

```bash
git clone --depth 1 https://github.com/SaFo-Lab/A2ASecBench.git third_party/a2asecbench
git -C third_party/a2asecbench fetch --depth 1 origin e02109ebdcce3fe926884fbacbc935eef44e4aa3
git -C third_party/a2asecbench checkout --detach e02109ebdcce3fe926884fbacbc935eef44e4aa3
uv venv --python 3.10 third_party/a2asecbench/.venv
uv pip install --python third_party/a2asecbench/.venv/bin/python -r results/setup/bootstrap-20261114/requirements-a2asecbench.txt
uv pip install --python third_party/a2asecbench/.venv/bin/python --no-deps -e third_party/a2asecbench
```

CaMeL은 manifest SHA checkout 후 원본에서 다음 명령으로 설치한 로그가 있다.

```bash
cd third_party/camel
uv sync --frozen --no-dev
```

Progent은 manifest SHA checkout 후 다음과 같이 snapshot dependencies와 editable artifact를 분리해 복원할 수 있다(이 snapshot 방식의 재설치는 NOT_RUN).

```bash
uv venv --python 3.10 third_party/progent/.venv
uv pip install --python third_party/progent/.venv/bin/python -r results/setup/bootstrap-20261114/requirements-progent.txt
uv pip install --python third_party/progent/.venv/bin/python --no-deps -e third_party/progent
```

DRIFT는 `agentdojo==0.1.35` 등의 원본 version 요구를 독립 환경에서 충족시켜야 한다. standalone AgentDojo checkout이나 CaMeL의 0.1.34를 같은 환경에 강제로 합치지 않는다. 설치와 모델 실험은 NOT_RUN.

## 실제 실행 명령과 향후 재실행

기록된 성공 명령은 A2A repo cwd에서 다음과 같다. `--trials 1`은 설정에 들어 있는 **case별 1회**, 총200건이다.

```bash
.venv/bin/python orchestration.py --config configs/offline/asrf_eval.yaml --trials 1 --out ../../results/setup/bootstrap-20261114/a2a-asrf-original/trials.jsonl
```

재실행할 경우 기존 로그를 보존하려면 새 name/output 경로를 쓴다.

```bash
python3 scripts/bootstrap_run.py --name a2a-asrf-rerun-01 --cwd /home/cclab/controllable_agent/third_party/a2asecbench --timeout 600 -- .venv/bin/python orchestration.py --config configs/offline/asrf_eval.yaml --trials 1 --out ../../results/setup/a2a-asrf-rerun-01/trials.jsonl
```

기존 pytest와 `scripts/validate_release.py`는 timeout124. 성공한 test 개수를 추정하지 않는다. 재검증은 별도 실행 작업에서 개별 test를 좁혀 timeout 위치를 찾고 원본을 수정하지 않은 채 진단한다.

ORBIT은 PyPI 동명 패키지를 설치하지 않는다. 공식 v1.0.4 wheel/source/SHA256SUMS를 다운로드·검증했고 의존성 설치만 timeout됐다. 재개 시 설치가 먼저 필요하다.

```bash
python3 scripts/bootstrap_run.py --name orbit-install-resume-01 --timeout 600 -- uv pip install --python experiments/orbit-release/.venv/bin/python inspect-ai==0.3.263 ./third_party/orbit-release-v1.0.4/orbit-1.0.4-py3-none-any.whl
```

설치 후 공식 release의 `examples/first_benchmark.py`를 깨끗한 실행 디렉터리로 복사하고 기본 모드/`--negative-control`을 실행한다. 자세한 복사·실행 명령은 [ORBIT 감사](artifacts/ORBIT.md). 현재 example 실행 NOT_RUN이다. wheel/source는 Git에서 제외했고 [release metadata](../results/setup/bootstrap-20261114/orbit-release-manifest.json)와 원격 release URL을 남겼다.

## 감사 스크립트와 안전 경계

`python3 scripts/audit_bootstrap.py`는 **원시 로그·vendor checkout·venv를 보유한 로컬 환경 전용**이다. 설치·모델 호출·benchmark 없이 기존 Git metadata/installed distributions/로그/ASRF 행을 읽어 manifest, package snapshots, command index, 대표 이벤트, 200행 sink observation projection, hash/count를 생성한다. Git lazy fetch도 비활성화한다. 전체 원시 trial은 로컬에 보존하고 Git에 올리지 않는다.

GitHub fresh clone에서는 `python3 scripts/audit_bootstrap.py --verify-saved`로 공유된 source SHA 형식/URL, 명령 log hash/exit/metadata, 200행 projection과 summary의 집계, package snapshot 일치를 검증한다. 외부 checkout·venv·원시 trial·설치는 필요 없다. 이는 저장된 증거의 정합성 검증이며 새로운 독립 benchmark 재현은 아니다. 2건 full-event 표본 외에 전체200건의 sink 이벤트를 `a2a-asrf-observations.jsonl`에 보존했다.

`scripts/bootstrap_run.py`는 개별 명령의 증거를 새 이름에 기록하고 KEY/TOKEN/SECRET/PASSWORD/CREDENTIAL 환경변수를 제거한다. 현재 버전은 dotenv 로딩 비활성화와 timeout 시 process group 종료를 추가했다. **과거 로그는 이 변경 전 helper로 생성된 기록**이다. 이것은 OS sandbox가 아니며 파일 기반 credentials나 모든 외부 네트워크를 차단하는 도구가 아니다. 승인된 offline command만 검토 후 사용한다. paid provider·실제 외부 서비스 변경은 별도 승인 대상이다.
