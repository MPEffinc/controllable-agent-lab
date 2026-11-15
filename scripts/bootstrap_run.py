#!/usr/bin/env python3
"""Run one reviewed local command with secrets removed and persistent evidence."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--name', required=True)
    p.add_argument('--cwd', default=str(ROOT))
    p.add_argument('--timeout', type=int, default=600)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    if not command or '/' in a.name or '..' in a.name:
        p.error('provide a simple unique name and command after --')
    output = ROOT / 'results/setup/bootstrap-20261114' / a.name
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.with_suffix('.json').exists() or output.with_suffix('.log').exists():
        p.error('evidence already exists; use a new name')
    env = {k: v for k, v in os.environ.items()
           if not any(s in k.upper() for s in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'CREDENTIAL'))}
    env.update(PYTHONUNBUFFERED='1', WANDB_MODE='disabled', HF_HUB_OFFLINE='1',
               PYTHON_DOTENV_DISABLED='1', AWS_EC2_METADATA_DISABLED='true',
               UV_CACHE_DIR=str(ROOT / '.cache/bootstrap-uv'))
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    t = time.monotonic()
    with output.with_suffix('.log').open('w') as log:
        log.write(f'UTC start: {start}\nCWD: {a.cwd}\nCommand: {shlex.join(command)}\n')
        log.flush()
        try:
            process = subprocess.Popen(command, cwd=a.cwd, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                # A parent may exit before children which ignored SIGTERM.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                log.write('\nTIMEOUT\n')
                code = 124
        except OSError as e:
            log.write(f'\n{type(e).__name__}: {e}\n')
            code = 127
        log.write(f'\nEXIT_CODE={code}\n')
    metadata = dict(name=a.name, cwd=a.cwd, command=command, start_utc=start,
                    end_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                    duration_seconds=round(time.monotonic()-t, 3), exit_code=code,
                    credential_env_removed=True, log=str(output.with_suffix('.log').relative_to(ROOT)))
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata))
    return code

if __name__ == '__main__':
    sys.exit(main())
