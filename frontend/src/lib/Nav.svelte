<script lang="ts">
	import { page } from '$app/state';
	import { de } from '$lib/text/de';

	const links = [
		{ href: '/yard', label: de.nav.yard },
		{ href: '/quests', label: de.nav.quests },
		{ href: '/factions', label: de.nav.factions },
		{ href: '/character', label: de.nav.character }
	];
</script>

<nav aria-label="Hauptnavigation">
	{#each links as l (l.href)}
		<a
			href={l.href}
			class:active={page.url.pathname.startsWith(l.href)}
			aria-current={page.url.pathname.startsWith(l.href) ? 'page' : undefined}>{l.label}</a
		>
	{/each}
</nav>

<style>
	nav {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 20;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		background: #120e0b;
		border-top: 1px solid var(--line);
		padding-bottom: env(safe-area-inset-bottom);
	}
	a {
		text-align: center;
		padding: 0.85rem 0.25rem;
		color: var(--text-dim);
		text-decoration: none;
		font-size: 0.85rem;
		font-weight: 600;
	}
	a.active {
		color: var(--accent-strong);
		box-shadow: inset 0 2px 0 var(--accent);
	}
</style>
