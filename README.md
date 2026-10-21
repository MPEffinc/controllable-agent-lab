# Controllable Agent Lab
악성 관측 도구가 섞인 멀티에이전트 운영 복구 실습 저장소. 단계별 기록은 docs/progress.md, 개념 메모는 docs/concepts/.
실행: source .venv/bin/activate

## 현재 상태
- 현재 단계: S1 실험 완료 (결과를 함께 읽은 뒤 s1-done 태그 예정)
- 마지막 커밋: 9bcd95a [S1] call_llm: USD 비용 예산, 출력 상한 25000, 이상 감지 (이후 커밋은 이 절 아래에 쌓인다)
- 요약: 프롬프트 주입 관찰 27회(실험 3종 × 추론 강도 3 × 3회, 0.002 USD). 지시문 주입은 보고에 반영되지 않았고, 지시문 없는 값 위조는 9/9 그대로 보고됐다. 관찰용이며 비율은 주장하지 않는다. 결과는 runs/s01_summary.json.
- 막힌 곳: 없음
- 막힌 곳: 없음
