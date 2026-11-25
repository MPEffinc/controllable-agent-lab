# K14 OpenShell v0.1.9 동적 effective policy와 L7 audit/enforce 결과

[사전 등록](manifest.md)을 먼저 저장하고 공식 v0.1.9 소스 commit `ce58cf8e9b953281352d98a637e41616295b1318`의 릴리스 CLI/Gateway 및 Sandbox binary를 사용했다. 세부 코드 경로·정책 합성 전제는 [원문/소스 대조](../../deep_h2_effective.md). 유료 모델/API 호출 0, 외부 비용 USD 0. 로컬 synthetic upstream만 호출했다.

## 활성 구성과 전후 효과

| 조건 | 활성 정책·PEP | 원시 요청 | upstream ledger 변화 |
|---|---|---|---|
| provider attach | 별도 Gateway `127.0.0.1:18081`, sandbox `h2eff-01`, base network 0. `h2pypi` attach `--wait` 뒤 [receipt](attach.json) `ready`/`policy_active=true`; [full policy](full-after.json)에 `_provider_h2pypi` 추가, [base](base-after.json)는 network 0 | PyPI 호출은 **실행하지 않음** | 해당 없음 |
| L7 audit | [audit.yaml](audit.yaml): `/bin/wget`→`172.17.0.1:18083`, `GET /ok`만 rule 허용, `enforcement: audit`; policy version 2 [snapshot](full-audit.json) | [GET /blocked](audit-request.log) HTTP 200 | `/blocked` 추가 1 |
| L7 enforce | 같은 rule, [enforce.yaml](enforce.yaml): `enforcement: enforce`; policy version 3 [snapshot](full-final.json) | [GET /blocked](enforce-blocked.log) HTTP 403 | 추가 0 |
| 정상 대조 | 같은 enforce 정책 | [GET /ok](enforce-allowed.log) HTTP 200 | `/ok` 추가 1 |

[upstream 원시 ledger](upstream-ledger.log)는 `/blocked`와 `/ok` 한 줄씩이다. [Supervisor 로그](supervisor.log)는 provider attach 및 두 policy set의 `CONFIG:DETECTED`/`CONFIG:LOADED` 해시를 기록한다. audit 시 `/blocked`는 기본 shorthand OCSF에서 `HTTP:GET ALLOWED`로 표기됐다. 원본 OCSF JSON은 이 실험에서 수집하지 않았으므로 전체 telemetry에 위반 이유가 없다고 단정하지 않는다. 본 결과의 `effect`는 synthetic upstream에 HTTP 요청이 도달해 ledger에 기록된 사건이다.

## 재현성·정리

- 공식 이전 실험 binary SHA256: CLI `2db8e54f63feebe9f994efaf6004bbd45c55bc70ea455eda42fe82a0ea7c7e69`, Gateway `865e8c5ae15a599ca001d023efc137527ff8e102b0cccb90a85184a1c6e33978`, Sandbox `6c3afd40f40922c9c84be19460779c951b61c6c542aaa95e4c2c8a4b0e7f48c4`. 릴리스 archive의 공식 checksums는 `local/openshell-20261124/releases/v0.1.9/*checksums-sha256.txt`에 보존.
- Gateway 시작 스크립트 [gateway.sh](gateway.sh), synthetic upstream 코드 [local_provider.py](local_provider.py), 입력 정책 두 개, 전후 base/full JSON, attach receipt, 요청 원시 로그, Supervisor 로그를 보존했다. 실험 담당 세션이 사용량 한도로 종료되어 **중간 CLI subcommand의 정확한 argv 원문은 별도 파일에 기록되지 않았다**. 따라서 이 run은 raw policy/effect 근거는 있으나 명령 단위 재실행 기록이 불완전하다. 재실행 시 공식 CLI의 `profile import`, `provider create`, `sandbox provider attach`, `policy set`에 대해 저장된 v0.1.9 `--help`를 확인하고 정책 파일을 사용해야 한다.
- 담당 세션 종료 후 이 조사에서 생성한 Gateway PID `2957370`와 upstream PID `2962775`에만 `SIGTERM`을 보내고, 포트 `18081`/`18083`이 닫혔고 `h2eff*` 컨테이너가 없음을 확인했다. 기존 `oslab-*`/`sregym-*` 컨테이너는 그대로 있었다. 격리 DB/인증서와 원시 로그는 보존. 로그에서 명백한 key/token 문자열은 검사 시 발견되지 않았으나 전수 비밀 감사를 의미하지 않는다.

**판정:** 이 v0.1.9 설정에서 provider 규칙의 동적 적용과 enforce 차단/정상 통과는 `RESOLVED_IN_SCOPE`. 다른 provider의 모든 효과 경로, 사용자의 업무 의미, full telemetry의 의미 정확성은 `UNVERIFIED`.
