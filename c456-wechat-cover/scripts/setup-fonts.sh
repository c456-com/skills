#!/usr/bin/env bash
# 下载 Noto Sans SC（SIL OFL 开源字体）到 assets/fonts/
# 技能包不打包字体（全量 4.5MB），首次使用跑一次即可。
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
FONTS="$DIR/assets/fonts"
TMP="$(mktemp -d)"

echo "→ 下载 @fontsource-variable/noto-sans-sc ..."
cd "$TMP"
npm pack @fontsource-variable/noto-sans-sc --silent >/dev/null
tar xzf fontsource-variable-noto-sans-sc-*.tgz

mkdir -p "$FONTS"
cp package/files/*.woff2 "$FONTS"/
cp package/index.css "$FONTS/noto.css"

COUNT=$(ls "$FONTS"/*.woff2 | wc -l | tr -d ' ')
SIZE=$(du -sh "$FONTS" | cut -f1)
rm -rf "$TMP"

echo "✓ 字体就绪：$COUNT 个分片，$SIZE"
echo "  $FONTS"
echo
echo "字体许可：SIL Open Font License 1.1（可商用、可修改、可再分发）"
