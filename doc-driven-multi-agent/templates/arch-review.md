# Arch Review：<Feature>

> **Verdict:** ARCH_PASS | ARCH_FAIL
> **Reviewer:** Architect (Arch)
> **Scope:** <commit/PR/worktree>
> **Spec:** docs/superpowers/specs/<feature>.md
> **make ci evidence:** PASS（粘贴摘要或引用 comm entry）

## Spec 对齐

- <条目 1：是否对齐？>
- <条目 2：是否对齐？>

## 架构与并发

- <模块边界是否清晰？>
- <并发写入路径是否安全？>
- <存储布局是否符合约定？>

## 测试与可维护性

- <测试是否有意义？>
- <是否存在死代码或重复？>
- <命名和结构是否清晰？>

## 直接编辑（如有）

- `path:line` — <变更说明>

## Handoff

- **Target:** <Analyst (PASS) | Dev (FAIL)>
- **Address:** `docs/superpowers/reviews/arch-review-<feature>.md`（当前文档）, `docs/superpowers/comms/<feature>.md`
- **Task:** <PASS：Analyst 验证 | FAIL：Dev 按清单返工>
