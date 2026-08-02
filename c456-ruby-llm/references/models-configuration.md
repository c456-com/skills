# Models, Configuration & Async

官方：https://rubyllm.com/configuration/ · https://rubyllm.com/models/ · https://rubyllm.com/async/

## 全局配置（initializer）

```ruby
# config/initializers/ruby_llm.rb
RubyLLM.configure do |config|
  config.openai_api_key = ENV["OPENAI_API_KEY"]
  config.anthropic_api_key = ENV["ANTHROPIC_API_KEY"]
  config.gemini_api_key = ENV["GEMINI_API_KEY"]

  config.default_model = ENV.fetch("LLM_MODEL", "gpt-4o-mini")
  config.request_timeout = 120
  config.logger = Rails.logger
  config.log_level = Rails.env.production? ? :info : :debug

  # OpenAI 兼容网关
  config.openai_api_base = ENV["LLM_BASE_URL"]
  config.openai_use_system_role = true
end
```

c456-aio 环境变量映射：

| ENV | 作用 |
|-----|------|
| `AIO_LLM_API_KEY` / `OPENAI_API_KEY` | API key |
| `AIO_LLM_BASE_URL` | 网关 base |
| `AIO_LLM_MODEL` | 默认模型 |
| `AIO_LLM_TIMEOUT` | 超时秒 |
| `AIO_LLM_STUB` | `1` 强制 stub / `0` 强制真实 |
| `AIO_LLM_RETRIES` | 瞬态错误重试 |
| `AIO_LLM_MAX_TOKENS` | max_tokens |
| `AIO_LLM_DISABLE_THINKING` | 部分网关 thinking 开关 |

## 多租户 / 单次覆盖 — RubyLLM.context

```ruby
ctx = RubyLLM.context do |config|
  config.openai_api_key = tenant.llm_api_key
end
chat = ctx.chat(model: "gpt-4o-mini")
```

不污染全局 `RubyLLM.configure`。

## 模型注册表

```bash
bin/rails ruby_llm:load_models
```

```ruby
RubyLLM.models.all
RubyLLM.models.find("gpt-4o")
model.supports?(:vision)
model.supports?(:function_calling)
model.input_price_per_million
```

`assume_model_exists: true` — 自定义网关模型未在 registry 时跳过校验。

## Extended Thinking

```ruby
chat.with_thinking(effort: :medium)  # 视 provider
# Chunk#thinking 在 streaming 中可见
```

OpenCode Go 等需 `thinking: { type: "disabled" }` — 见 c456-aio `provider_params`。

## Async（Fiber 并发）

官方：https://rubyllm.com/async/

```ruby
require "async"

Async do |task|
  a = task.async { RubyLLM.chat.ask("Q1") }
  b = task.async { RubyLLM.chat.ask("Q2") }
  [a.wait, b.wait]
end.wait
```

与 Workflow Parallel 模式配合；注意 API rate limit。

## Provider 列表

OpenAI, Anthropic, Gemini, Vertex, Bedrock, DeepSeek, Mistral, Ollama, OpenRouter, Perplexity, xAI, Azure, GPUStack, OpenAI-compatible

Ollama 本地：

```ruby
config.ollama_api_base = "http://localhost:11434/v1"
```

## 反模式

- ❌ 硬编码 model id 不查 registry — 升级时 breakage
- ❌ 生产 debug log 打 full prompt（PII）
- ❌ 全局 configure 写 tenant key — 用 context
