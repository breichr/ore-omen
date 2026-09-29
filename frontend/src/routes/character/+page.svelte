<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { api, ApiError, type Character } from '$lib/api';
	import Offline from '$lib/Offline.svelte';
	import { ATTRIBUTES, SKILLS_BY_ATTRIBUTE } from '$lib/rules';
	import { de, errorText } from '$lib/text/de';

	let { data } = $props();

	let fresh = $state<Character | null>(null);
	const ch = $derived(fresh ?? data.me?.character ?? null);

	let addAttributes = $state<Record<string, number>>({});
	let addSkills = $state<Record<string, number>>({});
	let error = $state('');
	let notice = $state('');
	let busy = $state(false);

	const sum = (o: Record<string, number>) => Object.values(o).reduce((a, b) => a + b, 0);
	const freeAttributes = $derived((ch?.unspent_attribute_points ?? 0) - sum(addAttributes));
	const freeSkills = $derived((ch?.unspent_skill_points ?? 0) - sum(addSkills));
	const pending = $derived(sum(addAttributes) + sum(addSkills) > 0);

	function bump(target: Record<string, number>, key: string, delta: number) {
		target[key] = Math.max(0, (target[key] ?? 0) + delta);
	}

	function reset() {
		addAttributes = {};
		addSkills = {};
	}

	async function save() {
		busy = true;
		error = '';
		notice = '';
		try {
			fresh = await api<Character>('/me/points', {
				method: 'POST',
				body: { attributes: addAttributes, skills: addSkills }
			});
			reset();
			notice = de.points.saved;
			await invalidateAll();
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}
</script>

{#if data.offline || !ch}
	<Offline />
{:else}
	<main>
		<p><a href="/yard">{de.points.back}</a></p>
		<h1>{de.points.title}</h1>
		<p class="dim">
			{ch.name} · {de.classes[ch.character_class]?.name} · {de.yard.level(ch.level)}
		</p>

		<h2>{de.points.attributesTitle}</h2>
		<p class="free">{de.points.freeAttributes(freeAttributes)}</p>
		{#each ATTRIBUTES as a (a)}
			{@const extra = addAttributes[a] ?? 0}
			<div class="card line">
				<span>{de.attributes[a].name}</span>
				<span class="stepper">
					<button
						aria-label={de.create.decrease(de.attributes[a].name)}
						disabled={!extra}
						onclick={() => bump(addAttributes, a, -1)}>−</button
					>
					<span class="value" class:changed={extra}>{ch.attributes[a] + extra}</span>
					<button
						aria-label={de.create.increase(de.attributes[a].name)}
						disabled={freeAttributes <= 0}
						onclick={() => bump(addAttributes, a, 1)}>+</button
					>
				</span>
			</div>
		{/each}

		<h2>{de.points.skillsTitle}</h2>
		<p class="free">{de.points.freeSkills(freeSkills)}</p>
		<p class="dim small">{de.points.cap(ch.skill_cap)}</p>
		{#each ATTRIBUTES as a (a)}
			<h3>{de.attributes[a].name}</h3>
			{#each SKILLS_BY_ATTRIBUTE[a] as sk (sk)}
				{@const extra = addSkills[sk] ?? 0}
				{@const value = (ch.skills[sk] ?? 0) + extra}
				<div class="card line">
					<span>
						{de.skills[sk]}
						{#if sk in ch.duel_values}<span class="dim small"> · {de.points.duelValue}</span>{/if}
					</span>
					<span class="stepper">
						<button
							aria-label={de.create.decrease(de.skills[sk])}
							disabled={!extra}
							onclick={() => bump(addSkills, sk, -1)}>−</button
						>
						<span class="value" class:changed={extra}>{value}</span>
						<button
							aria-label={de.create.increase(de.skills[sk])}
							disabled={freeSkills <= 0 || value >= ch.skill_cap}
							onclick={() => bump(addSkills, sk, 1)}>+</button
						>
					</span>
				</div>
			{/each}
		{/each}

		{#if error}<p class="error" role="alert">{error}</p>{/if}
		{#if notice}<p class="dim" role="status">{notice}</p>{/if}

		<button class="btn" disabled={busy || !pending} onclick={save}>{de.points.save}</button>
		<button class="btn btn-ghost" disabled={busy || !pending} onclick={reset}
			>{de.points.reset}</button
		>

		<h2>{de.points.duelValues}</h2>
		<div class="card">
			{#each Object.entries(ch.duel_values) as [k, v] (k)}
				<div class="line plain"><span>{de.skills[k]}</span><strong>{v}</strong></div>
			{/each}
		</div>
	</main>
{/if}

<style>
	.free {
		font-weight: 700;
		color: var(--accent);
		margin: 0.25rem 0 0.5rem;
	}
	h3 {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-dim);
		margin: 1rem 0 0.4rem;
	}
	.small {
		font-size: 0.85rem;
	}
	.line {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 0.5rem;
		padding-bottom: 0.5rem;
	}
	.line + .line {
		margin-top: 0.4rem;
	}
	.plain + .plain {
		margin-top: 0.2rem;
	}
	.stepper {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.stepper button {
		width: 40px;
		height: 40px;
		border-radius: 8px;
		border: 1px solid var(--line);
		background: var(--bg-input);
		color: var(--text);
		font-size: 1.2rem;
	}
	.stepper button:disabled {
		opacity: 0.35;
	}
	.value {
		min-width: 2ch;
		text-align: center;
		font-weight: 700;
	}
	.value.changed {
		color: var(--accent-strong);
	}
</style>
