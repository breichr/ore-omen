<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import { de, errorText } from '$lib/text/de';

	let { mode }: { mode: 'login' | 'register' } = $props();

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let busy = $state(false);

	const isLogin = $derived(mode === 'login');

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		error = '';
		try {
			await api(isLogin ? '/auth/login' : '/auth/register', {
				method: 'POST',
				body: { email, password }
			});
			await goto('/', { invalidateAll: true });
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}
</script>

<main>
	<p class="brand">{de.app.name}</p>
	<h1>{isLogin ? de.auth.loginTitle : de.auth.registerTitle}</h1>
	<p class="story">{isLogin ? de.auth.loginIntro : de.auth.registerIntro}</p>

	<form onsubmit={submit} novalidate>
		<label for="email">{de.auth.email}</label>
		<input id="email" type="email" autocomplete="email" required bind:value={email} />

		<label for="password">{de.auth.password}</label>
		<input
			id="password"
			type="password"
			autocomplete={isLogin ? 'current-password' : 'new-password'}
			required
			minlength={isLogin ? undefined : 8}
			bind:value={password}
		/>
		{#if !isLogin}<p class="dim">{de.auth.passwordHint}</p>{/if}

		{#if error}<p class="error" role="alert">{error}</p>{/if}

		<button class="btn" type="submit" disabled={busy || !email || !password}>
			{isLogin ? de.auth.login : de.auth.register}
		</button>
	</form>

	<p class="switch">
		<a href={isLogin ? '/register' : '/login'}>{isLogin ? de.auth.toRegister : de.auth.toLogin}</a>
	</p>
</main>

<style>
	.brand {
		margin: 1.5rem 0 0;
		color: var(--accent);
		font-family: var(--font-story);
		letter-spacing: 0.2em;
		text-transform: uppercase;
		font-size: 0.8rem;
	}
	.switch {
		margin-top: 1.5rem;
		text-align: center;
	}
</style>
