# Rails Integration — acts_as_chat 场景

官方：https://rubyllm.com/rails/

## 场景 A：全新 Rails 项目接入

```bash
bundle add ruby_llm
bin/rails generate ruby_llm:install
bin/rails db:migrate
bin/rails ruby_llm:load_models   # v1.13+ 填充 Model registry
```

可选 Chat UI：

```bash
bin/rails generate ruby_llm:chat_ui
# → http://localhost:3000/chats （Turbo 流式）
```

自定义表名：

```bash
bin/rails generate ruby_llm:install chat:Conversation message:ChatMessage
```

## 场景 B：Model 声明

```ruby
# app/models/chat.rb
class Chat < ApplicationRecord
  acts_as_chat
  belongs_to :user, optional: true
end

# app/models/message.rb
class Message < ApplicationRecord
  acts_as_message
end

# app/models/tool_call.rb
class ToolCall < ApplicationRecord
  acts_as_tool_call
end

# app/models/model.rb  — AI 模型 registry 表，非 ML model
class Model < ApplicationRecord
  acts_as_model
end
```

## 场景 C：持久化对话

```ruby
chat = Chat.create!(model: "claude-sonnet-4")
chat.ask "Explain ActiveRecord", with: "doc.pdf"
# messages 自动 append；token 用量可追踪
```

## 场景 D：Agent + chat_model

```ruby
class WorkAssistant < RubyLLM::Agent
  chat_model Chat
  model "gpt-4o-mini"
  instructions
  tools SearchDocsTool
end

chat = WorkAssistant.create!(user: current_user)
chat.ask "Hello"
```

Instructions 持久化：

- `create!` — 应用并持久化
- `find` — 运行时应用，不写库
- `sync_instructions!(chat)` — 显式写库

## 场景 E：与 SPA（React Router）共存

c456-app 路径：**API-only Rails + 独立 SPA**，不用 Inertia 渲染 Chat。

- 后端：`POST /api/v1/chats/:id/messages` + Job 流式
- 前端：fetch + SSE / `useChat`
- 可选仍用 `acts_as_chat` 持久化，但 UI 自研

不要混用 `ruby_llm:chat_ui`（ERB/Turbo）与 SPA  unless 明确需要 admin 页。

## 场景 F：Structured output 持久化

```ruby
chat.with_schema(PersonSchema).ask("Generate Alice")
# response content 存 message；schema 约束由 gem 保证
```

## 反模式

- ❌ 跳过 `ruby_llm:load_models` — 模型选择 UI / capability 检测失效
- ❌ Message 表手写 JSON 存 tool_calls — 用 `acts_as_tool_call`
- ❌ 在 AR callback 里同步长 `ask` — 用 Job

## 延伸阅读

- 生产 SSE → [streaming-sse.md](streaming-sse.md)
- c456-app 架构：API-only + JWT，见 c456-app `AGENTS.md`
