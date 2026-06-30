# Feature / New-Development Prompt Template

写 prompt 前先做三件事：
1. 研究领域知识（wiki、概念页）
2. 阅读现有源码（复用已有的类/函数/数据结构）
3. 设计验收标准（怎么验证结果）

## 模板正文

```markdown
# 【一句话目标】— XX 功能开发

## 理论基础（如果需要）
用表格/列表说明核心概念，引用 wiki 知识库。

## 需求

1. **需求一**：……
2. **需求二**：……
3. **需求三**：……

## 存储设计（有则写，无则删）

```
表名 pattern_recognition:
  ts_code TEXT       # 股票代码
  trade_date TEXT    # 交易日
  pattern_name TEXT  # 识别器名称
  zone TEXT          # 区划
  score FLOAT        # 置信度 0-1
  features_json TEXT # 特征详情
  UNIQUE(ts_code, trade_date, pattern_name)
```

## 验收标准

1. CLI 命令 `sandu xxx` 输出特定内容
2. DuckDB 查询 `SELECT * FROM ... LIMIT 10` 返回数据
3. 单元测试 `pytest tests/...` 通过
4. 文件存在于 `path/to/output`

## 设计约束

- 不破坏现有代码
- 可扩展（如 Pattern Registry + BaseDetector 抽象类）
- 多 worker 安全（DuckDB 短连接模式）
- 断点续扫支持

## 相关文件（让 Agent 自行阅读）

- `stock_picker/patterns/sandu_ab.py` — 核心分类器
- `stock_picker/core/bundle_indexer.py` — DuckDB 连接管理
- `stock_picker/cli/registry.py` — CLI 注册参考
```

## 原则

- 只写「做什么」和「怎么验收」，**不写「具体怎么改」**
- Agent 是专业软件开发 AI，过度指定浪费双方 token
- 验收标准必须可执行（有具体命令和预期输出）

---

## Superpowers 工程方法附注

对复杂/新功能开发，在 prompt 末尾追加以下工程方法指引：

```markdown
## 工程方法：Superpowers 流程

请遵循 Superpowers 工程方法论，不要跳过阶段直接写代码：

### 阶段 1：Brainstorming（需求澄清）
阅读本 prompt + 相关源码后，先输出需求理解与设计方向。

### 阶段 2：Writing Plans（任务拆解）
拆成 2–5 分钟子任务，写入 `docs/superpowers/specs/`。

### 阶段 3：TDD
先写测试（RED）→ 再写实现（GREEN）→ 最后重构（REFACTOR）。

### 阶段 4：Subagent-Driven
复杂模块可派生子 agent 并行执行，完成后代码审查。

### 阶段 5：Verification
每完成一个子功能必须运行验收命令，提供运行时证据。
```
