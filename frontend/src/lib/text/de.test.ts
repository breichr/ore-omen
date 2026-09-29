import { describe, expect, it } from 'vitest';
import { de, errorText } from './de';

describe('de texts', () => {
	it('has a name for every class and attribute code the API uses', () => {
		for (const c of ['gunslinger', 'prospector', 'quack', 'preacher', 'bounty_hunter']) {
			expect(de.classes[c]?.name).toBeTruthy();
		}
		for (const a of ['strength', 'dexterity', 'intellect', 'charisma']) {
			expect(de.attributes[a]?.name).toBeTruthy();
		}
	});
	it('maps error codes and falls back for unknown ones', () => {
		expect(errorText('name_taken')).toContain('Namen');
		expect(errorText('does_not_exist')).toBe(de.errors.unknown);
	});
});
