---
title: Handoff 聊天消息模板（所有角色）
type: reference
status: active
last-reviewed: 2026-06-30
---

# Handoff 聊天消息模板

> **Comm log 才是权威 handoff；** 聊天区块只是方便人类在会话之间转发的可复制摘要。

## 通用规则

| 规则 | 说明 |
|------|-------------|
| **Comm timestamp** | 写 entry 前运行 `TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z'`，不要编造 |
| **第一人称开场** | `我是 <Role Name> (<Code>)。`，不要用“你是 PO/Dev……”作为主体 |
| **Comm 优先** | 发送聊天区块前，发送方必须已经追加包含 Handoff 三要素的 comm |
| **接收流程** | 确认角色 → 找到 Target 匹配的 comm entry → 阅读 Address 文档 → 执行 Task |
| **越界拒绝** | 请求超出角色边界 → 第 1/2 次拒绝；第 3 次明确确认后才可 `OVERRIDE_ROLE_BOUNDARY` |

### Handoff 三要素（每个区块必填）

```markdown
**Handoff:**
- **Target:** <Role Name> (<Code>)
- **Address:** `docs/...`（至少 1 个路径，包含当前 comm entry）
- **Task:** 一两句话说明下一个角色要做什么
```

### 聊天区块必填字段

| 字段 | 说明 |
|-------|-------------|
| 开场 | 第一人称角色声明 |
| 请先阅读 | 当前 comm entry + Address 路径，按顺序排列 |
| 背景 | 可选，用 1–2 句话说明上下文 |
| 请执行 | 具体任务，动词开头 |
| 预期产出 | verdict 标签、文档、CI/test 证据 |
| 注意事项 | comm log 要求、禁止事项 |

---

## 越界拒绝（所有角色）

当人类或上一个会话要求你执行**明显超出当前角色边界**的工作时：

**第 1 / 第 2 次拒绝（可复制）：**

```markdown
我是 <Role Name> (<Code>)。

你要求我执行“<task summary>”，但这属于 <Correct Role Name> (<Code>) 的职责。
这超出了我的角色权限。**我不会执行这项工作。**

正确路径：
1. comm Handoff → Target: <Correct Role>
2. Address: <spec/plan/review path>
3. Task: <该角色要做什么>

请为 <Correct Role> 打开一个会话，或请人类转发上面的 Handoff。

如果你仍坚持让我以 <current role> 身份执行，请在第 3 次或之后明确书面确认；
确认后我会记录 `OVERRIDE_ROLE_BOUNDARY` 并继续。
```

**例外执行后（comm 必须包含）：**

```markdown
**Said / Decided:**
- `OVERRIDE_ROLE_BOUNDARY` — 人类第 3 次确认由 <Code> 执行“<task summary>”
- 确认原文：«…»
```

---

## PM → PO

**场景：** Plan 已就绪，请求 G1.5 设计对齐或 Dev 分派批准

```markdown
我是 Project Manager (PM)。请对 feature `<feature-slug>` 做 **G1.5 设计对齐**，或评审 plan。

**请先阅读（按顺序）：**
1. `docs/superpowers/comms/<feature>.md` — 最新 PM entry
2. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`

**请确认任务范围是否与产品设计一致；如批准，请分派 Dev（G2）。**

**预期产出：** comm `APPROVED` + Handoff 三要素 → Developer (Dev)
```

---

## PM → Arch

```markdown
我是 Project Manager (PM)。请对 feature `<feature-slug>` 做**架构预审**（复杂任务）。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/specs/<feature>.md`
3. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`

**请评估实现方案（存储 / 并发 / 模块边界）。**

**预期产出：** comm `ARCH_PRE_PASS`，或修改清单 + Handoff → Product Owner (PO)
```

---

## PO → PM

```markdown
我是 Product Owner (PO)。Feature `<feature-slug>` 的设计已冻结。请编写 plan 并排期。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/specs/<feature>.md` — Status: approved

**请编写包含任务、依赖和风险的 plan；复杂任务标记为需要 Arch pre-review。**

**预期产出：** `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` + comm Handoff
```

---

## PO → Dev

```markdown
我是 Product Owner (PO)。请 Developer (Dev) 实现 feature `<feature-slug>` 的 **Task <N>**（G2 implementation go）。

**请先阅读（按顺序）：**
1. `docs/superpowers/comms/<feature>.md` — this PO Handoff
2. `docs/superpowers/specs/<feature>.md` — acceptance criteria §…
3. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` — Task <N>
4. PM 提供的 worktree path（检查 plan meta）

**请按 plan Task <N> 做 TDD；只在 worktree 中工作；完成后 Handoff 给 Arch。**

**预期产出：** code + pytest；`make ci` PASS；comm Handoff → Architect (Arch)

**注意：** 不要扩 scope；实现问题找 Arch，不要直接找 PO。
```

---

## PO → Arch

```markdown
我是 Product Owner (PO)。请对 feature `<feature-slug>` 做**架构预审**（存储 / 并发 / 方案）。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/specs/<feature>.md`

**请评估实现可行性；如果发现产品语义问题 → `ESCALATE_PO`。**

**预期产出：** comm `ARCH_PRE_PASS`，或修改建议 + Handoff
```

---

## Arch → Dev

```markdown
我是 Architect (Arch)。Feature `<feature-slug>` 的代码评审 verdict：**ARCH_FAIL**。请 Developer (Dev) 返工。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/reviews/arch-review-<feature>-YYYY-MM-DD.md` — 返工 checklist

**请按 review checklist 做 TDD 修复；重新提交给我前确保 `make ci` 通过。**

**预期产出：** fixed code + comm Handoff → Architect (Arch)

**注意：** 如果需要改变产品语义或 ADR，请停止编码，等待 PO/Arch 更新文档。
```

---

## Arch → Analyst

```markdown
我是 Architect (Arch)。Feature `<feature-slug>` 的代码评审 verdict：**ARCH_PASS**。请 Data Analyst (Analyst) 做独立数据验证。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/reviews/arch-review-<feature>-YYYY-MM-DD.md`
3. `docs/superpowers/specs/<feature>.md` — acceptance criteria

**请按 spec 做独立验证（三阶段或 spec 指定流程）；不要修改产品代码。**

**预期产出：** `reviews/<feature>-analyst-*.md` + comm `DATA_PASS` / `DATA_FAIL`
```

---

## Arch → PO

```markdown
我是 Architect (Arch)。Feature `<feature-slug>` 存在**产品语义 / 验收标准**问题，需要 Product Owner (PO) 决策（ESCALATE_PO）。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/specs/<feature>.md`
3. `docs/superpowers/reviews/arch-review-*.md`（如有）

**请澄清或更新 spec；Dev 继续前，comm 中必须有 `APPROVED`。**

**预期产出：** 更新后的 spec 或决策文档 + comm Handoff → Dev / PM
```

---

## Dev → Arch

```markdown
我是 Developer (Dev)。Feature `<feature-slug>` 的 **Task <N>** 已完成。请 Architect (Arch) 做代码评审。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry（含 Verification 表）
2. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` — Task <N>
3. Code paths：（列出变更文件）

**Dev 已执行测试（请不要重跑完整 CI）：**
- （从 comm Verification 表复制：command、result、duration）
- Not run：（理论案例、完整回测 → Analyst）

**请静态评审实现质量和 spec 对齐情况；签署 `ARCH_PASS` / `ARCH_FAIL`。**

**预期产出：** arch-review doc + comm Handoff → Analyst（PASS）或 Dev（FAIL）
```

---

## Analyst → Dev

```markdown
我是 Data Analyst (Analyst)。Feature `<feature-slug>` 的数据验证 verdict：**DATA_FAIL**。请 Developer (Dev) 按 bug list 修复。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/reviews/<feature>-analyst-YYYY-MM-DD.md` — bug list + 复现步骤

**请按 review 修复数据 bug；不要修改 spec。修复后 Handoff 给 Arch 复审。**

**预期产出：** fixed code + pytest/ci + comm Handoff → Architect (Arch)
```

---

## Analyst → PO

```markdown
我是 Data Analyst (Analyst)。Feature `<feature-slug>` 的数据验证 verdict：**DATA_PASS**。请 Product Owner (PO) 做产品验收（G3）。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/reviews/<feature>-analyst-YYYY-MM-DD.md`
3. `docs/superpowers/specs/<feature>.md` — acceptance criteria

**请对照 spec 评审分析报告；如通过，签署 `PRODUCT_ACCEPTED` 进入关闭流程。**

**预期产出：** comm `PRODUCT_ACCEPTED` + Handoff → Project Manager (PM) 归档
```

---

## PO → PM（产品验收）

```markdown
我是 Product Owner (PO)。Feature `<feature-slug>` 产品验收：**PRODUCT_ACCEPTED**。请 Project Manager (PM) 执行归档关闭（G4）。

**请先阅读：**
1. `docs/superpowers/comms/<feature>.md` — 当前 entry
2. `docs/superpowers/reviews/`（Arch + Analyst 链路）
3. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` — 确认全部 `[x]`

**请确认 plan 全绿、reviews 完整、daily 已更新。然后启动 G4 closure。**

**预期产出：** comm `COMMIT_REQUEST` → PO, Dev, Analyst
```

---

## 默认 Handoff 方向速查

| 来自 | 默认交给 | 模板章节 |
|------|-----------|-----------------|
| PM | PO / Arch | PM → PO · PM → Arch |
| PO | PM / Dev / Arch | PO → PM · PO → Dev · PO → Arch |
| Arch | Dev / Analyst / PO | Arch → Dev · Arch → Analyst · Arch → PO |
| Dev | Arch | Dev → Arch |
| Analyst | Dev / PO | Analyst → Dev · Analyst → PO |
