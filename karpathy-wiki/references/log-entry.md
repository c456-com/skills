# 日志条目格式

## 根层 init

```markdown
## [{{DATE}}] init | 初始化 Meta-Wiki

- 创建根层 raw/wiki/shared/domains 目录结构
- 写入 AGENTS.md、wiki/index.md、wiki/log.md
- 技能来源：karpathy-wiki（c456-com/skills）
{{DOMAIN_INIT_LINES}}
```

## 新增领域

```markdown
## [{{DATE}}] create | 新增领域 {{DOMAIN_DISPLAY_NAME}}

- 路径：`domains/{{DOMAIN_NAME}}/`
- 写入领域 AGENTS.md、wiki/index.md、wiki/log.md
- 已更新根 wiki/index.md 领域注册表
```

## 领域层 init

```markdown
## [{{DATE}}] init | 初始化领域 {{DOMAIN_DISPLAY_NAME}}

- 创建 domains/{{DOMAIN_NAME}}/ 三层目录
- 写入 AGENTS.md、wiki/index.md
```

## 操作类型

`ingest` · `query` · `lint` · `update` · `create` · `init`

保持 append-only，不修改历史条目。
