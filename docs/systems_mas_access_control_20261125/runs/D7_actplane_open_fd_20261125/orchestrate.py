import json
import subprocess
import time
from pathlib import Path

ROOT = Path('/work')
(ROOT / 'forbidden').write_text('baseline\n')
(ROOT / 'allowed').write_text('baseline\n')
child = subprocess.Popen(['/usr/local/bin/python3.12', '/work/agent.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
for _ in range(200):
    if (ROOT / 'ready').exists():
        break
    time.sleep(0.05)
else:
    raise TimeoutError('agent did not preopen file')

with (ROOT / 'loader.log').open('w') as log:
    loader = subprocess.Popen(['/usr/local/bin/actplane-process', '--config', '/work/policy.bin', '--seed-pid', str(child.pid), '--seed-label', '1'], stdout=log, stderr=subprocess.STDOUT)
    for _ in range(200):
        time.sleep(0.05)
        if 'ActPlane: ready' in (ROOT / 'loader.log').read_text():
            break
        if loader.poll() is not None:
            break
    ready = 'ActPlane: ready' in (ROOT / 'loader.log').read_text()
    (ROOT / 'go').write_text('go\n')
    child_out, child_err = child.communicate(timeout=15)
    time.sleep(0.3)
    loader.terminate()
    try:
        loader.wait(timeout=3)
    except subprocess.TimeoutExpired:
        loader.kill()
    result = {'loader_ready': ready, 'agent_exit': child.returncode,
              'agent_stdout': child_out, 'agent_stderr': child_err,
              'forbidden_content': (ROOT / 'forbidden').read_text(),
              'allowed_content': (ROOT / 'allowed').read_text()}
    (ROOT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
