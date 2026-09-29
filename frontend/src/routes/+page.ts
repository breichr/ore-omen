import { redirect } from '@sveltejs/kit';
import { ApiError, getMe } from '$lib/api';
import { homeFor } from '$lib/guard';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const me = await getMe(fetch);
		redirect(307, homeFor(me));
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') return { offline: true };
		throw e;
	}
};
