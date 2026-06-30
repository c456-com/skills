# Bug-Fix 委派 Prompt 模板

向 Cursor Agent 委派 bug-fix 任务时使用的结构化 prompt 模式。核心原则：**给全上下文，让 Agent 自己想出实现方案**。

## 模板结构

按以下顺序组织 prompt（参考真实案例：DuckDB 多线程连接冲突）：

---

### 1. 一句话问题描述

> `segment-fault` — 多 worker 并行拉取分钟 K 线时 DuckDB 报 `ConnectionException: Can't open a connection to same database file with a different configuration`

---

### 2. 完整错误栈/现象

粘贴完整堆栈或可复现的输出。**不要省略中间帧**——Agent 需要看到完整调用链才能定位根因。

```python
# 贴 terminal 输出
_duckdb.ConnectionException: Connection Error: Can't open a connection to same database file with a different configuration than existing connections
  File "stock_picker/core/bundle_indexer.py", line 321, in _index_connect
    return duckdb.connect(str(idx), read_only=read_only), idx
  File "stock_picker/core/bundle_indexer.py", line 363, in upsert_market_coverage
    con, idx = _index_connect(index_path)
  File "stock_picker/core/reference_sync_registry.py", line 47, in mark_coverage
    upsert_market_coverage(scope_key, data_start, data_end, status=status)
  ...
```

---

### 3. 根因分析（你已知的部分）

说明你已理解的根因，但**不指定具体改法**。Agent 会验证并实现。

> 多个 worker 同时打开 bundle_index.duckdb，但读用 read_only=True、写用 read_only=False。DuckDB 不允许同一文件被不同配置的多连接同时打开。

---

### 4. 期望行为

> 24 个 worker 并行拉取 1m 数据时应能正常工作，不报 DuckDB 连接冲突。

---

### 5. 相关文件

列出需要修改的文件路径。Agent 会自己读。

> 主要文件：stock_picker/core/bundle_indexer.py（_index_connect, upsert_market_coverage, get_market_coverage）
> 调用链文件：stock_picker/core/reference_sync_registry.py, stock_picker/core/lake_sync.py

---

### 6. 可选：方向性提示（仅限你有把握的场景）

当你对解决方向比较确定时，可以给一个 brief hint。不要给具体代码。

> 建议方向：模块级共享连接 + threading.Lock，所有操作走同一连接避免配置冲突。

---

### 7. 验证步骤

Agent 需要知道怎样确认修复有效。**列出命令，不手动代劳**。

> 修复后请跑以下命令验证：
> 1. `python -m pytest stock_picker/tests/unit/test_bundle_indexer.py -v`（4/4 PASS）
> 2. `sandu market-data prepare --phase minute-smoke --seed 42`（5/5 PASS）
> 3. 然后 commit

---

## 真实案例：DuckDB 多线程连接冲突

完整 prompt 原文如下，可作为参考：

```
## actual prompt content

修复 stock_picker 的 DuckDB 多线程连接冲突问题。

## Bug

sandu market-data prepare --phase minute-1m --resume --workers 24
因多线程并行写 market_coverage 导致大量 DuckDB 连接冲突失败，最终过早早停。

完整报错：
_duckdb.ConnectionException: Connection Error: Can't open a connection to same database file with a different configuration than existing connections
TransactionContext Error: Conflict on update!

调用链（通过 bundle_indexer 的 _index_connect 打开新连接）：
sync_one_stock_1m_only() [minute_universe_sync.py:311]
  → _update_lake_coverage() [lake_sync.py:53/57]
    → mark_coverage() [reference_sync_registry.py:47]
      → upsert_market_coverage() [bundle_indexer.py:363]
        → _index_connect() [bundle_indexer.py:321]

## 根因

多个 worker 同时打开 bundle_index.duckdb，但有些用 read_only=True 有些用 read_only=False。DuckDB 不允许同一文件被不同配置的多连接同时打开。

## 期望行为

24 个 worker 并行拉取 1m 数据时应能正常工作，不报 DuckDB 连接冲突。

## 建议方向

模块级共享连接 + threading.Lock，所有读/写操作通过同一个连接执行（加锁保护），避免配置不一致。主要修改点在 bundle_indexer.py（_index_connect 改为 contextmanager + 缓存连接、upsert/get/count 改为 with 块），reference_sync_registry.py 和 lake_sync.py 相应适配。

## 相关文件

stock_picker/core/bundle_indexer.py
stock_picker/core/reference_sync_registry.py
stock_picker/core/lake_sync.py
stock_picker/core/minute_universe_sync.py

## 验证

修复后至少跑 smoke（5/5 PASS）且 24 worker 不报 ConnectionError。
不需要我手动介入读代码或写补丁，请自行实现。
```

## 已修复的 commit

- `50496af` — fix(indexer): 共享 DuckDB 连接消除 minute-1m 多线程配置冲突
