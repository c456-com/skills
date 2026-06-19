# 复制到项目根 .config/ 的示例（勿提交含密钥的 json）

录入书籍前，先按 [`skill-install.md`](skill-install.md) 确保 `book-extract`、`wiki-book-ingest` 已通过 `npx skills` 安装。

从**各技能安装目录**（`npx skills list --json` 返回的 `path`）复制 example，勿用 `../../其它技能/...` 相对路径：

```bash
# 将 <book-extract-path>、<wiki-book-ingest-path> 替换为 list 中的实际 path
cp "<book-extract-path>/references/book-extract.example.json" .config/book-extract.json
cp "<wiki-book-ingest-path>/references/wiki-book-ingest.example.json" .config/wiki-book-ingest.json
```

Init 时创建空 `.config/` 目录，并在根 `.gitignore` 追加 [`gitignore-snippet.md`](gitignore-snippet.md) 内容（merge：已存在则不重复追加）。
