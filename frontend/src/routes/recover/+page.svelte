<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import Offline from '$lib/Offline.svelte';
	import RecoveryKey from '$lib/RecoveryKey.svelte';
	import { de, errorText } from '$lib/text/de';

	let { data } = $props();

	let username = $state('');
	let key = $state('');
	let newPassword = $state('');
	let error = $state('');
	let busy = $state(false);
	let newKey = $state('');

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		error = '';
		try {
			const res = await api<{ recovery_key: string }>('/auth/recover', {
				method: 'POST',
				body: { username, recovery_key: key, new_password: newPassword }
			});
			newKey = res.recovery_key;
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}
</script>

{#if data.offline}
	<Offline />
{:else if newKey}
	<RecoveryKey key={newKey} rotated oncontinue={() => goto('/', { invalidateAll: true })} />
{:else}
	<main>
		<h1>{de.recovery.title}</h1>
		<p class="story">{de.recovery.intro}</p>

		<form onsubmit={submit} novalidate>
			<label for="username">{de.auth.username}</label>
			<input
				id="username"
				type="text"
				autocomplete="username"
				autocapitalize="none"
				spellcheck="false"
				maxlength="20"
				bind:value={username}
			/>

			<label for="key">{de.recovery.key}</label>
			<input
				id="key"
				type="text"
				autocomplete="off"
				autocapitalize="characters"
				spellcheck="false"
				placeholder={de.recovery.keyPlaceholder}
				bind:value={key}
			/>

			<label for="password">{de.recovery.newPassword}</label>
			<input id="password" type="password" autocomplete="new-password" bind:value={newPassword} />
			<p class="dim">{de.auth.passwordHint}</p>

			{#if error}<p class="error" role="alert">{error}</p>{/if}

			<button class="btn" type="submit" disabled={busy || !username || !key || !newPassword}>
				{de.recovery.submit}
			</button>
		</form>

		<p class="switch"><a href="/login">{de.auth.toLogin}</a></p>
	</main>
{/if}

<style>
	.switch {
		margin-top: 1.5rem;
		text-align: center;
	}
</style>
