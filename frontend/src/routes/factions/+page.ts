import { api, ApiError, type Factions } from '$lib/api';
import { guard } from '$lib/guard';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const g = await guard('character', fetch);
	if (g.offline) return { ...g, factions: null };
	try {
		return { ...g, factions: await api<Factions>('/factions', { fetch }) };
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') {
			return { me: null, offline: true as const, factions: null };
		}
		throw e;
	}
};
