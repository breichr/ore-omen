import { redirect } from '@sveltejs/kit';
import { ApiError, getMe } from '$lib/api';
import { homeFor } from '$lib/guard';
import type { PageLoad } from './$types';

// Guests see the landing page; players go straight to where they belong.
export const load: PageLoad = async ({ fetch }) => {
	let me;
	try {
		me = await getMe(fetch);
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') return { offline: true };
		throw e;
	}
	if (me) redirect(307, homeFor(me));
	return { offline: false };
};
