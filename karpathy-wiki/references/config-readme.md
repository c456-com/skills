# 复制到项目根 .config/ 的示例（勿提交含密钥的 json）

将 [`book-extract.example.json`](../../book-extract/references/book-extract.example.json) 复制为 `.config/book-extract.json`。

将 [`wiki-book-ingest.example.json`](../../wiki-book-ingest/references/wiki-book-ingest.example.json) 复制为 `.config/wiki-book-ingest.json`。

Init 时创建空 `.config/` 目录，并在根 `.gitignore` 追加 [`gitignore-snippet.md`](gitignore-snippet.md) 内容（merge：已存在则不重复追加）。
