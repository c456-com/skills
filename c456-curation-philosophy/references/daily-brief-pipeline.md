# 每日 AI 简报 — 采集管线与恢复路径

> SaaS 化管线：**确定性采集脚本 + agent 选编**。脚本只抓和归一化，不做判断；选稿、核实、写作全部由 cron agent 完成。

## 组件

| 组件 | 位置 | 职责 |
|------|------|------|
| cron 任务 | `c456-daily-brief`，每天 07:00 CST | 跑脚本 → 选编 → 推送简报 |
| 采集脚本 | `~/.hermes/profiles/hermes-c456/scripts/ai-radar.py` | HN + GitHub + RSS 采集，输出 ~14KB markdown |
| 补发脚本 | `~/.hermes/profiles/hermes-c456/scripts/deliver-today-brief.sh` | no-agent 任务用，逐字投递当天已归档简报 |
| 归档 | `c456-com/daily/briefs/YYYY-MM-DD-ai-brief.md` | 简报全文存档 |
| 方法论 | 本技能 §1.4（四轨） | 选稿标准 |

## 采集源

**Hacker News**：Algolia API `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=25`（JSON，按 points 排序，取前 15）。稳定，无鉴权。

**GitHub**（用 `gh` CLI，已登录 `xiaohui-zhangxh`）：
```bash
gh search repos --created ">YYYY-MM-DD" --sort stars --limit 15 \
  --json fullName,description,stargazersCount,language,url,createdAt
gh search repos ai llm agent rag mcp --sort stars --updated ">YYYY-MM-DD" --limit 15 --json ...
```
比抓 `github.com/trending` HTML 稳（trending 页面结构会变，正则容易空）。

**RSS**（`blogwatcher-cli`，38 个源已登记）：
```bash
BLOGWATCHER_SILENT=1 BLOGWATCHER_WORKERS=6 blogwatcher-cli scan      # ~10s，约 17/38 源会 fail，正常
blogwatcher-cli articles --all --since YYYY-MM-DD                     # 注意：没有 --unread 参数
```

## 踩过的坑

| 坑 | 真相 |
|----|------|
| 脚本 `from hermes_tools import ...` | **必炸**。hermes_tools 只存在于 agent 进程，脚本进程会 `ModuleNotFoundError`。脚本只用 stdlib（subprocess/urllib/json/re）。旧 job `ai-pricing-monitor` 就是这样连续失败的 |
| `blogwatcher-cli articles --unread` | 不存在。只有 `--all` / `--since` / `--before` / `-b` / `-c` |
| 采集输出不设预算 | RSS 两天能出 300+ 条，不限量会把 GH/HN 段落挤出 prompt。脚本按段限行（每源 2-3 条）+ 总长截断 |
| cron 指定 `provider: custom:unsloth` + `base_url: 127.0.0.1:8888` | 被安全策略拦（named provider 的凭据只能发往自己的 endpoint），job 连续失败。**cron 不要 override model/provider，继承 profile 默认** |

## 失败恢复

1. `cronjob_manage(action='list')` 看 `last_error` 和 `last_status`。
2. 脚本挂了 → 直接 `python3 ~/.hermes/profiles/hermes-c456/scripts/ai-radar.py` 看 stderr；没有“采集异常”段就是正常。
3. 采集全挂（断网）→ 手动 `curl` HN API + `gh search` 补当日素材，按四轨格式手写简报并归档。
4. `cronjob_manage(action='run')` 是后台执行，结果稍后回到对话——不要阻塞等待。

## 投递链路（坑，已实测）

**元宝投递只靠「网关 tick」，手动 run 不行。**

| 路径 | 谁跑 | 元宝投递 |
|------|------|---------|
| 定时 tick（07:00） | hermes-c456 网关进程（带 live yuanbao 适配器） | ✅ 实测 `delivery_outcome=delivered` |
| 手动 `cronjob(action='run')` | 桌面 `serve` 进程（无法访问网关的 yuanbao 适配器） | ❌ `Yuanbao adapter is not running` |
| 手动 `run` **在网关重启窗口内** | 桌面 serve 接替 tick | ❌ 同上 |

原因：元宝是「无独立发送客户端」的平台（`_send_yuanbao` 必须用活适配器的常驻 WebSocket），而桌面后端与网关是两个进程。桌面调度器本来会按 tick 让位于已运行的网关（`profile_gate` + `web_server._check_gateway_running`），**但网关刚重启、`gateway.pid` 还没就绪的那个窗口里它会接管**，那时投递就会失败。

**判断方法**：看 `~/.hermes/profiles/hermes-c456/logs/gui.log` 里的 `Desktop cron scheduler will tick N profile(s): [...]`——名单里有 `hermes-c456` 就说明那个时刻是桌面在 tick（=投递会失败）。

**恢复手段**：简报已归档，不会丢。补发用 no-agent 任务（逐字投递脚本 stdout）：

```
# 建“in 1m”一次性任务，script=deliver-today-brief.sh, no_agent=true, deliver=yuanbao
hermes cron add --name tmp-deliver-today-brief --in 1m \
  --no-agent --script deliver-today-brief.sh --deliver yuanbao
```

或直接用工具：`cronjob_manage(action='create', schedule='in 1m', script='deliver-today-brief.sh', no_agent=True, deliver='yuanbao')`，跑完记得 `action='remove'` 清掉临时任务。

**验证投递是否真的送达**（不要只信 `last_status`）：查 `cron/executions.db` 的 `delivery_outcome`，`delivered` 才算成功；或建一个 2 分钟的探针任务实测。

## 失败恢复（内容层）
