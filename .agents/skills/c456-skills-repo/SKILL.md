---
name: c456-skills-repo
description: Maintain the c456-com/skills 技能分发仓库 — README 分类、submodule 管理、registry 注册、Logo 品牌化
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: []
platforms: [macos, linux]
metadata:
  hermes:
    tags: [c456, skills, repo, maintenance, branding]
---

# c456-skills-repo

Maintain the [`c456-com/skills`](https://github.com/c456-com/skills) repository — the central skills distribution hub for C456. Covers README organization, third-party skills as submodules, registry.json, and branding assets.

## README 分类原则

技能列表分为三个章节，按表头 `###` 三级标题加 emoji：

| 章节 | Emoji | 内容 |
|------|-------|------|
| **通用技能** | 🧰 | 非 C456 绑定的通用技能，可复用于任意项目（如 tmux-cursor-agent、book-extract、llm-wiki-domains 等，含 c456-software-dev-sop / c456-ai-summit 虽带前缀但实质通用） |
| **C456 通用技能** | 🏢 | 与 C456 业务绑定的技能（如 c456-cli、c456-llm-wiki、c456-product-channel-article 等） |
| **第三方技能（submodule）** | 📦 | 其他开源技能或技能包，通过 git submodule 引入 |

每个章节用 markdown 表格展示：名称（可点链接到目录） | 说明 | 来源（仅第三方）

## Submodule 管理模式

### 位置规则

第三方技能包直接放在仓库**根目录**，与本地技能平级。**不要**再套一层 `submodules/` 目录。

```bash
# ✅ 正确
git submodule add <repo-url> pm-skills
# 结果：pm-skills/ 和 llm-wiki-domains/、c456-cli/ 同层

# ❌ 错误
git submodule add <repo-url> submodules/pm-skills
```

### 单技能 vs 技能包

- **单技能**: `git submodule add <url> <skill-name>` — 根目录名称即技能名
- **技能包**: `git submodule add <url> <pack-name>` — 包内可能嵌套多个技能目录（如 Claude 插件包格式 `plugins/` → `skills/`）

### 是否注册到 registry.json

视情况而定：
- 技能包的个别技能如果要用 `npx skills` 发现，需要在根目录建 **symlink** 指向包内的实际 SKILL.md 路径，同时注册到 `registry.json`
- 如果只是作为参考/引用，不注册也可

## registry.json 维护

`registry.json` 是 `npx skills` 发现技能的索引。每条记录格式：

```json
{
  "name": "skill-name",
  "description": "简短说明",
  "tags": ["tag1", "tag2"],
  "version": "1.0.0"
}
```

- `name` 必须与技能目录名一致（`npx skills` 据此找 `SKILL.md`）
- 新增本地技能时同步添加条目
- 第三方技能注册前先确认 `npx skills` 能解析（需要目录下直接有 `SKILL.md`）

## Logo / 品牌化

### 存放位置

`docs/logo.svg` — SVG 格式，可嵌入 README 或用作 GitHub social preview。

### 品牌规范

C456 系列仓库统一视觉风格（参考 hermes-docker）：

| 属性 | 值 |
|------|-----|
| 背景色 | 深海军蓝 `#0a1628` ~ `#0f1f3a` |
| 高亮色 | 青蓝色（cyan） `#22d3ee` ~ `#06b6d4` |
| 主文字 | 白色，粗体无衬线 |
| 副文字 | 灰色 `#94a3b8` 或 `#475569`，细体或宽距 |
| 装饰 | 半透明网格线、发光效果、粒子光点 |
| 整体 | 圆角边框，科技感深色主题 |

### 图标隐喻建议

- **六边形簇** — 模块化、互联、技能聚合
- **拼接块/拼图** — 技能组件的组合
- **节点网络** — 分布式的注册表/市场

## Pitfalls

- ❌ **不要在根目录再加一层子目录**：submodule 直接放根目录，和本地技能同级
- ❌ **不要跳过 registry.json**：本地技能新建后必须注册，否则 `npx skills add -l` 看不到
- ❌ **不要在技能目录名中用空格或大写**：全小写 + 连字符（`c456-product-channel-article`）
- ⚠️ **Claude 插件包格式**（如 pm-skills）的技能在 `plugins/*/skills/` 下面，`npx skills` 不能直接识别。如需注册，建 symlink 或写 wrapper SKILL.md
