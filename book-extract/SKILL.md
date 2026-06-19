---
name: book-extract
description: >-
  书籍素材提取：PDF（MinerU 或视觉大模型）与拍照（仅视觉）。由用户选择识别方式，不自动推荐。
  vision_mode 支持 agent_native 或 external_api（含本地千问等 OpenAI 兼容端点）。
  当用户提到 PDF 录入、拍照录入、book-extract、MinerU、千问识图、书籍转 raw 时使用。
---

# Book Extract（书籍素材提取）

将 **PDF** 或 **拍照书页** 提取为 `raw/books/` 下的 Markdown + 图片，供后续 **wiki-book-ingest** 编译。

技能目录：<https://github.com/c456-com/skills/tree/main/book-extract>

## 技能安装（执行前必做）

按 [`references/skill-install.md`](references/skill-install.md)：**检测 → 缺则安装 → 已装则 update → 从 path 加载**。

1. 检测 `book-extract` 是否已安装（`npx skills list --json`）
2. **未安装** → `npx skills add c456-com/skills --skill book-extract -y`（新装后不必再 update）
3. 书籍流水线还需 `wiki-book-ingest`、`karpathy-wiki` — 缺则 `add`；**早已安装**的 → `npx skills update karpathy-wiki book-extract wiki-book-ingest -y`（勿 `check` 全量）
4. 从安装目录的 `path` 读 `SKILL.md`、`references/`、`scripts/` — **禁止** `../wiki-book-ingest/...` 相对路径

## 输出目标

```
domains/<domain>/raw/books/<book-name>/
├── images/              # 页图
├── pages/               # page-NNN.md（视觉路径）
│   └── page-000.md
└── book.md              # MinerU 路径或合并后的全书 MD（可选）
```

并写 `.extract-meta.yml`（用户选择的 `extract_method`、`vision_mode`、页数）。

## 硬性约束

1. **识别方式由用户选择** — **禁止** Agent 根据 PDF 质量自动替用户决定 MinerU 或视觉；仅可简要说明各选项差异后询问
2. **先预览、用户确认、再执行**（方式、页范围、费用/耗时粗算）
3. **`external_api` 禁止 Agent 临时写 HTTP/API 代码** — 只能 Shell 调用 `scripts/vision_*.py`
4. **拍照录入禁止 Tesseract / 传统 OCR** — 仅视觉大模型
5. 配置读 **项目根** `.config/book-extract.json`（gitignore）

---

## Phase 0 — 确认输入

| 项 | 说明 |
|----|------|
| 输入 | PDF 路径，或照片目录（HEIC/JPG/PNG） |
| 输出域 | `domains/<domain>/` 路径 |
| 书名 | kebab-case 目录名 + 中文显示名 |

---

## Phase 1 — 询问识别方式（必选，不自动识别）

**拍照**：只有视觉路径，但仍须问 `vision_mode`（见 Phase 2）。

**PDF**：用下面**简表**问用户选哪一种（一次问清，不要先跑 MinerU 试跑再推荐）：

| 选项 | 标识 | 成本 | 特点 |
|------|------|------|------|
| **A. MinerU** | `mineru` | 免费，本地慢 | 电子版、表格/公式结构化好 |
| **B. 视觉大模型** | `vision` | 本地或 API | 图文/K 线/版式理解好；**即使 MinerU 能转，用户也可选此项** |

话术示例：

> 这本 PDF 可以用两种方式提取：  
> **A MinerU**（免费本地，偏文字与表格）  
> **B 视觉大模型**（如本地千问 3.6 / Agent 读图 / 云端 API，偏识图与版式）  
> 你更想用哪一种？

用户选定前**不要**执行 MinerU 全量或视觉全量。

可选：用户问差异时，可补充「扫描件、K 线多 → 视觉往往更好；纯文字电子书 → MinerU 省 API」，但**不得**据此覆盖用户选择。

### 路径 A：MinerU（用户选 `mineru`）

复用 [pdf-converter](https://github.com/baklib-tools/skills/tree/main/skills/pdf-converter) 或本机 `mineru`：

```bash
mineru -p book.pdf -o ./out -b pipeline --lang ch -m auto -t True -f True
```

长书在预览中确认页范围后可分页。产出 `.md` + `images/` 拷入 `raw/books/<book>/`。

### 路径 B：视觉大模型（用户选 `vision`）

PDF 先拆页图；拍照做 HEIC→PNG、缩放（见下）。

```bash
mkdir -p work/pages
pdftoppm -png book.pdf work/pages/page

for f in *.HEIC; do sips -s format png "$f" --out "out/${f%.HEIC}.png"; done
for f in out/*.png; do magick "$f" -resize 1536x1536 -quality 80 "$f"; done
```

---

## Phase 2 — 视觉子模式（路径 B 与拍照）

用户选 `vision` 后，再问（可合并成一轮）：

| `vision_mode` | 做法 | 典型场景 |
|---------------|------|----------|
| **`agent_native`** | Agent **Read** 读图，按 [`references/vision-extract-prompt.md`](references/vision-extract-prompt.md) 写 `page-*.md` | Cursor 等多模态 Agent |
| **`external_api`** | **只调用** `scripts/vision_*.py` | 本地 **千问 3.6**（LM Studio）、批量、云端 API |

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
  --images-dir work/pages \
  --output-dir domains/my-book/raw/books/my-book/pages \
  --batch-size 2 \
  --resume
```

确认 LM Studio（或同类）已起服务且模型已加载。

### `agent_native` 流程

1. `.config/book-extract.json` 设 `"vision_mode": "agent_native"`
2. 每批 1–2 张 Read → `pages/page-NNN.md`
3. 跳过已有页 = resume

### `external_api` 流程（禁止即兴写代码）

1. 复制 example → `.config/book-extract.json`，`"vision_mode": "external_api"`
2. `vision.provider`：
   - `openai_compatible` → [`scripts/vision_openai_compatible.py`](scripts/vision_openai_compatible.py)（**含本地千问**）
   - `anthropic` → [`scripts/vision_anthropic.py`](scripts/vision_anthropic.py)

环境变量可覆盖密钥：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`（本地千问通常不需要）。

---

## Phase 3 — 预览与确认

展示：用户选的 `extract_method`、`vision_mode`、将处理的页范围、将创建的路径。**用户确认后**再执行。

---

## Phase 4 — 验收

- [ ] `raw/books/<book>/` 有 Markdown 与 `images/`
- [ ] `.extract-meta.yml` 记录**用户选择**的方式（非自动判定）
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
- 知识库结构：**karpathy-wiki**
- MinerU：pdf-converter（仅用户选 `mineru` 时参考）
