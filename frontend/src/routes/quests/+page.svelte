<script lang="ts">
	import { onMount } from 'svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { api, ApiError, type QuestInstance, type QuestSummary } from '$lib/api';
	import { clock, useClock } from '$lib/clock.svelte';
	import Nav from '$lib/Nav.svelte';
	import Offline from '$lib/Offline.svelte';
	import { de, errorText } from '$lib/text/de';
	import { formatCountdown, formatDuration, serverOffset } from '$lib/time';

	let { data } = $props();
	const q = $derived(data.quests);

	let error = $state('');
	let busy = $state(false);

	onMount(() => useClock());
	const serverNow = $derived(clock.now + (q ? serverOffset(q.as_of, data.loadedAt) : 0));
	const remaining = (iso: string) => (Date.parse(iso) - serverNow) / 1000;

	let refreshedFor = '';
	$effect(() => {
		const ends = [
			...(q?.open ?? []).filter((o) => o.state === 'traveling').map((o) => o.finishes_at)
		];
		if (q?.activity) ends.push(q.activity.finishes_at);
		const due = ends.find((iso) => remaining(iso) <= 0);
		if (due && due !== refreshedFor) {
			refreshedFor = due;
			invalidateAll();
		}
	});

	const groups = $derived.by(() => {
		const list = q?.quests ?? [];
		const dailies = new Map<string, QuestSummary[]>();
		for (const x of list.filter((x) => x.type === 'daily')) {
			if (!dailies.has(x.faction!)) dailies.set(x.faction!, []);
			dailies.get(x.faction!)!.push(x);
		}
		return {
			chain: list.filter((x) => x.type === 'chain'),
			dailies: [...dailies],
			faction: list.filter((x) => x.type === 'faction')
		};
	});

	const resetTime = $derived(
		q
			? new Date(q.next_reset).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
			: ''
	);

	async function run<T>(fn: () => Promise<T>): Promise<T | undefined> {
		busy = true;
		error = '';
		try {
			return await fn();
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}

	async function startQuest(id: string) {
		const inst = await run(() => api<QuestInstance>(`/quests/${id}/start`, { method: 'POST' }));
		if (inst) await goto(`/quests/${inst.id}`);
	}

	async function travel(region: string) {
		if (await run(() => api('/travel', { method: 'POST', body: { region } })))
			await invalidateAll();
	}

	function reasonText(x: QuestSummary): string {
		if (x.reason === 'wrong_region') return de.regions[x.region];
		if (x.reason === 'reputation_too_low' && x.min_tier) {
			return de.questScreen.fromRep(de.tiers[x.min_tier]);
		}
		return de.questScreen.reasons[x.reason ?? ''] ?? '';
	}
</script>

{#snippet questCard(x: QuestSummary)}
	<div class="card quest" class:unavailable={!x.available}>
		<div class="row">
			<div>
				<div class="strong">{x.title}</div>
				<div class="dim small">
					{de.regions[x.region]} ·
					{x.duration_min
						? de.questScreen.duration(formatDuration(x.duration_min * 60))
						: de.questScreen.instant}
				</div>
			</div>
			{#if x.available}
				<button class="small-btn" disabled={busy} onclick={() => startQuest(x.id)}>
					{de.questScreen.start}
				</button>
			{:else}
				<span class="reason">{reasonText(x)}</span>
			{/if}
		</div>
		<p class="desc">{x.intro}</p>
	</div>
{/snippet}

{#if data.offline || !q}
	<Offline />
{:else}
	<main class="with-nav">
		<h1>{de.questScreen.title}</h1>
		<p class="dim">{de.questScreen.here(de.regions[q.region])}</p>

		{#if error}<p class="error" role="alert">{error}</p>{/if}

		{#if q.activity}
			<div class="card row activity">
				<div>
					<div class="strong">
						{de.questScreen.activity[q.activity.kind]}{#if q.activity.kind === 'travel'}
							: {de.regions[q.activity.ref]}{/if}
					</div>
					<div class="countdown">{formatCountdown(remaining(q.activity.finishes_at))}</div>
				</div>
			</div>
		{/if}

		{#if q.open.length}
			<h2>{de.questScreen.open}</h2>
			{#each q.open as o (o.id)}
				<a class="card row open" href="/quests/{o.id}">
					<div>
						<div class="strong">{o.title}</div>
						<div class="dim small">
							{o.state === 'choice'
								? de.questScreen.openChoice
								: `${de.questScreen.openTraveling} · ${formatCountdown(remaining(o.finishes_at))}`}
						</div>
					</div>
					<span aria-hidden="true">→</span>
				</a>
			{/each}
		{/if}

		{#if groups.chain.length}
			<h2>{de.questScreen.onboarding}</h2>
			{#each groups.chain as x (x.id)}{@render questCard(x)}{/each}
		{/if}

		<h2>{de.questScreen.dailies}</h2>
		<p class="dim small">{de.questScreen.dailiesReset(resetTime)}</p>
		{#each groups.dailies as [faction, list] (faction)}
			<h3>{de.factions[faction]}</h3>
			{#each list as x (x.id)}{@render questCard(x)}{/each}
		{/each}

		<h2>{de.questScreen.factionQuests}</h2>
		{#if groups.faction.length === 0}<p class="dim">{de.questScreen.none}</p>{/if}
		{#each groups.faction as x (x.id)}{@render questCard(x)}{/each}

		<h2>{de.questScreen.travelTitle}</h2>
		{#each q.travel as t (t.region)}
			<div class="card row">
				<div>
					<div class="strong">{de.regions[t.region]}</div>
					<div class="dim small">
						{t.seconds !== null
							? formatDuration(t.seconds)
							: (de.questScreen.reasons[t.reason ?? ''] ?? '')}
					</div>
				</div>
				<button
					class="small-btn ghost"
					disabled={busy || t.seconds === null || !!q.activity}
					onclick={() => travel(t.region)}>{de.questScreen.travel}</button
				>
			</div>
		{/each}
	</main>
	<Nav />
{/if}

<style>
	h3 {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-dim);
		margin: 1rem 0 0.4rem;
	}
	.card + .card {
		margin-top: 0.5rem;
	}
	.row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 0.75rem;
	}
	a.open {
		color: var(--text);
		text-decoration: none;
		border-color: var(--accent);
	}
	.strong {
		font-weight: 600;
	}
	.small {
		font-size: 0.85rem;
	}
	.desc {
		margin: 0.4rem 0 0;
		font-family: var(--font-story);
		color: var(--text-dim);
		font-size: 0.95rem;
	}
	.unavailable {
		opacity: 0.75;
	}
	.reason {
		flex: none;
		font-size: 0.8rem;
		color: var(--text-dim);
		text-align: right;
		max-width: 40%;
	}
	.countdown {
		font-variant-numeric: tabular-nums;
		color: var(--accent-strong);
		font-weight: 700;
	}
	.activity {
		margin-top: 1rem;
		border-color: var(--accent);
	}
	.small-btn {
		flex: none;
		min-height: 40px;
		padding: 0.4rem 0.8rem;
		border-radius: 8px;
		border: none;
		background: var(--accent);
		color: #1a130c;
		font-weight: 700;
	}
	.small-btn.ghost {
		background: transparent;
		color: var(--accent);
		border: 1px solid var(--line);
	}
	.small-btn:disabled {
		opacity: 0.4;
	}
</style>
