# Schema — 结构化输出场景

官方：https://rubyllm.com/chat/（Structured Output 节）· Schema gem：`ruby_llm/schema`

## 场景 A：RubyLLM::Schema 类（推荐）

```ruby
class ProductSchema < RubyLLM::Schema
  string :name, description: "Product name"
  number :price
  array :features do
    string
  end
end

response = RubyLLM.chat
  .with_schema(ProductSchema)
  .ask("Analyze this product", with: "product.txt")

data = response.content  # Hash
```

Agent 内联 schema：

```ruby
class CriticAgent < RubyLLM::Agent
  schema do
    string :verdict, enum: %w[pass revise]
    string :feedback
  end
end
```

## 场景 B：手动 JSON Schema

```ruby
schema = {
  type: "object",
  properties: {
    name: { type: "string" },
    age: { type: "integer" }
  },
  required: %w[name age],
  additionalProperties: false
}

RubyLLM.chat.with_schema(schema).ask("Generate a person")
```

## 场景 C：chat_json 过渡模式（c456-aio）

在全面迁移 `with_schema` 前，`LlmClient#chat_json` 用 OpenAI 兼容：

```ruby
build_chat(temperature: 0.2, params: {
  response_format: { type: "json_object" }
}).with_instructions(system).ask(user)
```

配合 system prompt 描述 JSON 形状；解析失败 raise `LlmError`。

**新代码优先** `with_schema(ProductSchema)` —  provider 差异由 gem 处理。

## 场景 D：六块 Profile 抽取（领域示例）

```ruby
# ProfileExtractAgent + schema 或 chat_json
# 输出 identity / product / claims / competitors / keywords / footprint
# 每块含 provenance, confidence, sources
# Agent 只返回草稿 → UI 确认 → CommitProfileDraft 写库
```

## 场景 E：JSON 解析容错

```ruby
def parse_json_content(text)
  text = text.strip
  text = text.sub(/\A```(?:json)?\s*/i, "").sub(/\s*```\z/, "") if text.match?(/\A```/)
  JSON.parse(text)
rescue JSON::ParserError => e
  raise LlmError, "非法 JSON: #{e.message}"
end
```

## 选型

| 方式 | 优点 | 缺点 |
|------|------|------|
| `RubyLLM::Schema` | 类型安全、跨 provider | 需定义类 |
| `with_schema(Hash)` | 快速原型 | 维护成本高 |
| `response_format: json_object` | 兼容老网关 | 无 compile-time 校验 |

## 反模式

- ❌ 靠 prompt「请输出 JSON」却不 schema — 解析失败率高
- ❌ Schema 输出直接 `create!` — 仍须确认门闩
- ❌ 在 Tool 里返回巨型 JSON 代替 schema chat — 职责混乱
