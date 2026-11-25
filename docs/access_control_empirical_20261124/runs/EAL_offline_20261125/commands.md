# 실행 명령 — EAL-Bench 공식 저장소 오프라인 감사

작업 루트 `/home/cclab/controllable_agent`. 아래 명령은 논문 저자가 링크한 저장소를 별도 `third_party/`에 받은 뒤 **모델/API 호출 없이** 실행했다. 원본 checkout은 수정하지 않았고 출력은 이 run 폴더의 `tables/`, `diagnosis.json`에 저장했다.

```bash
git ls-remote https://github.com/tommasocerruti/eal-bench.git HEAD
git clone --filter=blob:none --depth=1 https://github.com/tommasocerruti/eal-bench.git third_party/EAL-Bench
cd third_party/EAL-Bench
git rev-parse HEAD
python3 -m analysis.paper_results --domain all --output-dir /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/EAL_offline_20261125/tables
python3 -m analysis.extension_results
python3 -m analysis.extension_results --diagnosis --out /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/EAL_offline_20261125/diagnosis.json
sha256sum results/extensions/manifest.json results/extensions/snapshots/seven_summary.json results/extensions/snapshots/gate_added_table.json results/extensions/snapshots/parity_pool.json analysis/extension_results.py
git status --short
```

`analysis.paper_results`는 manifest가 명시한 **논문 v1, 5 writer**의 저장 count를 검증한다. 논문 v2의 7 writer 표와 혼동하지 않는다. `analysis.extension_results`는 v2 관련 snapshot 200개 파일 해시를 확인하지만 누락된 raw trial을 재실행하거나 재채점하지 않는다. Python 3.12.15, 외부 Python 의존성 설치 0, 모델/API 0.
