# CONTINUITY — 원본 artifact 학습 준비

확인일: 2026-11-17 (Asia/Seoul). **이번 작업은 소스·환경 읽기만 수행했다.** 아래 실습 명령은 미실행이다. 과거 실행 로그는 별도 근거로만 연결한다.

## 출처와 현재 환경

- 원본 논문: [CONTINUITY v1, 2026-09-04](https://arxiv.org/html/2609.05269v1). 논문 본문의 Artifact 링크가 [zast-ai/continuity](https://github.com/zast-ai/continuity)를 직접 가리킨다. 이번에 연결 GitHub 도구로 고정 SHA의 README를 다시 확인했다.
- 소스: `third_party/continuity`, SHA `59cfe60930d247d1890b366ded686c718020a11e`, MIT, project version `1.0.0`. `git status --short`는 빈 출력이었다. 파일 목록에 core/experiment/tests/scripts/results/figures가 모두 존재한다.
- 기존 독립 환경 `third_party/continuity/.venv`를 재사용한다. 이번 metadata 읽기에서 Python 3.11.17, distributions 20개를 확인했다. 원본 `requirements.txt`의 직접 의존성 5개와 일치: `cryptography==46.0.4`, `numpy==2.3.5`, `pandas==2.2.3`, `matplotlib==3.10.8`, `pytest==9.0.2`.
- 원본 Python 조건 `>=3.11`. Docker/GPU/API 키/모델 불필요. 실험은 adversarial planner가 제안했을 action을 직접 구성하는 결정론적 in-memory conformance suite다. 실제 LLM agent 평가가 아니라는 점이 이 연구의 원본 방법에 포함된다.
- 원본의 포함된 `results/`는 저자 결과다. 새 실습 출력은 `local/guided-reproduction-20261117/runs/continuity/<새-run-id>/`로 지정하고, 원본 `results/` 및 과거 `results/r1/`을 덮어쓰지 않는다.

## 논문 질문과 코드의 연결

아래 논문 설명은 [§3](https://arxiv.org/html/2609.05269v1#S3), [§5–7](https://arxiv.org/html/2609.05269v1#S5), [§8](https://arxiv.org/html/2609.05269v1#S8), [§12](https://arxiv.org/html/2609.05269v1#S12)에 연결된다. 함수와 실행 동작은 고정 source를 직접 읽은 결과다.

| 질문 | 논문 위치 | 원본 구현과 확인점 |
|---|---|---|
| Problem / threat | §3.2, §4 | 외부 content와 planner, 일부 non-root component의 악성 동작을 모델링한다. `experiment.py::_mutate_fault`(854), `make_scenario`(562), `materialise`(962)가 공격 후보와 변경을 구성한다. |
| Policy representation | §5.1–5.4, §6, 부록 B | `core.py::DeploymentPolicy`(524), `ComponentContract`(400), `RootGrant`(207), `PredicateSpec`(177), `FieldConstraint`(183), `ReleaseCredential`(300), `ExecutionPermit`(473). 서명된 dataclass와 deterministic predicate registry다. Datalog/YAML 엔진이 아니다. |
| Policy generation | §6.6, §7.5–7.6, §10.4 | `experiment.py::build_infrastructure`(222)가 개발자가 작성한 계약/신뢰 issuer/role mapping을 구성하고, `_root_constraints`(445)·`make_scenario`가 테스트용 grant를 생성한다. `core.py::issue_permit`(1347)은 검증 결정에서 permit을 만든다. 자연어 정책 자동 생성기는 이 artifact에서 확인되지 않았다. |
| Enforcement | §6.7–6.8, §7.3–7.4 | `ContinuityVerifier.verify_bundle`(1248) → `issue_permit`(1347) → `EffectBroker.dispatch`(1508) → `FinalitySink.execute`(1440) → `SimulatedWorld.apply`(1393). 검증 허용과 최종 effect를 별도로 관찰한다. |
| Correctness / update | §7.6, §9, §10.4 | `lint_pipeline`(671)은 필수 field·guarantee 연결 검사다. `_verify_root/_verify_releases/_verify_transitions`는 scope 확대·잘못된 release·contract 변경을 검사한다. `FinalitySink.execute`는 현재 `RuntimeState`의 policy tuple/revoked IDs를 다시 읽고 action/subject/audience/expiry/nonce/idempotency를 검사한다. lint가 정책 의미의 정확성을 증명하지는 않는다. |
| Evaluation | §8, 부록 C | `scripts/run_experiments.py` → `run_main`(1395), `run_ablation`(1489), `run_performance`(1573). `DOMAINS`(108), `ATTACK_FAULTS`, `SYSTEMS`(1141), `ABLATIONS`가 실험 설정이다. |
| Limits | §12 | trusted validator의 의미 오류, 모든 effect/context 경로의 완전성, production provider의 durable/concurrent finality는 보장 밖이다. 실제 구현의 `SimulatedWorld`와 `NonceLedger`는 in-memory다. |

## 첫 정책 예시

원본 `src/continuity/experiment.py::_root_constraints`의 finance grant는 다음 제약을 포함한다. 아래는 원본 코드에서 발췌한 것이며 새로 만든 정책이 아니다.

```python
FieldConstraint(
    "/action/parameters/amount_cents",
    PredicateSpec("int_range", {"min": 1, "max": 1_000_000}),
)
```

이 제약만 충족했다고 실행되는 것은 아니다. `make_scenario`는 principal/actor/task와 operation·resource scope, tool/server/effect, provenance/context digest를 담은 root grant를 만든다. 정상 경로의 destination alias 변환도 `TransformRule("/action/destination", "alias_resolution", True)`와 directory issuer의 witness가 필요하다. `verify_bundle`가 허용해야 permit을 발급하며, permit 발급 뒤 action을 바꾸면 sink가 거부한다.

## 가장 작은 원본 실습 — 사용자 진행 시 실행

cwd는 `/home/cclab/controllable_agent/third_party/continuity`다. 두 테스트를 먼저 읽고 실행한다. pytest cache와 bytecode 생성은 끈다. 원본 코드나 기존 결과를 수정하지 않는다.

```bash
cd /home/cclab/controllable_agent/third_party/continuity
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_experiment.py::test_benign_and_valid_typed_release_execute \
  tests/test_experiment.py::test_post_permit_action_substitution_is_stopped_at_sink
```

목적과 관찰 지점:

- `test_benign_and_valid_typed_release_execute`(10): 원본 finance seed17의 `benign`/`benign_external` 두 경우를 실행한다. 기대값은 `disposition == EXECUTE`, `effect_count == 1`, `lifecycle_correct`다. typed release가 있는 외부 값을 무조건 차단하지 않는 정상 효용도 확인한다.
- `test_post_permit_action_substitution_is_stopped_at_sink`(74): 허용·permit 발급 뒤 action을 바꾼다. 기대값은 `disposition == DENY`, `first_outcome == E_ACTION_SUBSTITUTION`, `effect_count == 0`이다. 처음 admission을 통과해도 최종 Tool Effect는 차단될 수 있음을 배운다.
- pytest의 통과 메시지는 assertion 결과다. 세부 값이 필요하면 디버거로 `run_system` 반환 `RunResult`와 `FinalitySink.execute`의 반환값을 본다. 실제 외부 송금이나 원격 tool 호출은 발생하지 않는다.

다음 심화는 `test_finality_policy_revalidation`, `test_finality_revocation_revalidation`, `test_ambiguous_external_field_escalates`, `test_nonce_replay_executes_exactly_once`, `test_targeted_ablations_expose_corresponding_faults`다. 첫 두 경우를 이해한 뒤 하나씩 진행한다. replay의 `IDEMPOTENT_REPLAY`는 이전 outcome을 반환할 수 있으므로 허용 응답 수를 effect 수로 세면 안 된다.

## 원본 Evaluation 진입점 — 지금 실행하지 않음

사용자가 범위 확대를 승인한 뒤 새 디렉터리 이름을 사용한다. 아래 `session-01`이 이미 있으면 새 이름을 쓴다.

```bash
cd /home/cclab/controllable_agent/third_party/continuity
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_experiments.py \
  --quick --output ../../local/guided-reproduction-20261117/runs/continuity/session-01
```

`--quick`도 한두 테스트가 아니라 488 scenarios × 7 systems = 3,416 main 실행이며 ablation/performance까지 함께 실행한다. `raw_results.csv`의 `disposition`, `first_outcome`, `second_outcome`, `effect_count`, `violation_accepted`, `lifecycle_correct`를 먼저 보고 `summary.csv`와 대조한다. full은 `--quick`을 뺀 같은 runner이며 3,460 scenarios / 24,220 main runs다. 이것을 지금 한꺼번에 실행하지 않는다.

Scorer는 `experiment.py::run_system`(1224)에서 실행 후 `len(world.effects)`를 읽는다. 일반 공격은 effect>0, retry/replay는 effect>1을 harmful로 본다. 따라서 attack label 자체만으로 모든 case에서 effect0을 기대하면 잘못 해석하게 된다. 원본 runner의 CSV는 완전한 provider sink trace를 직렬화하지 않는다.

## 과거 기록과 이번 관찰의 구분

- **이번 직접 관찰:** source SHA/clean status, 파일/함수 내용, 설치 환경 metadata. 새 테스트·suite는 실행하지 않았다.
- **과거 로컬 실행 기록:** [기존 감사](../r1_continuity_artifact.md)에 tests30 및 quick 실행 로그가 있다. 이 기록을 이번 독립 재실행 성공으로 바꾸어 말하지 않는다.
- **원본 저자 결과:** checkout의 `results/`와 [논문 §8](https://arxiv.org/html/2609.05269v1#S8). 새 로컬 결과와 분리한다.
- **후속 자체 연구:** R1/R2/R3 adapter·synthetic MAS 결과는 이 가이드의 원본 실습 범위에 합산하지 않는다.
