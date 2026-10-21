# Controllable Agent Lab
악성 관측 도구가 섞인 멀티에이전트 운영 복구 실습 저장소. 단계별 기록은 docs/progress.md, 개념 메모는 docs/concepts/.
실행: source .venv/bin/activate

## 현재 상태
- 현재 단계: S1 완료(태그 s1-done), S2 시작
- 마지막 커밋: ead4c0a [S1] 프롬프트 주입 관찰: 도구 모드 스위치, 판정기, 27회 실행 결과 (이후 커밋은 이 절 아래에 쌓인다)
- 요약: S1 에서 에이전트 루프와 프롬프트 주입 관찰 27회(실험 3종 × 추론 강도 3 × 3회, 0.002 USD)를 했다. 지시문 주입은 보고에 반영되지 않았고 지시문 없는 값 위조는 9/9 그대로 보고됐다. 관찰용이며 비율은 주장하지 않고, 원인은 가릴 수 없다. 결과는 runs/s01_summary.json, 해석은 docs/progress.md.
- 막힌 곳: 없음
