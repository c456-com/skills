# 每日内容策展 Cron 任务

## 任务配置

Cron job `c456-daily-curation` (job_id: d2d568de4207)
- 排期：每天 7:00 (0 7 * * *)
- 技能：c456-voice-journalist, c456-write, c456-curation-philosophy
- 工具集：terminal, file, web
- 投递：all（通过 yuanbao gateway，但 WebSocket 竞态问题可能导致投递失败——产出始终存入 signal 草稿）
- 版本：v7（2026-07-30，三轨并行版）
- 前序版本：v4（旧策展）→ v5（GEO/AIO 聚焦）→ v6（来源多样化 + blogwatcher feed 修复）→ v7（三轨并行）

## 任务流程

全自动执行：按客户画像采集 RSS → 按三轨道分类精选 → 逐条读原文 → 溯源验证 → 建信号草稿（不公开）→ 推送清单给用户。

**三轨并行原则（v7 核心变更）：**
- **轨道 1（GEO/AIO 实操，必选 5-8 条）**：检验标准「能帮中小品牌直接动手做什么」
- **轨道 2（格局信号，可选 0-5 条）**：检验标准「如果成立，我们之前的什么假设会变化」
- **轨道 3（材料储备，可选 0-3 条）**：检验标准「能成为未来哪个主题的来源」
- 信号正文只包含轨道 1，轨道 2 以额外清单推送，轨道 3 只进 raw/素材库

**来源多样化规则：**
- 轨道 1 必须覆盖 ≥2 个不同品类（A-F）
- 轨道 2 和轨道 3 可使用品类 G（不限来源）
- 单个域名不超过 4 条

**客户画像驱动：** cron prompt 内嵌客户画像摘要，筛选规则和关键词随画像变化。

参见 `c456-curation-philosophy` 技能 §1.4（三轨框架）和 `c456-write` 技能 §D 每日信息策展。

## 踩坑记录

| 坑 | 说明 |
|----|------|
| 误把每条信息建为独立信号 | 应是**一条**信号包含全部条目，不是每条一个信号 |
| 投放投递不达 | deliver=all；但 yuanbao WS 竞态可能导致 `get_active_adapter()` 返回 None |
| **投递配置被改成 `all`（2026-07 多次踩坑）** | cron 的 `deliver` 字段可能在某次 `update` 操作中被改成 `all`，而 `deliver=all` 在没有多平台 home channel 时解析失败（`no delivery target resolved for deliver=all`），任务跑了但用户永远收不到。**症状：`last_status=ok` 但 `last_delivery_error` 非空。修复：`cronjob update --deliver origin`。每次更新 cron 后必须 `cronjob action='list'` 检查 `deliver` 是否为 `origin`。** |
| **web_search 在 cron 中不可用** | 曾导致 cron 卡在 `web_search` 并发调用超时（`idle for 800s limit 600s`）整日无产出。策展 cron 一律用 `curl -sL <URL>` 读原文，**不要在 cron prompt 中要求 web_search**。 |
| 忘了阅读原文就写摘要 | 必须 curl 获取正文后撰写，不可凭标题写 |
| 社区帖直接引用 | Tier 2 源发现热点后，必须溯源到官方/权威源再引用 |
| **blogwatcher feed_url 为空** | 首次配置后检查 blogwatcher db：`SELECT id, name, feed_url FROM blogs WHERE feed_url IS NULL OR feed_url=''`。无 feed_url 的源靠 scrap 首页不会产出内容。修复后需手动跑一次 scan 确认。 |
| **cron prompt 被意外覆盖** | cron job 的 prompt 字段可能在另一会话中被更新。修改后应 `cronjob action='list'` 确认 `prompt_preview` 正确。 |
| **来源单一化** | 当 blogwatcher 产出不足时，agent 会 fallback 到 prompt 中列出的源。如果这些源太少或同质化，每日结果将来自同一域名。v7 通过三轨道和品类 G 扩展信息面。 |
| **信息面变窄（v7 新增）** | 当用户反馈「信息面越来越窄」「怎么都是这些」，问题不在筛选规则，在策展框架本身。启动框架级自检：当前运行了几条轨道？轨道 2 是否覆盖了品类之外的来源？详见 c456-curation-philosophy §9.2。 |

## 来源品类（A-G 分类）

### 品类 A — GEO / AI 搜索优化（核心）
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| Search Engine Land | https://searchengineland.com/feed | 35 |
| Moz Blog | https://moz.com/blog/feed | 34 |
| Search Engine Journal | https://searchenginejournal.com/feed | 36 |
| Google Search Central | https://developers.google.com/search/blog/feed.xml | 46 |
| Perplexity Blog | https://blog.perplexity.ai/feed.xml | 45 |

### 品类 B — 品牌营销 / 内容策略
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| Content Marketing Institute | https://contentmarketinginstitute.com/feed/ | 41 |
| HubSpot Marketing | https://blog.hubspot.com/marketing/feed | 42 |
| Animalz | https://www.animalz.co/feed/ | 43 |
| SparkToro | https://sparktoro.com/blog/feed/ | 47 |
| Neil Patel | https://feeds.feedburner.com/neilpatel | 37 |

### 品类 C — AI 行业动态
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| TechCrunch | https://techcrunch.com/feed/ | 24 |
| VentureBeat AI | https://venturebeat.com/category/ai/feed/ | 26 |
| Ars Technica | https://feeds.arstechnica.com/arstechnica/index | 25 |
| Latent Space | https://www.latent.space/feed | 14 |
| Simon Willison | https://simonwillison.net/atom/entries/ | 17 |
| TLDR AI | https://tldr.tech/api/rss/ai | 18 |

### 品类 D — 中国生态（含独立评论）
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| 36kr 快讯（只取 AI/创业/品牌相关） | https://36kr.com/feed-newsflash | 16 |
| 机器之心 | https://www.jiqizhixin.com/rss | 29 |
| sspai | https://sspai.com/feed | 11 |
| ChineseSEO | https://www.chinese-seo.com/feed/ | 44 |

### 品类 E — 商业 / 策略
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| SaaStr | https://www.saastr.com/feed/ | 15 |
| Jason Fried | https://world.hey.com/jason/feed.atom | 4 |
| DHH | https://world.hey.com/dhh/feed.atom | 5 |
| Smart Passive Income | https://www.smartpassiveincome.com/feed/ | 38 |
| GitHub Blog | https://github.blog/feed/ | 21 |
| LangChain | https://blog.langchain.dev/rss/ | 23 |
| Pragmatic Engineer | https://newsletter.pragmaticengineer.com/feed | 27 |
| Google AI | https://blog.google/technology/ai/rss/ | 22 |
| Google Devs | https://developers.googleblog.com/feeds/posts/default | 33 |
| Hermes Agent Releases | https://github.com/nousresearch/hermes-agent/releases.atom | 40 |

### 品类 F — 工具发现（不定期）
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| Product Hunt | https://www.producthunt.com/feed?category=tech | 8 |

### 品类 G — 格局/储备（v7 新增，仅用于轨道 2 和轨道 3）
不限来源。任何领域的信息，只要符合轨道 2（格局信号）或轨道 3（材料储备）的检验标准即可收录。
→ 聚焦：改变前提的格局信号、未来主题的素材储备

### Tier 2 — 信号雷达（只检测热点，引用需溯源到官方/权威源）
| 源名 | URL | blogwatcher id |
|------|-----|----------------|
| Hacker News | https://hnrss.org/frontpage | 19 |
| V2EX | https://www.v2ex.com/index.xml | 12 |
| Indie Hackers | https://hnrss.org/frontpage?q=indie+hackers | 20 |
| 知乎热榜 | 手动检测 | — |

## blogwatcher 维护

blogwatcher 数据库位置：`~/.blogwatcher-cli/blogwatcher-cli.db`

### 检查所有源是否有 feed_url
```sql
SELECT id, name, 
  CASE WHEN feed_url IS NULL OR feed_url = '' THEN '❌ MISSING' ELSE '✅ OK' END 
FROM blogs ORDER BY id;
```

### 修复缺失的 feed_url
```sql
UPDATE blogs SET feed_url='<正确RSS地址>' WHERE id=<id> AND (feed_url IS NULL OR feed_url='');
```

### 查看最近产出分布
```sql
SELECT b.name, COUNT(a.id) as cnt 
FROM articles a JOIN blogs b ON a.blog_id=b.id 
WHERE a.published_date >= 'YYYY-MM-DD' 
GROUP BY b.name ORDER BY cnt DESC;
```

### 新增 feed
```sql
INSERT OR IGNORE INTO blogs (name, url, feed_url) VALUES ('名称', 'RSS地址', 'RSS地址');
```

## 已删除的旧 cron
- job_id `4e5978bf39cb` — v4 策展，旧客户画像（小企业主），2026-07-26 删除
- 替换为 v5 → v6 → v7

## cron prompt 版本历史

| 版本 | 日期 | 变化 |
|------|------|------|
| v4 | 旧版 | 小企业主/自由职业者画像，web_search removed |
| v5 | 2026-07-26 | 转向 GEO/AIO 聚焦，中小品牌画像，新增 CMI/HubSpot/Animalz 源 |
| v6 | 2026-07-28 | 新增品类分类 A-F，强制源多样化（≥2品类/≤4条每域），修复 blogwatcher 13 个缺失 feed_url，新增 7 个源，blogwatcher 总数 38 |
| v7 | 2026-07-30 | 三轨并行策展（轨道1 GEO实操 + 轨道2 格局信号 + 轨道3 材料储备），新增品类 G，框架级自检机制，新增 cron skill: c456-curation-philosophy |
