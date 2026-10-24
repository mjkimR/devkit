<script lang="ts">
	import RoadmapView from './features/roadmap/RoadmapView.svelte';

	let props: import('svelte').ComponentProps<typeof RoadmapView> = $props();
</script>

<RoadmapView {...props} />
