# 每日策展回填 + 原文读取技术

> c456-write §D 流程步骤 5-7 的配套操作细节。2026-08-03 实测通过。

## 1. wiki/c456-meta.yml 回填（python 字符串插入，不用 patch 工具）

**为什么不能用 patch 工具**：c456-meta.yml 是 markdown 文件（内含 ```yaml 代码块），整体不是合法 YAML。patch 工具做 YAML 语法校验会拒绝写入，报错形如：

```
Failed to write changes: Refusing to write '.../wiki/c456-meta.yml':
candidate content fails .yml syntax validation
(YAMLError: while scanning for the next token
found character '`' that cannot start any token ... line 12, column 1: ```yaml)
```

**正确做法**（锚点取最后一个 entry 的 `    wiki_pages: []` 后跟两个空行 + `---` 分隔线）：

```bash
cd ~/read-and-writes/c456-wiki
python3 << 'EOF'
path = 'wiki/c456-meta.yml'
with open(path) as f:
    content = f.read()

new_entry = """  - c456_id: <ID>
    c456_kind: signal
    c456_title: "c456 每日信号精选 | YYYY-MM-DD"
    c456_url: "https://c456.com/intakes/<ID>"
    sync_path: null
    status: draft
    wiki_pages: []
"""

anchor = '    wiki_pages: []\n\n\n---'
assert anchor in content, 'anchor not found'
content = content.replace(anchor, '    wiki_pages: []\n\n' + new_entry + '\n---', 1)

with open(path, 'w') as f:
    f.write(content)
print('OK - entry added')
EOF
```

要点：
- 锚点 `    wiki_pages: []\n\n\n---` 必须唯一（末尾 `---` 前的最后一条 entry）。若文件结构变化找不到锚点，先 `grep -n "wiki_pages: \[\]" wiki/c456-meta.yml | tail` 定位再调整。
- 完成后 `tail -25 wiki/c456-meta.yml` 验证格式对齐。

## 2. wiki/log.md 追加

append-only，`cat >>` 即可：

```bash
cat >> wiki/log.md <<'EOF'

## [YYYY-MM-DD] create | c456 每日信号精选（ID <ID>，draft）
- 轨道 1：N 条，覆盖品类 X/Y/Z（来源列表）
- 轨道 2：N 条（...）——只推送不入信号
- 轨道 3：N 条素材入库建议（...）
- 状态：draft，等待选稿后决定发布
EOF
```

## 3. 原文读取：curl 抓 HTML 后如何提取正文

cron 内 web_search API 不可靠，读原文一律 `curl -sL`。抓到的 HTML 不能直接 `cat`，用 python 提取正文。

### 3.1 通用提取函数（带站点选择器回退）

```python
import re, html

def extract(fn, maxlen=4000):
    raw = open(fn, encoding='utf-8', errors='ignore').read()
    raw = re.sub(r'<script[\s\S]*?</script>', ' ', raw)
    raw = re.sub(r'<style[\s\S]*?</style>', ' ', raw)
    # 按站点选择器依次尝试，命中且长度够就返回
    for pat in [r'<div[^>]*class="[^"]*article-content[^"]*"[\s\S]*?</div>\s*</div>',
                r'<div[^>]*class="[^"]*articleBody[^"]*"[\s\S]*?(?=<div[^>]*class="[^"]*related|$)',
                r'<article[\s\S]*?</article>',
                r'<div[^>]*class="[^"]*entry-content[^"]*"[\s\S]*?</div>\s*</div>',
                r'<main[\s\S]*?</main>']:
        m = re.search(pat, raw, re.S)
        if m:
            body = re.sub(r'<[^>]+>', ' ', m.group(0))
            body = html.unescape(body)
            body = re.sub(r'\s+', ' ', body).strip()
            if len(body) > 400:
                return body[:maxlen]
    return ''
```

### 3.2 各站点实测要点（2026-08-03）

| 站点 | 做法 | 注意 |
|------|------|------|
| **Search Engine Land** | 选择器用 `article-content`；`<article>` 会抓到侧边栏（相关文章、作者简介）| 抓完检查 title 是否匹配；404 页 title 是 "Page not found" 直接放弃 |
| **HubSpot Marketing** | `article-content` 或 `<article>` 均可；正文前有 TOC 和导语 | 首页/侧栏的 HubSpot 自家产品广告会混进 `<article>`，用 `article-content` 过滤 |
| **sspai** | 需要 `-H "User-Agent: Mozilla/5.0 ..."` 否则可能被拒；`<article>` 可取 | 早报是聚合页，单条新闻正文在 `<article>` 内 |
| **V2EX** | 需要 UA；无 `<article>`，用全文本 strip（删 script/style 后直接去标签）| 回复区内容会一起出现，需自行截断到正文结束 |
| **Simon Willison** | 无 `<article>` 标签，用全文本 strip | 页首 sponsor 段会混入，从正文标题处截取 |

**兜底**：结构化提取返回空时，用全文本 strip（删 script/style 后 `re.sub(r'<[^>]+>', ' ', raw)`），从标题附近截取。

### 3.3 RSS feed 批量抓取 + 解析（blogwatcher 失败时）

```bash
cd /Users/xiaohui/hermes-workspaces/c456-com/.tmp
for u in "https://searchengineland.com/feed" "https://moz.com/blog/feed" \
         "https://tldr.tech/api/rss/ai" "https://simonwillison.net/atom/entries/" \
         "https://contentmarketinginstitute.com/feed/" "https://blog.hubspot.com/marketing/feed"; do
  n=$(echo "$u" | md5 | head -c 8)
  curl -sL --max-time 30 "$u" -o "feed-$n.xml"
  echo "$u -> feed-$n.xml ($(wc -c < feed-$n.xml) bytes)"
done
```

解析：Atom 用 `{http://www.w3.org/2005/Atom}entry`；RSS 用 `.//item`，pubDate 是英文月份名需映射（Jan→01...）。筛选 `date >= 前天` 作为候选，然后读昨天 digest 查重（`.tmp/daily-digest-YYYY-MM-DD.md` 按日期存档，逐条对标题/主题避免重复收录）。

### 3.4 抓取注意

- 所有抓取命令在 `.tmp/` 下执行，文件名用 URL 的 md5 前 8 位，避免中文字符和超长 slug。
- 一次抓取 5-6 个源用 for 循环 + 并行（两条 terminal 调用各抓一半），不要一条命令串 10 个。
- 页面 404 或标题不符 → 放弃该条，不要硬凑。
