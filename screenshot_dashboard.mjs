import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const indexPath = path.join(__dirname, 'Frontend', 'index.html');
const wavPath = path.join(__dirname, 'Backend', 'test_audio.wav');

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900'],
  defaultViewport: { width: 1440, height: 900 }
});

const page = await browser.newPage();

// Allow cross-origin fetch to localhost:8000
await page.setExtraHTTPHeaders({ 'Accept': '*/*' });

await page.goto(`file:///${indexPath.replace(/\\/g, '/')}`);
await page.waitForSelector('#page-landing', { visible: true });

// Navigate to dashboard
await page.evaluate(() => navigateTo('page-dashboard'));
await page.waitForSelector('#page-dashboard:not(.hidden)', { timeout: 5000 });
await new Promise(r => setTimeout(r, 1500));

// Upload the test WAV file via the hidden file input
const inputHandle = await page.$('#dbFileInput');
await inputHandle.uploadFile(wavPath);

// Wait for results to appear
await page.waitForSelector('#dbResults.visible', { timeout: 30000 });
await new Promise(r => setTimeout(r, 800));

await page.screenshot({ path: 'screenshot_dashboard_api.png', fullPage: false });
console.log('Screenshot saved: screenshot_dashboard_api.png');

await browser.close();
