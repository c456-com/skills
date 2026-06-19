# book-extract

PDF / 拍照 → `raw/books/`。**识别方式由你选**，Agent 不自动替你做决定。

技能目录：<https://github.com/c456-com/skills/tree/main/book-extract>

## 快速开始

```
请用 npx skills 安装 c456-com/skills 的 book-extract（未安装则先安装；缺 wiki-book-ingest / karpathy-wiki 也一并安装），
帮我把这本 PDF 录入 domains/stock-trading。
先问我用 MinerU 还是视觉大模型识别，我选视觉的话再问 agent_native 还是本地千问/外部 API。
展示预览后我确认再执行。
```

## PDF：两种方式（你选，不自动推荐）

| 方式 | 说明 |
|------|------|
| **MinerU** | 免费本地，偏文字与表格 |
| **视觉大模型** | 偏识图与版式；**即使 MinerU 能转 PDF，你也可以选视觉**（例如本地千问 3.6） |

拍照：仅视觉。

## 视觉：三种落地

| 模式 | 说明 |
|------|------|
| **agent_native** | 执行技能的 AI 自己 Read 读图 |
| **external_api + 本地千问** | LM Studio `http://127.0.0.1:1234/v1` + `vision_openai_compatible.py` |
| **external_api + 云端** | OpenAI / Anthropic 等，走标准脚本 |

本地千问配置示例：[`references/book-extract.example-qwen-local.json`](references/book-extract.example-qwen-local.json)

```bash
cp references/book-extract.example-qwen-local.json .config/book-extract.json
# BOOK_EXTRACT_PATH=$(npx skills list --json 中 book-extract 的 path)
python3 "$BOOK_EXTRACT_PATH/scripts/vision_openai_compatible.py" --project-root . --images-dir work/pages --output-dir domains/.../pages --resume
```

## 配置

```bash
mkdir -p .config
cp references/book-extract.example.json .config/book-extract.json
# 或千问本地：cp references/book-extract.example-qwen-local.json .config/book-extract.json
```

`.config/` 加入 `.gitignore`。

## 安装

```bash
npx skills add c456-com/skills --skill book-extract -y
npx skills update book-extract -y
```

## 流水线

Agent 会按 [skill-install.md](references/skill-install.md) 缺则安装：

1. **karpathy-wiki**
2. **book-extract**
3. **wiki-book-ingest**
