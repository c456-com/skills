#!/usr/bin/env python3
"""Identity-persistence oracle for CamoFox (server-side session authority).

Identity is NOT "cookie present" — it is "cookie value maps to a live server-side
session record". That makes the judge falsifiable: a stale/garbled restore shows
as authenticated:false even when the cookie string still arrives.

Endpoints
  GET /login?u=<name>        mint a session, set HttpOnly probe_sid + probe_token,
                             set localStorage ls_marker (page-rendered), show sid
  GET /who                   JSON authority: authenticated, sid, localStorage not visible here
  GET /lsread                READ-ONLY page: renders existing localStorage ls_marker (sets nothing)
  GET /idb-set               page: writes a token into IndexedDB (renders it for confirmation)
  GET /idb-read              READ-ONLY page: reads the IndexedDB token, renders status
  GET /logout                destroy the server-side session (cookie stays in browser)
"""
import json
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

SESSIONS = {}          # sid -> {"user":..., "issued":...}
LOCK = threading.Lock()

# Page that only READS localStorage (never writes) — so a hit proves restore, not self-fill.
LS_READ = b"""<!doctype html><html><head><meta charset=utf-8><title>lsread</title></head>
<body><pre id=out>LS_ABSENT</pre><script>
var v = localStorage.getItem('ls_marker');
document.getElementById('out').textContent = v === null ? 'LS_ABSENT' : v;
</script></body></html>"""

# Page that writes localStorage then renders it
LS_WRITE = b"""<!doctype html><html><head><meta charset=utf-8><title>lswrite</title></head>
<body><pre id=out>pending</pre><script>
localStorage.setItem('ls_marker', 'LS_FROM_LOGIN');
document.getElementById('out').textContent = localStorage.getItem('ls_marker');
</script></body></html>"""

# IndexedDB write page
IDB_WRITE = b"""<!doctype html><html><head><meta charset=utf-8><title>idb-set</title></head>
<body><pre id=out>IDB_PENDING</pre><script>
var r = indexedDB.open('idtest', 1);
r.onupgradeneeded = function (e) {
  var d = e.target.result;
  if (!d.objectStoreNames.contains('kv')) d.createObjectStore('kv');
};
r.onsuccess = function (e) {
  var d = e.target.result;
  var tx = d.transaction('kv', 'readwrite');
  tx.objectStore('kv').put('IDB_TOKEN_777', 'probe');
  tx.oncomplete = function () { document.getElementById('out').textContent = 'IDB_WROTE'; };
  tx.onerror = function () { document.getElementById('out').textContent = 'IDB_WRITE_FAILED'; };
};
r.onerror = function () { document.getElementById('out').textContent = 'IDB_OPEN_FAILED'; };
</script></body></html>"""

# IndexedDB read-only page
IDB_READ = b"""<!doctype html><html><head><meta charset=utf-8><title>idb-read</title></head>
<body><pre id=out>IDB_PENDING</pre><script>
var r = indexedDB.open('idtest', 1);
r.onupgradeneeded = function (e) {
  var d = e.target.result;
  if (!d.objectStoreNames.contains('kv')) d.createObjectStore('kv');
};
r.onsuccess = function (e) {
  var d = e.target.result;
  var tx = d.transaction('kv', 'readonly');
  var q = tx.objectStore('kv').get('probe');
  q.onsuccess = function () {
    var v = q.result;
    document.getElementById('out').textContent = v === undefined ? 'IDB_ABSENT' : v;
  };
  q.onerror = function () { document.getElementById('out').textContent = 'IDB_READ_FAILED'; };
};
r.onerror = function () { document.getElementById('out').textContent = 'IDB_OPEN_FAILED'; };
</script></body></html>"""

PLAIN = b'<!doctype html><html><body>ok</body></html>'


class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'   # no keep-alive: one connection per request
    timeout = 10
    daemon_threads = True
    disable_nagle_algorithm = True

    def _send(self, body, ctype='application/json', cookies=None):
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        for c in cookies or []:
            self.send_header('Set-Cookie', c)
        self.end_headers()
        self.wfile.write(body)

    def _cookies(self):
        raw = self.headers.get('Cookie') or ''
        out = {}
        for part in raw.split(';'):
            if '=' in part:
                k, v = part.strip().split('=', 1)
                out[k] = v
        return out

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        ck = self._cookies()
        sid = ck.get('probe_sid')

        if u.path == '/login':
            user = (q.get('u') or ['tester'])[0]
            with LOCK:
                new_sid = 'sid-' + secrets.token_hex(6)
                SESSIONS[new_sid] = {'user': user, 'issued': __import__('time').time()}
            self._send(LS_WRITE, 'text/html; charset=utf-8', [
                f'probe_sid={new_sid}; Path=/; Max-Age=86400; HttpOnly; SameSite=Lax',
                'probe_token=PROBE_VALUE_12345; Path=/; Max-Age=86400; HttpOnly; SameSite=Lax',
            ])
        elif u.path == '/who':
            with LOCK:
                rec = SESSIONS.get(sid) if sid else None
            self._send(json.dumps({
                'authenticated': rec is not None,
                'user': rec['user'] if rec else None,
                'sid_presented': sid,
                'cookie_names': sorted(ck.keys()),
                'token_ok': ck.get('probe_token') == 'PROBE_VALUE_12345',
                'live_sessions': len(SESSIONS),
            }, ensure_ascii=False).encode())
        elif u.path == '/lsread':
            self._send(LS_READ, 'text/html; charset=utf-8')
        elif u.path == '/idb-set':
            self._send(IDB_WRITE, 'text/html; charset=utf-8')
        elif u.path == '/idb-read':
            self._send(IDB_READ, 'text/html; charset=utf-8')
        elif u.path == '/logout':
            with LOCK:
                SESSIONS.pop(sid, None)
            self._send(PLAIN, 'text/html; charset=utf-8')
        elif u.path == '/status':
            self._send(json.dumps({'live_sessions': len(SESSIONS), 'sids': list(SESSIONS)}).encode())
        else:
            self._send(b'{"error":"not found"}')

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    print(f'oracle on http://127.0.0.1:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
