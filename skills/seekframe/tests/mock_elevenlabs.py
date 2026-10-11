"""Stand-in for the ElevenLabs API so eleven.py can be tested without a key or credits.

python3 mock_elevenlabs.py PORT CALLS_LOG [free|paid]
"""
import base64
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT, LOG = int(sys.argv[1]), sys.argv[2]
TIER = sys.argv[3] if len(sys.argv) > 3 else 'paid'
EN, NL = {'language_id': 'en'}, {'language_id': 'nl'}
MODELS = [
    {'model_id': 'eleven_multilingual_v2', 'can_do_text_to_speech': True, 'languages': [EN, NL], 'model_rates': {'character_cost_multiplier': 1.0}},
    {'model_id': 'eleven_flash_v2', 'can_do_text_to_speech': True, 'languages': [EN], 'model_rates': {'character_cost_multiplier': 0.5}},
    {'model_id': 'eleven_flash_v2_5', 'can_do_text_to_speech': True, 'languages': [EN, NL], 'model_rates': {'character_cost_multiplier': 0.5}},
    {'model_id': 'eleven_english_sts_v2', 'can_do_text_to_speech': False},
]
VOICES = {'VOICE_EN': 'premade', 'VOICE_NL': 'professional'}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body)

    def authorised(self):
        if self.headers.get('xi-api-key') == 'test-key':
            return True
        self.reply({'detail': 'unauthorized'}, 401)
        return False

    def do_GET(self):
        if not self.authorised():
            return
        if self.path == '/v1/user/subscription':
            return self.reply({'tier': 'free' if TIER == 'free' else 'starter', 'status': 'active', 'character_count': 1000, 'character_limit': 10000})
        if self.path == '/v1/models':
            return self.reply(MODELS)
        if self.path.startswith('/v2/voices'):
            return self.reply({'voices': [{'voice_id': v, 'name': v, 'category': c, 'labels': {}} for v, c in VOICES.items()]})
        m = re.match(r'^/v1/voices/([^/?]+)', self.path)
        if m and m.group(1) in VOICES:
            return self.reply({'voice_id': m.group(1), 'name': m.group(1), 'category': VOICES[m.group(1)]})
        self.reply({'detail': 'not found'}, 404)

    def do_POST(self):
        if not self.authorised():
            return
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        with open(LOG, 'a') as f:
            f.write(json.dumps({'path': self.path, 'body': body}) + '\n')
        m = re.match(r'^/v1/text-to-speech/([^/]+)/with-timestamps', self.path)
        if not m:
            return self.reply({'detail': 'bad path'}, 404)
        if TIER == 'free' and VOICES.get(m.group(1)) != 'premade':
            return self.reply({'detail': {'code': 'paid_plan_required'}}, 402)
        text = body['text']
        starts = [0.15 + i * 0.065 for i in range(len(text))]
        self.reply({'audio_base64': base64.b64encode(b'ID3' + text.encode()).decode(),
                    'alignment': {'characters': list(text), 'character_start_times_seconds': starts, 'character_end_times_seconds': [t + 0.06 for t in starts]}})


HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
