// Parameterized frame grabber for gif-animation route A.
// Usage: node grab.js <input.html> <outDir> [durationSec=4] [fps=15] [width=750] [height=420]
// Requires the page to expose window.render(t) with t in [0,1] and to render deterministically.
const { chromium } = require('/Users/xiaohui/.local/lib/node_modules/@askjo/camofox-browser/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

const [, , htmlFile, outDir, durStr, fpsStr, wStr, hStr] = process.argv;
if (!htmlFile || !outDir) {
  console.error('usage: node grab.js <input.html> <outDir> [durationSec] [fps] [width] [height]');
  process.exit(1);
}
const DURATION = parseFloat(durStr || '4');
const FPS = parseInt(fpsStr || '15', 10);
const W = parseInt(wStr || '750', 10);
const H = parseInt(hStr || '420', 10);
const TOTAL = Math.round(FPS * DURATION);
const HOLD = 5; // held end frames so the loop reads cleanly
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

(async () => {
  fs.rmSync(outDir, { recursive: true, force: true });
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(htmlFile));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(200);

  for (let i = 0; i < TOTAL; i++) {
    const t = i / (TOTAL - 1);
    await page.evaluate((v) => window.render(v), t);
    await page.screenshot({ path: path.join(outDir, `f${String(i).padStart(4, '0')}.png`) });
  }
  for (let i = 0; i < HOLD; i++) {
    await page.screenshot({ path: path.join(outDir, `f${String(TOTAL + i).padStart(4, '0')}.png`) });
  }

  await browser.close();
  console.log(`${path.basename(htmlFile)} -> ${outDir}: ${TOTAL + HOLD} frames @${FPS}fps ${DURATION}s ${W}x${H}@2x`);
})();
