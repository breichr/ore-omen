<script lang="ts">
	import AuthForm from '$lib/AuthForm.svelte';
	import Offline from '$lib/Offline.svelte';

	let { data } = $props();
</script>

{#if data.offline}
	<Offline />
{:else}
	<AuthForm mode="register" />
{/if}
