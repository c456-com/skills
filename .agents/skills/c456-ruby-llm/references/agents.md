# Agents — 可复用 Assistant 场景

官方：https://rubyllm.com/agents/

## 何时用 Agent vs RubyLLM.chat

| 用 `RubyLLM.chat` | 用 `RubyLLM::Agent` |
|-------------------|---------------------|
| 一次性脚本 | 多处复用同一套 instructions + tools |
| 动态拼 prompt | 类级配置 + 可选 ERB prompts |
| 无命名边界 | 团队可读：`MonitorPromptAgent` |

## 场景 A：纯 Ruby Agent（无 AR）

```ruby
class SupportAgent < RubyLLM::Agent
  model "gpt-4o-mini"
  temperature 0.3
  instructions "You are a concise support assistant. Always cite docs."
  tools SearchDocsTool, LookupAccountTool
end

SupportAgent.new.ask "How do I reset API key?"
# 或 SupportAgent.chat.ask "..."  → 返回 RubyLLM::Chat
```

## 场景 B：OpenAI 兼容网关 + c456-aio 模式

```ruby
class MonitorPromptAgent < RubyLLM::Agent
  model ENV.fetch("AIO_LLM_MODEL", "deepseek-v4-flash"),
        provider: :openai,
        assume_model_exists: true

  temperature 0.3
  instructions <<~TEXT
    你是监测问句生成助手。调用 keyword_to_monitor_prompts 工具。
    禁止输出裸名词；不要直接写库。
  TEXT

  tools KeywordToMonitorPromptsTool
end
```

## 场景 C：Rails 持久化（chat_model）

```ruby
class WorkAssistant < RubyLLM::Agent
  chat_model Chat   # ApplicationRecord，acts_as_chat

  model "gpt-4o-mini"
  instructions display_name: -> { chat.user.name }
  tools SearchDocsTool
end

# 创建持久会话
chat = WorkAssistant.create!(user: current_user)
chat.ask "Hello"

# 加载已有
chat = WorkAssistant.find(params[:id])
WorkAssistant.sync_instructions!(chat)  # 显式持久化 instructions
```

## 场景 D：Prompt 文件（app/prompts）

```ruby
class WorkAssistant < RubyLLM::Agent
  chat_model Chat
  instructions   # 无参 → 查找 app/prompts/work_assistant/instructions.txt.erb
end
```

命名：`Admin::SupportAgent` → `app/prompts/admin/support_agent/`

## 场景 E：运行时 inputs / 动态 tools

```ruby
class WorkAssistant < RubyLLM::Agent
  chat_model Chat
  inputs :workspace

  instructions { "Helping workspace #{workspace.name}" }

  tools do
    [ TodoTool.new(chat: chat), DriveTool.new(user: chat.user) ]
  end
end

WorkAssistant.new(workspace: ws).ask "List todos"
```

## 场景 F：Agent + Schema（结构化 Agent）

```ruby
class CriticAgent < RubyLLM::Agent
  schema do
    string :verdict, enum: %w[pass revise]
    string :feedback
  end
  instructions "Review draft quality."
end

result = CriticAgent.new.ask("Task: ...\nDraft: ...").content
# => {"verdict"=>"revise", "feedback"=>"..."}
```

## Agent 实例 API

实例委托完整 `RubyLLM::Chat` API：`ask`, `with_tool`, `with_model`, `on_tool_call`, …  
底层 chat：`agent.chat`

## 反模式

- ❌ 一个 Agent 承担建档 + 竞品 + 问句 + 落库
- ❌ Agent 内 `create!` 业务记录（除非明确的 draft 预览会话）
- ❌ `find` 后假设 instructions 已持久化 — 运行时应用，需 `sync_instructions!` 才写库

## 延伸阅读

- 多 Agent 编排 → [agentic-workflows.md](agentic-workflows.md)
- c456 边界 → [c456-aio-patterns.md](c456-aio-patterns.md)
