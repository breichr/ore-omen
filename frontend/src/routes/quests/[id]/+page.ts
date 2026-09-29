import { error } from '@sveltejs/kit';
import { api, ApiError, type QuestInstance } from '$lib/api';
import { guard } from '$lib/guard';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
	const g = await guard('character', fetch);
	if (g.offline) return { ...g, instance: null, loadedAt: 0 };
	try {
		const instance = await api<QuestInstance>(`/quests/instances/${params.id}`, { fetch });
		return { ...g, instance, loadedAt: Date.now() };
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') {
			return { me: null, offline: true as const, instance: null, loadedAt: 0 };
		}
		if (e instanceof ApiError && e.status === 404) error(404, 'not_found');
		throw e;
	}
};
