<script lang="ts">
	import { onMount } from 'svelte';
	import { de } from '$lib/text/de';

	type InstallEvent = Event & { prompt: () => Promise<void> };

	let deferred = $state<InstallEvent | null>(null);
	let showIosHint = $state(false);

	onMount(() => {
		const standalone =
			window.matchMedia('(display-mode: standalone)').matches ||
			(navigator as Navigator & { standalone?: boolean }).standalone === true;
		if (standalone) return;

		const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent);
		let dismissed = false;
		try {
			dismissed = localStorage.getItem('oo-install-dismissed') === '1';
		} catch {
			/* storage unavailable */
		}
		if (dismissed) return;
		showIosHint = isIos;

		const onPrompt = (e: Event) => {
			e.preventDefault();
			deferred = e as InstallEvent;
		};
		window.addEventListener('beforeinstallprompt', onPrompt);
		return () => window.removeEventListener('beforeinstallprompt', onPrompt);
	});

	async function install() {
		await deferred?.prompt();
		deferred = null;
	}

	function dismiss() {
		deferred = null;
		showIosHint = false;
		try {
			localStorage.setItem('oo-install-dismissed', '1');
		} catch {
			/* storage unavailable */
		}
	}
</script>

{#if deferred || showIosHint}
	<div class="card install">
		{#if deferred}
			<button class="btn" onclick={install}>{de.install.button}</button>
		{:else}
			<p class="dim">{de.install.iosHint}</p>
		{/if}
		<button class="link" onclick={dismiss}>{de.install.dismiss}</button>
	</div>
{/if}

<style>
	.install {
		margin-top: 1.5rem;
	}
	.install .btn {
		margin-top: 0;
	}
	.link {
		background: none;
		border: none;
		color: var(--text-dim);
		margin-top: 0.5rem;
		padding: 0.5rem 0;
		text-decoration: underline;
	}
</style>
