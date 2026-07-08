---
name: product-niche-discovery
category: research
tags: [product-discovery, pain-points, market-research, niche-finding, competitive-analysis]
description: "产品赛道发现 / product niche discovery：当用户要找赛道、挖痛点、做 market research、竞品/差评/定价抓取、生成关键词或准备 PMF/JTBD 分析原始材料时触发；用于 52 渠道执行层调研。"
version: 1.2.2
author: c456-com
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [product-discovery, pain-points, market-research, niche-finding, competitive-analysis]
    related_skills: [market-research, web-research-scraping, camofox-scraping]
---

# Product Niche Discovery — 找赛道/挖痛点

> **定位于执行层**：方向层（方法论/分析框架）交给 [phuryn/pm-skills](https://github.com/phuryn/pm-skills)——它提供 brainstorm、JTBD、customer-journey-map、competitor-analysis 等 68 个技能。
>
> 本技能负责：渠道遍历、关键词生成、差评/定价/需求挖掘、数据采集与结构化输出。

## 核心原则

### 不接受修补工具

如果 Camofox 挂了、某个渠道被屏蔽了——**跳过、换方法、记缺口**。不要 clone 仓库、改源码、降级依赖。

```
工具不通 → web_search 兜底 + 报告中注明缺失
不能跑   → 不等于要修，等于下次再试
```

### channels.json + channels.user.json

渠道注册表分两层：`channels.json`（我维护，随技能发布）和 `channels.user.json`（用户自定义，gitignore 掉）。运行时合并，同 id 覆盖，无 id 追加。

## 架构

```
用户输入（赛道关键词）
  │
  ├─→ 关键词引擎 (SOP 四步法)
  │    种子词 → 五维扩展 → 工具放大 → AI补全
  │
  ├─→ 渠道注册表 (channels.json + channels.user.json)
  │    52个默认渠道，用户可追加
  │
  ├─→ 执行引擎 (按渠道配置调度爬取策略)
  │    web_search / Camofox / browser / web_extract / xurl
  │
  └─→ 结构化输出
        原始数据 → 可喂给 phuryn/pm-skills 分析框架
```

## 渠道图谱

```
社区讨论 (13)
  ├── Reddit r/selfhosted, r/SaaS, r/startups, r/entrepreneur, r/SideProject
  ├── Hacker News, Indie Hackers, SaaStr
  ├── X/Twitter Search, Dev.to, Slashdot
  └── LinkedIn, Facebook Groups, Discord 社群

产品发现 (10)
  ├── ProductHunt (+ Topics), SaaSHub
  ├── BetaList, Launching Next, Uneed.best, DevHunt, Peerlist, MicroLaunch
  └── AlternativeTo, Alternative.me

开发者渠道 (4)
  ├── GitHub Issues, Discussions, Stack Overflow
  └── StackShare, Chrome Web Store

评价平台 (15)
  ├── G2, Capterra, GetApp, Software Advice
  ├── PeerSpot, SaaSworthy, SoftwareWorld
  ├── Trustpilot, AppSumo, Crozdesk
  ├── App Store, Google Play, Amazon Reviews
  └── G2 Competitors, G2 Grid Reports

中文社区 (8)
  ├── 知乎, V2EX, 少数派, 小红书
  ├── 虎嗅, 36氪, 掘金
  ├── B站/抖音评论区, PMCAFF, 人人都是产品经理
  ├── 豆瓣小组, 虎扑, 什么值得买
  └── 知识星球, 牛客网, 脉脉

趋势数据 (3)
  ├── Google Trends, Exploding Topics, AnswerThePublic
```

## 关键词生成 SOP（四步法）

见 `references/keyword-sop.md` 完整版。

### 速查：五维扩展矩阵

| 维度 | 用途 | 中文模板 | 英文模板 |
|------|------|---------|---------|
| 疑问/求助 | 挖需求 | X怎么选、为什么X慢 | how to choose X, why is X slow |
| 吐槽/负面 | 挖痛点 | X难用、X太卡、弃用X | X sucks, frustrated with X |
| 对比/替代 | 挖竞品空隙 | A vs B、X替代品 | X alternative, better than X |
| 场景+人群 | 扩覆盖面 | 学生用X、团队X | [use case] + [audience] + X |
| 功能+属性 | 抓长尾 | 支持Y的X、离线X | X with Y, open source X |

### 搜索技巧

```
site:reddit.com "keyword" (frustrating OR sucks OR alternative)
site:zhihu.com "关键词" (难用 OR 替代品 OR 避雷)
site:g2.com "product" "wish it had"
```

## 工作流

### 快速扫描 (quick_scan)

对所有 easy 渠道走一遍，快速了解市场概况。

### 深度调研 (deep_dive)

对高优渠道（priority ≥ 4）做完整遍历：

1. 社区抓吐槽 — Reddit/HN/知乎/V2EX
2. 评价平台抓差评 — G2/Capterra/PeerSpot/App Store（按最低分排序）
3. 开发者渠道抓功能请求 — GitHub Issues/Stack Overflow
4. 产品发现看竞品 — ProductHunt/SaaSHub/AlternativeTo
5. 定价页抓定价 — 竞品官网 pricing
6. 汇总输出 → 喂给 phuryn/pm-skills

### 竞品监控 (competitor_watch)

定时任务：定期检查指定竞品的新差评/新 feature request/新定价。

### 评论全扫 (review_sweep)

遍历所有 review 平台，抓竞品 1-3 星差评并聚类。

## 与 phuryn/pm-skills 的桥接

本技能产出**原始数据**，phuryn 做**方法论分析**：

```
本技能产出样本                   phuryn/pm-skills 分析
──────────                       ───────────────────
差评/吐槽/需求原始数据            → competitor-analysis
用户提问/替代品数据                → customer-journey-map
定价页数据                        → business-model / pricing-strategy
产品功能对比                      → analyze-feature-requests
目标人群反馈                      → persona-generator
```

## 验证原则

| 原则 | 说明 |
|------|------|
| 先差评再好评 | 中差评 > 好评，抱怨里藏着差异化机会 |
| 频次 > 单条 | 同个抱怨出现 5+ 次 = 可验证痛点 |
| 跨平台印证 | Reddit + G2 + Quora 三方都提到 = 高置信度 |
| 特定场景>通用场景 | "远程团队" > "团队" |

## 引用

- [phuryn/pm-skills](https://github.com/phuryn/pm-skills) — 方向层方法论框架
- `references/channels.json` — 52 个渠道注册表 + channels.user.json 合并机制
- `references/keyword-sop.md` — 关键词生成四步 SOP
