# 认领会话身份：这个 pane 到底是不是「我派的那单」

> `tmux-opencode-agent` SKILL.md §1.5 的展开。适用于：派活后不确定任务有没有真跑、
> 探针没报任何东西、多个窗看着一模一样、或要重开/复用会话时先认领身份。

## 0. 为什么要做这一步

`session_id` 是探针唯一的过滤条件。服务端不认识的 id，探针**不会报错、不会退出**，
它只是永远等不到事件——而 `ps` 照样显示它活着。
⇒ 「探针进程存在」与「探针在监听有效目标」是两件事，前者不能推出后者。

## 1. 锚点验真（服务端清单是唯一真源）

```python
import json, base64, urllib.request, subprocess
URL = subprocess.run(["opencode","service","status"],capture_output=True,text=True).stdout.strip()
PW  = json.load(open('~/.config/opencode/service.json'))['password']
AUTH = "Basic " + base64.b64encode(f"opencode:{PW}".encode()).decode()
def get(p):
    r = urllib.request.Request(URL+p); r.add_header("Authorization", AUTH)
    return json.load(urllib.request.urlopen(r, timeout=25))

SID = "<要挂探针的 session_id>"
all_ids   = {s.get("id") for s in get("/api/session").get("data", [])}
active    = set(get("/api/session/active").get("data", {}).keys())

print("服务端认得吗 :", SID in all_ids)
print("当前 active  :", SID in active)
```

| 判据 | 结论 | 动作 |
|------|------|------|
| 不在 `all_ids` | **锚点是假的**（抄错 / 已归档 / 根本不是这个服务端的会话） | ⛔ 别挂探针。换 id 或新开会话 |
| 在 `all_ids`，不在 `active`，但屏上在忙 | 它在跑，**但不属于这个 id** | 走第 2 节认 pane 身份 |
| 在 `active` | 锚点有效 | 可挂探针 |

⚠️ **目录字段是 `location.directory`，不是 `directory`。**
读顶层 `directory` 会拿到全空，看起来像「这些会话都不属于本项目」——
**那是字段名错，不是环境不对**。踩过这个坑的后果是差点把「探针盯错」误报成「整台机器的会话都不对」，
白查一轮环境。

⚠️ `/api/session/active` 的 `data` 形状实测出现过两种：字典 `{sessionID: {...}}`
与分页对象 `{"data": ...}`。**先打 `type()` 再当字典用**，形状不对时按 list 处理会静默取空。

## 2. 认 pane 身份：pane 到底绑着哪个 opencode

```bash
tmux display-message -p -t <sess>:0 '#{pane_pid}'          # pane 的 shell pid
ps -eo pid,ppid,command | awk -v p=<pane_pid> '$1==p || $2==p'   # 它的 opencode 子进程
curl -s -u "opencode:$PW" "$URL/api/session/active" | grep -c 'ses_'  # active 会话数
```

三个问题**分开答**，只有第三个决定「屏上这屏是谁的」：

- **`pane_pid` 互不相同** ⇒ 各自独立的 opencode **进程**
- **`pane_pid` 相同** ⇒ 连进程都是同一个
- **⛔ 但前两条都不证明「会话独立」**：多个 TUI 前端可以连**同一个**服务端会话
  （实测：两个 pane 进程不同，服务端只有 1 个 active 会话，两窗在跑同一件活、屏内容一致）
  ⇒ **判「这几窗是一份还是几份」只比 active 会话数**，不靠 pane 数、也不靠进程数

对方报「同目录多个实例会并进同一个界面的多 tab」时，**先分开「几个进程」与「几个会话」再判**，
两条命令给出答案；**既不照单全收也不照单否定**。

## 3. 屏内容雷同：先分诊，别急着归因

派完活逐窗核它读到的是**哪一份** brief：

```bash
tmux capture-pane -p -t <sess>:0 -S -3000 \
  | grep -oE '<brief 文件名>.*\.md' | sort | uniq -c
```

两个 pane 命中同一份 ⇒ **我把同一份指令发了两次**，这是我的错。
但**在断定「我发重了」之前**先核 active 会话数（§2）：若只有 1 个 active 会话，
则两窗**本来就共享一个上下文**，屏内容一致是必然、不是我的错。
**先分诊「一份还是多份」，再谈是谁的错。**

## 4. 任务在跑的唯一判据：标记串

`ps` 有探针、屏底有 `esc interrupt`、产物还没落盘——三者齐了**也不能**推出「它在干我派的活」。
唯一判据是**我那条指令里的独特标记串出现在该 pane 历史里**：

```bash
# 派活时就在指令里塞一个独特标记（例：T3EXIT-V2-8F3K），事后 grep 它
tmux capture-pane -p -t <sess>:0 -S -3000 | grep -c 'T3EXIT-V2-8F3K'
```

| 结果 | 含义 |
|------|------|
| ≥1 | 指令确实落在这个 pane（**但仍不证明它在执行**，只证明它收到了） |
| 0 | 指令没到这里 ⇒ 找错 pane 了，或被审批拦下没发出去（见 SKILL.md「派活指令被安全审批拦下」节） |

## 5. 目录归属：第二把交叉核钥匙

```python
for s in get("/api/session").get("data", []):
    d = (s.get("location") or {}).get("directory") or ""   # ⚠️ 嵌套在 location 里
    if d and not d.startswith("<本单工作树>"):
        print("不属于本单工作树:", s.get("id"), d)
```

会话的目录不落在本单工作树上 ⇒ **它不是这个项目的**。
目录为空时**既不能当「不匹配」也不能当「匹配」**（真源可能就没填），
需靠标记串（§4）或产物落盘路径来定归属。

## 6. 自查清单（派活后第一件事）

- [ ] 指令里有独特标记串？
- [ ] 该 id 在服务端 `all_ids` 里？（`scripts/watch.py` 启动即核，不过会 `ANCHOR-FAIL`）
- [ ] 需要它在跑时，它在 `active` 里？
- [ ] 探针挂了 `--expect-dir` 吗？（同项目多 worktree 防串台）
- [ ] 该 pane 读到的是**我这单**的 brief？
- [ ] 投递通道配对了吗？（永不退出的探针**必须** `watch_patterns`，见 SKILL.md §6.5）
- [ ] 探针**只有**一个？同一 target 两个探针 ⇒ 每个信号投两遍

**⛔ 报「探针在盯」之前**先过这七条。`ps` 活只证明脚本没死，
不证明锚点对、不证明信号能投到我这儿。
