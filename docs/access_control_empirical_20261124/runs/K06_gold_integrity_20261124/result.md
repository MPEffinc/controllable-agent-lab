# Gold 저장 산출물 확인 결과

- 사전 질문: [prereg.md](prereg.md).
- 원저자 소스 commit `a0cf180977d799cf943514b67ffc260fc579b9a5`; Python 3.10.12; 모델/API 호출 0, 비용 USD 0.
- 명령: `cd third_party/K06-autocedar/dataset/gold-reference-dataset && python3 verify_gold.py`.
- exit 0, stdout 원문: `Verified 200 case(s): gold policies, schemas, and predicate ASTs match.` stderr 없음. 실행 시간 약 0.56초.
- 원본 `verify_gold.py`는 200개 디렉터리의 7개 파일 구성과 `spec.json`/`registry.json`에서 재컴파일된 `gold.cedar`, `schema.cedarschema`, `predicate_ast.json`의 일치를 확인한다. LLM rewrite·원문 의미·독립적인 사람의 gold 승인·Cedar 동치 검사는 이 명령의 범위 밖이다.
