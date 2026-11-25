# Controllable Agent / MAS 접근통제 실증 조사

기준일 2026-11-24 UTC. 신규 Gap을 전제하지 않고 K01–K15의 원문·공식 코드·실행 조건과 대안 연구를 대조한다. 기존 문서와 실험 로그는 보존하고 이 디렉터리에 새 근거만 기록한다.

## 재개 순서

1. [STATUS.md](STATUS.md)에서 마지막 완료 작업·비용·막힘·다음 명령을 확인한다.
2. [QUEUE.md](QUEUE.md)에서 완료 조건이 아직 열린 질문을 하나 고른다. [paper_registry.md](paper_registry.md)와 [coverage_matrix.md](coverage_matrix.md)의 `UNKNOWN`을 먼저 확인한다.
3. 실행 전 `runs/<run>/prereg.md`에 질문, 저자 주장, 예측, 반증 관찰, 최소 비용, 종료 조건을 적는다. 실행 뒤 원시 로그·정책·전후 효과·모델/seed/비용·해석을 [reproduction_log.md](reproduction_log.md)에 추가한다.
4. 결과를 [limitation_chains.md](limitation_chains.md), [hypotheses.md](hypotheses.md), [research_need_assessment.md](research_need_assessment.md)에 반영한다. `UNVERIFIED`는 0점이나 실패로 간주하지 않는다.

가장 검토 가치가 있는 조건, 기존 최강 반박, 기각 조건은 [Gap 후보 감시표](gap_watchlist.md)에 있다. H1 자연어 target은 [원문 대조](deep_h1.md)·[19건 공개 trace 탐색](deep_h1_trace.md)·[좁은 판정](h1_gap_verdict.md), H2 동적 경로는 [원문 대조](deep_h2.md), H3 위임/철회/효과는 [원문 대조](deep_h3.md)와 [교집합 감사](deep_h3_combination.md), H8 조건부 권한은 [PM/Cedar 대조와 판정](h8_conditional_gap_verdict.md)에서 이어진다. 후보 표의 순위는 신규성 확정이 아니다.

고정 commit·의존성 해시·호스트 조건은 [environment_manifest.md](environment_manifest.md), 이전 자료의 정확한 재사용 범위는 [prior_audit.md](prior_audit.md)에 있다.

## 이번 세션의 결정적 재현 명령

저장소 루트에서:

```bash
third_party/progent/.venv/bin/python docs/access_control_empirical_20261124/runs/progent_manual_boundary/run.py
third_party/progent/.venv/bin/python docs/access_control_empirical_20261124/runs/progent_subset/run.py
```

원본 Progent repo `b02783b896d4`의 기존 격리 venv를 사용하며 외부 API를 호출하지 않는다. `runs/progent_manual_boundary/results.json`에 네 조건의 정책·입력·전후 로컬 효과가 저장된다. 두 번째 명령은 `SECAGENT_ONLY_ALLOW_NARROW`로만 활성화되는 생성 규칙 포함 함수 자체를 시험한다. 원본 코드에는 패치를 적용하지 않았다. AutoCedar의 공식 verifier 실행 명령과 고정 도구 해시는 [K06 manifest](runs/K06_verify_20261124/manifest.md), K11 테스트와 OpenShell 이전 실행 재감사는 [reproduction_log.md](reproduction_log.md)를 참고한다.

[H5 동일 호출 대조](runs/H5_dispatch_effect/result.md)는 원본 Progent wrapper와 기존 BusyBox Docker image를 사용한 별도 합성 실험이다. 해당 실행 폴더에는 결과가 보존돼 있어 `run.py`가 **기존 출력 위에 다시 쓰지 않도록 중지**한다. 다시 실행하려면 `run.py`와 `runner.sh`를 새 임시 폴더로 복사한 뒤 기존 Progent venv로 그 복사본을 실행하고, 새 결과를 별도 run으로 기록한다. 이 실험은 Docker 자원 격리 대조이며 OpenShell 논문/제품 재현이 아니다.

[K07 공식 NIST PM 3.3.0 독립 시험](runs/K07_condition_boundary/result.md)은 root `env/K07_pm_worktree`의 격리 worktree와 `env/K07_m2_cache`를 사용한다. [정확 Maven 명령](runs/K07_condition_boundary/commands.md)은 test source를 이미 넣은 worktree에서만 재실행한다. 원본 `third_party/K07-nist-policy-machine`은 clean이며, NGAC-IR 저자 생성기 자체는 확보되지 않았다. [K05 공식 Cedar CLI 조건 대조](runs/K05_conditional_alternative_20261124/result.md)는 그 자리의 `run.py`로 재현 가능하지만 보존된 `raw.json`을 덮어쓰므로 새 run 사본을 만들어 실행한다. 두 결과의 인메모리 ledger를 원격 서비스 effect로 읽지 않는다.

[K07 복수 route·조건부 금지 7조건](runs/K07_route_composition_20261125/result.md)과 [K05 Cedar 규칙별 조건 6조건](runs/K05_route_composition_20261125/result.md)은 각자의 `prereg.md`·`commands.md`·원시 입력·로컬 ledger를 보존한다. 전자는 **공식 NIST PM의 독립 구성**, 후자는 **공식 Cedar CLI의 기존 대안**이며 NGAC-IR 저자 생성기나 원격 provider 재현이 아니다.

[CONTINUITY EUR120/9000 원본 함수 대조](runs/M1_continuity_amount_20261125/result.md)는 별도 `run.py`와 `commands.md`에 verifier·permit·FinalitySink 경로를 기록했다. Donno의 공유 HMAC/A2A/보험 서비스 재현이 아니다. [Multi-CaMeL AssetOpsBench 공개 trace 감사](m3_assetops_trace_audit_20261125.md)는 실험 자료를 찾지 못한 정확한 검색 범위를 기록한다.

[EAL-Bench 공식 코드 오프라인 감사](runs/EAL_offline_20261125/result.md)는 보조 문헌의 공개 집계·해시를 검증했다. 원본 raw trial 부재와 논문 v1/v2 경계를 결과에서 구별한다. 재실행 명령은 [여기](runs/EAL_offline_20261125/commands.md); 모델/API를 호출하지 않는다.

[M4 원저자 retrieval guard 입력 경계](runs/M4_guard_boundary_20261125/result.md)는 논문이 직접 연결한 Apache-2.0 코드의 `guard()`를 2개 합성 입력에서 호출한다. 표지 없는 agent journal이 남고 외부에서 `revoked_at`을 주면 제거되는 것을 확인했다. 저자 Graphiti/LLM write-back·실제 provider 효과는 재현하지 않았다. [MAP-Graph 보조 공개 artifact 감사](runs/H11_risk_metadata_20261125/result.md)는 저자 연관 후보 commit의 2,700개 저장 지표 중 41개 unsafe 행을 집계하고 원본 risk gate를 4개 합성 입력에서 시험한다. 논문 HTML의 직접 코드 링크/평가 commit 대응은 미확정이고, 원시 실행 trace·실제 서비스 효과는 없다. 두 run 모두 `commands.md`에서 오프라인 재현한다.

이후 [H10 EAL 원본 gate와 공식 corpus case 6입력](runs/H10_source_scope_20261125/result.md)은 고정 lock의 격리 venv를 설치해 source-only 검사와 금액 scope를 분리했다. [H12 M4 guard→loopback HTTP/SQLite 6조건](runs/M4_live_20261125/result.md), [H11 MAP-Graph 원본 gate→mock outbox·900행 저장 지표 대조](runs/H11_counterfactual_20261125/result.md)는 모두 원본 함수와 독립 fixture의 역할을 나눠 기록했다. 각 run의 `prereg.md`·`commands.md`·`result.md`·raw 출력에서 재현하며, 실제 Graphiti/LLM/외부 provider 논문 평가를 재현한 것으로 읽지 않는다. 사용자 승인 유료 API 총 상한은 USD 5이나 현재 사용 가능 키가 없어 이번 추가 비용은 USD 0. [강한 최신 대안 감사](h13_hard_counter_20261125.md)는 WTB v4 등을 포함한다.

## 상태와 제한

실험 저장소 루트의 R1/R2/R3, `docs/guided_reproduction_20261117/`, `docs/research_need_discovery_20261123/`, `docs/experiments/20261124_openshell/`을 참고 자료로 읽는다. Progent 실험은 원저자 전체 AgentDojo 재현이 아니다. OpenShell 기록은 별도 이전 실행이다. 논문 저자 수치와 로컬 효과는 서로 다른 열로 기록한다. 로컬에 첨부 지시서와 동일한 이름의 파일이 없어 사용자 메시지 본문 전문을 실행 기준으로 삼았다.
