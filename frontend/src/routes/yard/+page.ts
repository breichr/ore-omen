import { api, ApiError, type Jobs, type Quests, type Settlement } from '$lib/api';
import { guard } from '$lib/guard';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const g = await guard('character', fetch);
	if (g.offline) return { ...g, settlement: null, jobs: null, quests: null, loadedAt: Date.now() };
	try {
		const [settlement, jobs, quests] = await Promise.all([
			api<Settlement>('/settlement', { fetch }),
			api<Jobs>('/jobs', { fetch }),
			api<Quests>('/quests', { fetch })
		]);
		return { ...g, settlement, jobs, quests, loadedAt: Date.now() };
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') {
			return {
				me: null,
				offline: true as const,
				settlement: null,
				jobs: null,
				quests: null,
				loadedAt: 0
			};
		}
		throw e;
	}
};
