#!/usr/bin/env python3
"""TTS 微服务 - 文字转语音 MP3"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess, tempfile, os, urllib.parse

PORT = 8091

class TTSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith('/tts'):
            self.send_error(404)
            return
        
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        text = params.get('text', [''])[0]
        voice = params.get('voice', ['zh-CN-XiaoxiaoNeural'])[0]
        
        if not text:
            self.send_error(400, 'Missing text')
            return

        try:
            tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tmp.close()
            
            subprocess.run([
                'edge-tts', '--text', text,
                '--voice', voice,
                '--write-media', tmp.name
            ], capture_output=True, timeout=10)
            
            with open(tmp.name, 'rb') as f:
                data = f.read()
            os.unlink(tmp.name)
            
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            print(f'TTS Error: {e}')
            self.send_error(500)

    def log_message(self, format, *args):
        print(f'TTS: {args[0]}')

if __name__ == '__main__':
    print(f'🔊 Edge TTS service on port {PORT}')
    HTTPServer(('0.0.0.0', PORT), TTSHandler).serve_forever()
