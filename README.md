# Controllable Agent Lab
악성 관측 도구가 섞인 멀티에이전트 운영 복구 실습 저장소. 단계별 기록은 docs/progress.md, 개념 메모는 docs/concepts/.
실행: source .venv/bin/activate

## 현재 상태
- 현재 단계: S1 진행 중 (call_llm() 완성, 에이전트 루프는 다음 조각)
- 마지막 커밋: fa5e39e [S0] 비용 규약과 README 현재 상태 추가 (이후 S1 첫 커밋이 이 절 아래에 쌓인다)
- 요약: lab/common.py 의 call_llm() 이 responses 형식 호출을 정규화하고 토큰 기록·상한·HTTP 오류 기록을 한다. 모델은 gpt-6-luna 하나.
- 막힌 곳: 없음
