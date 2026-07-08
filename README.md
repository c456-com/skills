# c456 Skills

C456 系列技能库。安装与更新统一使用 **[Vercel `npx skills`](https://github.com/vercel-labs/skills)**（GitHub 为技能源）。

## 技能列表

### 🧰 通用技能

非 C456 绑定的通用技能，可复用于任意项目。

| 名称 | 说明 |
|------|------|
| [llm-wiki](llm-wiki/SKILL.md) | 卡帕西 LLM Wiki / knowledge base — 互联 Markdown 知识摄取、搜索、查询与维护 |
| [llm-wiki-domains](llm-wiki-domains/SKILL.md) | 多领域 LLM Wiki / meta-wiki — 多主题隔离知识库、跨领域路由与根层导航 |
| [book-extract](book-extract/SKILL.md) | 书籍素材提取 — PDF、扫描件、拍照书页、OCR → `raw/books/`（MinerU 或视觉） |
| [wiki-book-ingest](wiki-book-ingest/SKILL.md) | 书籍知识摄取 — `raw/books/` → llm-wiki 概念、来源、线索与章节检查 |
| [tmux-cursor-agent](tmux-cursor-agent/SKILL.md) | Cursor Agent over tmux — 状态检测、四步消息协议、取消执行、监控 daemon |
| [tmux-pane-workspace](tmux-pane-workspace/SKILL.md) | Tmux pane workspace — pane 聚焦缩放、多 pane 布局、圆桌会议、职业角色来源与会议日志 |
| [doc-driven-multi-agent](doc-driven-multi-agent/SKILL.md) | 文档驱动多代理协作 — 角色 SOP、handoff 三要素、G0-G4 门禁、越界拒绝 |
| [camofox-scraping](camofox-scraping/SKILL.md) | CamoFox scraping — 抓取 Cloudflare / 反爬页面，失败时回退 web_search |
| [product-niche-discovery](product-niche-discovery/SKILL.md) | 产品赛道发现 — 52 渠道找赛道、挖痛点、抓竞品/差评/定价原始材料 |
| [short-viral-content](short-viral-content/SKILL.md) | 短视频爆款内容 — 小红书、抖音、视频号标题、关键词、描述与话题标签 |
| [c456-team-work](c456-team-work/SKILL.md) | 辉常团队工作流 — 多角色 AI Agent 团队入口、职业角色选择、handoff/relay、通知与开发闭环 |
| [llm-wiki-versioned](llm-wiki-versioned/SKILL.md) | LLM Wiki 版本化 — `.versioned/` 快照、旧结论回溯、版本对比、provenance |
| [c456-software-dev-sop](c456-software-dev-sop/SKILL.md) | 软件开发 SOP — 需求、调研、兼容性评估、编码、测试、文档同步与验收 |

### 🏢 C456 通用技能

与 C456 业务绑定的技能。

| 名称 | 说明 |
|------|------|
| [c456-cli](c456-cli/SKILL.md) | C456 CLI / c456.com 操作 — intake、playbook、assets、搜索、截图上传与 API 工作流 |
| [c456-llm-wiki](c456-llm-wiki/SKILL.md) | C456 LLM Wiki 扩展 — 给 `llm-wiki` 后接 `c456-sync/`，支持引用型镜像、版本绑定、发布与拉取 |
| [c456-product-channel-article](c456-product-channel-article/SKILL.md) | C456 产品/渠道长文 — tool/channel 介绍、公众号渠道稿、五段式产品叙事 |
| [c456-signal-product-vs](c456-signal-product-vs/SKILL.md) | C456 产品对比 signal — tool vs tool、选型建议、竞品差异与信息源分层 |
| [c456-signal-researcher](c456-signal-researcher/SKILL.md) | C456 signal 研究写作 — 新闻收录、行业动态、事实核验、来源块与站内关联 |
| [c456-sync-public-markdown](c456-sync-public-markdown/SKILL.md) | C456 public Markdown — `c456-sync/` 对外正文、frontmatter 剥离与发布格式检查 |
| [c456-playbook-publishing](c456-playbook-publishing/SKILL.md) | C456 playbook 发布 — 长文写作、配图上传、字数校验、CLI 发布与本地元数据同步 |
| [c456-rails-startup](c456-rails-startup/SKILL.md) | Rails startup — Rails + Inertia + React + shadcn/ui 从零脚手架与 hello-world 验证 |

### 📦 第三方技能

第三方技能从上游仓库安装。下表路径便于在本仓库浏览；安装见上方「第三方技能」。

来自 [phuryn/pm-skills](https://github.com/phuryn/pm-skills) 的产品管理技能包，共 68 个技能。

#### pm-ai-shipping（AI 交付）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-ai-shipping/intended-vs-implemented](pm-skills/pm-ai-shipping/skills/intended-vs-implemented/SKILL.md) | 找出系统预期行为与代码实际行为之间差距的方法——通用扫描器因缺乏意图模型而漏掉的 bug 类型。定义何为文档化意图、何为实现证据、哪些不一致值得关注，以及如何避免空泛结论。 |
| [pm-skills/pm-ai-shipping/shipping-artifacts](pm-skills/pm-ai-shipping/skills/shipping-artifacts/SKILL.md) | 让 AI 构建（vibe-coded）应用在上线前可审查的持久文档集。每个应用都需要的小型核心——架构、用户/权限流、权限、变量/密钥、测试覆盖图——以及按需追加的条件文档：邮件、定时任务、SEO、嵌入式 Agent/自动化。定义每份文档应捕获什么、审查者如何使用。 |

#### pm-data-analytics（数据分析）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-data-analytics/ab-test-analysis](pm-skills/pm-data-analytics/skills/ab-test-analysis/SKILL.md) | 分析 A/B 测试结果：统计显著性、样本量验证、置信区间，以及上线/延长/停止建议。 |
| [pm-skills/pm-data-analytics/cohort-analysis](pm-skills/pm-data-analytics/skills/cohort-analysis/SKILL.md) | 对用户活跃数据做群组（cohort）分析——留存曲线、功能采用趋势、分群洞察。 |
| [pm-skills/pm-data-analytics/sql-queries](pm-skills/pm-data-analytics/skills/sql-queries/SKILL.md) | 根据自然语言描述生成 SQL 查询。支持 BigQuery、PostgreSQL、MySQL 等方言；可读取上传的 schema 图或文档。 |

#### pm-execution（执行与交付）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-execution/brainstorm-okrs](pm-skills/pm-execution/skills/brainstorm-okrs/SKILL.md) | 头脑风暴与公司目标对齐的团队级 OKR——定性目标 + 可量化关键结果。 |
| [pm-skills/pm-execution/create-prd](pm-skills/pm-execution/skills/create-prd/SKILL.md) | 用 8 段式模板撰写产品需求文档（PRD），覆盖问题、目标、用户群、价值主张、方案与发布计划。 |
| [pm-skills/pm-execution/dummy-dataset](pm-skills/pm-execution/skills/dummy-dataset/SKILL.md) | 生成逼真的测试用假数据集，可自定义列、约束与输出格式（CSV、JSON、SQL、Python 脚本）。 |
| [pm-skills/pm-execution/job-stories](pm-skills/pm-execution/skills/job-stories/SKILL.md) | 用「当 [情境]，我想 [动机]，以便 [结果]」格式撰写 Job Story，附详细验收标准。 |
| [pm-skills/pm-execution/outcome-roadmap](pm-skills/pm-execution/skills/outcome-roadmap/SKILL.md) | 将产出导向的路标转为成果导向，传达战略意图；把举措改写为反映用户与业务影响的结果陈述。 |
| [pm-skills/pm-execution/pre-mortem](pm-skills/pm-execution/skills/pre-mortem/SKILL.md) | 对 PRD 或上线计划做事前复盘（pre-mortem）风险分析。将风险分为真虎（真实问题）、纸虎（夸大担忧）、大象（未说出口的顾虑），并标注为阻塞上线、快速跟进或持续跟踪。 |
| [pm-skills/pm-execution/prioritization-frameworks](pm-skills/pm-execution/skills/prioritization-frameworks/SKILL.md) | 9 种优先级框架参考指南：公式、适用场景与模板——RICE、ICE、Kano、MoSCoW、机会得分等。 |
| [pm-skills/pm-execution/release-notes](pm-skills/pm-execution/skills/release-notes/SKILL.md) | 从工单、PRD 或变更日志生成面向用户的发布说明，按新功能、改进、修复等分类组织。 |
| [pm-skills/pm-execution/retro](pm-skills/pm-execution/skills/retro/SKILL.md) | 主持结构化 Sprint 回顾——做得好的、待改进的，以及带负责人与截止日的优先级行动项。 |
| [pm-skills/pm-execution/sprint-plan](pm-skills/pm-execution/skills/sprint-plan/SKILL.md) | 规划 Sprint：容量估算、Story 选取、依赖梳理与风险识别。 |
| [pm-skills/pm-execution/stakeholder-map](pm-skills/pm-execution/skills/stakeholder-map/SKILL.md) | 用权力/利益矩阵绘制干系人地图，为各象限制定沟通策略并生成沟通计划。 |
| [pm-skills/pm-execution/strategy-red-team](pm-skills/pm-execution/skills/strategy-red-team/SKILL.md) | 对 PRD、路标或战略做红队演练，在现实打脸前攻击其承重假设。先善意重构再攻击每条主张，按影响×概率×验证成本排序失败模式，给出最便宜的验证方式与终止条件。 |
| [pm-skills/pm-execution/summarize-meeting](pm-skills/pm-execution/skills/summarize-meeting/SKILL.md) | 将会议录音/转写整理为结构化纪要：日期、参与者、议题、关键决策、要点与行动项。 |
| [pm-skills/pm-execution/test-scenarios](pm-skills/pm-execution/skills/test-scenarios/SKILL.md) | 从用户故事生成完整测试场景：测试目标、初始条件、角色、逐步操作与预期结果。 |
| [pm-skills/pm-execution/user-stories](pm-skills/pm-execution/skills/user-stories/SKILL.md) | 按 3C（Card、Conversation、Confirmation）与 INVEST 原则撰写用户故事，含描述、设计链接与验收标准。 |
| [pm-skills/pm-execution/wwas](pm-skills/pm-execution/skills/wwas/SKILL.md) | 用 Why-What-Acceptance 格式创建产品待办条目——独立、有价值、可测试，并附战略上下文。 |

#### pm-go-to-market（上市策略）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-go-to-market/beachhead-segment](pm-skills/pm-go-to-market/skills/beachhead-segment/SKILL.md) | 识别产品上线的首个滩头市场细分。按痛点强度、付费意愿、可赢市场份额与转介绍潜力评估各细分。 |
| [pm-skills/pm-go-to-market/competitive-battlecard](pm-skills/pm-go-to-market/skills/competitive-battlecard/SKILL.md) | 制作可交付销售的竞争作战卡片，对比自家产品与特定竞品——定位、功能对比、异议处理与赢/输模式。 |
| [pm-skills/pm-go-to-market/growth-loops](pm-skills/pm-go-to-market/skills/growth-loops/SKILL.md) | 识别可持续牵引力的增长闭环（飞轮）。评估 5 类：病毒、使用、协作、用户生成内容与推荐。 |
| [pm-skills/pm-go-to-market/gtm-motions](pm-skills/pm-go-to-market/skills/gtm-motions/SKILL.md) | 在 7 类 GTM 动作中识别最佳策略与工具：Inbound、Outbound、付费数字、社区、合作伙伴、ABM、PLG。 |
| [pm-skills/pm-go-to-market/gtm-strategy](pm-skills/pm-go-to-market/skills/gtm-strategy/SKILL.md) | 制定上市（GTM）战略：营销渠道、信息传递、成功指标与上线时间线。 |
| [pm-skills/pm-go-to-market/ideal-customer-profile](pm-skills/pm-go-to-market/skills/ideal-customer-profile/SKILL.md) | 从研究数据识别理想客户画像（ICP）：人口统计、行为、JTBD 与需求。 |

#### pm-market-research（市场研究）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-market-research/competitor-analysis](pm-skills/pm-market-research/skills/competitor-analysis/SKILL.md) | 分析竞品优劣势与差异化机会，识别直接竞品并绘制竞争格局。 |
| [pm-skills/pm-market-research/customer-journey-map](pm-skills/pm-market-research/skills/customer-journey-map/SKILL.md) | 绘制端到端客户旅程图：阶段、触点、情绪、痛点与机会点。 |
| [pm-skills/pm-market-research/market-segments](pm-skills/pm-market-research/skills/market-segments/SKILL.md) | 识别 3–5 个潜在客户细分，含人口统计、JTBD 与产品契合度分析。 |
| [pm-skills/pm-market-research/market-sizing](pm-skills/pm-market-research/skills/market-sizing/SKILL.md) | 用自上而下与自下而上方法估算 TAM、SAM、SOM 市场规模。 |
| [pm-skills/pm-market-research/sentiment-analysis](pm-skills/pm-market-research/skills/sentiment-analysis/SKILL.md) | 分析用户反馈数据，识别带情感得分、JTBD 与产品满意度洞察的细分群。 |
| [pm-skills/pm-market-research/user-personas](pm-skills/pm-market-research/skills/user-personas/SKILL.md) | 从研究数据提炼 3 个用户画像：JTBD、痛点、收益与意外洞察。 |
| [pm-skills/pm-market-research/user-segmentation](pm-skills/pm-market-research/skills/user-segmentation/SKILL.md) | 基于行为、JTBD 与需求对反馈数据中的用户分群，至少识别 3 个独立细分。 |

#### pm-marketing-growth（营销增长）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-marketing-growth/marketing-ideas](pm-skills/pm-marketing-growth/skills/marketing-ideas/SKILL.md) | 生成 5 个创意且低成本的营销点子，含渠道、信息与互动理由。 |
| [pm-skills/pm-marketing-growth/north-star-metric](pm-skills/pm-marketing-growth/skills/north-star-metric/SKILL.md) | 定义北极星指标及 3–5 个支撑输入指标（指标星座）。区分业务类型（注意力、交易、生产力），并按 7 条标准校验北极星有效性。 |
| [pm-skills/pm-marketing-growth/positioning-ideas](pm-skills/pm-marketing-growth/skills/positioning-ideas/SKILL.md) | 头脑风暴与竞品差异化的产品定位思路，识别主要竞品并生成定位陈述与理由。 |
| [pm-skills/pm-marketing-growth/product-name](pm-skills/pm-marketing-growth/skills/product-name/SKILL.md) | 头脑风暴 5 个独特、易记的产品名，附与品牌价值观和目标受众对齐的理由。 |
| [pm-skills/pm-marketing-growth/value-prop-statements](pm-skills/pm-marketing-growth/skills/value-prop-statements/SKILL.md) | 从已有价值主张生成适用于营销、销售与新用户引导的价值主张表述。 |

#### pm-product-discovery（产品发现）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-product-discovery/analyze-feature-requests](pm-skills/pm-product-discovery/skills/analyze-feature-requests/SKILL.md) | 按主题、战略对齐、影响、工作量与风险分析并优先级排序功能需求列表。 |
| [pm-skills/pm-product-discovery/brainstorm-experiments-existing](pm-skills/pm-product-discovery/skills/brainstorm-experiments-existing/SKILL.md) | 为现有产品设计验证假设的实验——原型、A/B 测试、Spike 等低成本方法。 |
| [pm-skills/pm-product-discovery/brainstorm-experiments-new](pm-skills/pm-product-discovery/skills/brainstorm-experiments-new/SKILL.md) | 为新产品设计精益创业实验（pretotype）：XYZ 假设 + 落地页、讲解视频、预售等低成本验证方式。 |
| [pm-skills/pm-product-discovery/brainstorm-ideas-existing](pm-skills/pm-product-discovery/skills/brainstorm-ideas-existing/SKILL.md) | 从 PM、设计师、工程师多视角为现有产品头脑风暴产品/功能想法。 |
| [pm-skills/pm-product-discovery/brainstorm-ideas-new](pm-skills/pm-product-discovery/skills/brainstorm-ideas-new/SKILL.md) | 从 PM、设计师、工程师多视角为新产品初期发现阶段头脑风暴功能想法。 |
| [pm-skills/pm-product-discovery/identify-assumptions-existing](pm-skills/pm-product-discovery/skills/identify-assumptions-existing/SKILL.md) | 从价值、可用性、可行性与可实施性四维度识别现有产品功能想法的风险假设，采用多视角「魔鬼代言人」思考。 |
| [pm-skills/pm-product-discovery/identify-assumptions-new](pm-skills/pm-product-discovery/skills/identify-assumptions-new/SKILL.md) | 从 8 类风险（含 GTM、战略、团队等）识别新产品想法的风险假设。 |
| [pm-skills/pm-product-discovery/interview-script](pm-skills/pm-product-discovery/skills/interview-script/SKILL.md) | 撰写结构化客户访谈脚本：JTBD 探询、暖场、核心探索与收尾。遵循 The Mom Test——无诱导提问、不推销、聚焦过往行为。 |
| [pm-skills/pm-product-discovery/metrics-dashboard](pm-skills/pm-product-discovery/skills/metrics-dashboard/SKILL.md) | 定义并设计产品指标看板：关键指标、数据源、可视化类型与告警阈值。 |
| [pm-skills/pm-product-discovery/opportunity-solution-tree](pm-skills/pm-product-discovery/skills/opportunity-solution-tree/SKILL.md) | 构建机会-方案树（OST）结构化产品发现——将期望成果映射到机会、方案与实验。基于 Teresa Torres《Continuous Discovery Habits》。 |
| [pm-skills/pm-product-discovery/prioritize-assumptions](pm-skills/pm-product-discovery/skills/prioritize-assumptions/SKILL.md) | 用影响×风险矩阵对假设排序，并为每条建议验证实验。 |
| [pm-skills/pm-product-discovery/prioritize-features](pm-skills/pm-product-discovery/skills/prioritize-features/SKILL.md) | 按影响、工作量、风险与战略对齐对功能想法待办列表排序，给出 Top 5 建议。 |
| [pm-skills/pm-product-discovery/summarize-interview](pm-skills/pm-product-discovery/skills/summarize-interview/SKILL.md) | 将客户访谈转写整理为结构化模板：JTBD、满意度信号与行动项。 |

#### pm-product-strategy（产品战略）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-product-strategy/ansoff-matrix](pm-skills/pm-product-strategy/skills/ansoff-matrix/SKILL.md) | 生成 Ansoff 矩阵分析，映射市场渗透、市场开发、产品开发与多元化等增长策略。 |
| [pm-skills/pm-product-strategy/business-model](pm-skills/pm-product-strategy/skills/business-model/SKILL.md) | 生成含 9 大构建块的商业模式画布（Business Model Canvas）。 |
| [pm-skills/pm-product-strategy/lean-canvas](pm-skills/pm-product-strategy/skills/lean-canvas/SKILL.md) | 生成精益画布：问题、方案、指标、成本结构、UVP、不公平优势、渠道、细分与收入。 |
| [pm-skills/pm-product-strategy/monetization-strategy](pm-skills/pm-product-strategy/skills/monetization-strategy/SKILL.md) | 头脑风暴 3–5 种变现策略，含受众契合度、风险与验证实验。 |
| [pm-skills/pm-product-strategy/pestle-analysis](pm-skills/pm-product-strategy/skills/pestle-analysis/SKILL.md) | 做 PESTLE 宏观分析：政治、经济、社会、技术、法律与环境因素。 |
| [pm-skills/pm-product-strategy/porters-five-forces](pm-skills/pm-product-strategy/skills/porters-five-forces/SKILL.md) | 做 Porter 五力分析：同业竞争、供应商议价、买方议价、替代品威胁与新进入者威胁。 |
| [pm-skills/pm-product-strategy/pricing-strategy](pm-skills/pm-product-strategy/skills/pricing-strategy/SKILL.md) | 分析与设计定价策略：定价模型、竞品定价、支付意愿估算与价格弹性。 |
| [pm-skills/pm-product-strategy/product-strategy](pm-skills/pm-product-strategy/skills/product-strategy/SKILL.md) | 用 9 段式产品战略画布制定全面产品战略——愿景、细分、成本、价值主张、权衡、指标、增长、能力与护城河。 |
| [pm-skills/pm-product-strategy/product-vision](pm-skills/pm-product-strategy/skills/product-vision/SKILL.md) | 头脑风暴鼓舞人心、可实现且带情感共鸣的产品愿景，激励团队并对齐干系人。 |
| [pm-skills/pm-product-strategy/startup-canvas](pm-skills/pm-product-strategy/skills/startup-canvas/SKILL.md) | 为新产品的战略（9 段）与商业模式（成本+收入）生成创业画布，是 BMC/精益画布的替代方案，将战略与商业模式分离。 |
| [pm-skills/pm-product-strategy/swot-analysis](pm-skills/pm-product-strategy/skills/swot-analysis/SKILL.md) | 做详细 SWOT 分析——优势、劣势、机会与威胁，并给出可执行建议。 |
| [pm-skills/pm-product-strategy/value-proposition](pm-skills/pm-product-strategy/skills/value-proposition/SKILL.md) | 用 6 段 JTBD 模板设计详细价值主张——谁、为何、之前怎样、如何、之后怎样、替代方案。 |

#### pm-toolkit（工具箱）

| 名称 | 说明 |
|------|------|
| [pm-skills/pm-toolkit/draft-nda](pm-skills/pm-toolkit/skills/draft-nda/SKILL.md) | 起草双方保密协议（NDA）详细草案：信息类型、司法辖区及需法务审核的条款。 |
| [pm-skills/pm-toolkit/grammar-check](pm-skills/pm-toolkit/skills/grammar-check/SKILL.md) | 识别文本中的语法、逻辑与行文问题，给出针对性修改建议，不重写全文。 |
| [pm-skills/pm-toolkit/privacy-policy](pm-skills/pm-toolkit/skills/privacy-policy/SKILL.md) | 起草详细隐私政策：数据类型、司法辖区、GDPR 与合规考量及需法务审核的条款。 |
| [pm-skills/pm-toolkit/review-resume](pm-skills/pm-toolkit/skills/review-resume/SKILL.md) | 全面 PM 简历审阅与定制：10 项最佳实践，含 XYZ+S 公式、关键词优化、岗位定制与结构。 |

## 安装

在**项目根目录**执行（会写入对应 Agent 的技能目录并生成 `skills-lock.json`）：

```bash
# 列出本仓库所有技能
npx skills add c456-com/skills -l

# 安装单个（CLI 会询问或自动识别当前 Agent，勿手写 -a）
npx skills add c456-com/skills --skill llm-wiki -y
npx skills add c456-com/skills --skill llm-wiki-domains -y

# 一次装全部
npx skills add c456-com/skills --all -y
```

### 第三方技能

第三方技能从上游仓库安装。安装时使用**技能短名**（如 `create-prd`），而非仓库内路径（如 `pm-skills/pm-execution/create-prd`）：

```bash
# 列出 PM 技能包内全部 68 个技能
npx skills add phuryn/pm-skills -l

# 安装单个
npx skills add phuryn/pm-skills --skill create-prd -y

# 一次装全部
npx skills add phuryn/pm-skills --all -y
```

未加 `-a` 时：`npx skills` 根据环境交互选择 Agent（Cursor、Claude Code、Codex 等），或由执行安装的 AI 代为判断。仅当用户明确指定某 Agent 时才加 `-a <agent>`。

`skills-lock.json` 可提交到 Git，团队对齐同一版本。

不安装、仅对话里读 GitHub 原文亦可（见各技能 `SKILL.md` 链接）。

## 更新

```bash
npx skills check              # 查看哪些技能有更新
npx skills update -y          # 更新全部已安装技能
npx skills update llm-wiki-domains -y   # 只更新一个
```

从锁文件还原（类似 `npm ci`）：

```bash
npx skills experimental_install
```

## 维护（仓库维护者）

### 添加第三方技能包

其他开源技能或技能包以 git submodule 形式引入到仓库根目录，与本地技能平级：

```bash
# 引用单个技能
git submodule add <repo-url> <skill-name>

# 引用技能包（多个技能）
git submodule add <repo-url> <pack-name>
```

引入后可在 `registry.json` 注册个别技能以支持 `npx skills add c456-com/skills` 发现；未注册的技能仍从上游仓库（如 `phuryn/pm-skills`）安装。

克隆含 submodule 的仓库时：

```bash
git clone --recurse-submodules <repo-url>
# 或已克隆后
git submodule update --init --recursive
```

更新 submodule 到上游最新：

```bash
git submodule update --remote <pack-name>
```
