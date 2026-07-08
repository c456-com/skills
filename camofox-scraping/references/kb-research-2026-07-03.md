# 知识库市场调研 —— 数据源与发现（2026-07-03）

## 已抓取数据源（12/12 全部完成）

### 定价页面（🟢）
| 数据源 | URL | 关键发现 |
|--------|-----|---------|
| Outline | getoutline.com/pricing | 云端 $10/79/249/月，BSL 自托管免费 |
| AFFiNE | affine.pro/pricing | Free/Pro $6.75/月/Team $10/座/月，Believer $499.99 终身，自托管免费 |
| 思源 | b3log.org/siyuan/pricing | 免费 / 终身 ¥96 / 年付 ¥148 / 团队 ¥148/年，8GB 云存储 |

### 对比文章（🟢）
| 数据源 | URL | 内容 |
|--------|-----|------|
| selfhosting.sh | selfhosting.sh/best/wiki/ | 7 款 Wiki 对比（Wiki.js、BookStack、DokuWiki、MediaWiki、XWiki、Outline、Docmost） |
| Docsio | docsio.co/blog/free-knowledge-base-software | 9 款免费知识库对比，SaaS/开源分类 |
| Geekflare | geekflare.com/software/self-hosted-wiki-software/ | 7 款 Wiki 对比（Wiki.js、DokuWiki、MediaWiki、XWiki、BookStack、Gollum、Outline） |
| Contabo | contabo.com/blog/how-to-set-up-a-self-hosted-wiki-complete-guide/ | 部署指南 + 软件选择 |

### 社区讨论（🟢）
| 数据源 | URL | 互动数据 | 关键信息 |
|--------|-----|---------|---------|
| HN | news.mcan.sh/item/48053163 | 16 赞，21 条评论 | Obsidian/Outline/BookStack/Trilium/Joplin；移动端应用很重要 |
| 知乎 #1 | zhihu.com/question/645107504 | 17 个回答，3.1 万浏览 | 飞书+Obsidian 双链；10 年工具对比表 |
| 知乎 #2 | zhihu.com/question/15133096760 | 24 个回答，8500 浏览 | AnythingLLM+Ollama+Qwen3 RAG；知识结构方法论 |

### 需要登录的数据源（🔴→🟢 通过 Camofox 有头模式登录）
| 数据源 | 方式 | 关键发现 |
|--------|------|---------|
| 小红书 个人知识库 | Camofox 有头模式登录 + 持久化 | 30+ 条关于 AI 知识库搭建的帖子（Codex+Obsidian、DeepSeek+Notion、LLM Wiki），变现趋势，"第二大脑"概念流行 |

### 已屏蔽（❌）
| 数据源 | 原因 |
|--------|------|
| Reddit（3 篇帖子） | Cloudflare 机器人检测 —— CamoFox 被识别为机器人；需要代理或 Cookie 导入 |

## 持久化验证（2026-07-03）

- **已验证**：在 pkill 之前执行 DELETE /sessions/:userId 会触发 storageState 检查点保存
- **Profile**：kb-researcher → ~/.camofox/profiles/ea62cc266effacda9e8324513feab0dc/storage-state.json（35KB）
- **知乎登录在重启后保留**：✅ 已确认
- **小红书登录在重启后保留**：✅ 已确认（同一会话生命周期）

## 关键市场洞察

1. **自托管知识库市场**：Outline 和 AFFiNE 提供 BSL/免费自托管但付费云服务。思源终身定价 ¥96 —— 价格点非常低。
2. **AI 集成趋势**：知乎回答显示对本地 RAG（AnythingLLM+Ollama+Qwen3）的强烈兴趣。AI 增强的个人知识库正在兴起。
3. **移动端优先需求**：HN 和知乎用户一致认为移动端应用是个人 Wiki 使用的必备条件。
4. **Markdown 作为标准**：Obsidian 的 Markdown 优先方案在所有社区中占据主导偏好。
5. **知识结构方法论**：中国用户（知乎）强调系统化知识组织 —— 思维导图、矩阵框架、知识树。
6. **小红书变现焦点**：中国创作者积极构建"知识库 + 变现"系统；AI 工具（Codex、DeepSeek）用于知识库搭建是热门内容。
