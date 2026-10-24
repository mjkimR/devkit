<script lang="ts">
	import KnowledgeViews from './features/knowledge/KnowledgeViews.svelte';

	let props: import('svelte').ComponentProps<typeof KnowledgeViews> = $props();
</script>

<KnowledgeViews {...props} />
