# Images, Audio, Moderation — 独立 API 场景

## 文生图 — RubyLLM.paint

官方：https://rubyllm.com/images/

```ruby
image = RubyLLM.paint("a sunset over mountains in watercolor style")
# => 返回 image 对象，含 url / base64 等（视 provider）
```

场景：营销配图、原型示意 — **非** Chat 附件流程。

## 语音转文字 — RubyLLM.transcribe

官方：https://rubyllm.com/audio/

```ruby
text = RubyLLM.transcribe("meeting.wav")
# 或本地路径 / URL
```

场景：会议摘要前置、用户语音输入。大文件注意超时 — 调 `config.request_timeout`。

也可在 Chat 内：`chat.ask "Summarize", with: "audio.mp3"`（模型需支持 audio input）。

## 内容审核 — RubyLLM.moderate

官方：https://rubyllm.com/moderation/

```ruby
result = RubyLLM.moderate("user generated content")
# 检查 flagged categories
```

场景：UGC 发布前、Chat 用户输入 gate。审核失败应**确定性拦截**，不只靠模型自觉。

## Provider 差异

| API | 常见 Provider |
|-----|---------------|
| paint | OpenAI DALL-E, 部分 OpenRouter |
| transcribe | OpenAI Whisper |
| moderate | OpenAI Moderation |

OpenAI 兼容网关未必支持全部 — 调用前确认或 graceful degrade。

## 与多模态 Chat 的区别

| 方式 | 何时用 |
|------|--------|
| `ask(..., with: file)` | 模型同时理解文件内容并回答 |
| `transcribe` | 只要文本 transcript |
| `paint` | 生成新图像 |
| `moderate` | 分类/安全标签 |

## 反模式

- ❌ 用 `paint` 生成含精确 UI 的 production 资产 — 需设计稿流程
- ❌ 跳过 moderate 直接展示 UGC
- ❌ transcribe 结果不存 audit log（合规场景）
