<script lang="ts">
	let {
		view = $bindable<'files' | 'book' | 'proposals' | 'specs' | 'roadmap' | 'shared'>('files')
	}: {
		view?: 'files' | 'book' | 'proposals' | 'specs' | 'roadmap' | 'shared';
	} = $props();

	const tabs = [
		{ id: 'book', label: 'Book', icon: '📖', title: 'Living Spec (Book)' },
		{ id: 'proposals', label: 'Proposals', icon: '💡', title: 'Proposals' },
		{ id: 'specs', label: 'Specs', icon: '📋', title: 'Feature Specs' },
		{ id: 'roadmap', label: 'Roadmap', icon: '🗺️', title: 'Roadmap' },
		{ id: 'shared', label: 'Shared', icon: '🤝', title: 'Shared Space (공유 공간)' },
		{ id: 'files', label: 'Files', icon: '📁', title: 'Repository Files' }
	] as const;
</script>

<nav class="view-rail view-tabs" aria-label="Views">
	{#each tabs as tab}
		<button
			aria-pressed={view === tab.id}
			aria-label={tab.label}
			class:active={view === tab.id}
			title={tab.title}
			onclick={() => {
				view = tab.id;
			}}
		>
			<span class="rail-icon">{tab.icon}</span>
			<span class="rail-label">{tab.label}</span>
		</button>
	{/each}
</nav>

<style>
	.view-rail {
		display: flex;
		flex-direction: column;
		width: 56px;
		flex-shrink: 0;
		background-color: var(--bg-sidebar);
		border-right: 1px solid var(--border-sidebar);
		padding: 8px 0;
		gap: 6px;
		align-items: center;
		box-sizing: border-box;
	}

	.view-rail button {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 46px;
		height: 46px;
		border-radius: 8px;
		border: 1px solid transparent;
		background: transparent;
		color: var(--text-dim);
		cursor: pointer;
		padding: 3px 2px;
		transition: all 0.15s ease;
		box-sizing: border-box;
		font: inherit;
	}

	.view-rail button:hover {
		background: var(--tree-hover-bg);
		color: var(--text-primary);
	}

	.view-rail button.active {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
		border-color: rgba(99, 102, 241, 0.3);
		font-weight: 600;
	}

	.view-rail button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
	}

	.rail-icon {
		font-size: 16px;
		line-height: 1.1;
	}

	.rail-label {
		font-size: 9.5px;
		letter-spacing: -0.2px;
		line-height: 1.1;
		text-align: center;
		max-width: 44px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>
