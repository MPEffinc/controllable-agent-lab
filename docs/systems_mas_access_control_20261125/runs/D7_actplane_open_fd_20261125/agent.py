import json
import os
import time
from pathlib import Path

ROOT = Path('/work')
fd = os.open(ROOT / 'forbidden', os.O_WRONLY | os.O_APPEND)
(ROOT / 'ready').write_text(str(os.getpid()))
for _ in range(200):
    if (ROOT / 'go').exists():
        break
    time.sleep(0.05)
else:
    raise TimeoutError('loader did not signal go')

result = {'pid': os.getpid()}
try:
    result['preopened_write_bytes'] = os.write(fd, b'preopened\n')
    result['preopened_write_errno'] = None
except OSError as exc:
    result['preopened_write_bytes'] = 0
    result['preopened_write_errno'] = exc.errno
os.close(fd)
try:
    newfd = os.open(ROOT / 'forbidden', os.O_WRONLY | os.O_APPEND)
    result['new_open_errno'] = None
    os.close(newfd)
except OSError as exc:
    result['new_open_errno'] = exc.errno
try:
    (ROOT / 'allowed').write_text('normal\n')
    result['allowed_write_errno'] = None
except OSError as exc:
    result['allowed_write_errno'] = exc.errno
print(json.dumps(result), flush=True)
