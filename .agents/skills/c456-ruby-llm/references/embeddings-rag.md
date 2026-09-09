# Embeddings & RAG — 向量检索场景

官方：https://rubyllm.com/embeddings/

## 场景 A：单次向量化

```ruby
response = RubyLLM.embed("Ruby is elegant and expressive")
vector = response.vectors   # Float array
model  = response.model     # 如 text-embedding-3-small
```

批量：

```ruby
RubyLLM.embed(["doc one", "doc two", "doc three"])
```

## 场景 B：入库前自动生成（ActiveRecord）

```ruby
# migration: t.vector :embedding, limit: 1536
# Gemfile: gem "neighbor"

class Document < ApplicationRecord
  has_neighbors :embedding

  before_save :generate_embedding, if: :content_changed?

  private

  def generate_embedding
    self.embedding = RubyLLM.embed(content).vectors
  end
end
```

索引：`add_index :documents, :embedding, using: :hnsw, opclass: :vector_l2_ops`

## 场景 C：RAG Tool（Agent 内检索）

```ruby
class DocumentSearch < RubyLLM::Tool
  description "Searches internal knowledge base"
  param :query

  def execute(query:)
    vec = RubyLLM.embed(query).vectors
    hits = Document.nearest_neighbors(:embedding, vec, distance: "euclidean").limit(5)
    hits.map { |d| { title: d.title, excerpt: d.content.truncate(400) } }
  rescue StandardError => e
    { error: e.message }
  end
end
```

Agent：

```ruby
class SupportAgent < RubyLLM::Agent
  tools DocumentSearch
  instructions "Always search docs before answering. Cite titles."
end
```

## 场景 D：Workflow 内检索（不用 Tool）

```ruby
class AnswerWorkflow
  def call(question)
    vec = RubyLLM.embed(question).vectors
    context = Document.nearest_neighbors(:embedding, vec).limit(3).map(&:content).join("\n---\n")
    QAAgent.new.ask("Context:\n#{context}\n\nQuestion: #{question}").content
  end
end
```

Tool vs Workflow 内嵌：Agent 需自主决定「何时搜」→ Tool；固定先搜后答 → Workflow。

## 维度与模型

- 默认 embedding 模型因 provider 而异；配置见 [models-configuration.md](models-configuration.md)
- `limit:` 必须与模型输出维度一致（如 1536、3072）

## c456 P1 边界

c456-app P1：**不做**知识库向量检索/Agent 执行 — 仅 CRUD。本场景供 M2+ 或 c456-aio 参考。

## 反模式

- ❌ 每次 ask 全表 embed — 预计算 + 索引
- ❌ 检索结果塞进 Tool description
- ❌ 租户 A 文档被 B 的 query 命中 — 必须 `where(account_id: ...)`
