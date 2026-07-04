# 桥接文档：product-niche-discovery ⟷ phuryn/pm-skills

> **分层原则**：product-niche-discovery 负责**执行层**（渠道遍历、数据采集、结构化输出），phuryn/pm-skills 负责**方向层**（方法论框架、分析、策略生成）。

---

## 一、数据流向

```
用户输入（赛道关键词）
    ↓
[product-niche-discovery]
    ├─ 渠道遍历 (47 渠道注册表)
    ├─ 关键词生成 (四步 SOP)
    ├─ 数据采集 (web_search / Camofox / browser)
    └─ 结构化输出 (原始数据包)
                ↓
[phuryn/pm-skills —— 按需调用以下任一]
    ├─ competitor-analysis      ← 差评/吐槽/竞品对比
    ├─ customer-journey-map     ← 用户提问/替代品数据
    ├─ business-model           ← 定价页数据
    ├─ pricing-strategy         ← 定价页 + 评论
    ├─ analyze-feature-requests ← 功能请求/Issue
    ├─ persona-generator        ← 目标人群反馈
    ├─ market-segments          ← 用户分层数据
    ├─ market-sizing            ← TAM/SAM/SOM 估算
    ├─ swot-analysis            ← 竞品格局 + 市场洞察
    ├─ porters-five-forces      ← 行业竞争结构
    ├─ lean-canvas              ← 综合输出
    └─ value-proposition        ← 痛点 + Gap 分析
```

## 二、输出→技能映射矩阵

### 差评/吐槽/需求原始数据 → `competitor-analysis`

product-niche-discovery 产出格式：
```json
{"source":"V2EX t/902624","complaint":"Notion 网络不稳定","frequency":7,"platforms":["V2EX","知乎","HN"]}
```
→ 频次 ≥ 3 = 可验证痛点；跨平台印证 = 高置信度标注

### 用户提问/替代品数据 → `customer-journey-map`

product-niche-discovery 产出标注了 stage（discover → evaluate → deploy → maintain → regret/switch），直接映射到 customer-journey-map 的阶段。

### 定价页数据 → `business-model` + `pricing-strategy`

product-niche-discovery 定价映射表（含产品名、自托管价格、云版价格、部署难度、维护成本、来源 URL）直接注入 pricing-strategy 作为竞品定价基准。

### 功能请求/Issues → `analyze-feature-requests`

GitHub Issues 搜索结构化为 feature request entry（topic, description, source, label）。

### 目标人群反馈 → `user-personas` / `market-segments`

跨平台同一身份表述合并为用户画像草稿。

### 综合数据包 → swot / porters-five-forces / lean-canvas

一次完整 deep_dive 后的所有产出可打包进入综合分析框架。

## 三、接口规范

### product-niche-discovery 输出包格式

```json
{
  "metadata": {"seed_keywords":[],"channels_scanned":0,"sources_deep_dived":0},
  "findings": [
    {
      "type": "pain_point|pricing|gap|trend",
      "description": "string",
      "frequency": 3,
      "platforms": ["V2EX","HN","知乎"],
      "confidence": "high|medium|low",
      "evidence": ["url1","url2"],
      "for_phuryn_skill": "competitor-analysis|customer-journey-map|..."
    }
  ],
  "pricing_map": [],
  "competitive_landscape": {},
  "gaps": []
}
```

## 四、实战示例（知识库调研）

```yaml
feed_to_competitor_analysis:
  competitors: [Outline, BookStack, Wiki.js, AFFiNE, 思源, Notion, 语雀]
  weaknesses:
    - "部署门槛高（Docker Compose 非技术用户门槛）"  # V2EX/HN/知乎 三方印证
    - "个人发布流程繁琐"  # HN 16pts 21comments
    - "零 AI 引用能力"  # 13 款方案直接验证

feed_to_pricing_strategy:
  anchor_price: "思源 ¥96 终身"
  competitor_tiers:
    free: [BookStack, Wiki.js, DokuWiki]
    low: [思源 ¥96-148/yr, Docmost $8/mo]
    mid: [Outline $10-79/mo, AFFiNE $6.75/mo]
    high: [Confluence $6/seat/mo, Notion $10/mo]
  recommendation: "c456 定价 ¥99 起手式在 free-low 之间"

feed_to_swot:
  strengths: ["47 渠道已结构化", "自有的帮助台经验"]
  weaknesses: ["1 人团队", "品牌未建立"]
  opportunities: ["个人知识对外发布空白", "AI 引用零供给"]
  threats: ["Outline 随时加 publish 功能"]
```

*版本：v1.0*
*参考：product-niche-discovery v1.2.0, phuryn/pm-skills (68 skills)*
