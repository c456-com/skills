#!/usr/bin/env node
/**
 * CamoFox macOS Headful Patcher
 * 
 * Enables visible browser window on macOS by patching server.js in-place.
 * All 34 versions of @askjo/camofox-browser force headless:true on macOS.
 * This script restores from .bak, patches the headless expression, and launches.
 * 
 * Usage:
 *   node macos-headful-patcher.js
 * 
 * The window appears on your desktop at http://localhost:9377.
 * Verify: curl -s http://localhost:9377/
 */

import fs from 'fs';
import { spawn } from 'child_process';
import { join } from 'path';
import os from 'os';

const globalDir = join(os.homedir(), '.local', 'lib', 'node_modules', '@askjo', 'camofox-browser');
const serverPath = join(globalDir, 'server.js');

if (!fs.existsSync(serverPath)) {
  console.error('CamoFox not found. Install: npm install -g @askjo/camofox-browser');
  process.exit(1);
}

// Restore original from backup if it exists
const backupPath = serverPath + '.bak';
if (fs.existsSync(backupPath)) {
  fs.copyFileSync(backupPath, serverPath);
}

let code = fs.readFileSync(serverPath, 'utf-8');
let patched = code;

// 1. Enable headful mode: headless: useVirtualDisplay ? false : true → headless: false
patched = patched.replace(
  'headless: useVirtualDisplay ? false : true',
  'headless: false'
);

// 2. Replace viewport to avoid Camoufox Firefox isMobile bug:
//    Error: "Found property <root>.viewport.isMobile - false"
patched = patched.replace(
  'viewport: { width: 1280, height: 720 },\n        permissions:',
  'noDefaultViewport: true,\n        permissions:'
);

// Write backup first time
if (!fs.existsSync(backupPath)) {
  fs.copyFileSync(serverPath, backupPath);
}
fs.writeFileSync(serverPath, patched, 'utf-8');

// Launch from the package directory so ESM imports resolve
const proc = spawn('node', [serverPath], {
  cwd: globalDir,
  env: { ...process.env, CAMOFOX_PORT: process.env.CAMOFOX_PORT || '9377' },
  stdio: 'inherit',
});

process.on('SIGINT', () => proc.kill('SIGINT'));
process.on('SIGTERM', () => proc.kill('SIGTERM'));
