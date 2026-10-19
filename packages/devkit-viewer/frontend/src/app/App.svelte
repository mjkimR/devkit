<script lang="ts">
	import SddViewer from '../lib/SddViewer.svelte';
	import {
		listRepositories,
		readLocation,
		repositoryRefs,
		repositorySource,
		writeLocation,
		type RepositorySummary
	} from './api';

	let repos = $state<RepositorySummary[]>([]);
	let repoId = $state('');
	let branches = $state<string[]>([]);
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
				if (!controller.signal.aborted) error = `저장소 목록을 불러오지 못했습니다: ${err.message}`;
			});
		return () => controller.abort();
	});

	$effect(() => {
		const id = repoId;
		if (!id) return;
		const controller = new AbortController();
		branches = [];
		branch = '';
		repositoryRefs(id, controller.signal)
			.then((refs) => {
				branches = refs.branches;
				const wanted = id === requested.repo ? requested.ref : '';
				branch = refs.branches.includes(wanted) ? wanted : refs.default_branch;
			})
			.catch((err) => {
				if (!controller.signal.aborted) error = `브랜치 목록을 불러오지 못했습니다: ${err.message}`;
			});
		return () => controller.abort();
	});

	$effect(() => {
		if (repoId && branch) history.replaceState(null, '', writeLocation(repoId, branch));
	});

	const source = $derived(repoId ? repositorySource(repoId) : null);
</script>

<div class="app">
	<nav class="picker" aria-label="저장소 선택">
		<label>
			저장소
			<select aria-label="저장소" bind:value={repoId}>
				{#each repos as repo (repo.id)}<option value={repo.id}>{repo.id}</option>{/each}
			</select>
		</label>
		<label>
			브랜치
			<select aria-label="브랜치" bind:value={branch} disabled={!branches.length}>
				{#if branch && !branches.includes(branch)}<option value={branch}>{branch}</option>{/if}
				{#each branches as name (name)}<option value={name}>{name}</option>{/each}
			</select>
		</label>
		{#if error}<span class="error" role="alert">{error}</span>{/if}
	</nav>
	<div class="viewer">
		{#if source && branch}
			{#key `${repoId}@${branch}`}
				<SddViewer dataSource={source} {repoId} {branch} initialView="book" />
			{/key}
		{/if}
	</div>
</div>

<style>
	:global(html),
	:global(body) {
		margin: 0;
		height: 100%;
		background: #0b0f17;
		font-family:
			-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
	}
	:global(#app) {
		height: 100%;
	}
	.app {
		display: flex;
		flex-direction: column;
		height: 100%;
	}
	.picker {
		display: flex;
		align-items: center;
		gap: 16px;
		padding: 8px 16px;
		background: #0f172a;
		border-bottom: 1px solid #1f2937;
		color: #cbd5e1;
		font-size: 13px;
	}
	label {
		display: flex;
		align-items: center;
		gap: 8px;
	}
	select {
		font: inherit;
		color: #f8fafc;
		background: #1f2937;
		border: 1px solid #374151;
		border-radius: 6px;
		padding: 4px 8px;
	}
	.error {
		color: #fecaca;
	}
	.viewer {
		flex: 1;
		min-height: 0;
	}
</style>
