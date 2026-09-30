# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.0] - 2026-09-30

### Changed

- 版本号承接仓库内既有 1.2.0 线，避免版本倒退；内容以本机现行运行时手册为准
- 新增判据：同一工作目录 OpenCode 的 TUI tab 模型与键位真源、AskUserQuestion 提问面板处置、
  假终态识别（`tool.failed` / 主轮 succeeded 不等于收工）、单会话制、发送侧字符硬闸
  （`!` 会把输入切进 shell 模式，正文禁用）、会话身份验真与归属硬闸
- 新增 `references/`：会话身份、面板选择与答复、OpenCode v2 凭据、假终态成因
- 新增 `scripts/screen_watch.py`（屏副路轮询，识别提问面板）
- 公开脱敏：本机家目录路径、内部项目名与内部 issue 编号、个人称呼

## [1.0.0] - 2026-09-30

### Added

- 首次发布：tmux 中 OpenCode 的驱动与监控手册（可见 TUI 编排）
- 会话身份验真与归属硬闸（锚点只能取自服务端清单，不取自己的笔记）
- SSE 事件流为主判据的轮次终态判定（`session.execution.succeeded` / `interrupted`），
  并明确 `tool.failed` / `step.failed` / 主轮 succeeded 的假终态边界
- 权限面板（`Permission required`）与提问面板（`AskUserQuestion`）的识别与处置配方，
  含选中项「字色 + 底色」解析与散文兜底
- 发送侧硬闸：模式行（`Build` / `Shell`）核对、正文禁用 `!` `#` 等触发字符、token 增量验真
- 会话 tab 模型（同目录 opencode 合并为一个 TUI 的多 tab）与键位真源
- 常驻监控探针 `scripts/watch.py`（ANCHOR 校验、跨重连去重、子会话兜底、寿命绑窗口）
  与屏副路 `scripts/screen_watch.py`（15s 轮询识别提问面板）
- 参考文档：会话身份、面板选择与答复、OpenCode v2 凭据、假终态成因
