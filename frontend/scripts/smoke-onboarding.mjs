// End-to-end check of the onboarding "Der letzte Zug" in a phone viewport.
// Takes about 2.5 minutes (two 1-minute steps).
// Usage: BASE_URL=http://localhost:4173 node scripts/smoke-onboarding.mjs [screenshot-dir]
import { chromium } from 'playwright-core';

const base = process.env.BASE_URL ?? 'http://localhost:4173';
const shots = process.argv[2];
const letters = () =>
	Array.from({ length: 6 }, () => String.fromCharCode(97 + Math.floor(Math.random() * 26))).join(
		''
	);
const username = `onb_${Date.now()}`;

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
const shot = async (n) => shots && page.screenshot({ path: `${shots}/${n}.png`, fullPage: true });
const step = (msg) => console.log('✓', msg);
const url = (path) => page.waitForURL((u) => u.pathname === path, { timeout: 15000 });
const wait = { timeout: 90_000 };

// Account and character
await page.goto(`${base}/register`);
await page.getByLabel('Benutzername').fill(username);
await page.getByLabel('Passwort').fill('geheim123');
await page.getByRole('button', { name: 'Konto anlegen' }).click();
await page.getByLabel('Ich habe den Schlüssel sicher notiert.').check();
await page.getByRole('button', { name: 'Weiter' }).click();
await url('/create');
await page.getByLabel('Name').fill(`Ada ${letters()}`);
await page.getByText('Prediger').click();
for (let i = 0; i < 4; i++) await page.getByRole('button', { name: 'Charisma erhöhen' }).click();
await page.getByRole('button', { name: 'Aussteigen' }).click();
await url('/yard');
await page.getByText('Der letzte Zug wartet noch auf dich.').click();
await url('/quests');
await shot('o1-quests');
step('yard points to the onboarding');

async function startQuest(title) {
	const card = page.locator('.quest', { hasText: title });
	await card.getByRole('button', { name: 'Aufbrechen' }).click();
	await page.waitForURL((u) => /^\/quests\/\d+$/.test(u.pathname));
}

// 1 · Ankunft
await startQuest('Der letzte Zug');
await page.getByText('Der Schaffner ist fort.', { exact: false }).waitFor();
await page.getByRole('button', { name: /Den Mantel mitnehmen/ }).click();
await page.getByText('Erhalten: Fremder Mantel').waitFor();
await shot('o2-arrival');
await page.getByRole('link', { name: 'Zu den Aufträgen' }).last().click();
step('1 · Ankunft: coat taken');

// 2 · Erste Arbeit (1 min)
await startQuest('Erste Arbeit');
await page.getByText('Unterwegs', { exact: true }).waitFor();
await page.getByText('Die letzte Kiste ist leichter', { exact: false }).waitFor(wait);
await page.getByText('+50 $').waitFor();
step('2 · Erste Arbeit: 1 minute, 50 $');
await page.getByRole('link', { name: 'Zu den Aufträgen' }).last().click();

// 3 · Ein Dach (1 min)
await startQuest('Ein Dach');
await page.getByText('Das Zelt steht.', { exact: false }).waitFor(wait);
await page.getByText('Haupthaus Stufe 1').waitFor();
step('3 · Ein Dach: tent built');
await page.getByRole('link', { name: 'Zu den Aufträgen' }).last().click();

// 4 · Der Mann aus dem Abteil: chance shown at the option
await startQuest('Der Mann aus dem Abteil');
await page.getByText('Charisma + Überreden – 75 %').waitFor();
await shot('o3-check');
await page.getByRole('button', { name: /Nachhaken/ }).click();
await page.getByText(/W20: \d+ → \d+ gegen 15/).waitFor();
await shot('o4-check-result');
step('4 · first check with chance and roll');
await page.getByRole('link', { name: 'Zu den Aufträgen' }).last().click();

// 6 · Die Stadt ruft
await startQuest('Die Stadt ruft');
await page.getByRole('button', { name: /Der Karte folgen/ }).click();
await page.getByText('Hüter +20').waitFor();
await page.getByText('Kompanie −5').waitFor();
await page.getByText('Aschenbande −2').waitFor();
await shot('o5-city');
step('6 · faction chosen, side effects shown');

await page.getByRole('link', { name: 'Fraktionen' }).click();
await url('/factions');
await page.getByText('Die Hüter der Schlucht').waitFor();
await shot('o6-factions');
await page.getByRole('link', { name: 'Hof' }).click();
await url('/yard');
if (await page.getByText('Der letzte Zug wartet noch auf dich.').count())
	throw new Error('onboarding hint should be gone');
step('onboarding finished');

await browser.close();
console.log('onboarding smoke test passed');
