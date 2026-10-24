<script lang="ts">
	let {
		breadcrumbs = [],
		currentPath = '',
		onnavigate
	}: {
		breadcrumbs: string[];
		currentPath: string;
		onnavigate: (path: string, isTree: boolean) => void;
	} = $props();
</script>

<nav class="breadcrumb-bar" aria-label="Breadcrumb">
	<button class="crumb-btn" onclick={() => onnavigate('', true)}>root</button>
	{#each breadcrumbs as part, idx}
		<span class="crumb-sep">/</span>
		{#if idx === breadcrumbs.length - 1 && !currentPath.endsWith('/')}
			<span class="crumb-current">{part}</span>
		{:else}
			<button
				class="crumb-btn"
				onclick={() => onnavigate(breadcrumbs.slice(0, idx + 1).join('/') + '/', true)}
			>
				{part}
			</button>
		{/if}
	{/each}
</nav>

<style>
	.breadcrumb-bar {
		display: flex;
		align-items: center;
		gap: 4px;
		font-size: 12px;
		margin-left: 12px;
		overflow-x: auto;
		white-space: nowrap;
	}

	.crumb-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 2px 6px;
		border-radius: 4px;
		font-size: 12px;
	}

	.crumb-btn:hover {
		color: var(--text-primary);
		background-color: var(--btn-hover-bg);
	}

	.crumb-sep {
		color: var(--text-dim);
	}

	.crumb-current {
		color: var(--text-primary);
		font-weight: 600;
		padding: 2px 6px;
	}
</style>

