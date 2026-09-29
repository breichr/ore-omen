<script lang="ts">
	import { untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import Offline from '$lib/Offline.svelte';
	import {
		ATTRIBUTES,
		ATTRIBUTE_START_FREE_POINTS,
		ATTRIBUTE_START_VALUE,
		CLASSES
	} from '$lib/rules';
	import { suggestCharacterName } from '$lib/nameSuggestion';
	import { de, errorText } from '$lib/text/de';

	let { data } = $props();

	// Suggestion from the username; the player can change it
	let name = $state(untrack(() => suggestCharacterName(data.me?.user.username ?? '')));
	let characterClass = $state('');
	let allocation = $state<Record<string, number>>(
		Object.fromEntries(ATTRIBUTES.map((a) => [a, 0]))
	);
	let error = $state('');
	let busy = $state(false);

	const spent = $derived(Object.values(allocation).reduce((s, v) => s + v, 0));
	const left = $derived(ATTRIBUTE_START_FREE_POINTS - spent);
	const ready = $derived(name.trim().length >= 3 && characterClass !== '' && left === 0);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		error = '';
		try {
			await api('/characters', {
				method: 'POST',
				body: { name, class: characterClass, allocation }
			});
			await goto('/yard', { invalidateAll: true });
		} catch (e) {
			error = errorText(e instanceof ApiError ? e.code : 'unknown');
		} finally {
			busy = false;
		}
	}
</script>

{#if data.offline}
	<Offline />
{:else}
	<main>
		<h1>{de.create.title}</h1>
		<p class="story">{de.create.intro}</p>

		<form onsubmit={submit} novalidate>
			<label for="name">{de.create.name}</label>
			<input id="name" type="text" autocomplete="off" maxlength="20" bind:value={name} />
			<p class="dim">{de.create.nameHint}</p>

			<h2>{de.create.classTitle}</h2>
			<div class="classes" role="radiogroup" aria-label={de.create.classTitle}>
				{#each CLASSES as code (code)}
					{@const info = de.classes[code]}
					<label class="card class" class:selected={characterClass === code}>
						<input type="radio" name="class" value={code} bind:group={characterClass} />
						<span class="class-name">{info.name}</span>
						<span class="dim">{info.role}</span>
						<span class="ability"><strong>{de.create.ability}:</strong> {info.ability}</span>
					</label>
				{/each}
			</div>

			<h2>{de.create.attributesTitle}</h2>
			<p class="dim">{de.create.attributesIntro}</p>
			<p class="points" aria-live="polite">{de.create.pointsLeft(left)}</p>
			<ul class="attributes">
				{#each ATTRIBUTES as code (code)}
					{@const info = de.attributes[code]}
					<li class="card attribute">
						<div>
							<div class="attr-name">{info.name}</div>
							<div class="dim">{info.hint}</div>
						</div>
						<div class="stepper">
							<button
								type="button"
								aria-label={de.create.decrease(info.name)}
								disabled={allocation[code] === 0}
								onclick={() => allocation[code]--}>−</button
							>
							<span class="value">{ATTRIBUTE_START_VALUE + allocation[code]}</span>
							<button
								type="button"
								aria-label={de.create.increase(info.name)}
								disabled={left === 0}
								onclick={() => allocation[code]++}>+</button
							>
						</div>
					</li>
				{/each}
			</ul>

			{#if error}<p class="error" role="alert">{error}</p>{/if}

			<button class="btn" type="submit" disabled={busy || !ready}>{de.create.submit}</button>
		</form>
	</main>
{/if}

<style>
	.classes {
		display: grid;
		gap: 0.5rem;
	}
	.class {
		margin: 0;
		display: grid;
		gap: 0.1rem;
		font-weight: normal;
		cursor: pointer;
	}
	.class input {
		position: absolute;
		opacity: 0;
		pointer-events: none;
	}
	.class:has(input:focus-visible) {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}
	.class.selected {
		border-color: var(--accent);
		background: #2c2118;
	}
	.class-name {
		font-family: var(--font-story);
		font-size: 1.1rem;
		font-weight: 600;
	}
	.ability {
		font-size: 0.9rem;
	}
	.points {
		font-weight: 700;
		color: var(--accent);
		margin: 0.5rem 0;
	}
	.attributes {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.5rem;
	}
	.attribute {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}
	.attr-name {
		font-weight: 600;
	}
	.stepper {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.stepper button {
		width: 44px;
		height: 44px;
		border-radius: 8px;
		border: 1px solid var(--line);
		background: var(--bg-input);
		color: var(--text);
		font-size: 1.3rem;
	}
	.stepper button:disabled {
		opacity: 0.35;
		cursor: default;
	}
	.value {
		min-width: 2ch;
		text-align: center;
		font-size: 1.2rem;
		font-weight: 700;
	}
</style>
