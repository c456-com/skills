# 大体积 raw 是否纳入 Git（Agent 询问用户后写入 .gitignore）

书籍/拍照录入后，若 `raw/` 总体积较大，**询问用户**是否将原始素材排除在版本库外（wiki 编译结果通常仍提交）。

## 体积粗算

```bash
du -sh raw domains/*/raw 2>/dev/null
find domains -path '*/raw/images/*' -o -path '*/raw/books/*' | head
```

经验阈值（可调）：单域 `raw/` **> 50MB**，或 `images/` 页图 **> 200 张**，建议与用户讨论是否 gitignore。

## 常见排除项（用户确认后 merge 进根 `.gitignore`）

```
# 大体积原始素材（用户选择不提交时取消注释）
# domains/*/raw/images/
# domains/*/raw/books/
# **/raw/vision-output/
# *.pdf
```

## 原则

| 层级 | 默认建议 |
|------|----------|
| `wiki/` | **提交** — 编译后的可问答知识 |
| `raw/` 小文件（MD、政策短文） | 可提交 |
| `raw/images/`、`raw/books/` 全书图、PDF | **询问** — 常放本地或对象存储，不推 Git |
| `.config/` | **永不提交** |

用户选择「wiki 进 Git、raw 不进」时：在 `wiki/sources/` 保留文字摘要与溯源路径即可，不依赖 raw 进远程仓库。
