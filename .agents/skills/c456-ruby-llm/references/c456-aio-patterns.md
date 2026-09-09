# c456-aio Production Patterns

> 只读参考：`c456-aio` 已跑通的 RubyLLM 架构。勿在本技能中修改 aio 业务代码。

关联规格：

- `docs/superpowers/specs/2026-07-26-rubyllm-multi-agent-architecture-design.md`
- `docs/superpowers/specs/2026-07-30-ai-first-agent-tool-boundary-design.md`

## 目录结构

```
config/initializers/ruby_llm.rb   # 全局 RubyLLM.configure
app/services/aio/llm_client.rb    # 薄 façade：chat / chat_json / chat_stream
app/agents/                       # RubyLLM::Agent 子类
app/tools/                        # RubyLLM::Tool 子类
app/workflows/                    # 纯 Ruby 编排（BrandOnboardingWorkflow 等）
app/jobs/                         # ChatStreamJob — 流式生成
```

## Initializer 要点

```ruby
RubyLLM.configure do |config|
  config.openai_api_key = ENV["AIO_LLM_API_KEY"].presence || ENV["OPENAI_API_KEY"].presence
  config.openai_api_base = ENV["AIO_LLM_BASE_URL"].presence || ENV["OPENAI_API_BASE"].presence
  config.openai_use_system_role = true
  config.default_model = ENV.fetch("AIO_LLM_MODEL", "deepseek-v4-flash")
  config.request_timeout = ENV.fetch("AIO_LLM_TIMEOUT", "240").to_i
  config.logger = Rails.logger
end
```

## LlmClient 职责

| 方法 | 用途 |
|------|------|
| `#chat` | 单次文本，temperature 0.4 |
| `#chat_json` | system+user JSON，`response_format: json_object` |
| `#chat_stream` / `#chat_streamed` | 流式；慢网关用 stream 收全文 |
| `#stub_mode?` | test / dev 无 key / `AIO_LLM_STUB=1` |
| `#with_retries` | SSL/timeout/429/5xx |
| `#build_chat` | `RubyLLM.context` + `provider: :openai, assume_model_exists: true` |

业务 Orchestrator（`ResearchOrchestrator`、`ProfileExtractor` 等）逐步迁移为 Agent/Workflow，过渡期仍可调 `LlmClient`。

## Agent 示例：MonitorPromptAgent

```ruby
class MonitorPromptAgent < RubyLLM::Agent
  model ENV.fetch("AIO_LLM_MODEL", "deepseek-v4-flash"),
        provider: :openai,
        assume_model_exists: true
  temperature 0.3
  instructions "调用 keyword_to_monitor_prompts；不要写库"
  tools KeywordToMonitorPromptsTool
end
```

类方法 `generate_candidates` 可仍走确定性 Service — Agent 与 Service 并存时文档标明主路径。

## Tool 示例：WebSearchTool

- 只读 I/O：`Aio::WebSearch.call`
- 错误 → `{ error: e.message }`
- 无 `create!`

## AI-First 边界（2026-07-30）

| AI 做 | 程序做 |
|-------|--------|
| 理解线索、SERP 选目标、竞品排序、问句措辞 | search/fetch/probe I/O |
| 进度文案、报告解读建议 | 配额、鉴权、Cable 广播 |
| 结构化候选 | 用户确认后 `CommitProfileDraft` |

**禁止再当主路径**：Ranker 硬编码选官网、启发式凑满问句、Tool 内 `Brand.create!`。

**用户确认优先于静默纠错**（Baklib 案例）。

## 流式架构摘要

1. `POST messages` → enqueue `ChatStreamJob`
2. Job 内 `ask { |chunk| encoder.append!(chunk) }`
3. `GET stream` + `Last-Event-ID` resume
4. `POST stop` 显式取消
5. 前端 AI Elements 展示 Tool/Reasoning

禁止：`ai_stream` gem、Live 同步跑 Agent、每 Agent 一套轮询事件。

## 环境变量速查

见 [models-configuration.md](models-configuration.md) 表格。

## 迁移到新项目（c456-app 等）

1. 复制 initializer 模式 + `LlmClient` façade
2. `app/agents` + `app/tools` 分离
3. Workflow 类放 `app/workflows` 或 `app/services/.../workflow`
4. Chat UI 若 SPA：Job+SSE，不用 `ruby_llm:chat_ui`
5. 测试默认 stub；集成测试覆盖 tenant 隔离（若有多租户 KB）

## 延伸阅读

- 多 Agent 清单与分期 → aio spec `2026-07-26-rubyllm-multi-agent-architecture-design.md`
- Wave 改造计划 → `plans/2026-07-30-ai-first-services-remolding.md`
