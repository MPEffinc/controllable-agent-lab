# Controllable Agent Lab
악성 관측 도구가 섞인 멀티에이전트 운영 복구 실습 저장소. 단계별 기록은 docs/progress.md, 개념 메모는 docs/concepts/.
실행: source .venv/bin/activate

## 현재 상태
- 현재 단계: S1 진행 중 (call_llm 비용 장치 변경 완료, 프롬프트 주입 관찰 실험 진행 예정)
- 마지막 커밋: ad04f10 [S1] 에이전트 루프: 도구 결과를 이력에 추가, 이력 JSON 저장 (이후 커밋은 이 절 아래에 쌓인다)
- 요약: call_llm()(lab/common.py)이 호출마다 토큰과 USD 추정(usd_estimate)을 기록하고 LAB_MAX_USD(기본 1.00)로 막는다. 도구 1개 에이전트 루프(lab/s01_agent/, `python -m lab.s01_agent.agent`)가 동작한다. 모델은 gpt-6-luna 하나.
- 막힌 곳: 없음
- 막힌 곳: 없음
