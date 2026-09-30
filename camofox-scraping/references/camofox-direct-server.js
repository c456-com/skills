#!/usr/bin/env node
/**
 * CamoFox Direct — minimal Playwright + Camoufox API server.
 * 
 * Bypasses the original camofox-browser's broken /type and /click
 * by using page.evaluate() for all interactions.
 * 
 * WARNING: No humanization! Use only when the original API's
 * /type and /click fail for specific elements.
 * 
 * Usage:
 *   NODE_PATH=$(npm root -g)/@askjo/camofox-browser/node_modules \\
 *     node camofox-direct-server.js
 */

const PW_PATH = require('os').homedir() +
  '/.local/lib/node_modules/@askjo/camofox-browser/node_modules/playwright-core';
const { firefox } = require(PW_PATH);
const http = require('http');
const os = require('os');
const path = require('path');
const fs = require('fs');

const PORT = process.env.CAMOFOX_PORT || 9377;
const BINARY_PATH = os.homedir() +
  '/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox';
const COOKIE_DIR = os.homedir() + '/.camofox';

async function main() {
  const browser = await firefox.launch({
    executablePath: BINARY_PATH,
    headless: !(process.env.CAMOFOX_HEADLESS === 'false'),
  });

  const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');

    // Health
    if (req.method === 'GET' && req.url === '/') {
      return res.end(JSON.stringify({
        ok: true, running: true, connected: browser.isConnected()
      }));
    }

    // Create tab
    if (req.method === 'POST' && req.url === '/tabs') {
      try {
        const ctx = await browser.newContext({ viewport: null });
        const page = await ctx.newPage();
        const tabId = 'tab-' + Date.now();
        if (!global.tabs) global.tabs = {};
        global.tabs[tabId] = { ctx, page };
        return res.end(JSON.stringify({ tabId }));
      } catch (err) {
        return res.end(JSON.stringify({ error: err.message }));
      }
    }

    // Navigate
    if (req.method === 'POST' && req.url.includes('/navigate')) {
      const tabId = req.url.split('/')[2];
      let body = '';
      req.on('data', c => body += c);
      return req.on('end', async () => {
        try {
          const { url } = JSON.parse(body);
          const tab = global.tabs?.[tabId];
          if (!tab) return res.end(JSON.stringify({ error: 'tab not found' }));
          await tab.page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
          res.end(JSON.stringify({
            url: tab.page.url(), title: await tab.page.title()
          }));
        } catch (err) {
          res.end(JSON.stringify({ error: err.message }));
        }
      });
    }

    // Evaluate JS
    if (req.method === 'POST' && req.url.includes('/evaluate')) {
      const tabId = req.url.split('/')[2];
      let body = '';
      req.on('data', c => body += c);
      return req.on('end', async () => {
        try {
          const { expression } = JSON.parse(body);
          const tab = global.tabs?.[tabId];
          if (!tab) return res.end(JSON.stringify({ error: 'tab not found' }));
          res.end(JSON.stringify({ result: await tab.page.evaluate(expression) }));
        } catch (err) {
          res.end(JSON.stringify({ error: err.message }));
        }
      });
    }

    // Save cookies
    if (req.method === 'POST' && req.url.includes('/save-cookies')) {
      const tabId = req.url.split('/')[2];
      try {
        const tab = global.tabs?.[tabId];
        if (!tab) return res.end(JSON.stringify({ error: 'tab not found' }));
        const cookies = await tab.ctx.cookies();
        const domain = new URL(tab.page.url()).hostname;
        const file = path.join(COOKIE_DIR, domain + '-cookies.json');
        fs.mkdirSync(COOKIE_DIR, { recursive: true });
        fs.writeFileSync(file, JSON.stringify(cookies, null, 2));
        res.end(JSON.stringify({ ok: true, count: cookies.length, file }));
      } catch (err) {
        res.end(JSON.stringify({ error: err.message }));
      }
      return;
    }

    res.end(JSON.stringify({ error: 'not found' }));
  });

  server.listen(PORT, () => {
    console.log(`Direct API at http://localhost:${PORT}`);
  });
}

main().catch(err => { console.error(err.message); process.exit(1); });
