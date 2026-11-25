# 실행 명령·원본 고정

작업 디렉터리: `/home/cclab/controllable_agent`. 원본 `third_party/continuity` commit `59cfe60930d247d1890b366ded686c718020a11e`(원본 `git status --short` 비어 있음), 기존 `.venv` Python 3.11.17. 신규 설치·모델·유료 API 없음.

사전등록 [prereg.md](prereg.md)를 쓴 뒤 최초 3입력을 실행했다. W 대조의 동일 주체·resource를 유지하도록 seed를 바꾸는 과정에서 최초 `raw.json`을 한 번 덮어썼다. 최초 seed 222 스크립트와 출력은 `run_seed222_exploratory.py` / `raw_seed222_exploratory_reconstructed.json`으로 **결정적으로 재실행**했고, 재실행 출력 SHA-256 `c1157c6f...`가 최초 실행 직후 기록한 SHA-256과 일치한다. 최종 사전등록 3입력 스크립트는 `run_preregistered_3case.py`, 원시는 `raw_preregistered_3case.json`(동일 내용 `raw.json`)으로 보존했다. 추가 위임 대조는 [extension_prereg.md](extension_prereg.md)를 먼저 작성하고 `run.py` / `raw_extension_4case.json`으로 별도 실행했다.

```bash
third_party/continuity/.venv/bin/python docs/access_control_empirical_20261124/runs/M1_continuity_amount_20261125/run_preregistered_3case.py > docs/access_control_empirical_20261124/runs/M1_continuity_amount_20261125/raw_preregistered_3case.json
third_party/continuity/.venv/bin/python docs/access_control_empirical_20261124/runs/M1_continuity_amount_20261125/run.py > docs/access_control_empirical_20261124/runs/M1_continuity_amount_20261125/raw_extension_4case.json
```

최종 파일 SHA-256:

| 파일 | SHA-256 |
|---|---|
| `run_preregistered_3case.py` | `40cc621139b8b57651bac321b7c68e47d219cc0cde3ff2bf3970d029203a4acf` |
| `raw_preregistered_3case.json` | `3208420339b3d201fe0e922f9cb41dfdec00fa39ac2626e3f111d0ad3daafb8f` |
| `run.py` (4입력 추가 대조) | `37d9b4a67f803c88cbe4950a4845e55b36aebcfe3456143a664bdb9d57d28f29` |
| `raw_extension_4case.json` | `098be77232859757acedda483ddf3423f10182cf91767a8f1fb1ea99758869d7` |

모델 이름·temperature·seed: **모델 없음**; 생성 난수 없음. `seed=111`은 N/A/D의 scenario ID용이며 W는 `seed=12_610_111`로 principal/actor/resource/destination을 같게 하고 task/nonce를 별도로 만든다. `SimulatedWorld`·`NonceLedger`는 모든 입력에서 공유한다.
