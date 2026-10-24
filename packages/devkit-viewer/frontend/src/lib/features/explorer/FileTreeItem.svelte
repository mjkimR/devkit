<script lang="ts">
	import type { TreeItem } from '../../api/repository';

	let {
		item,
		isSelected = false,
		onselect
	}: {
		item: TreeItem;
		isSelected?: boolean;
		onselect: (item: TreeItem) => void;
	} = $props();
</script>

<button class="tree-node" class:selected={isSelected} onclick={() => onselect(item)}>
	{#if item.type === 'tree'}
		<span class="node-icon folder">📁</span>
	{:else if item.name.endsWith('.md')}
		<span class="node-icon spec-file">📄</span>
	{:else}
		<span class="node-icon file">📑</span>
	{/if}
	<span class="node-name">{item.name}</span>
</button>

<style>
	.tree-node {
		display: flex;
		align-items: center;
		gap: 8px;
		width: 100%;
		padding: 6px 8px;
		background: none;
		border: none;
		border-radius: 6px;
		color: var(--text-muted);
		font-size: 13px;
		cursor: pointer;
		text-align: left;
		transition: background-color 0.1s ease;
	}

	.tree-node:hover {
		background-color: var(--tree-hover-bg);
		color: var(--text-primary);
	}

	.tree-node.selected {
		background-color: var(--tree-selected-bg);
		color: var(--tree-selected-text);
		font-weight: 600;
	}

	.node-icon {
		font-size: 14px;
	}

	.node-name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>

