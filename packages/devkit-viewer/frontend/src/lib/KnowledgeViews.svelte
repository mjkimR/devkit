<script lang="ts">
	import KnowledgeViews from './features/knowledge/KnowledgeViews.svelte';

	let {
		bookRequested = $bindable(false),
		...props
	}: import('svelte').ComponentProps<typeof KnowledgeViews> = $props();
</script>

<KnowledgeViews {...props} bind:bookRequested />
