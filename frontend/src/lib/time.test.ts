import { describe, expect, it } from 'vitest';
import { extrapolateMilli, formatCountdown, formatDuration, serverOffset } from './time';

describe('formatDuration', () => {
	it.each([
		[45, '45 s'],
		[300, '5 min'],
		[675, '11 min 15 s'], // Holzfällerplatz St. 3 (03-siedlung.md)
		[1519, '25 min 19 s'],
		[3600, '1 h'],
		[11533, '3 h 12 min']
	])('%i s → %s', (s, text) => expect(formatDuration(s)).toBe(text));
});

describe('formatCountdown', () => {
	it('formats minutes and hours', () => {
		expect(formatCountdown(65)).toBe('1:05');
		expect(formatCountdown(3723)).toBe('1:02:03');
		expect(formatCountdown(-3)).toBe('0:00');
		expect(formatCountdown(0.2)).toBe('0:01');
	});
});

describe('extrapolateMilli', () => {
	it('adds production and stops at capacity', () => {
		expect(extrapolateMilli(0, 20, 500, 3_600_000)).toBe(20_000);
		expect(extrapolateMilli(499_000, 20, 500, 3_600_000)).toBe(500_000);
		expect(extrapolateMilli(600_000, 20, 500, 3_600_000)).toBe(600_000);
	});
});

describe('serverOffset', () => {
	it('is server minus client time', () => {
		expect(serverOffset('2026-01-01T12:00:10Z', Date.parse('2026-01-01T12:00:00Z'))).toBe(10_000);
	});
});
