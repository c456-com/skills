---
name: book-extract
description: "书籍素材提取 / book extract：当用户要把 PDF、扫描件、拍照书页、OCR 书页或 MinerU 输出转成 raw/books/ Markdown + 图片时触发；用于书籍入库前的素材提取和来源整理。"
version: 3.0.1
---

# Book Extract（书籍素材提取）

将 **PDF** 或 **拍照书页** 提取为 `raw/books/` 下的 Markdown + 图片，供后续 **wiki-book-ingest** 编译。

技能目录：<https://github.com/c456-com/skills/tree/main/book-extract>

## 技能安装（执行前必做）

按 [`references/skill-install.md`](references/skill-install.md)：**检测 → 缺则安装 → 已装则 update → 从 path 加载**。

1. 检测 `book-extract` 是否已安装（`npx skills list --json`）
2. **未安装** → `npx skills add c456-com/skills --skill book-extract -y`（新装后不必再 update）
3. 书籍流水线还需 `wiki-book-ingest`、`llm-wiki-domains` — 缺则 `add`；**早已安装**的 → `npx skills update llm-wiki-domains book-extract wiki-book-ingest -y`（勿 `check` 全量）
4. 从安装目录的 `path` 读 `SKILL.md`、`references/`、`scripts/` — **禁止** `../wiki-book-ingest/...` 相对路径

## 输出目标

```
domains/<domain>/raw/books/<book-name>/
├── images/              # 页图
├── pages/               # page-NNN.md（视觉路径）
│   └── page-001.md      # 1 张图片 = 1 个 page-*.md（不含 .png/.jpg 源图）
└── book.md              # MinerU 路径或合并后的全书 MD（可选）
```

并写 `.extract-meta.yml`（用户选择的 `extract_method`、`vision_mode`、页数）。

### 输出格式（v3.0+）

每个 `page-NNN.md` 的 frontmatter 包含结构化字段：

```yaml
---
type: book-page
extract-backend: openai_compatible
image-index: 1               # 图片序号（1-based），对应 page-001.jpg
book-pages: [iii]           # 印刷书籍页码（可选，模型识别）
chapter: 序                  # 章节标题（可选）
header_text: 全部生命系列    # 页眉文字（可选）
footer_text: 003            # 页脚文字（可选）
---
```

- **核心变更 v3.0**：不再使用文本标记解析。模型直接输出 JSON `{"header_text":..., "footer_text":..., "book_pages":..., "chapter":..., "body":...}`，脚本解析 JSON 写入 frontmatter。
- 1 张图片 = 1 个 page-*.md
- 正文 CJK 空格自动清理
- 附有 `validate_raw_book()` 函数验证整本书的页面质量（缺页/空正文/格式异常）

## 硬性约束

1. **直接问、不试跑、不自动判断** — 收到 PDF 后**立刻**请用户选 A/B（或说明方式）；**禁止**先跑 MinerU、读 PDF 元数据/文字层、拆页抽样、`Read` 识图等任何形式的「探测」再询问或代选
2. **识别方式必须由用户明确确认** — MinerU / 视觉、`agent_native` / `external_api` 均须用户**亲口选定**后方可执行；**禁止**默认、推断或代选
3. **可提示用户自行判断，不可替用户判断** — 可同时附上 [`references/method-choice-guide.md`](references/method-choice-guide.md) 里的**自问表**，教用户**自己**对照特点选型；**禁止**「你的 PDF 是扫描件，建议用视觉」「我看了一下应该用 MinerU」等 Agent 下结论的话术
4. **先预览、用户确认、再执行**；用户未明确回答识别方式前，**不得**写入 `raw/` 或调用 MinerU / 视觉脚本
5. **`external_api` 禁止 Agent 临时写 HTTP/API 代码** — 只能 Shell 调用 `scripts/vision_*.py`
6. **拍照录入禁止 Tesseract / 传统 OCR** — 仅视觉（`vision_mode` 仍须用户确认）
7. 配置读 `.config/book-extract.json`；`defaults.extract_method` 保持 `user_choice`，**禁止**改成 `auto` 或预填路径
8. **临时文件只放 `.tmp/`** — PDF 拆页、拍照预处理、MinerU 中间产出等写入 **`.tmp/book-extract/<book-name>/`**（如 `pages/`、`photos/`、`mineru/`）；**禁止**在项目根创建 `work/`、`out/` 等目录（`.tmp/` 已在 llm-wiki-domains gitignore）

---

## Phase 0 — 确认输入

| 项 | 说明 |
|----|------|
| 输入 | PDF 路径，或照片目录（HEIC/JPG/PNG） |
| 输出域 | `domains/<domain>/` 路径 |
| 书名 | kebab-case 目录名 + 中文显示名 |

---

## Phase 1 — 直接询问识别方式（不试跑、不自动判断）

**流程**：确认输入（Phase 0）后 → **立即提问** → 等用户回复 → 再进入后续 Phase。**中间不做任何提取或探测。**

**拍照**：只有视觉；直接请用户选 `vision_mode`（Phase 2），不默认。

**PDF**：出示选项 + 可选附上 [`references/method-choice-guide.md`](references/method-choice-guide.md)（**用户自行判断**参考）。**必须收到用户明确答复**（A/B 或等价说明）后才能继续。

| 选项 | 标识 | 成本 | 特点 |
|------|------|------|------|
| **A. MinerU** | `mineru` | 免费，本地慢 | 电子版、表格/公式结构化好 |
| **B. 视觉大模型** | `vision` | 本地或 API | 图文/K 线/版式理解好 |

话术示例：

> 请选择 PDF 提取方式：  
> **A MinerU**（免费本地，偏文字与表格）  
> **B 视觉大模型**（偏识图与版式；本地千问 / Agent 读图 / 云端 API）  
> 请回复 A 或 B。  
> 不确定可参考下面「你怎么判断」自行对照（我不替你看 PDF 试跑或推荐）。

随后可粘贴或概括 `method-choice-guide.md` 中的**自问表**（教用户自己判断），**不要**根据你对文件的了解替用户选型。

**绝对禁止**（在用户选定前）：

- MinerU 试跑、全量、或「先看几页」
- 打开/解析 PDF 判断扫描件、文字层、乱码率
- 拆页、`Read` 读图、视觉 API 做质量评估
- 根据文件名、领域、历史对话**自动选**路径
- 「建议用…」「我帮你选 B」「那就 MinerU 吧」

用户明确选择后，在预览与 `.extract-meta.yml` 记录 `extract_method` 与 `user_confirmed: true`。

### 路径 A：MinerU（用户选 `mineru`）

复用 [pdf-converter](https://github.com/baklib-tools/skills/tree/main/skills/pdf-converter) 或本机 `mineru`。中间产出放 **`.tmp/book-extract/<book-name>/mineru/`**，勿用项目根 `./out`：

```bash
mkdir -p .tmp/book-extract/<book-name>/mineru
mineru -p book.pdf -o .tmp/book-extract/<book-name>/mineru -b pipeline --lang ch -m auto -t True -f True
```

长书在预览中确认页范围后可分页。产出 `.md` + `images/` 拷入 `raw/books/<book>/`。

### 路径 B：视觉大模型（用户选 `vision`）

PDF 先拆页图到 **`.tmp/book-extract/<book-name>/pages/`**；拍照预处理到 **`.tmp/book-extract/<book-name>/photos/`**。

```bash
BOOK=domains/<domain>/raw/books/<book-name>
mkdir -p .tmp/book-extract/<book-name>/pages
pdftoppm -png book.pdf .tmp/book-extract/<book-name>/pages/page

mkdir -p .tmp/book-extract/<book-name>/photos
for f in *.HEIC; do sips -s format png "$f" --out ".tmp/book-extract/<book-name>/photos/${f%.HEIC}.png"; done
for f in .tmp/book-extract/<book-name>/photos/*.png; do magick "$f" -resize 1536x1536 -quality 80 "$f"; done
```

识图完成后，页图可 **复制** 到 `$BOOK/images/` 留存；`.tmp/book-extract/<book-name>/` 为过程目录，勿在项目根建 `work/`。

---

## Phase 2 — 视觉子模式（路径 B 与拍照；须用户确认）

用户选 `vision`（或拍照）后，**直接请用户选** `vision_mode`（可附 `method-choice-guide.md` 视觉子模式表），**禁止**默认。

话术示例：

> 请选视觉执行方式：**1 agent_native**（当前 AI 读图）或 **2 external_api**（标准脚本 / 本地千问 / 云端 API）。请回复 1 或 2。

| `vision_mode` | 做法 |
|---------------|------|
| **`agent_native`** | Agent **Read** 读图，按 [`references/vision-extract-prompt.md`](references/vision-extract-prompt.md) 写 `page-*.md` |
| **`external_api`** | **只调用** `scripts/vision_*.py` |

用户确认后写入 `.extract-meta.yml` 的 `vision_mode`。

### 本地千问 3.6（`external_api` + OpenAI 兼容）

用户偏好本地视觉时，用已安装目录下 [`references/book-extract.example-qwen-local.json`](references/book-extract.example-qwen-local.json)（或 `npx skills list` 所得 `path` 下的同文件）：

```json
{
  "vision_mode": "external_api",
  "vision": {
    "provider": "openai_compatible",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "not-needed",
    "model": "qwen3.6-35b-a3b-mtp",
    "max_images_per_request": 2,
    "image_max_edge_px": 1536
  }
}
```

```bash
# BOOK_EXTRACT_PATH 来自 npx skills list 中 book-extract 的 path
python3 "$BOOK_EXTRACT_PATH/scripts/vision_openai_compatible.py" \
  --project-root /path/to/wiki-project \
  --images-dir .tmp/book-extract/my-book/pages \
  --output-dir domains/my-book/raw/books/my-book/pages \
  --batch-size 2 \
  --resume
```

确认 LM Studio（或同类）已起服务且模型已加载。

### `agent_native` 流程

1. `.config/book-extract.json` 设 `"vision_mode": "agent_native"`
2. 从 `.tmp/book-extract/<book-name>/pages/`（或 `photos/`）**逐张** Read → `domains/.../raw/books/<book>/pages/page-NNN.md`
3. **重要：读图时必须输出结构化 JSON** — 要求模型输出 `{"header_text":"","footer_text":"","book_pages":[],"chapter":"","body":"正文"}`，脚本解析 JSON 写入 frontmatter。正文中的配图用 `![描述: 图片说明]` 标注
4. 跳过已有页 = resume

### `external_api` 流程（禁止即兴写代码）

1. 复制 example → `.config/book-extract.json`，`"vision_mode": "external_api"`
2. `vision.provider`：
   - `openai_compatible` → [`scripts/vision_openai_compatible.py`](scripts/vision_openai_compatible.py)（**含本地千问**）
   - `anthropic` → [`scripts/vision_anthropic.py`](scripts/vision_anthropic.py)

环境变量可覆盖密钥：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`（本地千问通常不需要）。

---

## Phase 3 — 预览与确认

展示：用户**已确认**的 `extract_method`、`vision_mode`、将处理的页范围、将创建的路径。**用户再次确认后**再执行提取（识别方式与页范围可合并一轮确认，但识别方式不得跳过）。

---

## Phase 4 — 验收

- [ ] `raw/books/<book>/` 有 Markdown 与 `images/`
- [ ] `.extract-meta.yml` 记录**用户确认**的 `extract_method`、`vision_mode`（含 `user_confirmed: true`；非 Agent 自动判定）
- [ ] 提示下一步：**wiki-book-ingest**（先按 [`references/skill-install.md`](references/skill-install.md) 确保已安装，再读其 `SKILL.md`）

## 脚本文件

| 文件 | 用途 |
|------|------|
| [`scripts/vision_openai_compatible.py`](scripts/vision_openai_compatible.py) | OpenAI 兼容（含本地千问 / LM Studio） |
| [`scripts/vision_anthropic.py`](scripts/vision_anthropic.py) | Anthropic |
| [`scripts/vision_common.py`](scripts/vision_common.py) | 共享配置加载 |

脚本路径以 `npx skills list` 中 **book-extract** 的 `path` 为准。

## 相关技能

- 下一步编译：**wiki-book-ingest**（[`references/skill-install.md`](references/skill-install.md) 缺则安装）
- 知识库结构：**llm-wiki-domains**
- MinerU：pdf-converter（仅用户选 `mineru` 时参考）
