const http = require('http');
const fs = require('fs');
const path = require('path');

// ========== 配置 ==========
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.SILICONFLOW_API_KEY || '';
const ASR_API = 'https://api.siliconflow.cn/v1/audio/transcriptions';
const TTS_API = 'https://api.siliconflow.cn/v1/audio/speech';
const LLM_API = 'https://api.siliconflow.cn/v1/chat/completions';

// ========== 人设 ==========
const PROMPTS = {
  xinxin: `你是"新新"，一只绿色的青蛙布偶，闽南布偶戏的服装设计师。你的性格活泼好奇，喜欢问小朋友问题。
说话用词要像跟五岁小朋友聊天一样简单亲切。你最喜欢和小朋友讨论布偶衣服的颜色、花纹、面料。
每次回复控制在2-3句话，简短有趣。记得用小朋友能理解的语言。`,
  shanshan: `你是"善善"，一只棕色的小狮子布偶，闽南布偶戏的服装设计师。你的性格温柔善良，喜欢鼓励小朋友。
说话用词要像跟五岁小朋友聊天一样简单亲切。你最喜欢夸小朋友的设计想法，给他们建议。
每次回复控制在2-3句话，简短有趣。记得用小朋友能理解的语言。`
};

// ========== MIME 类型 ==========
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.gif': 'image/gif',
  '.json': 'application/json',
  '.ico': 'image/x-icon'
};

// ========== 工具函数 ==========
function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function json(res, data, code = 200) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

function serveStatic(req, res) {
  let filePath = req.url === '/' ? '/index.html' : req.url;
  filePath = path.join(__dirname, filePath.replace(/\.\./g, ''));
  
  const ext = path.extname(filePath);
  const contentType = MIME[ext] || 'application/octet-stream';
  
  try {
    const data = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  } catch {
    res.writeHead(404);
    res.end('Not Found');
  }
}

// ========== API 处理 ==========
async function handleChat(req, res) {
  const body = readBody(req);
  const buf = await body;
  let data;
  try { data = JSON.parse(buf.toString()); } catch { return json(res, { error: 'Invalid JSON' }, 400); }
  
  const { character, message } = data;
  if (!character || !message) return json(res, { error: 'Missing character or message' }, 400);
  if (!PROMPTS[character]) return json(res, { error: 'Unknown character' }, 400);
  if (!API_KEY) return json(res, { error: 'API key not configured' }, 500);
  
  try {
    const llmRes = await fetch(LLM_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-ai/DeepSeek-V3',
        messages: [
          { role: 'system', content: PROMPTS[character] },
          { role: 'user', content: message }
        ],
        max_tokens: 200,
        temperature: 0.9
      })
    });
    
    const llmData = await llmRes.json();
    const reply = llmData.choices?.[0]?.message?.content || '嗯...让我想一想~';
    json(res, { reply, character });
  } catch (e) {
    console.error('LLM error:', e);
    json(res, { error: 'AI 回复失败' }, 500);
  }
}

async function handleTTS(req, res) {
  if (!API_KEY) return json(res, { error: 'API key not configured' }, 500);
  
  const body = readBody(req);
  const buf = await body;
  let data;
  try { data = JSON.parse(buf.toString()); } catch { return json(res, { error: 'Invalid JSON' }, 400); }
  
  const { text } = data;
  if (!text) return json(res, { error: 'Missing text' }, 400);
  
  try {
    const ttsRes = await fetch(TTS_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: 'FunAudioLLM/CosyVoice2-0.5B',
        input: text,
        voice: 'FunAudioLLM/CosyVoice2-0.5B:alex',
        response_format: 'mp3'
      })
    });
    
    const audioBuf = Buffer.from(await ttsRes.arrayBuffer());
    res.writeHead(200, { 'Content-Type': 'audio/mpeg' });
    res.end(audioBuf);
  } catch (e) {
    console.error('TTS error:', e);
    json(res, { error: 'TTS failed' }, 500);
  }
}

async function handleASR(req, res) {
  if (!API_KEY) return json(res, { error: 'API key not configured' }, 500);
  
  // 简单转发 multipart，前端也可以直接调
  json(res, { error: 'ASR via server not supported, use client-side direct call' }, 501);
}

// ========== 路由 ==========
const server = http.createServer(async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  if (req.method === 'POST' && url.pathname === '/api/chat') return handleChat(req, res);
  if (req.method === 'POST' && url.pathname === '/api/tts') return handleTTS(req, res);
  if (req.method === 'POST' && url.pathname === '/api/asr') return handleASR(req, res);
  
  serveStatic(req, res);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🎭 新新&善善互动系统已启动: http://localhost:${PORT}`);
  console.log(`   API Key 状态: ${API_KEY ? '✅ 已配置' : '❌ 未配置（请设置 SILICONFLOW_API_KEY 环境变量）'}`);
  console.log(`   端点: /api/chat  /api/tts  /api/asr`);
});
