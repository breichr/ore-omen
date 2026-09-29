import { redirect } from '@sveltejs/kit';
import { ApiError, getMe, type Me } from './api';

export type Want = 'guest' | 'user' | 'no-character' | 'character';

/** Where a given session state belongs. */
export function homeFor(me: Me | null): string {
	if (!me) return '/login';
	return me.character ? '/yard' : '/create';
}

/**
 * Load the session and redirect if this page is not meant for it.
 * On network errors returns { offline: true } so the page can show a hint
 * instead of throwing the player back to the login screen.
 */
export async function guard(
	want: Want,
	f: typeof fetch
): Promise<{ me: Me | null; offline: false } | { me: null; offline: true }> {
	let me: Me | null;
	try {
		me = await getMe(f);
	} catch (e) {
		if (e instanceof ApiError && e.code === 'network') return { me: null, offline: true };
		throw e;
	}
	const ok =
		(want === 'guest' && !me) ||
		(want === 'user' && me) ||
		(want === 'no-character' && me && !me.character) ||
		(want === 'character' && me?.character);
	if (!ok) redirect(307, homeFor(me));
	return { me, offline: false };
}
