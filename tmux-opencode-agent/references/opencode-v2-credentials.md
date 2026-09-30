# OpenCode v2 凭据、鉴权头与额度判定

只在要核「账号还能不能用 / 这轮为什么报 credential 错」或要安全复现写状态操作时读。

## 1. 凭据真源 = sqlite，不是 auth.json

| 位置 | 是什么 |
|------|--------|
| `~/.local/share/opencode/opencode.db` → 表 `credential` | **v2 真源**：`id / integration_id / label / value / active` |
| `~/.local/share/opencode/{auth.json,account.json}` | **v1 遗留**，与 v2 不同步 |

- 同一 `integration_id`（`opencode-go` / `opencode` / `openrouter` …）可挂多条凭据，`label` 即账号名，`active=1` 为当前生效（只应有一条）。
- `value` 是 JSON：`{"type":"key","key":"sk-..."}`；OAuth 型为 `access/refresh`。
- 只读核法：`sqlite3 'file:<db>?mode=ro' …` 或 python `sqlite3.connect(uri=True)`。
- ⛔ 照 `auth.json` / `account.json` 取密钥会拿到**已作废的 key**，探测得 `Invalid credential` ⇒ 把好账号判成死的。

## 2. 原生命令（不自建维护件）

```bash
opencode auth list                            # 列集成 + 凭据 label
opencode auth switch <集成> <label>           # 切生效账号（等价于改 active）
opencode api GET  /api/integration/<id>       # 直打本地服务 API（列 connections，拿不回密钥）
opencode api POST /api/integration/<id>/connect/key -d '{"key":"sk-..","label":"acct-2"}'
```

- `auth switch` 要后台服务在跑；报 `Timed out waiting for the background service to start` 时加 `--standalone`（起私有服务直连同一 DB）。隔离 HOME 下 `--standalone` 是唯一可行姿势。
- 切换后**回读 DB 核 `active`** 再算成功，别信 CLI 自报的 Done。

## 3. 额度「还有没有」怎么判

公开 API **只给能/不能，不给余额数字**（`/zen/*/v1/usage` 只认账号级 token，个人 key 401；本地服务 OpenAPI 里也没有 credits/usage/billing 端点）。数字只在 opencode.ai 网页控制台（需登录）。

判定靠对 `/chat/completions` 发一次最小真请求（免费模型 + `max_tokens:1`）：

```bash
# opencode-go：Authorization: Bearer + 必须带 x-opencode-session
curl -sS -D h.txt -o b.txt -A "$UA" \
  -H "Authorization: Bearer $KEY" -H 'x-opencode-session: ses_probe0000000000000000000000' \
  -H 'content-type: application/json' \
  -d '{"model":"space-bunny-free","messages":[{"role":"user","content":"ping"}],"max_tokens":1}' \
  https://opencode.ai/zen/go/v1/chat/completions

# opencode（Zen）：改用 -H "x-api-key: $KEY"（拿 Bearer 会 401 Invalid credential）
```

| 现象 | 含义 |
|------|------|
| `200` | 可用 |
| 401 `CreditsError` / `Insufficient balance … /workspace/<wrk_>/billing` | **额度耗尽**（正文自带计费链接，转给辉哥充值用） |
| 401 `Invalid credential` | 该 key 失效/停用 |
| 400 `MissingSessionID` | 少 session 头（口径写错，不是账号问题） |

⛔ **判可用性一律打 `/chat/completions`，别打 `/models`**：`models` **不校验密钥**（无 key 也 200）⇒ 拿它当判据必然假绿。
⛔ **传输用 curl + 浏览器 UA**：Python `urllib` 的 TLS 指纹会被 Cloudflare 拦成 `Error 1010` / handshake timeout，看着像「账号坏了」，其实请求没到应用层。
⛔ 密钥别进命令行参数（`ps` 可见）：用 `curl -K <600 权限配置文件>`，用完即删。

## 4. 隔离复现（不碰真机活跃会话）

真机常有小弟在跑，`auth switch` / agent 配置这类**写状态**的操作别直接试：

1. `export HOME=<iso>/home`，工具要认的 DB env 也一并指向隔离库（否则仍打真库）。
2. 用真库的**全部 DDL** 建骨架表，再**复制 `__drizzle_migrations` 与 `migration` 两表的数据**——否则迁移器重跑，`table \`project\` already exists` 直接让 standalone 起不来。
3. 复制 `~/.cache/opencode/models.json` 进隔离 cache，否则 `Integration not found`（集成清单来自模型注册表）。
4. 插两条假凭据（`acct-a` active=1 / `acct-b` active=0）→ `opencode auth list --standalone` → `auth switch` → 回读 DB 验证 `active` 翻转。
5. terminal 的 env 跨调用保持，**混用后显式 `export HOME=$HOME` 回真机**，否则后续命令的 `~` 指到隔离目录。
