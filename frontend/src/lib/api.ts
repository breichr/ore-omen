// Thin client for the API. The client never calculates game results:
// it sends intents and renders what the server returns.

import { markOffline, markOnline } from './network.svelte';

export type Character = {
	id: number;
	name: string;
	character_class: string;
	level: number;
	xp: number;
	xp_level_start: number;
	xp_next_level: number;
	attributes: Record<string, number>;
	skills: Record<string, number>;
	skill_cap: number;
	unspent_attribute_points: number;
	unspent_skill_points: number;
	duel_values: Record<string, number>;
	max_life: number;
	dollars: number;
	bank_dollars: number;
	corruption: number;
	region: string;
	status: string;
};

export type Me = {
	user: { username: string; timezone: string };
	character: Character | null;
	server_time: string;
};

export type Settlement = {
	as_of: string;
	dollars: number;
	capacity: number;
	protected_share: number;
	resources: { name: string; amount_milli: number; rate_per_hour: number }[];
	buildings: {
		code: string;
		category: string;
		name: string;
		description: string;
		level: number;
		variant: string | null;
		produces: Record<string, number>;
		next: { level: number; cost: Record<string, number>; seconds: number } | null;
		can_build: boolean;
		reason: string | null;
	}[];
	queue: {
		id: number;
		type: string;
		target_level: number;
		started_at: string;
		finishes_at: string;
	}[];
	queue_slots: number;
	lost: Record<string, number>;
};

export type JobActivity = {
	id: number;
	job: string;
	started_at: string;
	finishes_at: string;
	status: string;
	result: { yield?: Record<string, number>; lost?: Record<string, number>; xp?: number };
};

export type Jobs = {
	as_of: string;
	current: JobActivity | null;
	last: JobActivity | null;
	jobs: {
		code: string;
		name: string;
		description: string;
		seconds: number;
		yield: Record<string, number>;
		xp: number;
		overflow: Record<string, number>;
	}[];
};

export class ApiError extends Error {
	constructor(
		public status: number,
		public code: string
	) {
		super(code);
	}
}

type Fetch = typeof fetch;

export async function api<T>(
	path: string,
	options: { method?: string; body?: unknown; fetch?: Fetch } = {}
): Promise<T> {
	const f = options.fetch ?? fetch;
	let res: Response;
	try {
		res = await f(`/api${path}`, {
			method: options.method ?? 'GET',
			credentials: 'same-origin',
			headers: options.body !== undefined ? { 'Content-Type': 'application/json' } : {},
			body: options.body !== undefined ? JSON.stringify(options.body) : undefined
		});
	} catch {
		markOffline();
		throw new ApiError(0, 'network');
	}
	markOnline();
	if (res.status >= 502 && res.status <= 504) throw new ApiError(res.status, 'network');
	const data = await res.json().catch(() => null);
	if (!res.ok) throw new ApiError(res.status, errorCode(res.status, data));
	return data as T;
}

function errorCode(status: number, data: unknown): string {
	const detail = (data as { detail?: unknown } | null)?.detail;
	if (detail && typeof detail === 'object' && 'code' in detail) {
		return String((detail as { code: unknown }).code);
	}
	if (status === 422) return 'validation';
	return 'unknown';
}

/** Current session state, or null when not logged in. Throws on network errors. */
export async function getMe(f?: Fetch): Promise<Me | null> {
	try {
		return await api<Me>('/me', { fetch: f });
	} catch (e) {
		if (e instanceof ApiError && e.status === 401) return null;
		throw e;
	}
}
