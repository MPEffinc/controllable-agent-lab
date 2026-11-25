# EAL-Bench 공개 아티팩트 오프라인 검증 — 사전 등록

- 검증 질문: 원저자 EAL-Bench v2의 장기 승인 메모리 결과가 공개 저장소의 고정된 집계 자료로 재계산되는가? 원시 trial 재채점 가능 범위와 집계 재출력 범위를 구별한다.
- 원래 주장: [EAL-Bench v2 §4.6, Appendix C.1–C.2](https://arxiv.org/html/2609.01836v2)는 source-authority filter와 event-based memory를 같은 typed-incremental 사례에서 비교한다. 출처 검사 후에도 잘못된 범위/철회 상태가 남고, event 방식은 비인가 행동을 줄이면서 정상 행동도 줄인다.
- 예상 결과: 저자 [공식 코드](https://github.com/tommasocerruti/eal-bench)의 오프라인 `analysis.paper_results`가 논문에 해당하는 저장 집계와 일치하며, 원시 JSONL 누락은 명시적으로 보고한다.
- 반증 관찰: 공개 집계가 논문 표와 다르거나, 소스·릴리스의 판본이 논문 v2와 연결되지 않거나, 원시 trial 파일이 없어 독립 재채점을 할 수 없으면 해당 수준을 `NOT_ESTABLISHED`로 기록한다.
- 최소 비용: `git` 읽기, 로컬 Python 집계·corpus validation만. 유료 API·원격 모델·실서비스 0. 원저자 checkout 무수정, 새 출력은 이 run 디렉터리에 저장한다.
- 완료 조건: 공식 링크/commit/라이선스/명령/도구 버전/집계 비교/누락 자료/실제 효과 수준을 결과 파일에 기록하고, Research Need 판정을 강한 기존 대응과 함께 반박한다.
