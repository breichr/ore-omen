<script lang="ts">
	import Offline from '$lib/Offline.svelte';
	import { de } from '$lib/text/de';

	let { data } = $props();
</script>

{#if data.offline}
	<Offline />
{:else}
	<main class="landing">
		<img class="mark" src="/icons/icon.svg" alt="" width="96" height="96" />
		<h1>{de.app.name}</h1>
		<p class="tagline">{de.app.tagline}</p>
		<p class="story">{de.landing.intro}</p>
		<ul>
			{#each de.landing.points as point (point)}
				<li>{point}</li>
			{/each}
		</ul>
		<a class="btn" href="/register">{de.landing.register}</a>
		<a class="btn btn-ghost" href="/login">{de.landing.login}</a>
	</main>
{/if}

<style>
	.landing {
		text-align: center;
		padding-top: calc(2rem + env(safe-area-inset-top));
	}
	.mark {
		display: block;
		margin: 0 auto;
		border-radius: 20px;
	}
	h1 {
		font-size: 2.2rem;
		margin: 1rem 0 0.25rem;
	}
	.tagline {
		margin: 0 0 1.5rem;
		color: var(--accent);
		font-family: var(--font-story);
		font-style: italic;
		font-size: 1.15rem;
	}
	ul {
		text-align: left;
		padding-left: 1.2rem;
		margin: 1.25rem 0 0.5rem;
		color: var(--text-dim);
	}
	li {
		margin: 0.4rem 0;
	}
	a.btn {
		text-align: center;
		text-decoration: none;
		line-height: 1.6;
	}
</style>
