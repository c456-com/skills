#!/usr/bin/env node
/**
 * 渲染公众号封面
 *
 * 用法:
 *   node scripts/render.cjs --preset presets/editorial-01.json \
 *     --data '{"no":"01","label":"AI 拆解","vol":"VOL.001","title":"...","sub":"...","art":"assets/chefhat.svg"}' \
 *     --out cover.png
 *
 * 依赖: playwright 或 playwright-core（任装一个即可）
 *       npm i -D playwright && npx playwright install chromium
 *       或用环境变量 PLAYWRIGHT_MODULE 指定已安装的模块路径
 */
const fs = require('fs');
const path = require('path');

const SKILL = path.resolve(__dirname, '..');

function loadChromium() {
  const cwd = process.cwd();
  const tries = [
    process.env.PLAYWRIGHT_MODULE,
    path.join(cwd, 'node_modules/playwright-core'),
    path.join(cwd, 'node_modules/playwright'),
    'playwright-core',
    'playwright',
  ].filter(Boolean);
  for (const m of tries) {
    try {
      return require(m).chromium;
    } catch (_) { /* try next */ }
  }
  console.error(
    '\n[wechat-cover] 找不到 playwright。安装其一即可：\n' +
    '  npm i -D playwright && npx playwright install chromium\n' +
    '或指定已安装模块：\n' +
    '  PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/render.cjs ...\n'
  );
  process.exit(1);
}

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  return i > -1 ? process.argv[i + 1] : def;
}

const presetPath = arg('preset', path.join(SKILL, 'presets/editorial-01.json'));
const dataRaw = arg('data', '{}');
const out = arg('out', 'cover.png');
const chromium = loadChromium();

const preset = JSON.parse(fs.readFileSync(presetPath, 'utf8'));
const data = JSON.parse(dataRaw);

// 字体：技能不打包字体，首次使用需先跑 scripts/setup-fonts.sh
let fontCss = '';
const notoCssPath = path.join(SKILL, 'assets/fonts/noto.css');
if (fs.existsSync(notoCssPath)) {
  fontCss = fs.readFileSync(notoCssPath, 'utf8')
    .replace(/url\(\.\/files\//g, 'url(' + path.join(SKILL, 'assets/fonts') + '/')
    .replace(/'Noto Sans SC Variable'/g, "'Noto Sans SC'");
} else {
  console.error(
    '[wechat-cover] 还没装字体，中文会 fallback 到系统字体（可能不是开源字体）。\n' +
    '  先跑: bash scripts/setup-fonts.sh\n'
  );
}

const p = preset.palette || {};
const ty = preset.type || {};
let html = fs.readFileSync(path.join(SKILL, 'templates/base.html'), 'utf8');

const repl = {
  __FONT_FACES__: fontCss,
  __BG__: p.bg || '#F6F3ED',
  __INK__: p.ink || '#1A1A1A',
  __ACCENT__: p.accent || '#FA9704',
  __MUTED__: p.muted || '#6B6154',
  __TITLE_SIZE__: (ty.title || 58) + 'px',
  __SUB_SIZE__: (ty.sub || 22) + 'px',
  __LABEL_SIZE__: (ty.label || 17) + 'px',
  __VOL_SIZE__: (ty.vol || 15) + 'px',
  __NO__: data.no || '01',
  __LABEL__: data.label || 'AI 拆解',
  __VOL__: data.vol || 'VOL.001',
  __TITLE__: data.title || '标题',
  __SUB__: data.sub || '',
  __BRAND__: data.brand || '策思路 C456 · c456.com',
  __ART__: data.art ? 'file://' + path.join(SKILL, data.art) : '',
};
for (const [k, v] of Object.entries(repl)) html = html.split(k).join(v);

// 装饰开关
const decor = preset.decor || {};
const hide = [];
if (!decor.dots) hide.push('d-dots');
if (!decor.blob) hide.push('d-blob');
if (!decor.brandline) hide.push('d-brandline');
if (hide.length) {
  html = html.replace('</style>',
    hide.map(id => `#${id}{display:none!important}`).join('\n') + '</style>');
}

const tmp = path.join(SKILL, 'templates/_build.html');
fs.writeFileSync(tmp, html);

(async () => {
  // 优先用系统 Chrome（不必让 playwright 再下 100MB 的 chromium）；
  // 找不到就交给 playwright 自己解析（需先 npx playwright install chromium）
  const sysChrome = process.env.CHROME_PATH
    || (process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : '');
  const launchOpts = sysChrome && fs.existsSync(sysChrome)
    ? { executablePath: sysChrome, headless: true }
    : { headless: true };
  const b = await chromium.launch(launchOpts);
  const page = await b.newPage({ viewport: { width: 1080, height: 460 }, deviceScaleFactor: 2 });
  await page.goto('file://' + tmp);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(350);
  const outPath = path.resolve(out);
  await page.screenshot({ path: outPath });
  await b.close();
  console.log(JSON.stringify({ ok: true, out: outPath, preset: preset.id, layout: preset.layout }, null, 2));
})();
