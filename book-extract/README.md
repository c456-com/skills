# book-extract

PDF / 拍照 → `raw/books/` 素材提取。MinerU（免费）或视觉大模型（Agent 自识别 / 外部 API 标准脚本）。

技能目录：<https://github.com/c456-com/skills/tree/main/book-extract>

## 快速开始

```
请从 https://github.com/c456-com/skills/tree/main/book-extract 读取 book-extract 技能，
帮我把这本 PDF 录入 domains/stock-trading，先探测质量、推荐路径，展示预览后我确认再执行。
```

## 两条提取路径

| 路径 | 成本 | 适用 |
|------|------|------|
| **MinerU** | 免费（本地） | 电子版 PDF、表格公式 |
| **视觉大模型** | 订阅或 API | 扫描件、K 线图、拍照 |

## 视觉识图两种方式

| 模式 | 说明 |
|------|------|
| **agent_native** | 执行技能的 AI 自己读图写 `page-*.md`，无需 API Key |
| **external_api** | 调用 `scripts/vision_*.py`，**禁止 AI 临时写 API 代码** |

## 配置

项目根 `.config/book-extract.json`（**git 忽略**）：

```bash
mkdir -p .config
cp references/book-extract.example.json .config/book-extract.json
# 编辑 vision_mode、api_key 等
```

根目录 `.gitignore` 增加：

```
.config/
```

## 外部 API 脚本

```bash
# OpenAI 兼容（含 OpenRouter、LM Studio 本地）
python3 scripts/vision_openai_compatible.py \
  --project-root . \
  --images-dir ./work/pages \
  --output-dir domains/my-book/raw/books/my-book/pages \
  --resume

# Anthropic
python3 scripts/vision_anthropic.py --project-root . ...
```

## 安装

```bash
npx skills add c456-com/skills --skill book-extract -y
npx skills update book-extract -y   # GitHub 更新后同步
```

## 流水线

1. [`karpathy-wiki`](../karpathy-wiki/README.md) — 初始化 `domains/<name>/`
2. **book-extract** — PDF/拍照 → `raw/books/`
3. [`wiki-book-ingest`](../wiki-book-ingest/README.md) — raw → wiki
4. `karpathy-wiki` — Query / Lint
