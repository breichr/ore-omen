// End-to-end smoke test of the M0 acceptance flow in a phone viewport:
// register → create character → close → reopen → still logged in; offline shell.
// Usage: BASE_URL=http://localhost:4173 node scripts/smoke.mjs [screenshot-dir]
import { chromium } from 'playwright-core';

const base = process.env.BASE_URL ?? 'http://localhost:4173';
const shots = process.argv[2];
const email = `smoke-${Date.now()}@example.com`;
const letters = () =>
	Array.from({ length: 6 }, () => String.fromCharCode(97 + Math.floor(Math.random() * 26))).join(
		''
	);
const name = `Rosa ${letters()}`; // names are unique; digits are not allowed

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const context = await browser.newContext({
	viewport: { width: 390, height: 844 },
	deviceScaleFactor: 2,
	isMobile: true,
	hasTouch: true,
	locale: 'de-DE'
});
const page = await context.newPage();
const shot = async (n) => shots && page.screenshot({ path: `${shots}/${n}.png`, fullPage: true });
const step = (msg) => console.log('✓', msg);
const expectUrl = async (path) => {
	await page.waitForURL((u) => u.pathname === path, { timeout: 10000 });
};

await page.goto(base);
await expectUrl('/login');
step('guest lands on /login');
await shot('1-login');

await page.getByRole('link', { name: /einsteigen/i }).click();
await expectUrl('/register');
await page.getByLabel('E-Mail').fill(email);
await page.getByLabel('Passwort').fill('geheim123');
await shot('2-register');
await page.getByRole('button', { name: 'Konto anlegen' }).click();
await expectUrl('/create');
step('registered, redirected to character creation');

await page.getByLabel('Name').fill(name);
await page.getByText('Kopfgeldjäger').click();
for (let i = 0; i < 3; i++) await page.getByRole('button', { name: 'Geschick erhöhen' }).click();
await page.getByRole('button', { name: 'Verstand erhöhen' }).click();
await shot('3-create');
await page.getByRole('button', { name: 'Aussteigen' }).click();
await expectUrl('/yard');
await page.getByText(name).waitFor();
await page.getByText('150 $').waitFor();
step(`character "${name}" created, yard shows name and 150 $`);
await shot('4-yard');

// "close the app and reopen": new page in the same browser profile
await page.close();
const page2 = await context.newPage();
await page2.goto(base);
await page2.waitForURL((u) => u.pathname === '/yard');
await page2.getByText(name).waitFor();
step('reopened: still logged in');

// Service worker + manifest
const swReady = await page2.evaluate(async () => {
	const reg = await navigator.serviceWorker.ready;
	return !!reg.active;
});
const manifest = await (await page2.request.get(`${base}/manifest.webmanifest`)).json();
if (!swReady || manifest.name !== 'Ore & Omen' || manifest.icons.length < 3) throw new Error('PWA');
step('service worker active, manifest ok');

// Offline: shell comes from cache, game state shows an offline hint
await page2.reload(); // ensure the page is controlled by the SW
await context.setOffline(true);
await page2.goto(`${base}/yard`);
await page2.getByText('Der Telegraf schweigt').waitFor();
await page2.getByText('Keine Verbindung').first().waitFor();
step('offline: app shell loads from cache with offline hint');
if (shots) await page2.screenshot({ path: `${shots}/5-offline.png` });
await context.setOffline(false);

// Logout
await page2.goto(`${base}/yard`);
await page2.getByRole('button', { name: 'Abmelden' }).click();
await page2.waitForURL((u) => u.pathname === '/login');
step('logout');

await browser.close();
console.log('smoke test passed');
