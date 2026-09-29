// Display helpers for timers. The server sends absolute end times; the client
// only counts down locally (docs/08-technik.md, "API").

/** "45 s", "5 min", "11 min 15 s", "3 h 12 min" (seconds hidden from 1 h on). */
export function formatDuration(totalSeconds: number): string {
	const s = Math.max(0, Math.round(totalSeconds));
	const h = Math.floor(s / 3600);
	const m = Math.floor((s % 3600) / 60);
	const sec = s % 60;
	if (h > 0) return m > 0 ? `${h} h ${m} min` : `${h} h`;
	if (m > 0) return sec > 0 ? `${m} min ${sec} s` : `${m} min`;
	return `${sec} s`;
}

/** Countdown "1:02:03" / "4:05" for running timers. */
export function formatCountdown(totalSeconds: number): string {
	const s = Math.max(0, Math.ceil(totalSeconds));
	const h = Math.floor(s / 3600);
	const m = Math.floor((s % 3600) / 60);
	const sec = String(s % 60).padStart(2, '0');
	return h > 0 ? `${h}:${String(m).padStart(2, '0')}:${sec}` : `${m}:${sec}`;
}

/** Offset to add to Date.now() to get server time. */
export function serverOffset(serverIso: string, clientNowMs: number): number {
	return new Date(serverIso).getTime() - clientNowMs;
}

/**
 * Display-only extrapolation of a resource between server snapshots:
 * stock + rate × elapsed, capped by storage. The server stays the source of truth.
 */
export function extrapolateMilli(
	amountMilli: number,
	ratePerHour: number,
	capacity: number,
	elapsedMs: number
): number {
	const cap = capacity * 1000;
	if (amountMilli >= cap) return amountMilli;
	const produced = Math.floor((ratePerHour * 1000 * Math.max(0, elapsedMs)) / 3_600_000);
	return Math.min(cap, amountMilli + produced);
}
