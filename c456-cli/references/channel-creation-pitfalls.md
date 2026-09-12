# 渠道创建常见问题

`c456 channel new` 的踩坑记录，来自实际使用。

## 问题1：`--auto-resolve-url` 可能失败

某些网站（如 Product Hunt）的 `--auto-resolve-url` 无法自动生成资料段，导致 422 校验失败。

**症状：**
```
❌ 创建失败：校验失败
  • 说明：请至少添加一个资料段或图标
```

**解决：** 改用 `--profile-data-json` 手动传入 `link_product` 资料段：

```bash
npx c456-cli channel new -u "<URL>" -t "标题" \
  --profile-data-json '{"facets":[{"profile_id":"link_product","data":{"url":"<URL>","name":"名称"}}],"primary_profile_id":"link_product"}' \
  --body-file .tmp/body.md
```

## 问题2：标题含特殊字符（引号、撇号、管道符）

Shell 引号嵌套会导致标题被截断或解析错误。

**症状：**
```
❌ 创建失败：校验失败
  • 说明：名称 不能为空
```

**可能原因：** 标题中的 `|`、`'`（单引号）、`"`（双引号）导致 shell 参数解析异常。

**解决：** 去掉标题中的特殊字符，或者用双引号包裹且确保内部无未转义的单引号。

```bash
# ❌ 单引号冲突
c456 channel new -t "Simon's Blog"     # shell 解析错误

# ✅ 去掉或换用
c456 channel new -t "Simon Blog"
```

## 问题3：`--body-file` 文件不存在或格式不对

**症状：** 命令成功但正文为空。

**解决：** 总是先写文件再提交，且用临时目录 `.tmp/`：

```bash
mkdir -p .tmp
echo "正文描述" > .tmp/body.md
c456 channel new -u "<URL>" -t "标题" --body-file .tmp/body.md
rm -f .tmp/body.md
```

## 通用最佳实践

```bash
# 完整工作流
mkdir -p .tmp
echo "渠道描述" > .tmp/body.md
npx c456-cli channel new \
  -u "https://example.com" \
  -t "渠道名" \
  --profile-data-json '{"facets":[{"profile_id":"link_product","data":{"url":"https://example.com","name":"渠道名"}}],"primary_profile_id":"link_product"}' \
  --body-file .tmp/body.md
```
