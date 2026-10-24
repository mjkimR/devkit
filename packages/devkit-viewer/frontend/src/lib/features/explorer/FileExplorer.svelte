<script lang="ts">
	import type { TreeItem } from '../../api/repository';
	import FileTree from './FileTree.svelte';

	let {
		treeItems = [],
		currentPath = '',
		currentBlobPath = '',
		loading = false,
		onnavigate,
		onparent
	}: {
		treeItems?: TreeItem[];
		currentPath?: string;
		currentBlobPath?: string;
		loading?: boolean;
		onnavigate: (path: string, isTree: boolean) => void;
		onparent: () => void;
	} = $props();

	let searchQuery = $state('');

	const filteredItems = $derived(
		treeItems.filter(
			(item) => !searchQuery || item.name.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);
</script>

<aside class="sidebar-explorer">
	<div class="sidebar-header">
		<span class="section-label">EXPLORER</span>
		{#if currentPath}
			<button class="up-btn" title="Up one level" onclick={onparent}> ⬆ Up </button>
		{/if}
	</div>

	<div class="search-box">
		<input
			type="text"
			placeholder="Filter files..."
			bind:value={searchQuery}
			class="filter-input"
		/>
	</div>

	<FileTree
		items={filteredItems}
		{currentPath}
		{currentBlobPath}
		{loading}
		onselect={(item) => onnavigate(item.path, item.type === 'tree')}
	/>
</aside>

<style>
	.sidebar-explorer {
		width: 280px;
		background-color: var(--bg-sidebar);
		border-right: 1px solid var(--border-sidebar);
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
	}

	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 10px 12px;
		border-bottom: 1px solid var(--border-sidebar);
	}

	.section-label {
		font-size: 11px;
		font-weight: 700;
		color: var(--text-dim);
		letter-spacing: 0.05em;
	}

	.up-btn {
		background: none;
		border: 1px solid var(--border-input);
		color: var(--text-muted);
		font-size: 11px;
		padding: 2px 6px;
		border-radius: 4px;
		cursor: pointer;
	}

	.up-btn:hover {
		background-color: var(--tree-hover-bg);
		color: var(--text-primary);
	}

	.search-box {
		padding: 8px 12px;
		border-bottom: 1px solid var(--border-sidebar);
	}

	.filter-input {
		width: 100%;
		background-color: var(--bg-input);
		border: 1px solid var(--border-input);
		border-radius: 4px;
		padding: 6px 8px;
		font-size: 12px;
		color: var(--text-primary);
		outline: none;
	}

	.filter-input:focus {
		border-color: #6366f1;
	}
</style>
