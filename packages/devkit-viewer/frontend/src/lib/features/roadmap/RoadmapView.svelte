<script lang="ts">
	import type { RepositoryDocument } from '../../api/documents';
	import type { RepositoryDataSource } from '../../api/repository';
	import {
		buildRoadmap,
		isActivityBranch,
		loadRoadmapDocuments,
		type BranchDocuments
	} from '../../api/roadmap';
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
	let branches = $state<BranchDocuments[]>([]);
	let errors = $state<string[]>([]);
	let loading = $state(false);
	let branchesUnavailable = $state(false);
	let history = $state(false);

	// Milestones and their members come from the default branch, whatever branch the viewer shows; Units still in
	// progress are read from the local plan- and dev- branches the data source lists.
	async function defaultBranch(repository: RepositoryDataSource, signal: AbortSignal) {
		if (repository.refs) {
			try {
				const refs = await repository.refs(signal);
				return { name: refs.default_branch, others: refs.branches };
			} catch {
				// Fall through: without refs only the default branch is read.
			}
		}
		try {
			return {
				name: String((await repository.info(signal)).default_branch || branch),
				others: null
			};
		} catch {
			return { name: branch, others: null };
		}
	}

	$effect(() => {
		const repository = source;
		const controller = new AbortController();
		base = [];
		baseRef = '';
		branches = [];
		errors = [];
		branchesUnavailable = false;
		loading = Boolean(repository);
		if (repository)
			void (async () => {
				const signal = controller.signal;
				const { name, others } = await defaultBranch(repository, signal);
				const names = (others ?? []).filter((n) => n !== name && isActivityBranch(n));
				const [selected, ...rest] = await Promise.all(
					[name, ...names].map(async (ref) => ({
						name: ref,
						...(await loadRoadmapDocuments(repository, ref, signal))
					}))
				);
				if (signal.aborted) return;
				base = selected.documents;
				baseRef = name;
				branchesUnavailable = others === null;
				branches = rest.map(({ name, documents }) => ({ name, documents }));
				errors = [
					...selected.errors,
					...rest.flatMap((o) => o.errors.map((error) => `${o.name}: ${error}`))
				];
				loading = false;
			})();
		return () => controller.abort();
	});

	// The file explorer shows the viewer's branch, so a document opens there only when it was read from that branch.
	const opens = (ref: string | null) => (ref ?? baseRef) === branch;
	const milestones = $derived(buildRoadmap(base, branches, { history }));
</script>

<div class="roadmap">
	<div class="filters">
		<label><input type="checkbox" bind:checked={history} /> Include completed/abandoned</label>
		{#if baseRef}<span class="note">Base: {baseRef} branch</span>{/if}
		{#if branchesUnavailable}
			<span class="note">Unable to read branch list; displaying {baseRef} branch only.</span>
		{:else if branches.length}
			<span class="note"
				>Includes {branches.length} active {branches.length === 1 ? 'branch' : 'branches'}</span
			>
		{/if}
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
