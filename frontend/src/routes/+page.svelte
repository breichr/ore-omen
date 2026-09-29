<script lang="ts">
	import Offline from '$lib/Offline.svelte';
	import { de } from '$lib/text/de';

	let { data } = $props();
</script>

{#if data.offline}
	<Offline />
{:else}
	<main><p class="dim">{de.app.loading}</p></main>
{/if}
