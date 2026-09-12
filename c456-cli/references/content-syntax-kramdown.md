# C456 富文本语法（Kramdown）

C456 正文使用 Kramdown 风格 Markdown。

## 标准语法

- `#` ~ `######` 标题（正文勿用 `#`，从 `##` 起）
- `**粗体**` `*斜体*` `` `行内代码` ``
- `- ` 无序列表 / `1. ` 有序列表
- `[链接](url)` / `![图片](url "title")`
- `>` 引用块
- ``` ``` 代码块（标注语言）
- `| 表头 | 表头 |` 表格
- `---` 分割线（勿在来源块前使用）

## Walkthrough 引用

在 signal/playbook 正文中引用其它 Walkthrough：

```markdown
:::walkthrough{id=4}
:::
```

**禁止**在 Walkthrough 自身正文中嵌入 `:::walkthrough{id=<当前id>}`。
