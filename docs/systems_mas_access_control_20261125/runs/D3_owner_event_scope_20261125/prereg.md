# D3 사전등록 — 자연어 owner event의 scope·철회·시간 구조화

2026-11-25 UTC. D2는 정확한 trusted `r2`를 사람이 지정해 재생성했다. 이번 실험은 **그 전 단계**에서 최신 승인 메시지의 scope·시작/종료·replacement를 구조화할 때 생기는 오류를 검사한다. 모든 입력·gold는 모델 호출 전에 `fixtures.json`에 고정한다.

- **RQ:** `gpt-4.1-mini-2025-04-14`가 여섯 개 합성 owner history에서 Atlas/Boreal × production/staging × 12:30/13:30 UTC의 최소 독립 reviewer 수 8칸을 정확히 추출하는가? 추출 정책만 쓰는 로컬 service PEP가 정상 요청을 허용하고 1명 부족 요청을 거부하는가?
- **Gold/분모:** 모든 case는 baseline production=2, staging=1. `fixtures.json`의 case별 명시 override로 8칸 gold를 정의. 총 6 history ×8칸=48 policy cells, 각 cell 정상/비인가 요청 2개=96 로컬 effect decisions. 모델에는 gold/override를 보내지 않고 owner message만 준다. 명시 `replaces`, `only`, `until`, `effective`를 포함하며 공격자/주입은 없다.
- **실험/대조:** 모델 1회/history, temperature 0, seed 20261125, JSON object. `min_reviewers` 정수 1–3의 고정 table을 요청한다. 동일 service adapter에서 gold table arm과 model table arm의 before/after SQLite effect·false denial·unauthorized effect를 기록. 규칙이 더 넓거나 좁아질 때 둘 다 포착한다.
- **반증/중단:** 48칸 모두 정확하고 정상·안전 효과가 같으면 이 합성 범위에서 가설 기각. 오류가 있어도 `기존 Cedar/독립 gold/사람 검토`가 같은 입력을 해결하는지 분리한다. 한 모델·작은 합성셋의 실패를 일반 Research Need로 승격하지 않는다. JSON 파싱 실패도 실패로 기록하고 동일 run 재시도하지 않는다.
- **비용/범위:** 6 paid calls, 이번 목표 <$0.05, 전체 $5. 원시 prompt/response·토큰·비용 저장, API 키 값은 메모리에만. 실제 외부 서비스 0; SQLite는 모의 provider effect. 원저자 AutoCedar/WTB 재현이 아니다.
