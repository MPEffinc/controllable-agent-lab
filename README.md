# Controllable Agent Lab
악성 관측 도구가 섞인 멀티에이전트 운영 복구 실습 저장소. 단계별 기록은 docs/progress.md, 개념 메모는 docs/concepts/.
실행: source .venv/bin/activate

## 현재 상태
- 현재 단계: S1 진행 중 (에이전트 루프와 이력 저장 완료, 프롬프트 주입 관찰 실험 2개 남음)
- 마지막 커밋: cead7af [S1] call_llm: status·불완전 사유, 추론 토큰 기록, 추론 강도 환경 변수 (이후 커밋은 이 절 아래에 쌓인다)
- 요약: call_llm()(lab/common.py)과 도구 1개 에이전트 루프(lab/s01_agent/, `python -m lab.s01_agent.agent`)가 동작하고, 실행 이력은 runs/ 에 JSON 으로 저장된다. 모델은 gpt-6-luna 하나, 누적 488 토큰.
- 막힌 곳: 없음
- 막힌 곳: 없음
