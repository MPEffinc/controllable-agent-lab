# A5 현행 Agent libOS 원저자 테스트 결과

2026-11-25 UTC. [사전등록](prereg.md). 공식 source SHA `85e8ff94c1e562bfb1f891714e3bf4bed9795690`, 패키지 v1.6.0. `uv sync --frozen --group dev`로 고정 `uv.lock`을 별도 `env/`에 설치(39 MB, git 제외). `PYTHONDONTWRITEBYTECODE=1 env/bin/python -m pytest -q`로 선택한 원저자 네 테스트 실행. 원시 `uv_sync.*`, `pytest.*` 로그 보존. exit 0, **4 passed in 5.68s**, API 비용 $0.

선택 테스트는 host manifest hash/SQLite 재열기, 명시 권한만 compilation, 자식의 더 좁은 `reports/q1.txt` read 허용과 `secrets/key.txt` read 거부, 부모 `filesystem.*` effect ceiling을 자식이 `jsonrpc.*`로 넓히거나 제거하려 할 때 거부, 명시 빈 effect ceiling의 `jsonrpc.call`/`human.write` 거부를 검사한다. 이것은 **원저자 코드에서 관측된 runtime decision과 내부 상태**다. 테스트는 실제 외부 서비스 상태를 변경하지 않아 effect 결과는 `DECISION_ONLY`다.

따라서 host가 올바른 manifest를 작성한다는 조건에서 단순 자식 권한 확대를 새 메커니즘 Gap으로 주장할 근거는 줄었다. 자연어 승인에서 manifest가 어떻게 정확히 만들어지는지, 런타임 밖 provider effect까지 항상 묶이는지, 긴 task에서 철회가 어떻게 반영되는지는 이 네 테스트로 확인되지 않았다. 논문 시점 판본과 현행 v1.6.0도 분리한다.
