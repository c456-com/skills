# Tools — Function Calling 场景

官方：https://rubyllm.com/tools/

## 场景 A：只读 I/O Tool（c456 推荐默认）

Tool 封装网络/DB **读取**，不含业务判断写库：

```ruby
class WebSearchTool < RubyLLM::Tool
  description "搜索公开网页，返回标题、URL 与摘要"

  param :query, desc: "搜索查询词"
  param :max_results, desc: "最多返回几条", required: false

  def execute(query:, max_results: 5)
    hits = MyApp::WebSearch.call(query: query, max_results: max_results.to_i.clamp(1, 8))
    { results: hits.map { |h| h.slice(:title, :url, :snippet) } }
  rescue StandardError => e
    { error: e.message }   # 可恢复：模型可换策略
  end
end
```

## 场景 B：params DSL（v1.9+）

```ruby
class SchedulerTool < RubyLLM::Tool
  description "预约会议"

  params do
    object :window do
      string :start, description: "ISO8601"
      string :finish, description: "ISO8601"
    end
    array :participants, of: :string
  end

  def execute(window:, participants:)
    # ...
  end
end
```

## 场景 C：挂到 Chat / Agent

```ruby
# 临时
RubyLLM.chat.with_tool(WebSearchTool).ask "查一下 Ruby 3.4 新特性"

# Agent 类级
class ResearchAgent < RubyLLM::Agent
  tools WebSearchTool, FetchPageTool
end
```

类名自动 snake_case → `web_search_tool`；可 `def name; "web_search"; end` 覆盖。

## 场景 D：Tool 包装子 Agent

```ruby
class SummarizeTool < RubyLLM::Tool
  description "Summarize long text via specialist agent"
  param :text

  def execute(text:)
    SummaryAgent.new.ask(text).content
  end
end
```

UI 层仍显示为 Tool 卡片；内部可以是另一个 Agent。

## 场景 E：halt — 终止 tool 循环

当 Tool 结果应作为**最终答案**、不让模型继续编造：

```ruby
class FinalAnswerTool < RubyLLM::Tool
  def execute(answer:)
    halt answer
  end
end
```

## 错误约定

| 情况 | 做法 |
|------|------|
| 可恢复（网络闪断、无结果） | `return { error: "..." }` |
| 不可恢复（未授权、配置缺失） | `raise` |
| 禁止写业务主表 | Tool 内不 `Brand.create!`；返回候选 JSON |

## 反模式

- ❌ Tool description 当 system prompt 重复发送
- ❌ Tool 内隐式落库 — Agent 边界见 [c456-aio-patterns.md](c456-aio-patterns.md)
- ❌ 一个 Tool 做 5 件事 — 拆原子 Tool，Workflow 编排

## 目录约定（Rails）

```
app/tools/          # RubyLLM::Tool 子类
app/agents/         # RubyLLM::Agent 子类
app/workflows/      # 纯 Ruby 编排（可选）
```

参考 c456-aio：`WebSearchTool`、`FetchPageTool`、`SelectFetchTargetsTool` 等。
