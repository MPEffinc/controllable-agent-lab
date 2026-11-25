#!/usr/bin/env python3
"""Synthetic GET-only upstream; writes only request paths, never request headers."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LEDGER = Path(__file__).with_name("upstream-ledger.log")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        with LEDGER.open("a", encoding="utf-8") as output:
            output.write(self.path + "\n")
        body = b"synthetic-ok\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(format % args, flush=True)


ThreadingHTTPServer(("172.17.0.1", 18083), Handler).serve_forever()
