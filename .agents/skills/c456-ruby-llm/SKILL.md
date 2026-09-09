---
name: c456-ruby-llm
description: "RubyLLM gem guide for Rails AI apps: chat, tool-calling, agents vs workflows, streaming/SSE, structured schema, multimodal attachments, acts_as_chat, embeddings, and test stubs. Use when building or refactoring LLM features in Ruby/Rails (incl. OpenAI-compatible gateways like OpenCode Go)."
version: 1.0.0
related_skills:
  - c456-rails-startup
  - doc-driven-multi-agent
---

# RubyLLM（c456-ruby-llm）

> **场景驱动技能**：先判断「你要做什么」，再打开对应 reference。官方文档：[rubyllm.com](https://rubyllm.com/) · Gem：[crmne/ruby_llm](https://github.com/crmne/ruby_llm)（当前稳定版 **1.16.x**）

本技能吸收 **c456-aio 生产实践**（多 Agent 架构、Tool 边界、流式 SSE、薄 façade 测试），但不修改 aio 业务代码。

## 何时触发

| 用户意图 | 加载本技能 |
|---------|-----------|
| Rails 项目接入 / 升级 `ruby_llm` | ✅ |
| 单次问答、多轮 Chat、换模型/温度 | ✅ → [chat](references/chat.md) |
| 让模型调用 Ruby 方法（function calling） | ✅ → [tools](references/tools.md) |
| 定义可复用 Assistant（instructions + tools） | ✅ → [agents](references/agents.md) |
| 多 Agent 编排（串行/路由/并行/评估循环） | ✅ → [agentic-workflows](references/agentic-workflows.md) |
| 流式输出、SSE、Job 异步生成 | ✅ → [streaming-sse](references/streaming-sse.md) |
| JSON Schema / 结构化输出 | ✅ → [schema](references/schema-structured-output.md) |
| 图片/PDF/音频/视频附件 | ✅ → [multimodal](references/multimodal-attachments.md) |
| `acts_as_chat` 持久化、Generator | ✅ → [rails](references/rails-integration.md) |
| Embeddings / RAG 检索步骤 | ✅ → [embeddings-rag](references/embeddings-rag.md) |
| 出图 / 转写 / 内容审核 | ✅ → [multimodal-apis](references/images-audio-moderation.md) |
| 配置多 Provider、OpenAI 兼容网关 | ✅ → [configuration](references/models-configuration.md) |
| 错误处理、重试、测试 stub | ✅ → [error-handling-testing](references/error-handling-testing.md) |
| c456-aio 目录模式、LlmClient、边界原则 | ✅ → [c456-aio-patterns](references/c456-aio-patterns.md) |

## 核心原则（Agent 必须遵守）

### 1. Agent ≠ Workflow

| 概念 | 是什么 | 不是什么 |
|------|--------|----------|
| **Agent** (`RubyLLM::Agent`) | 可复用的 Chat 配置：`model` + `instructions` + `tools` + 可选 `schema` | 整条业务链路的「上帝循环」 |
| **Workflow** | 普通 Ruby 类，用 Sequential / Routing / Parallel / Fan-in / Evaluator-Optimizer 协调多个 Agent | 另一个 gem 或框架 |

**禁止**把建档、开通、CRUD 等完整链路塞进单一 Agent 的无限 tool 循环。

### 2. Agent / Tool 边界（c456 实践）

| Agent / Tool 做 | 确定性代码做 |
|----------------|-------------|
| 理解、检索、生成草稿/候选/解释 | `create!` / `update!` 业务主表 |
| 结构化 JSON 建议 | 配额、鉴权、计费 |
| 只读外部 I/O（search/fetch） | Inertia/SPA 页面渲染 |
| Tool 返回 `{ error: "..." }` 可恢复错误 | 用户确认后的落库 |

**Agent 产出草稿；人确认后由 Service/Controller 写库。**

### 3. 流式与并发

- **Streaming 来自 ruby_llm**（`ask { |chunk| }`），不要用小众流协议 gem 绕过它。
- **生成在 Job/worker**；Web 层短 POST + 可 resume 的 SSE 订阅，**禁止**在 `ActionController::Live` 里同步跑完整个 Agent。
- `RubyLLM::Chunk` 是唯一上游分片模型：`content` / `tool_calls` / `thinking` 都要能传到前端（AI Elements `<Tool />` 等）。

### 4. 测试

- 默认 **stub**（test 环境或无 API key 的 development）。
- 薄 façade（如 `Aio::LlmClient`）统一 `chat` / `chat_json` / `chat_stream`，测试只 stub façade。
- 真实 HTTP 用 `AIO_LLM_STUB=0` + VCR 或 smoke，不进 CI 默认路径。

### 5. OpenAI 兼容网关

OpenCode Go 等网关常需：

```ruby
config.openai_use_system_role = true
config.openai_api_base = ENV["AIO_LLM_BASE_URL"]
# provider: :openai, assume_model_exists: true
```

慢模型 / 网关非流式超时 → **优先流式收全文**（见 c456-aio `LlmClient#chat_streamed`）。

## 场景索引（决策树）

```
需要 LLM？
├─ 一次性脚本 / 探索 → RubyLLM.chat.ask
├─ 要复用（同 instructions+tools）→ RubyLLM::Agent 子类
├─ 多步骤业务 → Workflow 类 + 多个 Agent
├─ 要持久化会话 → acts_as_chat 或 chat_model Agent
├─ 要实时 UI → Job + Chunk 编码 → SSE（references/streaming-sse.md）
├─ 要固定 JSON → with_schema（references/schema-structured-output.md）
├─ 要读文件 → ask(..., with: path)（references/multimodal-attachments.md）
└─ 要向量检索 → embed + Tool/Workflow 步骤（references/embeddings-rag.md）
```

## Quick Start

```ruby
# Gemfile
gem "ruby_llm", "~> 1.16"

# config/initializers/ruby_llm.rb
RubyLLM.configure do |config|
  config.openai_api_key = ENV["OPENAI_API_KEY"]
  config.default_model = ENV.fetch("LLM_MODEL", "gpt-4o-mini")
  config.request_timeout = 120
  config.logger = Rails.logger
end

# 最简对话
chat = RubyLLM.chat
response = chat.ask "What is Ruby?"
puts response.content
```

Rails 生成器：

```bash
bin/rails generate ruby_llm:install
bin/rails db:migrate
bin/rails ruby_llm:load_models   # v1.13+
```

## Reference 文档

| 主题 | 文件 |
|------|------|
| Chat 多轮、系统提示、换模型 | [references/chat.md](references/chat.md) |
| Tool 定义、params DSL、halt | [references/tools.md](references/tools.md) |
| Agent 类、prompts、chat_model | [references/agents.md](references/agents.md) |
| Workflow 模式、RAG 步骤 | [references/agentic-workflows.md](references/agentic-workflows.md) |
| Streaming + SSE + Job 架构 | [references/streaming-sse.md](references/streaming-sse.md) |
| Schema 结构化输出 | [references/schema-structured-output.md](references/schema-structured-output.md) |
| 多模态附件 | [references/multimodal-attachments.md](references/multimodal-attachments.md) |
| Rails acts_as_chat | [references/rails-integration.md](references/rails-integration.md) |
| Embeddings / RAG | [references/embeddings-rag.md](references/embeddings-rag.md) |
| paint / transcribe / moderate | [references/images-audio-moderation.md](references/images-audio-moderation.md) |
| 配置、模型注册表、Async | [references/models-configuration.md](references/models-configuration.md) |
| 错误、重试、测试 stub | [references/error-handling-testing.md](references/error-handling-testing.md) |
| c456-aio 生产模式 | [references/c456-aio-patterns.md](references/c456-aio-patterns.md) |

## 安装本技能

```bash
npx skills add c456-com/skills --skill c456-ruby-llm -y
```

## 与薄技能 `ruby-llm` 的关系

`~/.agents/skills/ruby-llm` 偏 API 参考罗列；**本技能**在 API 之上增加：

- 场景决策树与 c456 边界原则
- Rails + Job + SSE 生产架构
- c456-aio 已验证的 initializer / LlmClient / agents+tools 目录约定
- 测试 stub 与 OpenAI 兼容网关注意事项

两者可并存：本技能负责「怎么做」，薄技能可作 API 速查。
