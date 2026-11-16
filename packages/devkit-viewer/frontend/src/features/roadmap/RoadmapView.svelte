<script lang="ts">
	import type { RepositoryDocument } from '../../api/documents';
	import type { RepositoryDataSource } from '../../api/repository';
	import { buildRoadmap, loadRoadmapDocuments, type BranchDocuments } from '../../api/roadmap';
	import MilestoneItem from './MilestoneItem.svelte';

	let {
		source,
		branch,
		onOpen
	}: {
		source: RepositoryDataSource | null;
		branch: string;
		onOpen: (path: string) => void;
	} = $props();

	let base = $state<RepositoryDocument[]>([]);
	let baseRef = $state('');
	let branches: BranchDocuments[] = [];
	let errors = $state<string[]>([]);
	let loading = $state(false);
	let history = $state(false);

	$effect(() => {
		const repository = source;
		const currentBranch = branch;
		const controller = new AbortController();
		base = [];
		baseRef = currentBranch;
		errors = [];
		loading = Boolean(repository);
		if (repository)
			void (async () => {
				const signal = controller.signal;
				const selected = await loadRoadmapDocuments(repository, currentBranch, signal);
				if (signal.aborted) return;
				base = selected.documents;
				errors = selected.errors;
				loading = false;
			})();
		return () => controller.abort();
	});

	const opens = (_ref: string | null) => baseRef === branch;
	const milestones = $derived(buildRoadmap(base, branches, { history }));
</script>

<div class="roadmap">
	<div class="filters">
		<label><input type="checkbox" bind:checked={history} /> Include completed/abandoned</label>
		{#if baseRef}<span class="note">Base: {baseRef} branch</span>{/if}
	</div>
	{#if errors.length}
		<details class="index-errors">
			<summary>{errors.length} documents failed to load</summary>
			{#each errors as error}
				<p>{error}</p>
			{/each}
		</details>
	{/if}
	{#if loading}
		<p role="status">Loading roadmap…</p>
	{:else if !source}
		<p>Connect a repository to view the roadmap.</p>
	{:else if !milestones.length}
		<p class="empty">No milestones to display.</p>
	{:else}
		<ol class="milestones">
			{#each milestones as milestone (milestone.id)}
				<MilestoneItem
					{milestone}
					canOpenBase={opens(null)}
					canOpenMember={(memberBranch) => opens(memberBranch)}
					{onOpen}
				/>
			{/each}
		</ol>
	{/if}
</div>

<style>
	.roadmap {
		height: 100%;
		overflow: auto;
		color: var(--text-primary);
	}

	.filters {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 16px;
		padding: 16px;
		border-bottom: 1px solid var(--border-panel);
		font-size: 13px;
	}

	.note {
		color: var(--text-muted);
	}

	.milestones {
		list-style: none;
		margin: 0 auto;
		max-width: 960px;
		padding: 24px clamp(16px, 4vw, 64px);
	}

	.index-errors {
		padding: 12px 16px;
		color: var(--text-secondary);
	}

	.index-errors p {
		font-size: 12px;
		overflow-wrap: anywhere;
	}

	.empty {
		text-align: center;
		margin: 80px 0;
		color: var(--text-muted);
	}
</style>
