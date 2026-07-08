---
name: c456-playbook-publishing
category: c456-cli
tags: [c456, playbook, publishing, content, wiki-sync, article]
description: "C456 playbook publishing / 长文发布：当用户要为 c456.com 写软文、blog、技术分享、playbook、长文内容，或需要 frontmatter、配图上传、字数校验、CLI 发布和本地 wiki 元数据同步时触发。"
version: 1.0.1
author: c456-com
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [c456, playbook, publishing, content, wiki-sync, article]
    related_skills: [c456-cli, c456-llm-wiki]
---

# C456 Playbook 长文发布

> 向 c456.com 发布软文/技术分享的完整工作流：从文章撰写、配图到 CLI 发布与本地元数据同步。

**前置技能**：加载 `c456-cli` 确保能调用 CLI。

## 整体工作流

```
1. 调研已有打法样式（frontmatter + 正文格式）
2. 撰写 frontmatter 元数据 + 正文
3. 配图：下载目标网站的截图/架构图 → c456 asset upload → 引用 c456.com/our-assets/ 链接（不可用外部 CDN）
4. 验证字数
5. 保存到 c456-sync/playbook/
6. 通过 c456 CLI 发布
7. 验证线上内容
8. 更新本地文件元数据（c456-id, c456-url, synced-at）
```

## 1. 调研已有样式

发布前先查看已有 playbook 了解 frontmatter 和正文格式：

```bash
ls ~/read-and-writes/c456-wiki/c456-sync/playbook/
```

阅读一篇已有 playbook（如 `c456-是如何开发出来的.md` 或 `ai-开发五大核心技能工具组合打法.md`）作为格式参考。注意：

- frontmatter 的字段约定（`c456-kind`, `c456-title`, `c456-summary`）
- 标题层级（`#` 主标题、`##` 节标题）
- 配图嵌入方式（`![说明](url)`）
- 引语和结语的风格

## 2. Frontmatter（YAML 元数据头）

**发布前的前置 frontmatter：**

```yaml
---
c456-kind: playbook
c456-title: "标题 · 副标题（不超过 80 字符）"
c456-summary: "摘要，150 字以内，用于列表页展示"
local-wiki-source: wiki/sources/你的-标题.md
---
```

**发布后更新为完整元数据：**

```yaml
---
c456-id: <playbook-id>
c456-kind: playbook
c456-status: published
c456-title: "标题 · 副标题"
c456-url: "https://c456.com/playbooks/<id>"
c456-summary: "摘要"
local-wiki-source: wiki/sources/你的-标题.md
local-wiki-threads:
  - wiki/threads/你的-标题.md
synced-at: <YYYY-MM-DD>
---
```

## 3. 长文结构与风格

- **主标题**：`#` 即一级标题，与站点页面标题一致
- **节标题**：`##` 二级标题，分段清晰
- **小节**：`###` 三级标题，展开细节
- **引语**：文章开头使用 `>` blockquote 作为引语或核心观点摘要
- **表格**：使用标准 Markdown 表格对比数据、概念或选项
- **代码块**：使用 ```bash 或 ```markdown 标注语言
- **列表**：使用 `-` 无序列表或 `|` 表格
- **结语**：末尾总结核心观点，附「延展阅读」链接到相关页面
- **配图**：每 2-3 个章节嵌入一张配图（见第 4 节）

## 4. 配图规则（重点）

> **核心原则**：所有配图必须托管在 c456 自有素材库，不可引用外部 CDN／第三方图床。

### 4.1 禁止行为

| ❌ 不要做 | 原因 |
|-----------|------|
| 引用对方 CDN 链接（Unsplash / 官网 assets 等） | 链接可能过期、被屏蔽、或被对方防盗链 |
| 全页截图（整页滚动截图） | 信息密度低、视觉差、暴露无关内容 |
| 直接用 Unsplash 通用配图 | 与文章内容无关，降低专业性 |

### 4.2 正确做法

```
源网站有产品截图/架构图 → 下载到本地 → c456 asset upload → 引用 c456 链接
```

**步骤**：

1. **找图**：在目标网站页面定位有信息量的图片（产品架构图、核心界面截图、数据图表等）
2. **下载**：用 `curl` 或浏览器取图片 URL，下载到本地 `.tmp/`
   ```bash
   curl -sL -A "Mozilla/5.0" -o .tmp/xxx.png "<图片URL>"
   ```
3. **上传**到 c456 素材库
   ```bash
   npx c456 asset upload -f .tmp/xxx.png
   # 输出：id: N, previewUrl: https://c456.com/our-assets/N/.../hash
   ```
4. **嵌入文章**
   ```markdown
   ![中文说明](https://c456.com/our-assets/N/.../hash "alt标签")
   ```
5. **清理**临时文件和不再使用的旧素材
   ```bash
   npx c456 asset delete <旧id>   # 如果旧素材不再被引用
   rm .tmp/xxx.png
   ```

### 4.3 截图工具

如果页面没有现成的图片可下载，或现成图片不适合做配图，使用 `c456 screenshot` 截图网站的 hero 部分：

```bash
npx c456 screenshot --viewport 1440x900 -o .tmp/screenshot.png <URL>
```

规则：
- **优先截 hero 区域**（首屏标题/核心卖点/产品展示区），这是最有信息量的视觉部分
- **不要全页截图** — 只截取首屏（viewport 高度内），暴露无关内容会降低专业度
- 用合适的 viewport 尺寸确保截图清晰（推荐 1440×900）
- 截完后同样上传到素材库

### 4.4 配图数量建议

- 长文（5000+ 字）：2-3 张，均匀分布各章
- 万字长文：3-5 张，每个主要章节一张
- 放在关键位置：引语后（全景图）、核心章节（配图佐证）

## 5. 字数验证

使用 `wc -m` 统计字符数：

```bash
wc -m ~/read-and-writes/c456-wiki/c456-sync/playbook/你的-标题.md
```

用户要求「1 万字」时，目标约 18,000-22,000 字符（含 markdown 标记、英文、标点）。

## 6. 文件路径

文件保存到 c456-wiki 的 playbook 同步目录：

```
~/read-and-writes/c456-wiki/c456-sync/playbook/你的-标题.md
```

## 7. 剥离 Frontmatter（关键步骤）

**c456 API 的正文（body）直接存储文章 Markdown 内容，不接收 YAML frontmatter。** 本地文件中的 frontmatter（`---` 之间的元数据）只为本地 wiki 维护服务，发布前必须剥离。

在 `.tmp/` 下生成不含 frontmatter 和顶部 `# 标题` 的净稿：

```bash
cd ~/read-and-writes/c456-wiki
python3 << 'PYEOF'
import re
with open("c456-sync/playbook/你的-标题.md") as f:
    content = f.read()
# 去掉 YAML frontmatter（第一对 --- 之间的内容）
content = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)
content = content.lstrip('\n')
# 去掉第一个 # 标题行及其后的空行
lines = content.split('\n')
if lines and lines[0].startswith('# '):
    lines = lines[1:]
    while lines and lines[0].strip() == '':
        lines.pop(0)
clean = '\n'.join(lines)
with open(".tmp/你的-标题-净稿.md", "w") as f:
    f.write(clean)
print(f"净稿：{len(clean)} 字符")
print("第一行:", clean[:80])
PYEOF
```

## 8. CLI 发布

API Key 可在项目 `.c456-cli/config.json` 或环境变量 `C456_API_KEY` 获取：

```bash
# 导出 API Key
export C456_API_KEY=$(cat ~/read-and-writes/c456-wiki/.c456-cli/config.json | python3 -c "import sys,json; print(json.load(sys.stdin)['apiKey'])"）

# 发布（使用净稿，不含 frontmatter）
cd ~/read-and-writes/c456-wiki
npx c456 playbook new -t "完整标题（≤80字符）" --body-file .tmp/你的-标题-净稿.md
```

输出会显示 `ID: <数字>`，记录该 ID。

## 9. 验证正文正确性

```bash
npx c456 playbook show <id> | head -10
```

**合格：** 正文第一行是 `> 引语`、`## 小节` 或直接文字内容。
**不合格：** 第一行是 `---`、`c456-id:`、`c456-kind:` → frontmatter 未剥离，用 `update` 修正：

```bash
npx c456 playbook update <id> --body-file .tmp/你的-标题-净稿.md
```

## 10. 本地文件元数据更新

发布后用 patch 更新本地文件的 frontmatter：添加 `c456-id`、`c456-status: published`、`c456-url`、`local-wiki-threads`、`synced-at`。

## 11. 避坑指南

| 坑 | 说明 |
|----|------|
| **忘记导出 API Key** | 未设 `C456_API_KEY` 时 CLI 报 401 |
| **标题过长** | API 有截断，控制在 80 字符以内 |
| **发布后不更新本地元数据** | 后续同步会丢失 c456-id 关联，可能重复创建 |
| **图片引用外部 CDN** | 必须用 c456 asset upload 上传到自有素材库，不可引用第三方图床 |
| **`--body-file` 路径错误** | 路径是相对于当前工作目录的，先 `cd` 到 wiki 仓库根目录 |

## 参考

- [c456-cli](skill:c456-cli) — C456 CLI 工具操作
- [c456-playbook-publishing/references](references/) — 本技能子参考
