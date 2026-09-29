// End-to-end smoke test of the M0 acceptance flow in a phone viewport:
// landing → register (recovery key) → create character → close → reopen → still
// logged in → offline shell → logout → recover password with the key.
// Usage: BASE_URL=http://localhost:4173 node scripts/smoke.mjs [screenshot-dir]
import { chromium } from 'playwright-core';

const base = process.env.BASE_URL ?? 'http://localhost:4173';
const shots = process.argv[2];
const username = `smoke_${Date.now()}`;
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
await page.getByRole('heading', { name: 'Ore & Omen' }).waitFor();
if (new URL(page.url()).pathname !== '/') throw new Error('guest should see landing page');
step('guest sees landing page');
await shot('0-landing');

await page.getByRole('link', { name: 'Einsteigen' }).click();
await expectUrl('/register');
await page.getByLabel('Benutzername').fill(username);
await page.getByLabel('Passwort').fill('geheim123');
await shot('2-register');
await page.getByRole('button', { name: 'Konto anlegen' }).click();
const recoveryKey = (await page.getByTestId('recovery-key').textContent()).trim();
if (!/^[0-9A-Z]{5}(-[0-9A-Z]{5}){4}$/.test(recoveryKey)) throw new Error(`key ${recoveryKey}`);
await shot('2b-recovery-key');
const cont = page.getByRole('button', { name: 'Weiter' });
if (!(await cont.isDisabled())) throw new Error('continue must need confirmation');
await page.getByLabel('Ich habe den Schlüssel sicher notiert.').check();
await cont.click();
await expectUrl('/create');
step('registered, recovery key shown once, redirected to character creation');

await page.getByLabel('Name').fill(name);
await page.getByText('Kopfgeldjäger').click();
for (let i = 0; i < 3; i++) await page.getByRole('button', { name: 'Geschick erhöhen' }).click();
await page.getByRole('button', { name: 'Verstand erhöhen' }).click();
await shot('3-create');
await page.getByRole('button', { name: 'Aussteigen' }).click();
await expectUrl('/yard');
await page.getByText(name).waitFor();
await page.getByText('150 $', { exact: true }).waitFor();
step(`character "${name}" created, yard shows name and 150 $`);
await shot('4-yard');

// M1: build the tent, see it in the queue with a countdown, start and stop a job
await page.getByRole('button', { name: 'Bauen' }).first().click();
await page.getByText('Haupthaus → Stufe 1').waitFor();
await page
	.getByText(/^\d+:\d\d(:\d\d)?$/)
	.first()
	.waitFor();
await page.getByText('50 $', { exact: true }).waitFor();
step('tent under construction with countdown, 100 $ paid');
await page.getByRole('button', { name: 'Anfangen' }).first().click();
await page.getByText('Du arbeitest: Holz hacken').waitFor();
await shot('4b-yard-building');
page.once('dialog', (d) => d.accept());
await page.getByRole('button', { name: 'Aufhören' }).click();
await page.getByText('Du arbeitest: Holz hacken').waitFor({ state: 'detached' });
step('job started and cancelled');

// Spend start skill points: level 1 caps a skill at 3
await page.getByRole('link', { name: /Jetzt verteilen/ }).click();
await page.waitForURL((u) => u.pathname === '/character');
const aimUp = page.getByRole('button', { name: 'Zielen erhöhen' });
for (let i = 0; i < 3; i++) await aimUp.click();
if (!(await aimUp.isDisabled())) throw new Error('skill cap not enforced in UI');
await page.getByRole('button', { name: 'Übernehmen' }).click();
await page.getByText('Gespeichert.').waitFor();
await page.getByText('2 Skillpunkte frei').waitFor();
await shot('4c-character');
await page.getByRole('link', { name: 'Zurück zum Hof' }).click();
await page.waitForURL((u) => u.pathname === '/yard');
step('skill points spent, cap respected');

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
await page2.goto(`${base}/settings`);
await page2.getByRole('button', { name: 'Abmelden' }).click();
await page2.waitForURL((u) => u.pathname === '/');
await page2.goto(`${base}/login`);
step('logout');

// Forgot password: recover with the key, get a new one, land in the yard
await page2.getByRole('link', { name: /Notfallschlüssel/ }).click();
await page2.waitForURL((u) => u.pathname === '/recover');
await page2.getByLabel('Benutzername').fill(username);
await page2.getByLabel('Notfallschlüssel').fill(recoveryKey.toLowerCase());
await page2.getByLabel('Neues Passwort').fill('neuesPasswort');
await page2.getByRole('button', { name: 'Passwort setzen' }).click();
const newKey = (await page2.getByTestId('recovery-key').textContent()).trim();
if (newKey === recoveryKey) throw new Error('key must rotate');
await page2.getByLabel('Ich habe den Schlüssel sicher notiert.').check();
await page2.getByRole('button', { name: 'Weiter' }).click();
await page2.waitForURL((u) => u.pathname === '/yard');
step('password recovered with key, new key issued');

// Settings: rotate the key while logged in (needs the current password)
await page2.getByRole('link', { name: 'Einstellungen' }).click();
await page2.waitForURL((u) => u.pathname === '/settings');
await page2.getByLabel('Passwort').fill('falsch123');
await page2.getByRole('button', { name: 'Neuen Schlüssel erzeugen' }).click();
await page2.getByText('Das Passwort stimmt nicht.').waitFor();
await page2.getByLabel('Passwort').fill('neuesPasswort');
await page2.getByRole('button', { name: 'Neuen Schlüssel erzeugen' }).click();
const rotatedKey = (await page2.getByTestId('recovery-key').textContent()).trim();
if (rotatedKey === newKey) throw new Error('settings must issue a new key');
if (shots) await page2.screenshot({ path: `${shots}/6-settings-key.png` });
await page2.getByLabel('Ich habe den Schlüssel sicher notiert.').check();
await page2.getByRole('button', { name: 'Weiter' }).click();
await page2.getByRole('heading', { name: 'Einstellungen' }).waitFor();
step('settings: wrong password rejected, new key issued');

await browser.close();
console.log('smoke test passed');
