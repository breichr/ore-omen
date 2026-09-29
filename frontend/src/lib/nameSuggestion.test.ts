import { describe, expect, it } from 'vitest';
import { suggestCharacterName } from './nameSuggestion';

describe('suggestCharacterName', () => {
	it.each([
		['rosa', 'Rosa'],
		['rosa_1878', 'Rosa'],
		['mae_holloway', 'Mae Holloway'],
		['doc-mercy', 'Doc Mercy'],
		['Silas', 'Silas'],
		['jack__99__hart', 'Jack Hart'],
		['x1y2z3', 'Xyz']
	])('%s → %s', (username, expected) => {
		expect(suggestCharacterName(username)).toBe(expected);
	});

	it('returns empty when too little remains', () => {
		expect(suggestCharacterName('a1')).toBe('');
		expect(suggestCharacterName('1878')).toBe('');
		expect(suggestCharacterName('ab_12')).toBe('');
	});
});
