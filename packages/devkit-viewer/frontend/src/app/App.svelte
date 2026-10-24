<script lang="ts">
	import SddViewer from '../lib/SddViewer.svelte';
	import {
		listRepositories,
		readLocation,
		repositorySource,
		writeLocation,
		type RepositorySummary
	} from './api';

	let repos = $state<RepositorySummary[]>([]);
	let repoId = $state('');
	let branch = $state('');
	let error = $state('');
	const requested = readLocation(window.location.hash);

	$effect(() => {
		const controller = new AbortController();
		listRepositories(controller.signal)
			.then((items) => {
				repos = items;
				repoId = items.some((r) => r.id === requested.repo) ? requested.repo : (items[0]?.id ?? '');
			})
			.catch((err) => {
				if (!controller.signal.aborted) error = `Failed to load repositories: ${err.message}`;
			});
		return () => controller.abort();
	});

	$effect(() => {
		branch = repos.find((repo) => repo.id === repoId)?.default_branch ?? '';
	});

	$effect(() => {
		if (repoId) history.replaceState(null, '', writeLocation(repoId));
	});

	const source = $derived(repoId ? repositorySource(repoId) : null);
</script>

<div class="app">
	{#snippet pickerSnippet()}
		<nav class="picker" aria-label="Repository selection">
			<label>
				Repository
				<select aria-label="Repository" bind:value={repoId}>
					{#each repos as repo (repo.id)}<option value={repo.id}>{repo.id}</option>{/each}
				</select>
			</label>
			{#if branch}<span class="branch-tag">Branch: {branch}</span>{/if}
			{#if error}<span class="error" role="alert">{error}</span>{/if}
		</nav>
	{/snippet}

	{#if source && branch}
		{#key `${repoId}@${branch}`}
			<SddViewer
				dataSource={source}
				{repoId}
				{branch}
				initialView="dashboard"
				picker={pickerSnippet}
			/>
		{/key}
	{:else}
		<header class="loading-header">
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
				{@render pickerSnippet()}
			</div>
		</header>
	{/if}
</div>

<style>
	:global(html),
	:global(body) {
		margin: 0;
		height: 100%;
		overflow: hidden;
		background: #0b0f17;
		font-family:
			-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
		scrollbar-width: thin;
		scrollbar-color: #334155 transparent;
	}

	:global(::-webkit-scrollbar) {
		width: 8px;
		height: 8px;
	}

	:global(::-webkit-scrollbar-track) {
		background: transparent;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: #334155;
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: #475569;
	}
	:global(#app) {
		height: 100%;
		overflow: hidden;
	}
	.app {
		display: flex;
		flex-direction: column;
		height: 100%;
		overflow: hidden;
	}
	.picker {
		display: flex;
		align-items: center;
		gap: 12px;
		color: #cbd5e1;
		font-size: 12px;
	}
	label {
		display: flex;
		align-items: center;
		gap: 6px;
		color: #94a3b8;
	}
	select {
		font: inherit;
		color: #f8fafc;
		background: #1f2937;
		border: 1px solid #374151;
		border-radius: 4px;
		padding: 2px 6px;
		height: 26px;
		font-size: 12px;
	}
	.error {
		color: #fecaca;
		font-size: 12px;
	}
	.loading-header {
		display: flex;
		align-items: center;
		gap: 12px;
		height: 40px;
		padding: 0 14px;
		background-color: #0f172a;
		border-bottom: 1px solid #1f2937;
		flex-shrink: 0;
		box-sizing: border-box;
	}
	.brand-zone {
		display: flex;
		align-items: center;
		gap: 10px;
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
	}
	.brand-title {
		font-weight: 700;
		font-size: 13px;
		color: #f8fafc;
	}
</style>
