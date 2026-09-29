import { describe, expect, it } from 'vitest';
import { formatAmounts } from './format';

describe('formatAmounts', () => {
	it('puts dollars last and skips zeros', () => {
		expect(formatAmounts({ dollars: 15, cattle: 20, iron: 0 })).toBe('20 Vieh, 15 $');
		expect(formatAmounts({ wood: 3436 })).toBe('3.436 Holz');
	});
});
