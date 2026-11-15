#!/usr/bin/env python3
"""Record reviewed local R2 commands without overwriting prior evidence.

Same contract as scripts/r1_run.py (kept untouched for R1 reproducibility), but
evidence goes to results/r2/commands and the metadata also records the parent
commit and whether tracked files were dirty when the command ran.
"""
from __future__ import annotations
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


def git(*args):
    try:
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'UNKNOWN'


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--name', required=True)
    p.add_argument('--cwd', default=str(ROOT))
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    if not command or not a.name.replace('-', '').replace('_', '').isalnum():
        p.error('use a unique simple name and command after --')
    directory = ROOT / 'results/r2/commands'
    directory.mkdir(parents=True, exist_ok=True)
    meta = directory / f'{a.name}.json'
    log = directory / f'{a.name}.stdout.txt'
    if meta.exists() or log.exists():
        p.error('existing evidence; choose a new name')
    env = {k: v for k, v in os.environ.items() if not any(x in k.upper() for x in
           ('KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'CREDENTIAL'))}
    env.update(PYTHONUNBUFFERED='1', PYTHON_DOTENV_DISABLED='1', WANDB_MODE='disabled',
               HF_HUB_OFFLINE='1', AWS_EC2_METADATA_DISABLED='true',
               UV_CACHE_DIR=str(ROOT / '.cache/bootstrap-uv'))
    parent = git('rev-parse', 'HEAD')
    dirty = git('status', '--porcelain', '--untracked-files=no')
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    before = time.monotonic()
    with log.open('x') as stream:
        stream.write(f'UTC: {start}\nCWD: {a.cwd}\nCOMMAND: {shlex.join(command)}\n'
                     f'PARENT_COMMIT: {parent}\n')
        stream.flush()
        try:
            process = subprocess.Popen(command, cwd=a.cwd, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        pass
                    if sig == signal.SIGTERM:
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            pass
                process.wait()
                stream.write('\nTIMEOUT\n')
                code = 124
        except OSError as error:
            stream.write(f'\n{type(error).__name__}: {error}\n')
            code = 127
        stream.write(f'\nEXIT_CODE={code}\n')
    data = dict(name=a.name, command=command, cwd=a.cwd, start_utc=start,
                end_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                duration_seconds=round(time.monotonic() - before, 3), exit_code=code,
                log=str(log.relative_to(ROOT)), parent_commit=parent,
                tracked_files_dirty=bool(dirty), filtered_credential_env=True,
                note='Environment filtering only, not a network/OS sandbox')
    meta.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data))
    return code


if __name__ == '__main__':
    sys.exit(main())
