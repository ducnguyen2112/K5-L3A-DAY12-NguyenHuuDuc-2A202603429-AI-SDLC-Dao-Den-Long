"""Local-only web frontend; authoritative simulation is shared with headless."""
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from game.core import Game, TUNING

ROOT = Path(__file__).resolve().parent / 'web'

class Handler(BaseHTTPRequestHandler):
    game = Game(seed=12)

    def reply(self, code, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == '/api/state':
            return self.reply(200, {'snapshot': self.game.snapshot(), 'tuning': TUNING})
        path = (ROOT / self.path.split('?')[0].lstrip('/')).resolve()
        if self.path.split('?')[0] == '/':
            path = ROOT / 'index.html'
        if not path.is_relative_to(ROOT) or not path.is_file():
            self.send_error(404)
            return
        raw = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 <= length <= 16384:
                raise ValueError('Request too large')
            data = json.loads(self.rfile.read(length))
            if self.path == '/api/reset':
                type(self).game = Game(seed=12)
                return self.reply(200, {'snapshot': self.game.snapshot(), 'events': []})
            if self.path != '/api/step':
                return self.reply(404, {'error': 'Unknown route'})
            from game.core import validate_inputs
            patch = data.get('input', {})
            validate_inputs({'frames': [dict(patch, tick=0)]})
            steps = data.get('steps', 1)
            if type(steps) is not int or not 1 <= steps <= 12:
                raise ValueError('steps must be 1..12')
            events = []
            for i in range(steps):
                if self.game.state != 'playing':
                    break
                events.extend(self.game.step(patch if i == 0 else {}))
            self.reply(200, {'snapshot': self.game.snapshot(), 'events': events})
        except (ValueError, TypeError, KeyError) as exc:
            self.reply(400, {'error': str(exc)})

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = HTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Dao Den Long: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
