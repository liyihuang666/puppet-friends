# 🎭 新新 & 善善 — 闽南布偶戏服装设计 AI 互动系统

幼儿园大班社会领域教学互动工具。两位布偶小伙伴（🐸 新新 & 🦁 善善）陪小朋友一起设计闽南布偶戏服装，通过语音或文字对话。

## ✨ 功能

- 🎤 **语音输入** — 按住说话，自动转文字
- 💬 **AI 对话** — 新新（活泼好奇）和善善（温柔善良）各有性格
- 🔊 **语音朗读** — AI 回复用童声读出
- 🎨 **满屏展示** — 适配 Windows 一体机大屏

## 🚀 快速开始

### 方式一：直接打开（最简单）

1. 替换 `index.html` 中的 `YOUR_SILICONFLOW_API_KEY` 为你的 [硅基流动 API Key](https://siliconflow.cn)
2. 在 Windows 一体机上用 Chrome/Edge 浏览器打开 `index.html`
3. 大功告成！

### 方式二：带后端代理（推荐部署）

```bash
# 1. 设置 API Key
export SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxx

# 2. 启动
node server.js

# 3. 打开浏览器访问 http://localhost:3000
```

后端代理模式下，API Key 不会暴露在前端代码中。

## 🎭 角色设定

| 角色 | 名字 | 性格 | 特点 |
|------|------|------|------|
| 🐸 绿色青蛙 | 新新 | 活泼好奇 | 喜欢问小朋友问题，讨论颜色花纹面料 |
| 🦁 棕色狮子 | 善善 | 温柔善良 | 喜欢夸小朋友，给他们好建议 |

## 🛠 技术栈

- **ASR（语音识别）**: 硅基流动 SenseVoiceSmall
- **LLM（大模型）**: DeepSeek-V3
- **TTS（语音合成）**: 硅基流动 CosyVoice2

## 📁 文件结构

```
puppet-friends/
├── index.html      # 前端页面（主要文件）
├── server.js       # 后端代理（可选）
├── package.json    # 项目信息
└── img/
    ├── xinxin.jpg  # 新新角色图
    └── shanshan.jpg # 善善角色图
```

## 🖥️ 教室部署

1. 在一体机上安装 Chrome 浏览器
2. 用 HDMI/VGA 连接大屏
3. 浏览器全屏模式打开页面（F11）
4. 连接麦克风/摄像头（用于语音输入）
5. 即可开始互动

---

Made with ❤️ for the little designers 🎨
