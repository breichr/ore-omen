<script lang="ts">
	import { de } from '$lib/text/de';
	import { invalidateAll } from '$app/navigation';
</script>

<main>
	<h1>{de.app.name}</h1>
	<p class="story">{de.offline.page}</p>
	<button class="btn btn-ghost" onclick={() => invalidateAll()}>{de.app.retry}</button>
</main>
