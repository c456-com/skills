---
name: c456-publish
category: c456
tags: [c456, publish, cli, intake, playbook, seo, distribution]
description: "C456 数据发布层 — 从 c456-sync 到 C456 线上发布的完整流程。当用户需要将内容发布到 c456.com（tool/signal/channel/playbook/walkthrough）、处理净稿、CLI 发布、回填本地元数据或做发布后 SEO 分发时触发。前置条件：使用 c456-sync 技能确保正文格式正确。"
version: 1.0.0
related_skills:
  - c456-sync
  - c456-cli
  - c456-write
---

# c456-publish：C456 发布上线流程

> 数据发布层技能。将 `c456-sync/` 中的内容推送到 C456 线上，并处理后续的元数据回填与 SEO 分发。

**前置条件**：
1. 内容已按 `c456-sync` 技能格式要求写好
2. `c456` CLI 已安装并配置 API Key
3. 若需配封面截图，Chrome CDP 可用

---

## §1 前置准备：封面截图

**适用范围**：tool / channel 类型收录必须配封面截图。

**例外**：用户明确说不需要截图、或 URL 无法访问、或类型为 signal/playbook/walkthrough。

### 步骤

```bash
# 1. 启动 CDP（如未运行）
c456 browser start

# 2. 截取官网首屏（视口截图，不加 -f）
c456 screenshot <官网URL> -o .tmp/<name>-hero.png

# 3. 上传到素材库
c456 asset upload -f .tmp/<name>-hero.png
# 输出：id: <asset_id>, previewUrl: https://c456.com/our-assets/...

# 4. 正文开头写入配图
# ![标题-hero](c456:asset/<asset_id>)

# 5. 清理
rm .tmp/<name>-hero.png
```

---

## §2 净稿处理

**c456 API 的正文（body）直接存储 Markdown 内容，不接收 YAML frontmatter。** 本地 `c456-sync/` 文件中的 frontmatter 只为本地 wiki 维护服务，上行前**必须剥离**。

### 通用净稿脚本

在 `.tmp/` 下生成不含 frontmatter 和顶部 `#` 标题的干净正文：

```bash
cd ~/read-and-writes/c456-wiki
python3 << 'PYEOF'
import re
with open("c456-sync/<type>/<你的文件>.md") as f:
    content = f.read()
# 去掉 YAML frontmatter
content = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)
content = content.lstrip('\n')
# 去掉第一个 # 标题行及其后的空行
lines = content.split('\n')
if lines and lines[0].startswith('# '):
    lines = lines[1:]
    while lines and lines[0].strip() == '':
        lines.pop(0)
clean = '\n'.join(lines)
with open(".tmp/<你的文件>-净稿.md", "w") as f:
    f.write(clean)
print(f"净稿：{len(clean)} 字符")
print("第一行:", clean[:80])
PYEOF
```

### 验证净稿正确性

净稿的第一行**不应**是：
- `---`（frontmatter 未剥离）
- `c456-id:`、`c456-kind:`、`c456-title:` 等元数据
- `# `（一级标题未剥离）

正确第一行应为：`## `、导语段落、配图 markdown、或 `>` 引语。

---

## §3 CLI 发布

### 发布新内容（new）

```bash
# tool（手动指定）
c456 tool new -u <URL> -t "标题" [--auto-resolve-url] --body-file .tmp/<文件>-净稿.md

# signal（手动指定）
c456 signal new -t "标题" --body-file .tmp/<文件>-净稿.md

# channel（手动指定）
c456 channel new -u <URL> -t "标题" [--auto-resolve-url] --body-file .tmp/<文件>-净稿.md

# playbook（长文）
c456 playbook new -t "标题（≤80字符）" --body-file .tmp/<文件>-净稿.md

# walkthrough
c456 walkthrough new -t "标题" --body-file .tmp/<文件>-净稿.md
```

**⚠️ 关键**：`new` 就是发布行为。创建即上线，无需额外 publish/approve 步骤。

**记录输出**：`new` 会返回 `ID: <数字>`，立即记录该 ID。

### 更新已有内容（update）

如果首次发布时正文包含 frontmatter 或内容有误：

```bash
c456 intake update <id> --body-file .tmp/<类型>-净稿.md
# 或按类型指定：
c456 tool update <id> --body-file .tmp/净稿.md
c456 signal update <id> --body-file .tmp/净稿.md
c456 playbook update <id> --body-file .tmp/净稿.md
```

### 验证线上内容

```bash
c456 intake show <id> | head -10
```

**合格**：正文第一行是 `##`、导语段落、配图 markdown 或 `>` 引语。
**不合格**：第一行是 `---`、`c456-*` 元数据 → frontmatter 未剥离，用 `update` 修正。

---

## §4 回填本地元数据

发布成功后，更新本地的 c456-wiki 仓库文件以保持同步。

### 4.1 c456-sync 文件

在 `c456-sync/<type>/<name>.md` 的 frontmatter 中回填：

```yaml
c456-id: <id>
c456-url: https://c456.com/intakes/<id>
c456-status: published
```

### 4.2 wiki 实体页

在 `wiki/entities/<name>.md` 的 frontmatter 中标记为已发布：

```yaml
c456-status: published
```

### 4.3 wiki/log.md

追加发布日志：

```markdown
## [YYYY-MM-DD] c456-publish | <标题> → C456

- **操作**：`c456 <type> new ...` → ID: **<id>**
- **URL**：https://c456.com/intakes/<id>
- **回填**：`c456-sync/<type>/<file>.md`、`wiki/entities/<file>.md`
- **状态**：published
```

### 4.4 wiki/index.md

在对应实体行添加 `[c456:#<id>]` 标记。

---

## §5 长文发布（Playbook 专属）

发布 playbook 时，除上述通用流程外，还需要：

### 5.1 字数验证

```bash
wc -m c456-sync/playbook/<标题>.md
```

目标：用户要求「1 万字」时 ≈ 18,000-22,000 字符（含 markdown 标记）。

### 5.2 配图均匀分布

- 长文（5000+ 字）：2-3 张
- 万字长文：3-5 张
- 放在关键位置：引语后、核心章节

### 5.3 正文结构

| 元素 | 说明 |
|------|------|
| **主标题** | frontmatter `c456-title`，正文不用 `#` |
| **引语** | 文章开头使用 `>` blockquote 作核心观点摘要 |
| **节标题** | `##` 二级标题，分段清晰 |
| **表格** | 对比数据使用标准 Markdown 表格 |
| **代码块** | 用 ```bash 或 ```markdown 标注语言 |
| **结语** | 末尾总结 + 「延展阅读」链接到相关页面 |

---

## §6 发布后分发

内容发布到 C456 后，通过以下步骤确保被搜索引擎收录。

### 6.1 内部互链

从已有的相关 playbook/signal/tool 页面添加指向新内容的超链接：

```bash
# 查找相关文章
c456 search signals -q "<关键词>"

# 更新已有 playbook 的延展阅读段落
c456 playbook show <related_id>
c456 playbook update <related_id> --body-file .tmp/updated.md
```

### 6.2 搜索引擎提交

| 平台 | 操作 |
|------|------|
| **Google Search Console** | 提交新 URL 请求索引 |
| **百度站长平台** | 提交 URL，启用自动推送 |

### 6.3 内容分发矩阵

| 平台 | 内容形式 | 字数 | 目的 |
|------|---------|------|------|
| **知乎** | 深度专栏或回答相关问题 | 2500-4000 字 | 百度最高权重 |
| **掘金** | 精华摘要，含对比表和选型建议 | 2000-3000 字 | 技术流量 |
| **CSDN** | 简化技术版 | 1500-2500 字 | 技术搜索权重 |

**分发原则**：
- 标题含核心关键词
- 正文插入 2-3 次原文链接
- 各平台发不同版本，避免重复内容判罚
- 结尾统一引导：「点击阅读完整报告 → https://c456.com/<type>/<id>」

### 6.4 长尾词内容矩阵

将每篇内容拆成多个角度发布：

| 子主题 | 目标长尾词 | 平台 |
|--------|-----------|------|
| 单一工具评测 | "XX 工具好用吗" | 知乎 |
| 场景对比 | "XX vs YY 怎么选" | 掘金 |
| 选型指南 | "XX 如何选型 2026" | CSDN |

---

## §7 避坑指南

| 坑 | 说明 |
|----|------|
| **忘了截图** | tool/channel 必须有封面截图，这是正文第一张图 |
| **净稿第一行是 frontmatter** | 正文包含 `---` 或 `c456-*` → API 显示混乱，用 update 修正 |
| **用 `new` 而不是 `update` 修正** | 同一内容不能 `new` 两次。发错后走 `update` 替换正文 |
| **忘记导出 API Key** | 未设 `C456_API_KEY` 时 CLI 报 401 |
| **标题过长** | API 有截断，控制在 80 字符以内 |
| **`--body-file` 路径错误** | 路径是相对于当前工作目录的，先 `cd` 到仓库根目录 |
| **发布后不更新本地元数据** | 后续同步会丢失 `c456-id` 关联，可能重复创建 |
| **以为发完就完事** | SPA 架构不主动分发就不会被索引 |
| **不同平台发同一篇文章** | 判为重复内容，各平台发不同版本摘要 |
| **掘金发全文** | 判为营销文拒审，只发精华摘要 + 原文链接 |
| **不做内部互链** | 新页面没有入链，爬虫找不到入口 |

## 参考

- 正文格式规范：`c456-sync` 技能
- 内容写作方法：`c456-write` 技能
- CLI 操作：`c456-cli` 技能
- 全站 SEO 架构（含 sitemap、JSON-LD、SeoHead 组件）：`c456-playbook-seo-distribution` 旧版（归档）
