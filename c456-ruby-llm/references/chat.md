# Chat — 对话场景

官方：https://rubyllm.com/chat/

## 场景 A：一次性问答（脚本 / Rake / 探索）

```ruby
response = RubyLLM.chat.ask "Explain ActiveRecord callbacks in one paragraph"
puts response.content
```

无需 Agent 类；用完即弃。

## 场景 B：多轮对话（内存历史）

```ruby
chat = RubyLLM.chat(model: "claude-sonnet-4")
chat.with_instructions "You are a concise Rails mentor."

chat.ask "What is Zeitwerk?"
chat.ask "Give a concrete example in app/models"  # 自动带上文

chat.messages.each { |m| puts "[#{m.role}] #{m.content.to_s.truncate(80)}" }
```

## 场景 C：指定 Provider / 自定义网关

OpenAI 兼容网关（OpenCode Go、自建 vLLM 等）：

```ruby
ctx = RubyLLM.context do |config|
  config.openai_api_key = ENV["LLM_API_KEY"]
  config.openai_api_base = ENV["LLM_BASE_URL"]  # 含 /v1
  config.openai_use_system_role = true          # 部分网关必需
end

chat = ctx.chat(
  model: ENV.fetch("LLM_MODEL", "deepseek-v4-flash"),
  provider: :openai,
  assume_model_exists: true   # 跳过 registry 校验
)
```

## 场景 D：控制输出风格

```ruby
chat = RubyLLM.chat
  .with_temperature(0.2)           # 事实/JSON 偏低
  .with_instructions("Answer in Simplified Chinese.")
  .with_params(max_tokens: 2048)
```

| 任务 | 建议 temperature |
|------|------------------|
| 结构化抽取 / 分类 | 0.0–0.3 |
| 对话 / 解释 | 0.4–0.7 |
| 创意文案 | 0.8+ |

## 场景 E：从 Service 封装（c456 风格）

业务代码不直接散落 `RubyLLM.chat`，经薄 façade：

```ruby
# app/services/my_app/llm_client.rb — 模式见 references/c456-aio-patterns.md
client = MyApp::LlmClient.new
result = client.chat("prompt")
parsed = client.chat_json(system: "...", user: "...")
text   = client.chat_stream("prompt") { |chunk| broadcast(chunk) }
```

## 场景 F：事件钩子（调试 / 审计）

```ruby
chat.on_tool_call { |tc| Rails.logger.info("tool: #{tc.name}") }
chat.on_tool_result { |result| Rails.logger.info("result: #{result.inspect}") }
chat.on_new_message { |msg| ... }
```

## 反模式

- ❌ 每个 Controller action 里 `RubyLLM.chat` 裸调 — 难测、难换网关
- ❌ 把 system prompt 拼进 user 消息 — 用 `with_instructions`
- ❌ 非流式调用慢模型导致网关 60s 断连 — 改 `ask { |chunk| }` 收全文

## 延伸阅读

- 结构化 JSON → [schema-structured-output.md](schema-structured-output.md)
- 附件 → [multimodal-attachments.md](multimodal-attachments.md)
- 持久化 → [rails-integration.md](rails-integration.md)
