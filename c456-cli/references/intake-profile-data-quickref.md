# profile_data 快速参考

三种最常见 profile_data JSON 模板，用于 `c456 tool new` / `c456 channel new` 的 `--profile-data-json`。

## link_product（通用产品/官网）

```json
{"facets":[{"profile_id":"link_product","data":{"url":"https://example.com","name":"产品名"}}],"primary_profile_id":"link_product"}
```

## github_origin（GitHub 仓库）

```json
{"facets":[{"profile_id":"github_origin","data":{"_dict_key":"owner/repo","full_name":"owner/repo","url":"https://github.com/owner/repo"}}],"primary_profile_id":"github_origin"}
```

## social_account（社交媒体/频道）

```json
{"facets":[{"profile_id":"social_account","data":{"url":"https://youtube.com/@channel","name":"频道名"}}],"primary_profile_id":"social_account"}
```

## 故障排除

| 问题 | 解决 |
|------|------|
| `--auto-resolve-url` 返回 403（GitHub API 限流）或创建失败提示「至少添加一个资料段或图标」 | 改用显式 `--profile-data-json`。GitHub 仓库用 **`github_origin`** 段（比 `link_product` 语义更准）：`{"facets":[{"profile_id":"github_origin","data":{"_dict_key":"owner/repo","full_name":"owner/repo","url":"https://github.com/owner/repo"}}],"primary_profile_id":"github_origin"}`；不确定用 `link_product` |
| 422 "至少添加一个资料段或图标" | profile_data 为空或格式不对，检查 facet 结构（`--auto-resolve-url` 静默失败也会走到这里） |
| 不确定 profile_id | 用 `link_product` 最通用 |
