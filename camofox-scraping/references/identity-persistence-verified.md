# 身份保持（persistence）实测结论与自检规程

> 实测日期 2026-09-26 · fork v1.17.0（`bab5e7c`）· macOS 26.5.1
> 独立实例 9378 + 隔离 `CAMOFOX_PROFILE_DIR`，未动用户原有 9377。

## 结论：三层边界（与「进程重启就丢登录」相反）

| 层 | 跨浏览器进程重启后 | 机制 |
|---|---|---|
| HttpOnly cookie | ✅ 保持 | `context.storageState()` 落盘 |
| localStorage | ✅ 保持 | 同上（按 origin） |
| IndexedDB | ❌ **不保持** | 默认关闭，需 `plugins.persistence.indexedDB=true` |
| 同一进程内多 tab | ✅ 共享 | 同一 BrowserContext，无需任何手工导入 |

**推论**：依赖 IndexedDB 存登录态的站点（少数）重启后仍会掉登录；
cookie/localStorage 型站点（绝大多数）可复用。判断某站能否免重登，先看它把令牌放哪。

## 落盘路径（由 lib/persistence.js 保证）

```
$CAMOFOX_PROFILE_DIR/<SHA256(userId) 前 32 位十六进制>/storage-state.json
$CAMOFOX_PROFILE_DIR/<SHA256(userId) 前 32 位十六进制>/meta.json
```

默认 `~/.camofox/profiles/`。**目录名可验算**：`SHA256("cto-idtest")[:32] == 735a965b…3ff`（实测一致）。
→ 保持 `userId` 稳定才复用；换 `userId` 等于换人。

## 何时落盘 / 何时恢复

- 落盘时机：`session:cookies:import` · `session:storage:export` · `session:destroying` ·
  `server:shutdown`（plugins/persistence/index.js）
- 恢复时机：`session:creating` → 注入 `contextOptions.storageState`
- ⚠️ **只在这些时机写**。跑完一轮抓取直接 `kill -9` 服务进程（不走 DELETE /sessions）
  ⇒ 可能丢最后一次变更。收工前先 `DELETE /sessions/:userId`。

## 清除登录态

```bash
curl -sX DELETE "http://127.0.0.1:9377/sessions/$U/storage_state"
# → {"ok":true,"userId":...,"clearedLive":true,"removedPersisted":true}
```
它会关 live session、等在途写入、删 `storage-state.json` + `meta.json`。

## 自检规程（不靠「cookie 还在」当通过）

**错误做法**：`/who` 返回里看到 cookie 名字就算过。伪造的 cookie 也能过。

**正确做法**——让登录真源在服务端，裁判独立于被测系统：

1. 自建 oracle 服务持有会话表（`sid → user`），`/login` 发真 HttpOnly `probe_sid`；
2. `/who` 只认「sid 在服务端会话表里」，否则 `authenticated:false`；
3. **先证伪裁判**：伪造合法格式的 sid 进去 → 必须 `false`；真登录 → `true`；
   `/logout` → `false`。三步过，裁判才可信；
4. localStorage / IndexedDB 用**只读页**探针（只 `getItem`，不 `setItem`），
   否则命中可能只是页面自己又写了一遍；
5. 必设对照组：(a) 换 `userId` → 必须登出；(b) `DELETE .../storage_state` → 必须登出。

## 复现

`scripts/oracle_server.py` —— 登录真源 + 只读探针页（stdlib，无依赖）。

```bash
python3 scripts/oracle_server.py 8899            # 起真源服务（server-side session）
curl -s 127.0.0.1:8899/who                       # 金标准自检：裸请求应 authenticated:false
curl -s -H 'Cookie: probe_sid=sid-FAKE' 127.0.0.1:8899/who   # 证伪：伪造 cookie → false
# 两者结果必须不同；相同则裁判不可信，停下来查

CAMOFOX_PORT=9378 BROWSER_IDLE_TIMEOUT_MS=0 \
  CAMOFOX_PROFILE_DIR=/tmp/隔离目录 node server.js &        # 隔离实例
# 驱动：P1 登录 → DELETE /sessions（checkpoint）→ kill -9 → 重启 → P4 跨重启探针
#      → P5 换 userId 对照 → P6 DELETE .../storage_state → P7 清后再读
```

## 踩过的坑

| 坑 | 症状 | 修 |
|---|---|---|
| **Python 单线程 oracle 卡死** | `lsof` 看进程在，`curl` 全部超时，`page.goto: Timeout 30000ms` | `ThreadingHTTPServer` + `protocol_version='HTTP/1.0'` |
| shell 管道 `jqv` 吞报错 | 探针输出空行，误读成「登出」 | 用 Python subprocess 直收 JSON，把 `_raw`/错误原样打印 |
| `kill -9` 端口只释放 port，Camoufox 子进程变孤儿 | 收工后 `pgrep camoufox` 计数不降 | 按 PPID 甄别：非自己 PPID 的是别的实例的进程，不动 |
| `POST /tabs` 拿 `tabId` 用了 `python3 -c` 管道 | 报错被吞成空串 | 同样改成直接解析 |
