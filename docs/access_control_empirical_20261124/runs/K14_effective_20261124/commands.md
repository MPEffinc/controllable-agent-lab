# K14 v0.1.9 실제 CLI 순서 복원

아래는 2026-11-24 이번 세션에서 실행한 실질 명령의 argv 순서다. 경로는 `/home/cclab/controllable_agent` 기준이다. 인증서·DB는 무시되는 `local/openshell-h2-effective-20261124/`에만 저장했다. `GATEWAY`와 `CLI`는 공식 v0.1.9 릴리스 binary였다. 명령을 다시 실행하면 새 로컬 sandbox/Gateway가 생기므로 현재 결과 열람에는 실행할 필요가 없다.

```bash
RUN=docs/access_control_empirical_20261124/runs/K14_effective_20261124
LAB=/home/cclab/controllable_agent/local/openshell-h2-effective-20261124
CLI=local/openshell-20261124/releases/v0.1.9/openshell
export XDG_CONFIG_HOME="$LAB/cli-config"
export OPENSHELL_GATEWAY=h2eff

# 별도 세션에서 전경 Gateway. gateway.sh가 포트 18081, 고유 SQLite/mTLS를 사용.
bash "$RUN/gateway.sh" > "$RUN/gateway.log" 2>&1

# 두 번째 세션. 최초 gateway add는 OPENSHELL_LOCAL_TLS_DIR 누락으로 exit 1.
"$CLI" gateway add https://127.0.0.1:18081 --local --name h2eff
OPENSHELL_LOCAL_TLS_DIR="$LAB/gateway-state/tls" \
  "$CLI" gateway add https://127.0.0.1:18081 --local --name h2eff
"$CLI" status

# 초기 profile catalog는 빈 배열. 첫 create는 profile 미등록으로 exit 1.
"$CLI" profile list -o json
"$CLI" provider create --name h2pypi --type pypi
"$CLI" profile lint -f local/openshell-20261124/source-v0.1.9/providers/pypi.yaml
"$CLI" profile import -f local/openshell-20261124/source-v0.1.9/providers/pypi.yaml
"$CLI" provider create --name h2pypi --type pypi

"$CLI" sandbox create --name h2eff-01 --from busybox:1.36.1 \
  --cpu 0.5 --memory 512Mi --detach --no-auto-providers --timeout 120 \
  -- sh -c 'sleep 3600'

# 최초 -o yaml 시도는 해당 CLI가 json/table만 받으므로 exit 2. 이후 json 사용.
"$CLI" policy get h2eff-01 --base -o yaml
"$CLI" policy get h2eff-01 --base -o json > "$RUN/base-before.json"
"$CLI" policy get h2eff-01 --full -o json > "$RUN/full-before.json"
"$CLI" sandbox provider attach h2eff-01 h2pypi --wait --timeout 30 -o json > "$RUN/attach.json"
"$CLI" policy get h2eff-01 --base -o json > "$RUN/base-after.json"
"$CLI" policy get h2eff-01 --full -o json > "$RUN/full-after.json"
"$CLI" sandbox provider status h2eff-01 h2pypi -o json > "$RUN/provider-status.json"

# 별도 세션에서 synthetic upstream (172.17.0.1:18083).
python "$RUN/local_provider.py" > "$RUN/upstream.log" 2>&1

# 다시 CLI 세션. 각 policy set은 --wait로 실제 로드를 확인.
"$CLI" policy set h2eff-01 --policy "$RUN/audit.yaml" --wait --timeout 30
"$CLI" sandbox exec h2eff-01 --timeout 12 --no-login-shell -- \
  wget -T 5 -S -O - http://172.17.0.1:18083/blocked > "$RUN/audit-request.log" 2>&1
wc -l "$RUN/upstream-ledger.log" > "$RUN/ledger-before-enforce.txt"
"$CLI" policy set h2eff-01 --policy "$RUN/enforce.yaml" --wait --timeout 30
"$CLI" sandbox exec h2eff-01 --timeout 12 --no-login-shell -- \
  wget -T 5 -S -O - http://172.17.0.1:18083/blocked > "$RUN/enforce-blocked.log" 2>&1
"$CLI" sandbox exec h2eff-01 --timeout 12 --no-login-shell -- \
  wget -T 5 -S -O - http://172.17.0.1:18083/ok > "$RUN/enforce-allowed.log" 2>&1
"$CLI" policy get h2eff-01 --base -o json > "$RUN/base-final.json"
"$CLI" policy get h2eff-01 --full -o json > "$RUN/full-final.json"
"$CLI" logs h2eff-01 --since 10m --source sandbox > "$RUN/openshell-logs.txt" 2>&1
"$CLI" policy get h2eff-01 --rev 2 --full -o json > "$RUN/full-audit.json"
docker logs openshell-default--h2eff-01-262e9833-40f2-4046-8a5b-af8e7ec8ad5e-supervisor \
  > "$RUN/supervisor.log" 2>&1

# 이번 실험의 전용 자원만 삭제. provider/profile 삭제 후 Gateway와 upstream
# 프로세스 종료 및 포트 18081/18083 닫힘은 후속 정리에서 확인했다.
"$CLI" sandbox delete h2eff-01
"$CLI" provider delete h2pypi
"$CLI" profile delete pypi
```

`audit-request.log` exit 0, `enforce-blocked.log` exit 1, `enforce-allowed.log` exit 0이었다. 실패한 초기 명령은 보안 정책 결과가 아니며, 정상 재시도 전에 원인을 수정했다. 이 문서는 기록 보완용으로 작성했고 세션 중단 후 명령을 다시 실행하지 않았다.
