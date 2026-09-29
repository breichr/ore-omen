<script lang="ts">
	import { api, ApiError, type Factions } from '$lib/api';
	import Nav from '$lib/Nav.svelte';
	import Offline from '$lib/Offline.svelte';
	import { de, errorText } from '$lib/text/de';

	let { data } = $props();
	let fresh = $state<Factions | null>(null);
	const f = $derived(fresh ?? data.factions);
	let error = $state('');
	let busy = $state(false);

	// Bar from −1000 to +1000; zero in the middle
	const pos = (v: number) => ((v + 1000) / 2000) * 100;

	async function swear(code: string) {
		if (!confirm(de.factionScreen.oathConfirm(de.factions[code]))) return;
		busy = true;
		error = '';
		try {
			fresh = await api<Factions>(`/factions/${code}/oath`, { method: 'POST' });
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}
</script>

{#if data.offline || !f}
	<Offline />
{:else}
	<main class="with-nav">
		<h1>{de.factionScreen.title}</h1>
		<p class="dim">{de.factionScreen.intro}</p>
		{#if error}<p class="error" role="alert">{error}</p>{/if}

		{#each f.factions as x (x.code)}
			<section class="card faction">
				<div class="head">
					<span class="name">{de.factions[x.code]}</span>
					<span class="value">{x.value}</span>
				</div>
				<div
					class="bar"
					role="meter"
					aria-label={de.factions[x.code]}
					aria-valuemin={-1000}
					aria-valuemax={1000}
					aria-valuenow={x.value}
				>
					<div class="zero"></div>
					<div
						class="fill"
						class:negative={x.value < 0}
						style:left="{Math.min(pos(0), pos(x.value))}%"
						style:width="{Math.abs(pos(x.value) - pos(0))}%"
					></div>
					{#if x.cap < 1000}
						<div class="cap" style:left="{pos(x.cap)}%" title={de.factionScreen.cap(x.cap)}></div>
					{/if}
				</div>
				<div class="foot">
					<span class="tier">{de.tiers[x.tier]}</span>
					{#if f.oath === x.code}
						<span class="sworn">{de.factionScreen.sworn}</span>
					{:else if x.cap < 1000}
						<span class="dim small">{de.factionScreen.cap(x.cap)}</span>
					{/if}
				</div>
				{#if x.can_swear}
					<button class="btn btn-ghost" disabled={busy} onclick={() => swear(x.code)}>
						{de.factionScreen.oath}
					</button>
				{/if}
			</section>
		{/each}
		<p class="dim small">{de.factionScreen.oathHint}</p>
	</main>
	<Nav />
{/if}

<style>
	.faction + .faction {
		margin-top: 0.6rem;
	}
	.head,
	.foot {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
	}
	.name {
		font-family: var(--font-story);
		font-weight: 600;
		font-size: 1.05rem;
	}
	.value {
		font-weight: 700;
		font-variant-numeric: tabular-nums;
	}
	.bar {
		position: relative;
		height: 10px;
		margin: 0.5rem 0;
		border-radius: 5px;
		background: var(--bg-input);
		overflow: hidden;
	}
	.zero {
		position: absolute;
		left: 50%;
		top: 0;
		bottom: 0;
		width: 1px;
		background: var(--line);
	}
	.fill {
		position: absolute;
		top: 0;
		bottom: 0;
		background: var(--accent);
	}
	.fill.negative {
		background: var(--danger);
	}
	.cap {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 2px;
		background: var(--text-dim);
	}
	.tier {
		color: var(--accent);
		font-weight: 600;
		font-size: 0.9rem;
	}
	.sworn {
		color: var(--accent-strong);
		font-size: 0.85rem;
		font-weight: 600;
	}
	.small {
		font-size: 0.85rem;
	}
	.faction .btn {
		margin-top: 0.75rem;
	}
</style>
