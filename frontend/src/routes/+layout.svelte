<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { network, watchNetwork } from '$lib/network.svelte';
	import { de } from '$lib/text/de';

	let { children } = $props();

	onMount(() => watchNetwork());
</script>

{#if !network.online}
	<div class="offline" role="status">{de.offline.banner}</div>
{/if}

{@render children()}

<style>
	.offline {
		position: sticky;
		top: 0;
		z-index: 10;
		padding: calc(0.5rem + env(safe-area-inset-top)) 1rem 0.5rem;
		background: #4a2a22;
		color: var(--text);
		text-align: center;
		font-size: 0.9rem;
	}
</style>
