#!/usr/bin/env python3
"""语音识别微服务 - 接收音频文件，返回文字"""
import sys, json, tempfile, os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8090

class ASRHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/asr':
            self.send_error(404)
            return
        
        length = int(self.headers.get('Content-Length', 0))
        audio_data = self.rfile.read(length)
        
        if len(audio_data) < 1000:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'text': ''}).encode())
            return
        
        # 保存临时文件
        tmp = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        tmp.write(audio_data)
        tmp.close()
        
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel('tiny', device='cpu', compute_type='int8')
            segments, info = model.transcribe(tmp.name, language='zh', beam_size=5)
            text = ' '.join([s.text for s in segments])
            os.unlink(tmp.name)
        except Exception as e:
            text = ''
            try: os.unlink(tmp.name)
            except: pass
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'text': text.strip()}, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        print(f'ASR: {args[0]}')

if __name__ == '__main__':
    print(f'🎤 Whisper ASR service on port {PORT}')
    HTTPServer(('0.0.0.0', PORT), ASRHandler).serve_forever()
