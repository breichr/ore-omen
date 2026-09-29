import { describe, expect, it } from 'vitest';
import { homeFor } from './guard';
import type { Me } from './api';

const user = { username: 'rosa', timezone: 'Europe/Vienna' };

describe('homeFor', () => {
	it('sends guests to login', () => {
		expect(homeFor(null)).toBe('/login');
	});
	it('sends accounts without character to creation', () => {
		expect(homeFor({ user, character: null, server_time: '' })).toBe('/create');
	});
	it('sends players to the yard', () => {
		const me = { user, character: { name: 'Rosa' }, server_time: '' } as unknown as Me;
		expect(homeFor(me)).toBe('/yard');
	});
});
