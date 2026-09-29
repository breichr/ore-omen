import { de } from './text/de';

/** "25 Holz, 15 $" – resources first, dollars last. */
export function formatAmounts(amounts: Record<string, number>): string {
	const entries = Object.entries(amounts).filter(([, v]) => v);
	entries.sort(([a], [b]) => (a === 'dollars' ? 1 : 0) - (b === 'dollars' ? 1 : 0));
	return entries
		.map(([k, v]) =>
			k === 'dollars'
				? `${v.toLocaleString('de-DE')} $`
				: `${v.toLocaleString('de-DE')} ${de.resources[k] ?? k}`
		)
		.join(', ');
}
