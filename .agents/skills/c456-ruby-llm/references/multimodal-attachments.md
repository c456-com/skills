# Multimodal — 多模态附件场景

官方：https://rubyllm.com/chat/（Multi-modal 节）

## 场景 A：单文件问答

```ruby
chat = RubyLLM.chat(model: "gpt-4o")  # 或 claude-sonnet-4, gemini-2.5-flash

chat.ask "Describe this logo", with: "path/to/logo.png"
chat.ask "Summarize this paper", with: "report.pdf"
chat.ask "What happens in this video?", with: "demo.mp4"
chat.ask "Transcribe intent", with: "meeting.wav"
```

URL 也支持：

```ruby
chat.ask "What architecture?", with: "https://example.com/photo.jpg"
```

## 场景 B：多文件一次分析

```ruby
chat.ask "Compare these deliverables", with: [
  "diagram.png",
  "report.pdf",
  "notes.txt",
  "recording.mp3"
]
```

RubyLLM 用 Marcel 自动检测 MIME；无需手动指定类型。

## 场景 C：选模型（能力矩阵）

| 模态 | 常见模型 |
|------|----------|
| 图片 | gpt-4o, claude-sonnet-4, gemini-2.5-flash |
| PDF | claude-sonnet-4, gemini |
| 视频 | gemini-2.5-flash |
| 音频（chat 内） | gpt-4o-audio-preview |

查 registry：`RubyLLM.models.select { |m| m.supports?(:vision) }`

## 场景 D：独立 API（非 chat 附件）

| 任务 | API |
|------|-----|
| 文生图 | `RubyLLM.paint("watercolor sunset")` |
| 语音转文字 | `RubyLLM.transcribe("meeting.wav")` |
| 内容审核 | `RubyLLM.moderate("user text")` |

详见 [images-audio-moderation.md](images-audio-moderation.md)

## 场景 E：Rails 持久化 + 附件

```ruby
chat = Chat.find(id)
chat.ask "What's in this file?", with: "storage/report.pdf"
# acts_as_chat 持久化 messages；附件处理由 gem 编码进 message
```

## 反模式

- ❌ 把 PDF 全文读入 prompt 字符串 — 用 `with:` 让 gem 处理
- ❌ vision 模型未验证就上线 — 先查 `Model#supports?`
- ❌ 用户上传未做大小/类型限制 — Controller 层校验
