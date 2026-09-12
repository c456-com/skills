# 素材库与列表图标

## 上传配图（正文插图）

```bash
c456 asset upload -f /path/to/image.png
# 输出 markdownSnippet，直接粘贴到正文
```

输出形如：`![说明](https://c456.com/our-assets/<id>/<ts>/<hash> "c456:asset/<id>")`

## 设置 tool/channel 列表图标

```bash
# 先用 asset upload 上传图标
c456 asset upload -f /path/to/icon.png

# 然后更新 intake 的 profile_data 中的 list_icon_url
# 用 --profile-data-json-file 传入 JSON 文件
echo '{"list_icon_url":"https://c456.com/our-assets/<id>/<ts>/<hash>"}' > .tmp/icon-update.json
c456 intake update <id> --profile-data-json-file .tmp/icon-update.json
```

## 注意事项

- 图片必须上传到 c456 素材库，不可引用外部 CDN
- 列表图标建议用正方形，至少 64×64
- 正文配图建议用 1280×720 或相近宽高比
