<script lang="ts">
	import { de } from '$lib/text/de';

	let {
		key,
		rotated = false,
		oncontinue
	}: { key: string; rotated?: boolean; oncontinue: () => void } = $props();

	let confirmed = $state(false);
	let copied = $state(false);

	async function copy() {
		try {
			await navigator.clipboard.writeText(key);
			copied = true;
		} catch {
			/* clipboard unavailable: the key stays visible for manual copying */
		}
	}
</script>

<main>
	<h1>{rotated ? de.recovery.showNewTitle : de.recovery.showTitle}</h1>
	<p class="story">{de.recovery.showIntro}</p>
	{#if rotated}<p class="dim">{de.recovery.showOldInvalid}</p>{/if}

	<p class="card key" data-testid="recovery-key">
		{#each key.split('-') as group, i (i)}{#if i > 0}-<wbr />{/if}<span class="group">{group}</span
			>{/each}
	</p>
	<button class="btn btn-ghost" type="button" onclick={copy}>
		{copied ? de.recovery.copied : de.recovery.copy}
	</button>

	<label class="confirm">
		<input type="checkbox" bind:checked={confirmed} />
		{de.recovery.confirm}
	</label>

	<button class="btn" type="button" disabled={!confirmed} onclick={oncontinue}>
		{de.recovery.continue}
	</button>
</main>

<style>
	.key {
		margin-top: 1.5rem;
		font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
		font-size: 1.15rem;
		letter-spacing: 0.05em;
		text-align: center;
		user-select: all;
		color: var(--accent-strong);
	}
	.group {
		white-space: nowrap;
	}
	.confirm {
		display: flex;
		gap: 0.6rem;
		align-items: flex-start;
		font-weight: normal;
		margin-top: 1.5rem;
	}
	.confirm input {
		width: 1.3rem;
		height: 1.3rem;
		margin: 0.1rem 0 0;
		flex: none;
		accent-color: var(--accent);
	}
</style>
