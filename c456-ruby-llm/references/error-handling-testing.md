# Error Handling & Testing

官方：https://rubyllm.com/error-handling/

## 错误层次

```ruby
RubyLLM::Error                    # 基类
RubyLLM::UnauthorizedError        # 401
RubyLLM::RateLimitError           # 429
RubyLLM::ContextLengthExceededError
RubyLLM::ServiceUnavailableError  # 502/503/504
RubyLLM::ConfigurationError
RubyLLM::ModelNotFoundError
```

## 场景 A：分层 rescue

```ruby
begin
  RubyLLM.chat.ask(prompt)
rescue RubyLLM::RateLimitError
  sleep 2 && retry
rescue RubyLLM::ContextLengthExceededError
  truncate_and_retry
rescue RubyLLM::UnauthorizedError
  notify_ops "API key invalid"
rescue RubyLLM::Error => e
  Rails.logger.error("LLM: #{e.message}")
  raise MyApp::LlmError, e.message
end
```

## 场景 B：瞬态错误重试（c456-aio）

```ruby
TRANSIENT = /SSL|EOF|timeout|429|502|503|504|Faraday::/i

def with_retries
  attempts = ENV.fetch("AIO_LLM_RETRIES", "3").to_i
  try = 0
  begin
    try += 1
    yield
  rescue StandardError => e
    raise unless try < attempts && e.message.match?(TRANSIENT)
    sleep(0.35 * try)
    retry
  end
end
```

## 场景 C：Tool 内错误

```ruby
def execute(query:)
  ...
rescue StandardError => e
  { error: e.message }  # 模型可调整
end
```

## 场景 D：测试 stub 策略（c456-aio）

### stub 触发条件

```ruby
def stub_mode?
  case ENV["AIO_LLM_STUB"]
  when "1" then true
  when "0" then false
  else
    Rails.env.test? || (@api_key.blank? && Rails.env.development?)
  end
end
```

### 薄 façade 统一入口

```ruby
# 业务只调 LlmClient，测试 stub LlmClient 或 ENV
class LlmClient
  def chat(prompt)
    return stub_reply(prompt) if stub_mode?
    build_chat.ask(prompt.to_s)
  end

  def chat_json(system:, user:)
    return stub_json_reply if stub_mode?
    # ...
  end

  def chat_stream(prompt)
    if stub_mode?
      text = stub_reply(prompt)[:text]
      yield fake_chunks(text) if block_given?
      return text
    end
    # real streaming
  end
end
```

### Minitest 示例

```ruby
test "chat_json stub returns expected keys" do
  result = Aio::LlmClient.new.chat_json(system: "s", user: "u")
  assert result.is_a?(Hash)
  assert_includes result.keys, "identity"
end
```

### Controller 测试 stub Agent

```ruby
llm = Minitest::Mock.new
Aio::LlmClient.stub(:new, llm) do
  post research_path, params: { ... }
end
```

### 真实 HTTP

- `AIO_LLM_STUB=0` + VCR cassette
- 不进 CI 默认；manual smoke only

## 场景 E：CallLogger / 审计

c456-aio 记录每次调用：`kind`, `purpose`, `model`, `status`, `duration_ms`, `request/response`（注意 PII 裁剪）。

```ruby
CallLogger.record(
  kind: "llm",
  purpose: Current.ai_purpose || "chat",
  model: model,
  status: "ok",
  duration_ms: ms
)
```

## 场景 F：Streaming 错误

流中断时 rescue 在 block 外；已生成 partial 应持久化（SSE resume 场景）。

## 反模式

- ❌ 测试依赖真实 API key — CI  flaky + 费用
- ❌ stub 返回 `{}` 导致下游 NoMethodError — stub 形状与生产一致
- ❌ 吞掉 `RubyLLM::Error` 返回 nil — 显式 raise 或 Result 对象
