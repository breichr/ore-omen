// Renders static/icons/icon.svg into the PNG sizes the manifest and iOS need.
// Usage: node scripts/render-icons.mjs  (needs Chromium; set CHROMIUM_PATH if not found)
import { chromium } from 'playwright-core';
import { readFile } from 'node:fs/promises';

const svg = await readFile(new URL('../static/icons/icon.svg', import.meta.url), 'utf8');
const out = (name) => new URL(`../static/icons/${name}`, import.meta.url).pathname;

const targets = [
	{ name: 'icon-192.png', size: 192, pad: 0 },
	{ name: 'icon-512.png', size: 512, pad: 0 },
	{ name: 'apple-touch-icon.png', size: 180, pad: 0 },
	// Maskable: keep the motif inside the 80 % safe zone, background full-bleed
	{ name: 'icon-maskable-512.png', size: 512, pad: 0.14 }
];

const browser = await chromium.launch({
	executablePath: process.env.CHROMIUM_PATH || undefined
});
const page = await browser.newPage();
for (const t of targets) {
	const inner = Math.round(t.size * (1 - 2 * t.pad));
	const body = svg.replace('rx="96"', t.pad || t.name.startsWith('apple') ? 'rx="0"' : 'rx="96"');
	await page.setViewportSize({ width: t.size, height: t.size });
	await page.setContent(
		`<html><body style="margin:0;background:#16110d;display:grid;place-items:center;height:100vh">
		<div style="width:${inner}px;height:${inner}px">${body.replace('<svg ', '<svg width="100%" height="100%" ')}</div>
		</body></html>`
	);
	await page.screenshot({ path: out(t.name), omitBackground: false });
	console.log('wrote', t.name);
}
await browser.close();
