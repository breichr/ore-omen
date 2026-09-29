import { api, ApiError, type Quests } from '$lib/api';
import { guard } from '$lib/guard';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const g = await guard('character', fetch);
	if (g.offline) return { ...g, quests: null, loadedAt: 0 };
	try {
		return { ...g, quests: await api<Quests>('/quests', { fetch }), loadedAt: Date.now() };
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') {
			return { me: null, offline: true as const, quests: null, loadedAt: 0 };
		}
		throw e;
	}
};
