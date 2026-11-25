# 실행 기록

2026-11-25 UTC, `/home/cclab/controllable_agent`에서 실행. 보조 저장소는 `https://github.com/xiaoqi-7/MAP-Graph`, commit `d94b0bf3c73efdb60fcc08014989b44ce8eae99d`, clean worktree로 확인했다. 최초 `/tmp/mapgraph-h11` clone에서 시험하고 동일 SHA를 `third_party/MAP-Graph/`에 보존했다. 논문 HTML이 이 URL을 직접 가리키지는 않으므로 **저자 연관 보조 artifact 후보**로 표시한다. license 파일은 발견하지 못했다.

```bash
git -C /tmp/mapgraph-h11 rev-parse HEAD
python3 -I docs/access_control_empirical_20261124/runs/H11_risk_metadata_20261125/gate_metadata.py /tmp/mapgraph-h11/artifact > docs/access_control_empirical_20261124/runs/H11_risk_metadata_20261125/decisions.jsonl
```

최초 호출은 `src.map_graph` package `__init__`가 선택적 `openai` client를 eager import하여 `ModuleNotFoundError: openai`로 종료했고, 결과 JSONL은 비었다. 이는 gate 함수 자체의 실행 실패가 아니다. 원본 repo는 수정하지 않고 두 필수 소스 파일(`memory_baselines/base.py`, `map_graph/trust.py`)만 `importlib`로 load하도록 **실험 harness**를 수정했다. 사전등록의 오류 확인 후 1회 재시도 한도 안에서 다음 명령이 성공했다.

```bash
python3 -I docs/access_control_empirical_20261124/runs/H11_risk_metadata_20261125/gate_metadata.py /tmp/mapgraph-h11/artifact > docs/access_control_empirical_20261124/runs/H11_risk_metadata_20261125/decisions.jsonl
git clone /tmp/mapgraph-h11 third_party/MAP-Graph
git -C third_party/MAP-Graph remote set-url origin https://github.com/xiaoqi-7/MAP-Graph
python3 -I docs/access_control_empirical_20261124/runs/H11_risk_metadata_20261125/audit_metrics.py third_party/MAP-Graph/artifact > docs/access_control_empirical_20261124/runs/H11_risk_metadata_20261125/metrics_audit.json
sha256sum third_party/MAP-Graph/artifact/src/map_graph/trust.py third_party/MAP-Graph/artifact/final_results/canonical/main/task_metrics.csv
git -C third_party/MAP-Graph status --short
```

원본 `trust.py` SHA-256 `3dbcc82e992912181f8c7b960bb79b8623cff85f758fd21a78c132763c66e649`, `task_metrics.csv` SHA-256 `23ed3ac13c00c24e7064d75fd9cc85bc65dff8a4e4b9c6e1f47f145c1dfc5e24`. `git status --short` 출력 없음. 모델/seed/temperature: 함수 시험은 **모델 없음/seed 없음/temperature N/A**; 저장된 저자 결과는 논문 기준 Qwen2.5-7B-Instruct/temperature 0/생성 seed 42로, 이번에 모델 run을 다시 하지 않았다. 유료 API $0, 외부 effect 0, network effect 0.
