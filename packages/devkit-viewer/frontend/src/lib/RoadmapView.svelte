<script lang="ts">
	import type { RepositoryDocument } from './documents';
	import type { RepositoryDataSource } from './repository';
	import {
		buildRoadmap,
		isActivityBranch,
		loadRoadmapDocuments,
		type BranchDocuments
	} from './roadmap';

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
	{#if errors.length}<details class="index-errors">
			<summary>{errors.length} documents failed to load</summary>{#each errors as error}<p>
					{error}
				</p>{/each}
		</details>{/if}
	{#if loading}<p role="status">Loading roadmap…</p>
	{:else if !source}<p>Connect a repository to view the roadmap.</p>
	{:else if !milestones.length}<p class="empty">No milestones to display.</p>
	{:else}
		<ol class="milestones">
			{#each milestones as milestone (milestone.id)}
				<li class="milestone">
					<header>
						<span class="id">{milestone.id}</span>
						<span class="status status-{milestone.status}">{milestone.status}</span>
						{#if milestone.ready}
							<span class="readiness ready">Ready</span>
						{:else}
							{#if milestone.waitingFor.length}
								<span class="readiness waiting">Blocked by: {milestone.waitingFor.join(', ')}</span>
							{/if}
							{#if milestone.unknown.length}
								<span class="readiness unknown"
									>Unknown dependencies: {milestone.unknown.join(', ')}</span
								>
							{/if}
						{/if}
						{#if opens(null)}
							<button onclick={() => onOpen(milestone.path)}>View raw</button>
						{/if}
					</header>
					<h2>{milestone.title}</h2>
					{#if milestone.members.length}
						<ul class="members">
							{#each milestone.members as member (member.id)}
								<li>
									<span class="settled" class:done={member.settled}
										>{member.settled ? 'Settled' : 'In progress'}</span
									>
									{#if opens(member.branch)}
										<button class="title" onclick={() => onOpen(member.path)}>{member.title}</button
										>
									{:else}
										<span class="title">{member.title}</span>
									{/if}
									{#if member.branch}<span class="branch">🌿 {member.branch}</span>{/if}
									<span class="meta">{member.id} · {member.status}</span>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="empty-members">No members</p>
					{/if}
				</li>
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
		padding: 24px 16px;
		max-width: 960px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.milestone {
		border: 1px solid var(--border-panel);
		border-radius: 8px;
		background: var(--bg-panel);
		padding: 16px 20px;
	}
	.milestone header {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
	}
	.milestone h2 {
		font-size: 17px;
		margin: 10px 0;
	}
	.id {
		font-family: monospace;
		font-size: 12px;
		font-weight: 700;
		color: var(--tree-selected-text);
	}
	.status,
	.readiness,
	.branch,
	.settled {
		font-size: 11px;
		padding: 2px 8px;
		border-radius: 4px;
		background: var(--badge-bg);
		color: var(--badge-text);
	}
	.status-active,
	.ready,
	.settled.done {
		background: #064e3b;
		color: #6ee7b7;
	}
	.status-planned,
	.waiting {
		background: #78350f;
		color: #fde68a;
	}
	.unknown {
		background: #7f1d1d;
		color: #fecaca;
	}
	button {
		font: inherit;
		cursor: pointer;
		color: var(--text-primary);
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		background: var(--bg-btn);
		padding: 4px 10px;
		font-size: 12px;
	}
	header button {
		margin-left: auto;
	}
	button:hover {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
	}
	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
	}
	.members {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.members li {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
		font-size: 13px;
	}
	.members .title {
		border: 0;
		background: transparent;
		padding: 0;
		font-size: 13px;
		text-align: left;
	}
	.meta,
	.empty-members,
	.empty {
		color: var(--text-muted);
		font-size: 12px;
	}
	.empty {
		text-align: center;
		margin: 80px 0;
	}
	.index-errors {
		padding: 12px 16px;
		color: var(--text-secondary);
	}
	.index-errors p {
		font-size: 12px;
		overflow-wrap: anywhere;
	}
</style>
