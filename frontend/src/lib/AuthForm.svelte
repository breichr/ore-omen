<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import RecoveryKey from '$lib/RecoveryKey.svelte';
	import { de, errorText } from '$lib/text/de';

	let { mode }: { mode: 'login' | 'register' } = $props();

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let busy = $state(false);
	let recoveryKey = $state('');

	const isLogin = $derived(mode === 'login');

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		error = '';
		try {
			if (isLogin) {
				await api('/auth/login', { method: 'POST', body: { username, password } });
				await goto('/', { invalidateAll: true });
			} else {
				const res = await api<{ recovery_key: string }>('/auth/register', {
					method: 'POST',
					body: { username, password }
				});
				recoveryKey = res.recovery_key;
			}
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}
</script>

{#if recoveryKey}
	<RecoveryKey key={recoveryKey} oncontinue={() => goto('/', { invalidateAll: true })} />
{:else}
	<main>
		<p class="brand">{de.app.name}</p>
		<h1>{isLogin ? de.auth.loginTitle : de.auth.registerTitle}</h1>
		<p class="story">{isLogin ? de.auth.loginIntro : de.auth.registerIntro}</p>

		<form onsubmit={submit} novalidate>
			<label for="username">{de.auth.username}</label>
			<input
				id="username"
				type="text"
				autocomplete="username"
				autocapitalize="none"
				spellcheck="false"
				maxlength="20"
				required
				bind:value={username}
			/>
			{#if !isLogin}<p class="dim">{de.auth.usernameHint}</p>{/if}

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

			<button class="btn" type="submit" disabled={busy || !username || !password}>
				{isLogin ? de.auth.login : de.auth.register}
			</button>
		</form>

		<p class="switch">
			<a href={isLogin ? '/register' : '/login'}>{isLogin ? de.auth.toRegister : de.auth.toLogin}</a
			>
		</p>
		{#if isLogin}
			<p class="switch"><a href="/recover">{de.auth.toRecover}</a></p>
		{/if}
	</main>
{/if}

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
