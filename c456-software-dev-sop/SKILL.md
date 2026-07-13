---
name: c456-software-dev-sop
description: "软件开发 SOP / development workflow：当用户要从需求到实现推进功能、修 bug、做兼容性评估、同步文档或验收交付时触发；用于需求分析、理论调研、编码、测试和 llm-wiki 记录。"
version: 1.1.0
tags: [development, sop, workflow, documentation, knowledge-base]
---

# 通用软件开发 SOP

## 核心理念

- **理论来源与代码分离**：理论知识存在知识库（llm-wiki / c456-wiki），代码项目只存技术文档
- **先读文档再改代码**：改任何代码前，先确认有对应文档说明设计意图
- **兼容性评估前置**：每次改代码前评估影响面，提醒决策者，不自作主张做兼容
- **文档同步变更**：改代码的同时更新对应文档，保持一致性

## 工作流

### Step 1: 理解需求

读取项目文档，确认需求不偏离产品目标。

关键问题：
- 这个需求的"为什么"是什么？（业务价值）
- 验收标准是什么？
- 涉及哪些现有功能？

### Step 2: 读理论基础 / 知识库

如果需求涉及领域知识，先去知识库（如 c456-wiki）读取对应理论/概念。

知识库通常是 llm-wiki 结构（多领域场景使用 llm-wiki-domains）：
```
<knowledge-base>/
├── wiki/
│   ├── concepts/    ← 概念定义
│   ├── entities/    ← 实体说明
│   └── threads/     ← 推理链路/线索
└── raw/             ← 原始素材
```

项目文档中应有 `THEORY_REFERENCE.md` 或类似文件，记录理论到代码的映射关系。

### Step 3: 兼容性评估

每次改代码前，检查以下影响面：

```
□ 改了数据格式/DB 表结构？    → 影响已存数据
□ 改了 API/CLI 参数？         → 影响调用方和自动化
□ 改了函数签名？              → 影响调用方
□ 改了配置文件格式？          → 影响用户配置
□ 删了字段/列/路由？          → 影响已存数据和调用方
□ 改了核心算法逻辑？          → 影响计算结果一致性
```

**决策规则：**
- 项目尚未上线 → 直接改，不做兼容
- 已上线 → 标记 breaking change，规划迁移路径

**将评估结果告知决策者，由决策者决定是否做兼容。** 不要自作主张加兼容层。

### Step 4: 编码

- 遵循项目现有的代码风格和架构模式
- 如果新增模块，创建对应文档
- 如果涉及理论映射，更新 `THEORY_REFERENCE.md`（或项目对应的映射文档）

### Step 5: 文档同步

改完代码必须同步更新文档：

| 变更类型 | 需更新的文档 |
|---------|------------|
| 新增模块 | 创建模块文档 + 更新文档索引 |
| 修改逻辑 | 更新对应文档的 `last-reviewed` + 变更摘要 |
| 删除功能 | 标记对应文档为 `status: deprecated` |
| 理论映射变更 | 更新 `THEORY_REFERENCE.md` |

文档 Frontmatter 规范（每篇 .md 推荐包含）：

```yaml
---
title: 文档标题
type: product | architecture | domain | module | ops
status: draft | active | deprecated
last-reviewed: YYYY-MM-DD
theory-source: 可选，指向知识库的理论路径
code-path: 可选，指向代码路径
---
```

### Step 6: 验收

- 跑测试确认不破坏现有功能
- 检查文档是否最新
- 提交前运行 `git diff --stat` 确认改动范围
- 提交信息包含兼容性评估结论（如有影响）

## 统一文档规则：三层 + 流转路线

项目文档来自三种来源（产品负责人手写、负责人+AI 对话沉淀、AI 团队产出），
按来源与生命周期分为三层，外加归档层：

```
docs/
│
├── 产品方向/         ← 第 1 层：负责人手写（目标、PRD、CEO 视角）
│   ├── README.md       文档索引
│   ├── GOALS.md        产品/项目高层目标
│   └── *.md            方向性文档
│
├── 开发旅程/         ← 第 2 层：负责人+AI 对话沉淀（决策、讨论、评审）
│   ├── adr/            架构决策记录（不可逆、不可删改）
│   └── YYYY-MM-*.md    过程叙事（追加不删改）
│
├── superpowers/      ← 第 3 层：AI 团队按技能流程产出
│   ├── specs/          设计规格（brainstorming 产出）
│   ├── plans/          实现计划（writing-plans 产出）
│   ├── comms/          沟通日志（doc-driven 事实来源）
│   └── reviews/        评审报告
│
├── {领域目录}/       ← 归档层：实现完成后沉淀的稳定知识
│   ├── 00-产品/        产品概念、用户故事（稳定版）
│   ├── 10-架构/        系统架构、数据流、CLI 设计
│   ├── 20-领域/        领域模型、业务规则、理论映射
│   ├── 30-模块/        模块设计（按子模块分目录）
│   ├── 40-运维/        部署、数据维护、故障排查
│   └── archive/        过时文件备份
│
└── 项目级文档          ← 根目录保留
    ├── README.md       快速上手
    ├── AGENTS.md       AI 开发规范（推荐包含本 SOP 的链接或摘要）
    └── DOCS-CONVENTION.md  项目级特化（可选，覆盖本规则默认值）
```

### 三层写入纪律

| 层 | 谁写 | 写入方式 | 修改规则 |
|----|------|----------|----------|
| 产品方向 | 产品负责人 | 直接手写 | 负责人改，AI 不碰 |
| 开发旅程 | 负责人+AI | 对话后追加记录 | 追加不删改，历史记录 |
| superpowers | AI 团队（PM/PO/Arch/Dev/Analyst） | 按技能流程自动写入 | 功能完成后归档，不长期维护 |
| 归档层 | AI 团队（负责人在场确认） | 实现完成后手动迁移 | 按 SOP 分层维护 |

### 跨层流转路线

```
产品负责人写方向 → docs/产品方向/
                              ↓
负责人+AI 讨论决策 → docs/开发旅程/（adr + 过程记录）
                              ↓
AI 团队按技能生产 → docs/superpowers/{specs,plans,comms,reviews}
                              ↓
实现完成 → 有价值内容沉淀到 {领域目录}/（归档层稳定维护）
```

### 跨层引用规则

- 引用格式：`参见 docs/superpowers/specs/xxx.md §3.2`
- 允许上层引用下层（产品方向 → 开发旅程 → superpowers）
- 允许归档层引用各层（稳定文档引用原始来源）
- 不允许 superpowers 内文档反引用产品方向（避免耦合）
- 开发旅程中有价值的决策 → 转正为 `adr/` 独立条目
- superpowers specs 中的设计要点 → 实现后总结到归档层对应章节

### 文档 Frontmatter 规范

每篇 .md 推荐包含：

```yaml
---
title: 文档标题
type: product | journey | adr | spec | plan | comm | review | architecture | domain | module | ops
status: draft | active | deprecated | archived
source: handwrite | conversation | ai-team          # 来源标记
layer: 1 | 2 | 3 | archive                           # 所属层
last-reviewed: YYYY-MM-DD
theory-source: 可选，指向知识库的理论路径
code-path: 可选，指向代码路径
---
```

### 各技能在此框架中的定位

| 技能 | 所属层 | 产出文档路径 | 生命周期 |
|------|--------|-------------|----------|
| brainstorming（superpowers） | 第 3 层 | `docs/superpowers/specs/*-design.md` | 设计阶段，实现后归档 |
| writing-plans（superpowers） | 第 3 层 | `docs/superpowers/plans/YYYY-MM-DD-*.md` | 实现阶段，完成后归档 |
| doc-driven-multi-agent | 第 3 层 | `docs/superpowers/{comms,specs,plans,reviews}/` | 功能开发期活跃 |
| c456-docs-governance（项目级） | 全部层 | `docs/` 规范与命名 | 持续维护 |
| **本技能（c456-software-dev-sop）** | 全部层 + 归档层 | 定义文档分层与流转规则 | 持续维护 |

## 与知识库的关系

```
项目代码 + 技术文档          ← 本项目
  依赖 ↑ 引用
知识库（llm-wiki / llm-wiki-domains）     ← 理论知识源头
```

- 知识库存理论知识（领域概念、算法原理、业务规则）
- 项目存技术文档（架构、模块、API、运维）
- 技术文档中引用知识库路径，不复制理论内容
- 引用格式：`参见 <知识库路径>/wiki/concepts/<概念名>.md`

### 三层与知识库的映射

| 文档层 | 引用知识库方式 | 示例 |
|--------|---------------|------|
| 产品方向 | 引用领域概念定义 | `参见 <wikipath>/wiki/concepts/信号分层.md` |
| 开发旅程 | 不直接引用 | 决策过程不依赖理论 |
| superpowers specs | 引用理论来源做设计依据 | specs 中标注 `theory-source` |
| 归档层模块文档 | 强引用：映射字段 `theory-source` | frontmatter 中 `theory-source:` |
