# Agentic Workflows — 编排场景

官方：https://rubyllm.com/agentic-workflows/

> **Workflow = 普通 Ruby 类**，不是 gem 里的另一个基类。Agent 做一件事；Workflow 串起来。

## 模式选择

| 模式 | 何时用 | 典型 |
|------|--------|------|
| **Sequential** | 后一步依赖前一步输出 | 调研 → 写作 |
| **Routing** | 请求分派到不同专家 | 代码/创意/事实分类 |
| **Parallel** | 独立分析可同时跑 | 情感+摘要+关键词 |
| **Fan-in** | 多专家 → 综合 | Code Review 安全+性能+风格 |
| **Evaluator-Optimizer** | 有质量标准、可迭代 | Draft → Critic → 修订 |

## Sequential

```ruby
class ResearchWriterWorkflow
  def create_article(topic)
    notes = ResearchAgent.new.ask(topic).content
    WriterAgent.new.ask(notes).content
  end
end
```

c456-aio 对应：`BrandOnboardingWorkflow`（线索 → 检索 → 抽取 → 问句候选）。

## Routing

```ruby
class ModelRouterWorkflow
  def call(query)
    agent_class = case TaskClassifierAgent.new.ask(query).content.downcase
                  when /code/ then CodeAgent
                  when /creative/ then CreativeAgent
                  else FactualAgent
                  end
    agent_class.new.ask(query).content
  end
end
```

c456-aio 对应：`WorkspaceEnrichRouter`（Later）。

## Parallel（Async gem）

```ruby
require "async"

class ParallelAnalyzer
  def analyze(text)
    Async do |task|
      sentiment = task.async { SentimentAgent.new.ask(text).content }
      summary   = task.async { SummaryAgent.new.ask(text).content }
      keywords  = task.async { KeywordAgent.new.ask(text).content }
      { sentiment: sentiment.wait, summary: summary.wait, keywords: keywords.wait }
    end.wait
  end
end
```

## Fan-in

```ruby
class CodeReviewSystem
  def review(code)
    Async do |task|
      sec = task.async { SecurityAgent.new.ask(code).content }
      perf = task.async { PerformanceAgent.new.ask(code).content }
      style = task.async { StyleAgent.new.ask(code).content }
      ReviewSynthesizerAgent.new.ask(
        "security:\n#{sec.wait}\n\nperformance:\n#{perf.wait}\n\nstyle:\n#{style.wait}"
      ).content
    end.wait
  end
end
```

## Evaluator-Optimizer

```ruby
class EvaluatorOptimizerWorkflow
  MAX_ROUNDS = 3

  def call(task)
    draft = DraftAgent.new.ask(task).content
    MAX_ROUNDS.times do
      v = CriticAgent.new.ask("Task: #{task}\nDraft: #{draft}").content
      return draft if v["verdict"] == "pass"
      draft = DraftAgent.new.ask("Task: #{task}\nDraft: #{draft}\nFeedback: #{v['feedback']}").content
    end
    draft
  end
end
```

c456-aio 对应：`MonitorPromptRefineWorkflow`（可选）。

## RAG 作为 Workflow 一步

**不要**把 RAG 塞进 Tool description 当 prompt。

1. `RubyLLM.embed(query)` → 向量
2. DB 近邻搜索（neighbor/pgvector）
3. 结果注入 Agent context 或专用 Retrieval Tool

```ruby
class DocumentSearch < RubyLLM::Tool
  description "Searches knowledge base"
  param :query

  def execute(query:)
    vec = RubyLLM.embed(query).vectors
    docs = Document.nearest_neighbors(:embedding, vec, distance: "euclidean").limit(3)
    docs.map { |d| "#{d.title}: #{d.content.truncate(500)}" }.join("\n\n---\n\n")
  end
end

class SupportAgent < RubyLLM::Agent
  tools DocumentSearch
  instructions "Search before answering. Cite sources."
end
```

## c456-aio Agent 清单（参考）

| 单元 | 类型 |
|------|------|
| `BrandOnboardingWorkflow` | Sequential |
| `BrandOnboardingAgent` | Agent（对话壳，委托 Workflow） |
| `ProfileExtractAgent` | Agent + schema |
| `MonitorPromptAgent` | Agent + Tool |
| `CompetitorDiscoveryAgent` | Agent |
| `WorkspaceEnrichRouter` | Routing（Later） |

落库统一走 `CommitProfileDraft` 等确定性 Service — **Workflow 只返回候选**。

## 反模式

- ❌ 单一 Agent 无限 tool loop 完成 6 步建档
- ❌ Workflow 里直接 `Brand.create!` 跳过用户确认
- ❌ 为每个 Agent 发明一套轮询事件 — 用统一 Chat 流（见 streaming-sse.md）
