#!/usr/bin/env python3
"""一体化服务 - 静态文件 + chat API（通过 curl 调 DeepSeek）"""
import json, os, urllib.parse, time
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
HTML_DIR = '/var/www/puppet-friends'

with open('/tmp/ds_key.txt') as f:
    DS_KEY = f.read().strip()

MIME = {'.html': 'text/html; charset=utf-8', '.js': 'application/javascript',
        '.jpg': 'image/jpeg', '.png': 'image/png', '.css': 'text/css'}

class H(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        fp = os.path.join(HTML_DIR, 'index.html' if p in ('/', '') else p.lstrip('/'))
        ext = os.path.splitext(fp)[1].lower()
        try:
            with open(fp, 'rb') as f: data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', MIME.get(ext, 'application/octet-stream'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404)

    def do_POST(self):
        if self.path != '/chat':
            self.send_error(404); return
        
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        who = body.get('who', 'xinxin')
        text = body.get('text', '')
        if not text:
            self._json({'reply': ''}); return
        
        sys_p = '你是新新，绿色青蛙活泼好奇。闽南布偶服装设计师。对小朋友说话简单可爱。每次1-2句话。' if who == 'xinxin' else '你是善善，棕色狮子温柔善良。闽南布偶服装设计师。对小朋友说话简单可爱。每次1-2句话。'
        
        # 用 curl 调（验证过的方式）
        import subprocess
        payload = json.dumps({
            'model': 'deepseek-chat',
            'messages': [{'role': 'system', 'content': sys_p}, {'role': 'user', 'content': text}],
            'max_tokens': 150, 'temperature': 0.9
        })
        
        result = subprocess.run(
            ['curl', '-s', 'https://api.deepseek.com/v1/chat/completions',
             '-H', 'Content-Type: application/json',
             '-H', 'Authorization: Bearer ' + DS_KEY,
             '-d', payload],
            capture_output=True, text=True, timeout=15)
        
        try:
            data = json.loads(result.stdout)
            reply = data['choices'][0]['message']['content'] if 'choices' in data else '嗯...让我想一想~'
        except:
            reply = '嗯...让我想一想~'
        
        self._json({'reply': reply})

    def _json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(d, ensure_ascii=False).encode())

    def log_message(self, f, *a):
        print(f'[{time.strftime("%H:%M:%S")}] {a[0]}')

if __name__ == '__main__':
    print(f'🎭 http://0.0.0.0:{PORT}')
    HTTPServer(('0.0.0.0', PORT), H).serve_forever()
