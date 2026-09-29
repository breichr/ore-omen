<script lang="ts">
	import { onMount } from 'svelte';
	import { invalidateAll } from '$app/navigation';
	import { api, ApiError, type QuestInstance } from '$lib/api';
	import Applied from '$lib/Applied.svelte';
	import { clock, useClock } from '$lib/clock.svelte';
	import Nav from '$lib/Nav.svelte';
	import Offline from '$lib/Offline.svelte';
	import { de, errorText } from '$lib/text/de';
	import { formatCountdown } from '$lib/time';

	let { data } = $props();

	let chosen = $state<QuestInstance | null>(null);
	const inst = $derived(chosen ?? data.instance);
	let error = $state('');
	let busy = $state(false);

	onMount(() => useClock());
	// The event page has no server clock of its own: the local clock is close enough
	const left = $derived(inst ? (Date.parse(inst.finishes_at) - clock.now) / 1000 : 0);

	let refreshed = false;
	$effect(() => {
		if (inst?.state === 'traveling' && left <= 0 && !refreshed) {
			refreshed = true;
			invalidateAll().then(() => (refreshed = false));
		}
	});

	async function choose(index: number) {
		if (!inst) return;
		busy = true;
		error = '';
		try {
			chosen = await api<QuestInstance>(`/quests/instances/${inst.id}/choose`, {
				method: 'POST',
				body: { option: index }
			});
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}

	function checkLabel(check: NonNullable<QuestInstance['options'][number]['check']>): string {
		const attr = de.attributes[check.attribute]?.name ?? check.attribute;
		return check.skill ? `${attr} + ${de.skills[check.skill] ?? check.skill}` : attr;
	}
</script>

{#if data.offline || !inst}
	<Offline />
{:else}
	<main class="with-nav">
		<p><a href="/quests">{de.event.back}</a></p>
		<h1>{inst.title}</h1>
		<p class="story">{inst.intro}</p>

		{#if inst.state === 'traveling'}
			<div class="card travel">
				<div class="dim">{de.event.traveling}</div>
				<div class="countdown">{formatCountdown(left)}</div>
			</div>
		{/if}

		{#if inst.event}
			<p class="story event">{inst.event}</p>
		{/if}

		{#if error}<p class="error" role="alert">{error}</p>{/if}

		{#if inst.state === 'choice'}
			<div class="options">
				{#each inst.options as o (o.index)}
					<button
						class="option"
						disabled={busy || !!o.blocked}
						onclick={() => choose(o.index)}
						aria-describedby="opt-{o.index}"
					>
						<span class="label">{o.label}</span>
						<span class="meta" id="opt-{o.index}">
							{#if o.blocked}
								{de.event.blocked[o.blocked] ?? o.blocked}
							{:else if o.check && o.chance !== null}
								{checkLabel(o.check)} – {de.event.chance(o.chance)}
							{:else if o.combat}
								{de.event.combat}
							{/if}
						</span>
					</button>
				{/each}
			</div>
			{#if inst.options.some((o) => o.combat)}
				<p class="dim small">{de.event.combatNote}</p>
			{/if}
		{/if}

		{#if inst.state === 'done' && inst.outcome}
			<section class="card outcome">
				{#if inst.outcome.label}<div class="dim small">{inst.outcome.label}</div>{/if}
				{#if inst.outcome.success === true}
					<div class="verdict good">{de.event.success}</div>
				{:else if inst.outcome.success === false}
					<div class="verdict bad">{de.event.failure}</div>
				{/if}
				{#if inst.outcome.check}
					<div class="dim small">
						{de.event.check(
							inst.outcome.check.roll,
							inst.outcome.check.total,
							inst.outcome.check.difficulty
						)}
					</div>
				{/if}
				{#if inst.outcome.text}<p class="story">{inst.outcome.text}</p>{/if}
				<Applied applied={inst.outcome.applied} />
			</section>
			<a class="btn" href="/quests">{de.event.back}</a>
		{/if}
	</main>
	<Nav />
{/if}

<style>
	.event {
		border-left: 3px solid var(--accent);
		padding-left: 0.8rem;
	}
	.travel {
		text-align: center;
		margin: 1rem 0;
	}
	.countdown {
		font-size: 1.6rem;
		font-variant-numeric: tabular-nums;
		color: var(--accent-strong);
		font-weight: 700;
	}
	.options {
		display: grid;
		gap: 0.5rem;
		margin-top: 1rem;
	}
	.option {
		display: grid;
		gap: 0.2rem;
		text-align: left;
		padding: 0.8rem 1rem;
		min-height: 56px;
		border-radius: 10px;
		border: 1px solid var(--accent);
		background: var(--bg-raised);
		color: var(--text);
	}
	.option:disabled {
		border-color: var(--line);
		opacity: 0.55;
	}
	.label {
		font-weight: 600;
	}
	.meta {
		font-size: 0.85rem;
		color: var(--accent);
	}
	.option:disabled .meta {
		color: var(--text-dim);
	}
	.outcome {
		margin-top: 1rem;
	}
	.verdict {
		font-weight: 700;
		margin-top: 0.2rem;
	}
	.good {
		color: #9cc98a;
	}
	.bad {
		color: var(--danger);
	}
	.small {
		font-size: 0.85rem;
	}
</style>
