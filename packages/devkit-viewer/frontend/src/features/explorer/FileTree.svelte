<script lang="ts">
	import type { TreeItem } from '../../api/repository';
	import FileTreeItem from './FileTreeItem.svelte';

	let {
		items = [],
		currentPath = '',
		currentBlobPath = '',
		loading = false,
		onselect
	}: {
		items?: TreeItem[];
		currentPath?: string;
		currentBlobPath?: string;
		loading?: boolean;
		onselect: (item: TreeItem) => void;
	} = $props();
</script>

<div class="file-tree">
	{#if loading && !items.length}
		<div class="loading-state">Loading directory...</div>
	{:else if items.length === 0}
		<div class="empty-state">No matching items</div>
	{:else}
		{#each items as item (item.path)}
			<FileTreeItem
				{item}
				isSelected={currentPath === item.path || currentBlobPath === item.path}
				{onselect}
			/>
		{/each}
	{/if}
</div>

<style>
	.file-tree {
		flex: 1;
		overflow-y: auto;
		padding: 6px;
	}

	.loading-state,
	.empty-state {
		padding: 24px;
		text-align: center;
		font-size: 12px;
		color: var(--text-dim);
	}
</style>
