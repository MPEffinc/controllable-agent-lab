# K14 OpenShell v0.1.9 provider effective policy: 사전 등록

- 질문: credentialless `pypi` provider를 기존 sandbox에 붙이면 base policy는 그대로이고 effective policy에 `_provider_*` network rule이 추가되며, `--wait` 뒤 새 정책이 적용되는가? 동일 L7 rule 위반 요청에서 `audit`는 upstream으로 전달하고 `enforce`는 차단하는가?
- 원래 주장: [OpenShell v0.1.9 정책 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview)의 base/effective 합성, [provider profile 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/providers/profiles)의 attach/`--wait`, [network rule 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/network-rules)의 audit/enforce.
- 예상: 새 provider의 profile이 network endpoint를 제공하고 global policy가 없으면 full/effective에 `_provider_*`가 생긴다. `audit` 위반은 로그 후 전달, `enforce`는 `policy_denied`/upstream 0이다.
- 반증: profile에 endpoint가 있는데도 적용 완료 뒤 effective에 반영되지 않거나, `audit`가 규칙 위반을 차단하거나 `enforce`가 effect를 만들면 각 주장을 뒤집는다. 연결 실패/외부 서비스 응답 실패는 L7 차단으로 임의 해석하지 않는다.
- 비용·범위: 공식 릴리스 v0.1.9 binary, 별도 127.0.0.1:18081 Gateway/SQLite/인증서, 고유 `h2eff*` sandbox만. 이미 존재하는 `oslab-*`/`sregym-*`는 절대 변경하지 않는다. credentialless provider, LLM/API 호출 없음. synthetic 또는 공개 무상 GET만. CPU 0.5, RAM 512Mi, 1 sandbox. 컨테이너와 listener는 실험 소유만 정리.
- 완료 조건: commit·binary hash·정책·명령·base/full 전후·provider status·실제 요청 결과·원시 Supervisor 로그를 기록. L7 upstream 관측이 불가능하면 그 부분은 `NOT_RUN`/`DECISION_ONLY`로 둔다.
- 실행 전 환경: 이전 `oslab-*` 4개와 `sregym-*` 4개가 동작 중. 18080 Gateway 프로세스 없음. 격리 상태 디렉터리 `local/openshell-h2-effective-20261124/`에만 인증서·DB를 둔다.
