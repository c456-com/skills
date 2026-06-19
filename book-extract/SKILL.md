---
name: book-extract
description: >-
  书籍素材提取：PDF（MinerU 免费 / 视觉大模型）与拍照录入（仅视觉）。
  vision_mode 支持 agent_native（Agent 自识别）或 external_api（标准脚本，禁止临时写 API 代码）。
  当用户提到 PDF 录入、拍照录入、book-extract、MinerU、书籍转 raw、视觉识图时使用。
---

# Book Extract（书籍素材提取）

将 **PDF** 或 **拍照书页** 提取为 `raw/books/` 下的 Markdown + 图片，供后续 [`wiki-book-ingest`](../wiki-book-ingest/SKILL.md) 编译。

技能目录：<https://github.com/c456-com/skills/tree/main/book-extract>

## 输出目标

```
domains/<domain>/raw/books/<book-name>/
├── images/              # 页图
├── pages/               # page-NNN.md（视觉路径）
│   └── page-000.md
└── book.md              # MinerU 路径或合并后的全书 MD（可选）
```

并写 `.extract-meta.yml`（backend、页数、vision_mode、探测结论）。

## 硬性约束

1. **先预览、用户确认、再执行**（路径、页范围、费用粗算）
2. **`external_api` 禁止 Agent 临时写 HTTP/API 代码** — 只能 Shell 调用 `scripts/vision_*.py`
3. **拍照录入禁止推荐 Tesseract / 传统 OCR** — 仅视觉大模型（`agent_native` 或脚本）
4. 配置读 **项目根** `.config/book-extract.json`（gitignore，见 [`karpathy-wiki`](../karpathy-wiki/SKILL.md)）

---

## Phase 0 — 确认输入

| 项 | 说明 |
|----|------|
| 输入 | PDF 路径，或照片目录（HEIC/JPG/PNG） |
| 输出域 | `domains/<domain>/` 路径 |
| 书名 | kebab-case 目录名 + 中文显示名 |

---

## Phase 1 — PDF 探测与路径推荐（仅 PDF）

试跑前 3–5 页或检查 PDF 元数据：

| 判定 | 信号 | 推荐 |
|------|------|------|
| `scan_pdf` | 无文字层 / 纯扫描 | 视觉路径 |
| `low_text_quality` | MinerU 试跑乱码率高 | 视觉路径 |
| `image_heavy` | K 线、截图、手写多 | 视觉路径 |
| `digital_pdf` | 电子版、表格多 | **MinerU**（免费慢） |

展示预览表 + 推荐 + 用户确认。

### 路径 A：MinerU（免费）

复用 [pdf-converter](https://github.com/baklib-tools/skills/tree/main/skills/pdf-converter) 或本机 `mineru`：

```bash
mineru -p book.pdf -o ./out -b pipeline --lang ch -m auto -t True -f True
```

长书先 `--start 0 --end 9` 试跑。产出 `.md` + `images/` 拷入 `raw/books/<book>/`。

### 路径 B：视觉大模型

PDF 先拆页图：

```bash
mkdir -p work/pages
pdftoppm -png book.pdf work/pages/page
# 或: magick convert -density 150 book.pdf work/pages/page-%03d.png
```

拍照预处理（HEIC→PNG、缩放到 `image_max_edge_px`，默认 1536）：

```bash
for f in *.HEIC; do sips -s format png "$f" --out "out/${f%.HEIC}.png"; done
for f in out/*.png; do magick "$f" -resize 1536x1536 -quality 80 "$f"; done
```

---

## Phase 2 — 视觉模式选择（路径 B 与拍照必选）

| `vision_mode` | 做法 | 何时用 |
|---------------|------|--------|
| **`agent_native`** | Agent 用 **Read 工具**读 `images/`，按 [`references/vision-extract-prompt.md`](references/vision-extract-prompt.md) 写 `page-*.md` | Cursor/Claude 等多模态 Agent；**零 API 配置** |
| **`external_api`** | 读 `.config/book-extract.json`，**只调用标准脚本** | 批量离线、Agent 无视觉、指定便宜模型 |

### `agent_native` 流程

1. 确认 `.config/book-extract.json` 中 `"vision_mode": "agent_native"`（可无 api_key）
2. 每批 1–2 张图 Read → 写 `pages/page-NNN.md`（frontmatter 含 `source-images`）
3. `--resume` 语义：跳过已有 `page-*.md`

### `external_api` 流程（禁止即兴写代码）

1. 用户复制 [`references/book-extract.example.json`](references/book-extract.example.json) → `.config/book-extract.json`，设 `"vision_mode": "external_api"` 并填 `api_key` 或环境变量
2. 按 `vision.provider` 选脚本：

**OpenAI 兼容**（OpenAI / OpenRouter / DeepSeek / LM Studio / Ollama）：

```bash
python3 /path/to/skills/book-extract/scripts/vision_openai_compatible.py \
  --project-root /path/to/wiki-project \
  --images-dir work/pages \
  --output-dir domains/my-book/raw/books/my-book/pages \
  --batch-size 2 \
  --resume
```

**Anthropic**：

```bash
python3 /path/to/skills/book-extract/scripts/vision_anthropic.py \
  --project-root /path/to/wiki-project \
  --images-dir work/pages \
  --output-dir domains/my-book/raw/books/my-book/pages \
  --resume
```

环境变量可覆盖密钥：`OPENAI_API_KEY`、`OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY`。

---

## Phase 3 — 验收

- [ ] `raw/books/<book>/` 有 Markdown 与 `images/`
- [ ] `.extract-meta.yml` 记录 backend 与 vision_mode
- [ ] 提示下一步：[`wiki-book-ingest`](../wiki-book-ingest/SKILL.md)

## 脚本文件

| 文件 | 用途 |
|------|------|
| [`scripts/vision_openai_compatible.py`](scripts/vision_openai_compatible.py) | OpenAI 兼容多模态 API |
| [`scripts/vision_anthropic.py`](scripts/vision_anthropic.py) | Anthropic Messages API |
| [`scripts/vision_common.py`](scripts/vision_common.py) | 共享加载配置（勿单独调用） |

## 相关技能

- 下一步编译：[`wiki-book-ingest`](../wiki-book-ingest/SKILL.md)
- 知识库结构：[`karpathy-wiki`](../karpathy-wiki/SKILL.md)
- MinerU 细节：pdf-converter（仅路径 A 参考）
