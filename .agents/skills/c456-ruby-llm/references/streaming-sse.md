# Streaming + SSE — 生产流式场景

官方：https://rubyllm.com/streaming/

## 场景 A：CLI / 脚本实时打印

```ruby
chat = RubyLLM.chat
full = chat.ask "Write a haiku about Ruby" do |chunk|
  print chunk.content
end
# full 为完整 Message；block 内为 RubyLLM::Chunk
```

## Chunk 字段（上游唯一分片模型）

| 字段 | 说明 |
|------|------|
| `content` | 文本片段（可为 nil） |
| `tool_calls` | 模型发起 tool 调用 |
| `thinking` | 扩展思考（reasoning 模型） |
| `role` | 流式一般为 `:assistant` |
| `input_tokens` / `output_tokens` | 常在**最后一个** chunk 才准确 |

**Tool 流**：文本 → `tool_calls` → 执行 Tool → 继续文本。前端必须展示 Tool 卡片，不能压成一条「处理中…」。

## 场景 B：Rails Job + 可 resume SSE（c456-aio 架构）

```
POST /chats/:id/messages     → 落库 user msg → enqueue ChatStreamJob → 202 + streamId
GET  /chats/:id/stream       → text/event-stream，支持 Last-Event-ID 续传
POST /chats/:id/stop         → 取消 Job（客户端断开 ≠ stop）
```

**原则**：

- 生成在 **Solid Queue Job** 内：`agent.ask { |chunk| buffer.write(encode(chunk)) }`
- Web **不**长时间占用 Puma 线程跑完整 Agent
- 断线只关订阅；Job 继续写缓冲；重连带 `Last-Event-ID` 重放

```ruby
# app/jobs/chat_stream_job.rb（示意）
class ChatStreamJob < ApplicationJob
  def perform(chat_id, stream_id)
    chat = Chat.find(chat_id)
    encoder = MyApp::ChatStreamEncoder.new(stream_id)

    chat.ask do |chunk|
      encoder.append!(chunk)  # Chunk → SSE JSON 帧 + 递增 id
    end
  ensure
    encoder.finish!
  end
end
```

Encoder 对照 [AI SDK Stream Protocol](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol) 手写，便于 React `useChat` + AI Elements。

## 场景 C：网关非流式超时 → 流式收全文

c456-aio `LlmClient#chat_streamed`：慢引擎非流式响应可能被网关 60s 切断，统一走：

```ruby
def chat_streamed(prompt)
  full = +""
  chat_stream(prompt) { |chunk| full << chunk.content.to_s if chunk.content }
  { text: full, model: @model }
end
```

## 场景 D：Turbo Streams（简单场景）

官方示例：`ChatStreamJob` 内 `chat.ask { |chunk| Turbo::StreamsChannel.broadcast_replace_to(...) }`  
适合 admin 内嵌 Chat UI；高并发产品仍推荐 Job + 缓冲 + resume。

## 场景 E：Sinatra SSE（最小示例）

```ruby
get "/stream" do
  content_type "text/event-stream"
  stream(:keep_open) do |out|
    RubyLLM.chat.ask(params[:q]) do |chunk|
      out << "data: #{chunk.content.to_json}\n\n" if chunk.content
    end
  end
end
```

## 禁止

- ❌ 第三方 `ai_stream` 等绕过 ruby_llm 的流协议 gem
- ❌ 直接拼厂商原始 SSE 当产品协议（丧失 Chunk 抽象）
- ❌ `ActionController::Live` 同步跑完千级并发 Agent
- ❌ 默认用 ActionCable 当唯一 token 流（双向长连留给 stop/语音等）

## 容量

压力来自 **并发活跃流/订阅**，不是会话总数。  
Web 短请求吞吐 ≈ `WEB_CONCURRENCY × RAILS_MAX_THREADS`；生成扩 Solid Queue workers。

## 测试 stub 流

```ruby
# LlmClient#chat_stream stub 模式示例
text = "stub response"
mid = [text.length / 2, 1].max
yield RubyLLM::Chunk.new(role: :assistant, content: text[0...mid])
yield RubyLLM::Chunk.new(role: :assistant, content: text[mid..])
```

见 [error-handling-testing.md](error-handling-testing.md)
