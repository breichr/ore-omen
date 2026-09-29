<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import Offline from '$lib/Offline.svelte';
	import RecoveryKey from '$lib/RecoveryKey.svelte';
	import { de, errorText } from '$lib/text/de';

	let { data } = $props();

	let password = $state('');
	let error = $state('');
	let busy = $state(false);
	let newKey = $state('');

	async function rotate(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		error = '';
		try {
			const res = await api<{ recovery_key: string }>('/auth/recovery-key', {
				method: 'POST',
				body: { password }
			});
			password = '';
			newKey = res.recovery_key;
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}

	async function logout() {
		try {
			await api('/auth/logout', { method: 'POST' });
		} finally {
			await goto('/', { invalidateAll: true });
		}
	}
</script>

{#if data.offline || !data.me}
	<Offline />
{:else if newKey}
	<RecoveryKey key={newKey} rotated oncontinue={() => (newKey = '')} />
{:else}
	<main>
		<p><a href="/">{de.settings.back}</a></p>
		<h1>{de.settings.title}</h1>
		<p class="dim">{de.settings.account(data.me.user.username)}</p>

		<section class="card">
			<h2>{de.settings.keyTitle}</h2>
			<p class="dim">{de.settings.keyIntro}</p>
			<form onsubmit={rotate} novalidate>
				<label for="password">{de.auth.password}</label>
				<input
					id="password"
					type="password"
					autocomplete="current-password"
					bind:value={password}
				/>
				{#if error}<p class="error" role="alert">{error}</p>{/if}
				<button class="btn" type="submit" disabled={busy || !password}>
					{de.settings.keySubmit}
				</button>
			</form>
		</section>

		<button class="btn btn-ghost" onclick={logout}>{de.auth.logout}</button>
	</main>
{/if}

<style>
	section h2 {
		margin-top: 0;
	}
</style>
