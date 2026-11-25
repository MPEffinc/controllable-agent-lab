# AutoCedar gold dataset 저장 산출물 무결성 — 사전 질문

- 질문: 원저자 공개 200-case gold dataset의 저장 Cedar 정책/schema/AST가 저장된 structured spec·registry를 **LLM 없이** 다시 컴파일한 결과와 일치하는가?
- 원래 주장: dataset README는 `verify_gold.py`가 이 무결성을 확인한다고 설명한다. 자연어 의도와 gold의 동치 또는 AutoCedar 생성 정책의 정확성은 주장하지 않는다.
- 예상: 200개 모두 일치, exit 0.
- 반증: 파일 누락 또는 재컴파일 불일치.
- 비용: 로컬 Python 1회, API 0, seed는 저장된 case 입력에 포함.
- 종료: 원시 stdout/stderr/exit 기록 후 이 무결성 질문 닫기.
