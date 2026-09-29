<script lang="ts">
	import type { Applied } from '$lib/api';
	import { formatAmounts } from '$lib/format';
	import { de } from '$lib/text/de';

	let { applied }: { applied: Applied } = $props();

	const lines = $derived.by(() => {
		const out: { text: string; bad?: boolean }[] = [];
		const a = applied;
		const gains = { ...(a.resources ?? {}), ...(a.dollars ? { dollars: a.dollars } : {}) };
		const positive = Object.fromEntries(Object.entries(gains).filter(([, v]) => v > 0));
		const negative = Object.fromEntries(
			Object.entries(gains)
				.filter(([, v]) => v < 0)
				.map(([k, v]) => [k, -v])
		);
		if (Object.keys(positive).length) out.push({ text: '+' + formatAmounts(positive) });
		if (Object.keys(negative).length) out.push({ text: '−' + formatAmounts(negative), bad: true });
		if (a.lost && Object.keys(a.lost).length)
			out.push({ text: de.settlement.lost(formatAmounts(a.lost)), bad: true });
		if (a.xp) out.push({ text: de.event.applied.xp(a.xp) });
		if (a.levels_gained) out.push({ text: de.event.applied.level(a.levels_gained) });
		for (const [f, v] of Object.entries(a.reputation ?? {}))
			out.push({ text: `${de.factionShort[f]} ${v > 0 ? '+' : '−'}${Math.abs(v)}`, bad: v < 0 });
		if (a.corruption)
			out.push({ text: de.event.applied.corruption(a.corruption), bad: a.corruption > 0 });
		for (const i of a.items ?? []) out.push({ text: de.event.applied.item(de.items[i] ?? i) });
		for (const [b, l] of Object.entries(a.built ?? {}))
			out.push({ text: de.event.applied.built(b === 'main_house' ? 'Haupthaus' : b, l) });
		if (a.unlock?.length) out.push({ text: de.event.applied.unlock });
		if (a.delay_min) out.push({ text: de.event.applied.delay(a.delay_min), bad: true });
		if (a.stored && 'combat' in a.stored) out.push({ text: de.event.applied.combat, bad: true });
		else if (a.stored && Object.keys(a.stored).length) out.push({ text: de.event.applied.stored });
		return out;
	});
</script>

{#if lines.length}
	<ul class="applied">
		{#each lines as l, i (i)}
			<li class:bad={l.bad}>{l.text}</li>
		{/each}
	</ul>
{/if}

<style>
	.applied {
		list-style: none;
		padding: 0;
		margin: 0.75rem 0 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	li {
		background: #1f2a1c;
		border: 1px solid #3c5236;
		border-radius: 999px;
		padding: 0.2rem 0.7rem;
		font-size: 0.85rem;
	}
	li.bad {
		background: #2c1a16;
		border-color: #5a3228;
	}
</style>
