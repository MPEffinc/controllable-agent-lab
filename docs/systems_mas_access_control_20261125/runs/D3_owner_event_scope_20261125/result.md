# D3 자연어 승인 scope·시간 추출 결과

2026-11-25 UTC. [사전등록](prereg.md), [고정 owner history/gold](fixtures.json), [실행 코드](run.py), [원시 API](raw.jsonl), [모든 96 요청/전후 상태](result.json), `service_state.sqlite`. 모델 `gpt-4.1-mini-2025-04-14`, temperature 0, seed 20261125. 6 calls, 입력 1,390/출력 477 토큰, 추정 $0.0013192. 실제 외부 서비스 0.

6개 합성 history는 baseline, Atlas staging만 강화, Atlas production 예외 만료, Atlas staging 예외 철회, 과거 3명 production 규칙 대체, Boreal staging 미래 변경을 포함했다. 각 history에 2개 시점×4개 scope의 8칸을 검사했다. 모델 JSON 6/6 유효, **48/48 policy cell gold 일치**. 로컬 provider 모의 effect에서는 gold와 모델 정책 모두 **정상 48/48 허용, 1명 부족한 비인가 0/48 효과**였다. 분모는 case 간 독립 정책 칸/요청 수이며 일반 성공률 추정이 아니다.

**판정:** 이 작은 명료한 owner history 범위에서는 자연어 승인 구조화의 실패 사례가 나오지 않았다. H10/H13/D3의 **이 범위 한정** 실패 가설은 `REJECTED_HYPOTHESIS`; 광범위 Research Need는 `UNVERIFIED`. 장기 대화, 모호한 승인, 권한자 식별, 공격자 입력, provider가 실제로 어떤 효과를 수락했는지는 이 실험에 없다. 오류를 얻으려고 같은 결과를 재시도하거나 문장을 사후 수정하지 않았다.
