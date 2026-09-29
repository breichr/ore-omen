<script lang="ts">
	import { onMount } from 'svelte';
	import { invalidateAll } from '$app/navigation';
	import { api, ApiError, type Settlement } from '$lib/api';
	import { clock, useClock } from '$lib/clock.svelte';
	import { formatAmounts } from '$lib/format';
	import InstallPrompt from '$lib/InstallPrompt.svelte';
	import Nav from '$lib/Nav.svelte';
	import Offline from '$lib/Offline.svelte';
	import { de, errorText } from '$lib/text/de';
	import { extrapolateMilli, formatCountdown, formatDuration, serverOffset } from '$lib/time';

	let { data } = $props();

	const ch = $derived(data.me?.character);
	const s = $derived(data.settlement);
	const jobs = $derived(data.jobs);

	let error = $state('');
	let notice = $state('');
	let busy = $state(false);

	onMount(() => useClock());

	// Server time = local clock + offset measured when the data arrived
	const offset = $derived(s ? serverOffset(s.as_of, data.loadedAt) : 0);
	const serverNow = $derived(clock.now + offset);

	const names = $derived(Object.fromEntries((s?.buildings ?? []).map((b) => [b.code, b.name])));
	const jobNames = $derived(Object.fromEntries((jobs?.jobs ?? []).map((j) => [j.code, j.name])));

	const shownResources = $derived(
		(s?.resources ?? []).filter(
			(r) => r.amount_milli > 0 || r.rate_per_hour > 0 || ['wood', 'iron'].includes(r.name)
		)
	);

	function amount(r: Settlement['resources'][number]): number {
		if (!s) return 0;
		const elapsed = serverNow - Date.parse(s.as_of);
		return Math.floor(
			extrapolateMilli(r.amount_milli, r.rate_per_hour, s.capacity, elapsed) / 1000
		);
	}

	function remaining(iso: string): number {
		return (Date.parse(iso) - serverNow) / 1000;
	}

	// Reload once when a timer runs out; the server finishes it on read
	let refreshedFor = '';
	$effect(() => {
		const ends = [...(s?.queue ?? []).map((q) => q.finishes_at)];
		if (jobs?.current) ends.push(jobs.current.finishes_at);
		const due = ends.find((iso) => remaining(iso) <= 0);
		if (due && due !== refreshedFor) {
			refreshedFor = due;
			invalidateAll();
		}
	});

	// Built, buildable or under construction first; the rest folds away (decision M2)
	const inQueue = $derived(new Set((s?.queue ?? []).map((q) => q.type)));
	const relevant = (b: NonNullable<typeof s>['buildings'][number]) =>
		b.level > 0 || b.can_build || inQueue.has(b.code);
	const more = $derived((s?.buildings ?? []).filter((b) => !relevant(b)));
	const onboardingOpen = $derived(
		!!data.quests &&
			(data.quests.quests.some((x) => x.chain === 'onboarding') ||
				data.quests.open.some((o) => o.quest_id.startsWith('onboarding_')))
	);

	const categories = $derived.by(() => {
		const groups = new Map<string, NonNullable<typeof s>['buildings']>();
		for (const b of (s?.buildings ?? []).filter(relevant)) {
			if (!groups.has(b.category)) groups.set(b.category, []);
			groups.get(b.category)!.push(b);
		}
		return [...groups];
	});
	const hasBuildings = $derived((s?.buildings ?? []).some((b) => b.level > 0) || !!s?.queue.length);

	async function act(path: string, body?: unknown, after?: (res: unknown) => void) {
		busy = true;
		error = '';
		notice = '';
		try {
			const res = await api(path, { method: 'POST', body });
			after?.(res);
			await invalidateAll();
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}

	function cancelBuild(id: number) {
		if (!confirm(de.settlement.cancelConfirm)) return;
		act(`/settlement/queue/${id}/cancel`, undefined, (res) => {
			const lost = (res as Settlement).lost;
			if (lost && Object.keys(lost).length) notice = de.settlement.lost(formatAmounts(lost));
		});
	}

	function cancelJob() {
		if (!confirm(de.jobs.cancelConfirm)) return;
		act('/jobs/cancel');
	}

	const xpShare = $derived(
		ch ? (ch.xp - ch.xp_level_start) / Math.max(1, ch.xp_next_level - ch.xp_level_start) : 0
	);
	const hasPoints = $derived(
		!!ch && (ch.unspent_attribute_points > 0 || ch.unspent_skill_points > 0)
	);
</script>

{#snippet buildingCard(b: NonNullable<typeof s>['buildings'][number])}
	<div class="card building" class:built={b.level > 0}>
		<div class="row">
			<div>
				<div class="strong">
					{b.name}{#if b.variant}
						· {de.mainHouse[b.variant]}{/if}
				</div>
				<div class="dim small">
					{b.level ? de.settlement.level(b.level) : de.settlement.notBuilt}
					{#if Object.keys(b.produces).length}
						· {Object.entries(b.produces)
							.map(([r, n]) => `${de.resources[r]} ${de.settlement.perHour(n)}`)
							.join(', ')}
					{/if}
				</div>
			</div>
			{#if b.next}
				<button
					class="small-btn"
					disabled={busy || !b.can_build}
					onclick={() => act('/settlement/build', { type: b.code })}
				>
					{b.level ? de.settlement.upgrade(b.next.level) : de.settlement.build}
				</button>
			{/if}
		</div>
		<p class="desc">{b.description}</p>
		{#if b.next}
			<p class="small">
				<span class="dim">{de.settlement.cost}:</span>
				{formatAmounts(b.next.cost)} ·
				<span class="dim">{de.settlement.duration}:</span>
				{formatDuration(b.next.seconds)}
			</p>
			{#if b.reason && b.reason !== 'already_building'}
				<p class="dim small">{de.reasons[b.reason] ?? b.reason}</p>
			{/if}
		{:else}
			<p class="dim small">{de.settlement.maxed}</p>
		{/if}
	</div>
{/snippet}

{#if data.offline || !ch || !s || !jobs}
	<Offline />
{:else}
	<main class="with-nav">
		<header class="card who">
			<div class="who-row">
				<div>
					<div class="name">{ch.name}</div>
					<div class="dim">
						{de.classes[ch.character_class]?.name} · {de.yard.level(ch.level)} ·
						{de.regions[ch.region] ?? ch.region}
					</div>
				</div>
				<div class="money">{de.yard.dollars(ch.dollars)}</div>
			</div>
			<div
				class="xp"
				role="progressbar"
				aria-valuemin={ch.xp_level_start}
				aria-valuemax={ch.xp_next_level}
				aria-valuenow={ch.xp}
			>
				<div class="xp-fill" style:width="{Math.min(100, xpShare * 100)}%"></div>
			</div>
			<div class="dim small">{de.progress.xp(ch.xp, ch.xp_next_level)}</div>
			{#if hasPoints}
				<a class="points-link" href="/character"
					>{de.progress.pointsAvailable} {de.progress.distribute} →</a
				>
			{/if}
		</header>

		<section class="resources" aria-label={de.settlement.storage(s.capacity)}>
			{#each shownResources as r (r.name)}
				{@const value = amount(r)}
				<div class="res" class:full={value >= s.capacity}>
					<span class="res-name">{de.resources[r.name]}</span>
					<span class="res-value">{value.toLocaleString('de-DE')}</span>
					<span class="res-rate">
						{#if value >= s.capacity}{de.settlement
								.full}{:else if r.rate_per_hour}{de.settlement.perHour(r.rate_per_hour)}{/if}
					</span>
				</div>
			{/each}
		</section>
		<p class="dim small center">{de.settlement.storage(s.capacity)}</p>

		{#if onboardingOpen}
			<a class="card onboarding" href="/quests">{de.questScreen.onboardingHint} →</a>
		{/if}

		{#if error}<p class="error" role="alert">{error}</p>{/if}
		{#if notice}<p class="notice" role="status">{notice}</p>{/if}

		{#if !hasBuildings}
			<section class="card">
				<h2>{de.yard.emptyTitle}</h2>
				<p class="story">{de.yard.empty}</p>
				<p class="dim">{de.yard.firstStep}</p>
			</section>
		{/if}

		<h2>{de.settlement.queueTitle}</h2>
		<p class="dim small">{de.settlement.slots(s.queue.length, s.queue_slots)}</p>
		{#if s.queue.length === 0}
			<p class="dim">{de.settlement.queueEmpty}</p>
		{/if}
		{#each s.queue as q (q.id)}
			<div class="card row">
				<div>
					<div class="strong">
						{de.settlement.upgradeTo(names[q.type] ?? q.type, q.target_level)}
					</div>
					<div class="countdown">{formatCountdown(remaining(q.finishes_at))}</div>
				</div>
				<button class="small-btn ghost" disabled={busy} onclick={() => cancelBuild(q.id)}>
					{de.settlement.cancel}
				</button>
			</div>
		{/each}

		<h2>{de.jobs.title}</h2>
		{#if jobs.current}
			<div class="card row">
				<div>
					<div class="strong">
						{de.jobs.running(jobNames[jobs.current.job] ?? jobs.current.job)}
					</div>
					<div class="countdown">{formatCountdown(remaining(jobs.current.finishes_at))}</div>
				</div>
				<button class="small-btn ghost" disabled={busy} onclick={cancelJob}>{de.jobs.cancel}</button
				>
			</div>
		{:else}
			{#if jobs.last?.status === 'done'}
				<p class="notice">
					{de.jobs.done(jobNames[jobs.last.job] ?? jobs.last.job)} · +{formatAmounts(
						jobs.last.result.yield ?? {}
					)}, {de.jobs.xp(jobs.last.result.xp ?? 0)}
					{#if jobs.last.result.lost && Object.keys(jobs.last.result.lost).length}
						<br />{de.settlement.lost(formatAmounts(jobs.last.result.lost))}
					{/if}
				</p>
			{/if}
			<p class="dim small">{de.jobs.intro}</p>
			{#each jobs.jobs as j (j.code)}
				<div class="card job">
					<div class="row">
						<div>
							<div class="strong">{j.name}</div>
							<div class="dim small">
								{formatDuration(j.seconds)} · {formatAmounts(j.yield)} · {de.jobs.xp(j.xp)}
							</div>
						</div>
						<button class="small-btn" disabled={busy} onclick={() => act(`/jobs/${j.code}/start`)}
							>{de.jobs.start}</button
						>
					</div>
					<p class="desc">{j.description}</p>
					{#if Object.keys(j.overflow).length}
						<p class="warn small">{de.jobs.overflow(formatAmounts(j.overflow))}</p>
					{/if}
				</div>
			{/each}
		{/if}

		<h2>{de.settlement.buildingsTitle}</h2>
		{#each categories as [category, list] (category)}
			<h3>{de.categories[category] ?? category}</h3>
			{#each list as b (b.code)}
				{@render buildingCard(b)}
			{/each}
		{/each}

		{#if more.length}
			<details class="more">
				<summary>{de.settlement.moreBuildings(more.length)}</summary>
				{#each more as b (b.code)}
					{@render buildingCard(b)}
				{/each}
			</details>
		{/if}

		<InstallPrompt />

		<a class="btn btn-ghost" href="/settings">{de.settings.link}</a>
	</main>
	<Nav />
{/if}

<style>
	.who {
		margin-top: env(safe-area-inset-top);
	}
	.who-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
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
	.xp {
		height: 6px;
		margin-top: 0.6rem;
		border-radius: 3px;
		background: var(--bg-input);
		overflow: hidden;
	}
	.xp-fill {
		height: 100%;
		background: var(--accent);
	}
	.points-link {
		display: block;
		margin-top: 0.5rem;
		font-weight: 600;
	}
	.resources {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
		gap: 0.4rem;
		margin-top: 1rem;
	}
	.res {
		background: var(--bg-raised);
		border: 1px solid var(--line);
		border-radius: 8px;
		padding: 0.4rem 0.5rem;
		display: grid;
	}
	.res.full {
		border-color: var(--danger);
	}
	.res-name,
	.res-rate {
		font-size: 0.75rem;
		color: var(--text-dim);
	}
	.res.full .res-rate {
		color: var(--danger);
	}
	.res-value {
		font-weight: 700;
		font-variant-numeric: tabular-nums;
	}
	.small {
		font-size: 0.85rem;
	}
	.center {
		text-align: center;
	}
	h3 {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-dim);
		margin: 1.2rem 0 0.4rem;
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
	.strong {
		font-weight: 600;
	}
	.countdown {
		font-variant-numeric: tabular-nums;
		color: var(--accent-strong);
		font-weight: 700;
	}
	.desc {
		margin: 0.4rem 0 0;
		font-family: var(--font-story);
		color: var(--text-dim);
		font-size: 0.95rem;
	}
	.building:not(.built) {
		opacity: 0.85;
	}
	.building p.small {
		margin: 0.4rem 0 0;
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
		cursor: default;
	}
	.notice {
		background: #1f2a1c;
		border: 1px solid #3c5236;
		border-radius: 8px;
		padding: 0.6rem 0.8rem;
		font-size: 0.9rem;
	}
	.warn {
		color: var(--danger);
		margin: 0.3rem 0 0;
	}
	section h2 {
		margin-top: 0;
	}
	.onboarding {
		display: block;
		margin-top: 1rem;
		border-color: var(--accent);
		color: var(--accent-strong);
		font-weight: 600;
		text-decoration: none;
	}
	.more {
		margin-top: 1rem;
	}
	.more summary {
		cursor: pointer;
		color: var(--accent);
		font-weight: 600;
		padding: 0.6rem 0;
	}
</style>
