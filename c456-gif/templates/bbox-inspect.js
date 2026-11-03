const { chromium } = require('/Users/xiaohui/.local/lib/node_modules/@askjo/camofox-browser/node_modules/playwright-core');
const path = require('path');
const [, , htmlFile, ...ts] = process.argv;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const IDS = ['chef','hat','counter','pan','knife','board','book','tag0','tag1','tag2','tag3','final'];
(async () => {
  const b = await chromium.launch({ executablePath: CHROME, headless: true });
  const p = await b.newPage({ viewport: { width: 750, height: 420 } });
  await p.goto('file://' + path.resolve(htmlFile));
  await p.evaluate(() => document.fonts.ready);
  for (const tv of ts) {
    const t = parseFloat(tv);
    const res = await p.evaluate(([v, ids]) => {
      window.render(v);
      const out = { t: v, items: [] };
      for (const id of ids) {
        const el = document.getElementById(id);
        if (!el) { out.items.push({ id, missing: true }); continue; }
        let bb;
        try { bb = el.getBBox(); } catch (e) { out.items.push({ id, err: 'nobbox' }); continue; }
        // map through CTM to screen space
        const m = el.getCTM();
        const pts = [[bb.x,bb.y],[bb.x+bb.width,bb.y+bb.height]].map(([x,y]) => ({
          x: m.a*x + m.c*y + m.e, y: m.b*x + m.d*y + m.f
        }));
        out.items.push({
          id,
          op: +(el.getAttribute('opacity') ?? 1),
          x: Math.round(Math.min(pts[0].x, pts[1].x)),
          y: Math.round(Math.min(pts[0].y, pts[1].y)),
          w: Math.round(Math.abs(pts[1].x - pts[0].x)),
          h: Math.round(Math.abs(pts[1].y - pts[0].y))
        });
      }
      return out;
    }, [t, IDS]);
    const vis = res.items.filter(i => !i.missing && !i.err && i.op > 0.05);
    const bad = vis.filter(i => i.x < -8 || i.y < -8 || i.x + i.w > 758 || i.y + i.h > 428);
    console.log(`\n=== t=${t} ===`);
    console.log(vis.map(i => `${i.id}[${i.x},${i.y} ${i.w}x${i.h}]`).join('  '));
    if (bad.length) console.log('  !! OUT OF FRAME:', bad.map(i => i.id).join(','));
  }
  await b.close();
})();
