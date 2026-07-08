# Analyst 验证：<Feature>

> **Verdict:** DATA_PASS | DATA_FAIL
> **Spec:** docs/superpowers/specs/<feature>.md
> **Arch review:** docs/superpowers/reviews/arch-review-<feature>.md
> **Version:** <如适用，填写配置中的版本>

## 独立验证方法

- 使用的命令 / 脚本：<如何运行>
- 与 Dev 路径的差异：<你的运行方式与 Dev 有何不同>

## 阶段 ①：Reference Cases

| Case ID | Expected | Actual | Notes |
|---------|----------|--------|-------|
| case-1 | <value> | <value> | <match/mismatch> |
| case-2 | <value> | <value> | <match/mismatch> |

## 阶段 ②：Sample Set（例如 500 支股票）

- 命中率：<value>
- 误报样本：<带日期 / 代码的示例>
- 分布备注：<异常情况>

## 阶段 ③：Full Universe（如已执行）

- 总样本数：<N>
- 稳定性：<OK / issues>

## 结论与 DATA BUG List（Dev）

- BUG-1: ts_code=xxx date=yyy expected=a actual=b — 复现：`command`
- BUG-2: …

## 阈值 / 语义建议（PO）

- <可选：给 PO 考虑的建议>

## Handoff

- **Target:** <Developer (Dev) | Product Owner (PO)>
- **Address:** `docs/superpowers/reviews/<feature>-analyst-*.md`（当前文档）, `docs/superpowers/comms/<feature>.md`
- **Task:** <DATA_FAIL：修 bug → Arch | DATA_PASS：产品验收>
