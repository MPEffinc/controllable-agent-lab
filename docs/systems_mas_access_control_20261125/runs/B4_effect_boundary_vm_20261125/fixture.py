#!/usr/bin/env python3
"""B4 research fixture. Only the optional OS hook is original ActPlane."""
import argparse
import http.server
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path('/work')
DB = ROOT / 'service.sqlite'
PORT = 18441
PYTHON = '/usr/local/bin/python3.12'


def db_value():
    with sqlite3.connect(DB) as conn:
        return dict(conn.execute('SELECT key,value FROM records'))


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        mode = self.server.mode
        started = time.monotonic_ns()
        if mode in ('service', 'combined') and not (body['task'] == 'A' and body['key'] == 'A' and (ROOT / 'grant').read_text().strip() == '1'):
            status, decision = 403, 'service_deny'
        else:
            with sqlite3.connect(DB) as conn:
                conn.execute('UPDATE records SET value=value+1 WHERE key=?', (body['key'],))
            status, decision = 200, 'committed'
        response = {'decision': decision, 'duration_ns': time.monotonic_ns() - started}
        out = json.dumps(response).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


def serve(mode):
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    server.mode = mode
    server.serve_forever()


def client(mode, key, direct):
    if direct:
        try:
            fd = os.open(DB, os.O_WRONLY)
            os.close(fd)
            direct_result = 'opened'
        except OSError as exc:
            direct_result = f'{type(exc).__name__}:{exc.errno}'
    else:
        direct_result = None
    started = time.monotonic_ns()
    if mode == 'preflight':
        result = {'decision': 'preflight_deny_reachable_B'}
    elif mode == 'dispatch' and key != 'A':
        result = {'decision': 'dispatch_deny'}
    else:
        body = json.dumps({'task': 'A', 'key': key}).encode()
        request = urllib.request.Request(f'http://127.0.0.1:{PORT}/write', data=body, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                result = {'status': response.status, **json.load(response)}
        except urllib.error.HTTPError as exc:
            result = {'status': exc.code, **json.load(exc)}
    result.update({'request': {'task': 'A', 'key': key}, 'direct_db_open': direct_result, 'elapsed_ns': time.monotonic_ns() - started})
    print(json.dumps(result), flush=True)


def run_arm(mode, key, os_policy):
    DB.unlink(missing_ok=True)
    with sqlite3.connect(DB) as conn:
        conn.execute('CREATE TABLE records(key TEXT PRIMARY KEY,value INTEGER)')
        conn.executemany('INSERT INTO records VALUES (?,0)', [('A',), ('B',)])
    (ROOT / 'grant').write_text('1')
    before = db_value()
    server_log = open(ROOT / f'{mode}_{key}.server.log', 'w')
    server = subprocess.Popen([PYTHON, __file__, 'serve', mode], stdout=server_log, stderr=subprocess.STDOUT)
    time.sleep(0.2)
    direct = int(os_policy)
    loader = None
    loader_log = None
    if os_policy:
        # A stopped child is the seed subject. The unlabelled service and
        # orchestrator stay outside the agent's OS authority.
        child = subprocess.Popen(['/bin/bash', '-c', f'kill -STOP $$; exec {PYTHON} {__file__} client {mode} {key} {direct}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.1)
        loader_log = open(ROOT / f'{mode}_{key}.loader.log', 'w')
        loader = subprocess.Popen(['/usr/local/bin/actplane-process', '--config', '/work/policy.bin', '--seed-pid', str(child.pid), '--seed-label', '1'], stdout=loader_log, stderr=subprocess.STDOUT)
        for _ in range(100):
            time.sleep(0.1)
            if 'ActPlane: ready' in (ROOT / f'{mode}_{key}.loader.log').read_text():
                break
            if loader.poll() is not None:
                break
        ready = 'ActPlane: ready' in (ROOT / f'{mode}_{key}.loader.log').read_text()
        os.kill(child.pid, signal.SIGCONT)
    else:
        child = subprocess.Popen([PYTHON, __file__, 'client', mode, key, str(direct)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ready = None
    stdout, stderr = child.communicate(timeout=15)
    if loader:
        loader.terminate()
        try:
            loader.wait(timeout=3)
        except subprocess.TimeoutExpired:
            loader.kill()
        loader_log.close()
    server.terminate()
    server.wait(timeout=3)
    server_log.close()
    return {'mode': mode, 'key': key, 'os_ready': ready, 'before': before, 'after': db_value(), 'client_exit': child.returncode, 'client_stdout': stdout.strip(), 'client_stderr': stderr.strip()}


def run_all():
    rows = []
    for mode in ('none', 'preflight', 'dispatch', 'os', 'service', 'combined'):
        for key in ('A', 'B'):
            row = run_arm(mode, key, mode in ('os', 'combined'))
            rows.append(row)
            print(json.dumps(row), flush=True)
            if row['client_exit'] or row['os_ready'] is False:
                print('FAIL_CLOSED: incomplete arm', file=sys.stderr, flush=True)
    (ROOT / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['serve', 'client', 'all'])
    parser.add_argument('mode', nargs='?')
    parser.add_argument('key', nargs='?')
    parser.add_argument('direct', nargs='?', type=int, default=0)
    args = parser.parse_args()
    if args.command == 'serve':
        serve(args.mode)
    elif args.command == 'client':
        client(args.mode, args.key, args.direct)
    else:
        run_all()
