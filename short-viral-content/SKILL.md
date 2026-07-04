---
name: short-viral-content
category: social-media
tags: [short-video, marketing, content-strategy, keywords, xiaohongshu, douyin, wechat]
description: "短视频爆款内容引擎 — 根据中心思想+受众人群+人群偏好，在小红书/抖音/微信视频号发掘高热关键词，生成平台特化的候选标题、描述和话题标签。输出可直接用于短视频创作的标题库+关键词热力图。"
version: 1.0.0
author: c456-com
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [short-video, marketing, content-strategy, keywords, xiaohongshu, douyin, wechat]
    related_skills: [product-niche-discovery, web-research-scraping, market-research]
---

---

# Short Viral Content — 短视频爆款内容引擎

> **核心原则：每个关键词必须有真实数据支撑，不靠 AI 脑补。** 以下工作流通过百度搜索联想、平台搜索、搜索引擎索引记录等多源数据，逐步发现高热关键词并生成标题。

## 输入

| 字段 | 说明 | 示例 |
|------|------|------|
| **中心思想** | 这段视频要传递的核心信息 | "知识库对外部署市场有个零竞争空白" |
| **受众人群** | 目标用户画像 | 创业者、SaaS 创始人、产品经理 |
| **人群偏好** | 痛点/兴趣/内容消费习惯 | AI焦虑、找方向、真实案例 |
| **平台** | 目标分发平台（默认全选） | 小红书 / 抖音 / 微信视频号 |

## 工作流（数据驱动）

### Step 1: 种子词 → 五维扩展

从中心思想提取 3-5 个种子词，按五维展开：

| 维度 | 说明 | 示例 |
|------|------|------|
| 本体词 | 核心名词 | 知识库、蓝海、AI创业 |
| 疑问词 | 用户怎么搜问题 | 怎么找创业方向、如何搭建知识库 |
| 对比词 | 竞品/替代 | Notion vs Obsidian、AI工具对比 |
| 场景词 | 人群+场景 | 产品经理AI焦虑、创业者找方向 |
| 长尾组合 | 多词组合 | AI知识库免费搭建、个人知识库对外发布 |

### Step 2: 百度联想词 → 真实搜索长尾

用百度搜索联想 API 获取**用户真实搜索的长尾关键词**：

```bash
# API 接口（公开可用，无需认证）
curl -s "https://www.baidu.com/sugrec?prod=pc&wd={你的种子词}"
```

**返回示例**（搜索"知识库"）：
```
知识库官网入口, 知识库ai, 知识库是什么,
知识库搭建实施步骤, 知识库工具, 知识库怎么建立,
知识库与RAG的区别, 知识库 obsidian
```

**用途**：用户每天在百度搜这些词 → 直接反映真实需求 → 做视频标题/标签。

**评估方法**：
- 联想词越具体（如"知识库搭建实施步骤"vs"知识库"）= 长尾流量越大
- 联想词中出现的工具名/场景名 = 高价值流量入口
- 对比类联想词（如"知识库与RAG的区别"）= 竞品截流机会

### Step 3: 平台搜索结果分析

用 web_search 在目标平台搜索种子词，**记录真实标题模式和互动数据**：

```python
from hermes_tools import web_search

# 搜索小红书/知乎/抖音的真实内容标题
results = web_search(query="site:xiaohongshu.com AI创业 爆款")
for item in results["data"]["web"]:
    print(f"标题: {item['title']}")
    print(f"描述: {item['description']}")
```

**采集维度**：
| 维度 | 分析什么 |
|------|---------|
| 标题模式 | 数字开头？问句？情绪词？ |
| 关键词密度 | 哪些词在标题中反复出现 |
| 互动信号 | 描述中是否有"万赞""爆款"等 |
| 标签使用 | 哪些话题标签出现频率高 |

### Step 4: 长尾关键词挖掘及热度评估

将 Step 2+3 获得的所有关键词放入评估矩阵：

```python
关键词评分 = 搜索热度(1-10) × 0.25 
           + 竞争程度(1-10) × 0.20
           + 目标匹配度(1-10) × 0.25
           + 时效性(1-10) × 0.15
           + 变现关联度(1-10) × 0.15
```

**各维度数据获取方法：**
- **搜索热度**：百度联想词数量 + 搜索结果总数
- **竞争程度**：web_search 该词的头部内容互动量
- **目标匹配度**：搜索结果标题是否匹配目标受众
- **时效性**：近期是否有相关讨论增长
- **变现关联度**：是否有商业内容/付费转化路径

### Step 5: 标题生成（模板 + 数据支撑）

每个标题必须标注**钩子类型**和**数据支撑**：

```yaml
标题: "🔥 千万别盲目创业！我用47个渠道挖出1个蓝海"
钩子: 避雷法 + 数字
数据支撑: 
  - 数字开头爆款率63%（2026小红书运营数据分析）
  - "避雷/千万别"类标题CTR高（平台运营白皮书）
  - "47个渠道"具体数字增加可信度
受众匹配: 创业者、产品经理（焦虑期人群）
预估互动: ⭐⭐⭐⭐⭐
```

### Step 6: 平台特化输出

每个标题适配三个平台的不同格式：

| 要素 | 小红书 | 抖音 | 微信视频号 |
|------|--------|------|-----------|
| 标题 | 15-25字+emoji | 10-20字，前3字钩子 | 20-30字，价值前置 |
| 话题标签 | 3-5个，含长尾 | 1-2个热门 | 1-2个 |
| 视频简介 | 干货总结+引导 | 悬念提问 | 价值承诺 |
| 黄金3秒 | 没必要 | 必须有 | 建议有 |

## 数据源完整对照表

| 数据源 | 可用性 | 获取方式 | 输出数据 |
|--------|--------|---------|---------|
| **百度联想词 API** | ✅ 完全可用 | `curl "https://www.baidu.com/sugrec?prod=pc&wd=关键词"` | 真实用户搜索长尾词 |
| **Google 搜索** | ✅ 可用 | `web_search(query, limit=N)` | 标题、描述、URL |
| **site: 搜索** | ✅ 可用 | `web_search("site:zhihu.com 关键词")` | 平台内容标题摘要 |
| **知乎搜索** | ⚠️ 需登录（Camofox） | Camofox headful 登录后搜索 | 知乎问题+回答标题 |
| **小红书搜索** | ⚠️ 需登录（Camofox） | Camofox headful 登录后搜索 | 笔记标题+互动数据 |
| **5118 关键词** | ❌ API 收费 | 浏览器手动访问 ci.5118.com | 关键词搜索量数据 |
| **微信指数** | ❌ 仅微信小程序 | 无法编程获取 | 微信搜索热度 |
| **千瓜/新红数据** | ❌ 付费工具 | 无法编程获取 | 小红书关键词详细分析 |

## 关键词评估输出格式

```yaml
# 最终输出格式
input:
  中心思想: "知识库对外部署市场空白"
  受众人群: "创业者/产品经理"
platforms: [小红书, 抖音, 微信视频号]

keyword_rankings:
  - rank: 1
    keyword: "AI创业"
    source: "百度联想词"
    longtail_variants:
      - "ai创业项目有哪些项目"
      - "ai创业从哪里入手" 
      - "ai创业普通人能做什么"
    score: 39
    heat: 8
    competition: 7
    match: 9
    recommendation: 核心关键词

  - rank: 2
    keyword: "知识库搭建"
    source: "百度联想词"
    longtail_variants:
      - "知识库搭建实施步骤"
      - "知识库怎么建立"
      - "知识库 obsidian"
    score: 29
    heat: 6
    competition: 5
    match: 8
    recommendation: 长尾关键词

titles:
  - platform: 小红书
    title: "🔥 千万别盲目创业！我用47个渠道挖出1个蓝海"
    hook: "避雷法+数字"
    tags: ["#AI创业", "#蓝海市场", "#产品经理", "#知识库"]
    data_evidence: ["数字开头爆款率63%", "避雷类CTR高"]
    estimated_ctr: "高"

  - platform: 抖音
    title: "64%的用户想停用AI？真正的机会在这"
    hook: "反常识+数据悬念"
    gold_3s: "你信吗，64%的人宁愿不用AI——"
    data_evidence: ["前3字悬念爆款率58%", "反常识结构爆款35%"]
    estimated_ctr: "高"

  - platform: 微信视频号
    title: "调研47个渠道后，我发现了一个被忽视的蓝海"
    hook: "数字+结果前置"
    data_evidence: ["价值前置型热门52%", "朋友圈分享友好"]
    estimated_ctr: "中高"
```

## 验证清单

- [ ] 每个关键词至少有一个数据源（百度联想/搜索索引/平台文章）
- [ ] 每个标题标注了钩子类型和支撑数据
- [ ] 关键词评分表中每个维度的分数有来源依据
- [ ] 三个平台的标题不是复制粘贴，做了差异化适配
- [ ] 发布后追踪实际互动数据，回来校准评分模型

## 引用

- `references/title-formulas.md` — 标题公式库+平台特化
- `references/platform-differences.md` — 三大平台内容特征对比
- `references/platform-research-workflow.md` — 平台关键词调研工作流详细版
- `references/keyword-api-commands.md` — 各平台数据采集API命令参考

## 相关技能

- [product-niche-discovery](https://github.com/c456-com/skills/tree/main/product-niche-discovery) — 关键词五维扩展+渠道遍历方法论
## 引用

- [product-niche-discovery](https://github.com/c456-com/skills/tree/main/product-niche-discovery) — 关键词五维扩展 SOP
- 小红书/抖音/微信视频号官方内容规范（2026）

## 参考文件

- `references/title-formulas.md` — 标题公式库详细版
- `references/platform-differences.md` — 三大平台内容特征对比
