# 关键词数据采集 API 命令参考

> 可编程获取的公开数据接口，按可靠性排序。

---

## 1. 百度搜索联想词（首选 ✅）

**接口**：完全公开，无需认证，响应快。

```bash
# 基础用法
curl -s "https://www.baidu.com/sugrec?prod=pc&wd=你的关键词"

# 示例
curl -s "https://www.baidu.com/sugrec?prod=pc&wd=知识库" | python3 -c "
import json,sys
d = json.load(sys.stdin)
for g in d.get('g',[]):
    print(g.get('q',''))
"
```

**适用场景**：所有中文关键词的长尾挖掘。
**局限性**：无法区分搜索量级（每个词都返回 10 条）。

## 2. Web Search 平台索引查询

**接口**：通过 `web_search` 搜索特定平台索引。

```python
from hermes_tools import web_search

# 搜索小红书索引内容
r = web_search("site:xiaohongshu.com AI创业 爆款")
for item in r["data"]["web"]:
    print(item["title"], item["description"][:100])

# 搜索知乎
r = web_search("site:zhihu.com 知识库 自部署 推荐")

# 搜索少数派
r = web_search("site:sspai.com 知识管理 工具")

# 搜索 ProductHunt
r = web_search("site:producthunt.com knowledge base self-hosted")
```

## 3. 百度搜索结果数估算

**说明**：百度搜索结果页展示「找到约 X 个结果」，可以粗略估算竞争度。
**注意**：需要处理 CAPTCHA，建议网页抓取或用 browser 工具。

```bash
# 通过 web_search 获取搜索结果（web_search 后台会处理 CAPTCHA）
# hermestools 的 web_search 已内置
r = web_search("知识库搭建", limit=10)
print(f"结果数: {len(r['data']['web'])}")
```

## 4. 微信搜狗搜索

**接口**：搜狗微信搜索，可获取微信公众号文章。

```bash
curl -s "https://weixin.sogou.com/weixin?type=2&query=关键词" \
  -H "User-Agent: Mozilla/5.0"
```

**注意**：当前网络环境下可能受限，需要代理或浏览器。

## 5. Heremes 浏览器工具（需登录平台）

对于小红书/知乎等需要登录的平台，使用 Hermes browser：

```python
from hermes_tools import terminal

# 启动 Camofox（需提前登录并持久化）
# CAMOFOX_HEADLESS=false npx @askjo/camofox-browser

# 创建 tab 并搜索
curl -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","sessionKey":"..."}'
```

## 可靠度总结

| 方法 | 可靠度 | 返回数据 | 备注 |
|------|--------|---------|------|
| 百度联想词 API | ⭐⭐⭐⭐⭐ | 用户真实搜索长尾词 | 首选，完全公开 |
| web_search site: | ⭐⭐⭐⭐ | 标题+描述+URL | 依赖搜索引擎索引 |
| Camofox 登录后搜索 | ⭐⭐⭐ | 目标平台完整页面 | 需要登录态 |
| 百度搜索结果数 | ⭐⭐ | 竞争度粗略估算 | 需处理 CAPTCHA |
| 第三方付费工具 API | ⭐⭐⭐⭐⭐ | 完整流量数据 | 需要付费，不在此范围 |
