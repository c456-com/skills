# book-extract

PDF / 拍照 → `raw/books/`。**不试跑、不自动判断** — Agent 直接问你选哪种方式；可提供 [自行判断参考](references/method-choice-guide.md)，但不替你做决定。

技能目录：<https://github.com/c456-com/skills/tree/main/book-extract>

## 快速开始

```
请用 npx skills 安装 c456-com/skills 的 book-extract（未安装则先安装；缺 wiki-book-ingest / llm-wiki-domains 也一并安装），
帮我把这本 PDF 录入 domains/stock-trading。
必须先直接问我选 MinerU（A）还是视觉（B），可附自行判断说明，但不要试跑 PDF 或替我决定；选 B 时再问 agent_native 还是 external_api。
展示预览后我确认再执行。
```

## PDF：直接选方式（不试跑）

| 方式 | 说明 |
|------|------|
| **MinerU** | 免费本地，偏文字与表格 |
| **视觉大模型** | 偏识图与版式 |

不确定怎么选？看 [method-choice-guide.md](references/method-choice-guide.md) **自己对照 PDF 特点**；Agent 不试跑、不自动判断、不说「建议用某某」。

拍照：仅视觉；预处理目录同为 `.tmp/book-extract/<book-name>/photos/`。

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
python3 "$BOOK_EXTRACT_PATH/scripts/vision_openai_compatible.py" --project-root . --images-dir .tmp/book-extract/<book-name>/pages --output-dir domains/.../pages --resume
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

1. **llm-wiki-domains**
2. **book-extract**
3. **wiki-book-ingest**
