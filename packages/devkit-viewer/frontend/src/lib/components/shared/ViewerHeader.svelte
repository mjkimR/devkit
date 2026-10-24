<script lang="ts">
	import type { Snippet } from 'svelte';
	import Breadcrumbs from './Breadcrumbs.svelte';
	import ThemeToggle from './ThemeToggle.svelte';
	import type { RepositoryInfo } from '../../api/repository';

	let {
		repoId = '',
		repoInfo = null,
		branch = 'main',
		view = 'files',
		breadcrumbs = [],
		currentPath = '',
		hasCurrentBlob = false,
		rawMode = $bindable(false),
		theme = 'dark',
		picker = undefined,
		onnavigate,
		ontoggletheme
	}: {
		repoId?: string;
		repoInfo?: RepositoryInfo | null;
		branch?: string;
		view?: string;
		breadcrumbs?: string[];
		currentPath?: string;
		hasCurrentBlob?: boolean;
		rawMode?: boolean;
		theme?: 'dark' | 'light';
		picker?: Snippet;
		onnavigate: (path: string, isTree: boolean) => void;
		ontoggletheme: () => void;
	} = $props();
</script>

<header class="viewer-header">
	<div class="brand-zone">
		<div class="logo-badge">
			<svg
				viewBox="0 0 24 24"
				width="16"
				height="16"
				stroke="currentColor"
				stroke-width="2"
				fill="none"
			>
				<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
				<polyline points="2 17 12 22 22 17"></polyline>
				<polyline points="2 12 12 17 22 12"></polyline>
			</svg>
		</div>
		<span class="brand-title">Sdd Viewer</span>
		{#if picker}
			{@render picker()}
		{:else}
			{#if repoId || repoInfo?.repo_id}
				<span class="repo-tag">{repoId || repoInfo?.repo_id}</span>
			{/if}
			<span class="branch-tag">🌿 {branch}</span>
		{/if}
	</div>

	<!-- Breadcrumbs -->
	{#if view === 'files' || breadcrumbs.length}
		<Breadcrumbs {breadcrumbs} {currentPath} {onnavigate} />
	{/if}

	<div class="action-zone">
		{#if hasCurrentBlob && view === 'files'}
			<button class="mode-toggle-btn" class:active={rawMode} onclick={() => (rawMode = !rawMode)}>
				{rawMode ? '👁️ Preview' : '📝 Raw'}
			</button>
		{/if}
		<ThemeToggle {theme} ontoggle={ontoggletheme} />
	</div>
</header>

<style>
	.viewer-header {
		display: flex;
		align-items: center;
		gap: 12px;
		height: 40px;
		padding: 0 14px;
		background-color: var(--bg-header);
		border-bottom: 1px solid var(--border-header);
		flex-shrink: 0;
		box-sizing: border-box;
	}

	.brand-zone {
		display: flex;
		align-items: center;
		gap: 10px;
		flex-shrink: 0;
	}

	.logo-badge {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 22px;
		height: 22px;
		background: linear-gradient(135deg, #6366f1, #a855f7);
		color: #ffffff;
		border-radius: 5px;
		flex-shrink: 0;
	}

	.brand-title {
		font-weight: 700;
		font-size: 13px;
		color: var(--text-primary);
		white-space: nowrap;
	}

	.repo-tag {
		font-size: 11px;
		font-weight: 600;
		padding: 2px 6px;
		border-radius: 4px;
		background-color: var(--bg-viewport);
		color: #38bdf8;
		border: 1px solid #0284c7;
	}

	.branch-tag {
		font-size: 11px;
		padding: 2px 6px;
		border-radius: 4px;
		background-color: var(--branch-bg);
		color: var(--branch-text);
	}

	.action-zone {
		margin-left: auto;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.mode-toggle-btn {
		background-color: var(--bg-btn);
		border: 1px solid var(--border-btn);
		color: var(--text-btn);
		padding: 4px 10px;
		border-radius: 6px;
		font-size: 12px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.mode-toggle-btn:hover {
		background-color: var(--btn-hover-bg);
		color: var(--text-primary);
	}

	.mode-toggle-btn.active {
		background-color: #4f46e5;
		border-color: #6366f1;
		color: #ffffff;
	}
</style>

