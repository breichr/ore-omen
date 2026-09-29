<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import InstallPrompt from '$lib/InstallPrompt.svelte';
	import Offline from '$lib/Offline.svelte';
	import { de } from '$lib/text/de';

	let { data } = $props();

	const ch = $derived(data.me?.character);

	async function logout() {
		try {
			await api('/auth/logout', { method: 'POST' });
		} finally {
			await goto('/login', { invalidateAll: true });
		}
	}
</script>

{#if data.offline || !ch}
	<Offline />
{:else}
	<main>
		<header class="card who">
			<div>
				<div class="name">{ch.name}</div>
				<div class="dim">
					{de.classes[ch.character_class]?.name} · {de.yard.level(ch.level)} ·
					{de.regions[ch.region] ?? ch.region}
				</div>
			</div>
			<div class="money">{de.yard.dollars(ch.dollars)}</div>
		</header>

		<h1>{de.yard.title}</h1>
		<section class="card">
			<h2>{de.yard.emptyTitle}</h2>
			<p class="story">{de.yard.empty}</p>
			<p class="dim">{de.yard.comingSoon}</p>
		</section>

		<InstallPrompt />

		<button class="btn btn-ghost" onclick={logout}>{de.auth.logout}</button>
	</main>
{/if}

<style>
	.who {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: calc(env(safe-area-inset-top));
	}
	.name {
		font-family: var(--font-story);
		font-size: 1.2rem;
		font-weight: 600;
	}
	.money {
		font-weight: 700;
		color: var(--accent-strong);
	}
	section h2 {
		margin-top: 0;
	}
</style>
