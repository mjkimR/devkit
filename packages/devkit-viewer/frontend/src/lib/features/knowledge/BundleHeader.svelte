<script lang="ts">
	import type { RepositoryDocument, RenderedDocument } from '../../api/documents';

	let {
		selected,
		bundle = [],
		detail = null,
		taskChecks = { total: 0, checked: 0 },
		relations = [],
		ids,
		rendered,
		view = '',
		onOpen,
		onLocation,
		onJump,
		onSelectDetail,
		onOpenShared = undefined
	}: {
		selected: RepositoryDocument;
		bundle: RepositoryDocument[];
		detail?: RepositoryDocument | null;
		taskChecks: { total: number; checked: number };
		relations: string[];
		ids: Map<string, RepositoryDocument>;
		rendered: Map<string, RenderedDocument>;
		view?: string;
		onOpen: (path: string) => void;
		onLocation: (path: string, anchor: string, meta: Record<string, any>) => void;
		onJump: (path: string, headingId: string) => void;
		onSelectDetail: (path: string) => void;
		onOpenShared?: (slug: string) => void;
	} = $props();

	const fileLabel = (path: string) =>
		({
			'proposal.md': 'Proposal',
			'spec.md': 'Spec',
			'plan.md': 'Plan',
			'tasks.md': 'Tasks',
			'reconcile.md': 'Reconcile',
			'target-docs.md': 'Target Docs'
		})[path.split('/').at(-1)!] ?? path.split('/').slice(-2).join('/');
</script>

<div class="bundle-header">
	<h1>{selected.title}</h1>
	<p>{selected.meta.id} · {selected.meta.status ?? 'unknown'}</p>
	{#if taskChecks.total}
		<p>
			Task checks: {taskChecks.checked}/{taskChecks.total} — see records for verification and integration
			state.
		</p>
	{/if}
	{#if relations.length}
		<div class="relations">
			Related: {#each relations as id}
				{#if ids.has(id)}
					<button onclick={() => onOpen(ids.get(id)!.path)}>{id}</button>
				{:else}
					<span>{id}</span>
				{/if}
			{/each}
		</div>
	{/if}
	<nav aria-label="Bundle documents">
		{#each bundle as doc}
			<button
				class:active={detail?.path === doc.path}
				onclick={() => {
					onSelectDetail(doc.path);
					onLocation(doc.path, '', doc.meta);
				}}
			>
				{fileLabel(doc.path)}
			</button>
		{/each}
		{#if view === 'proposals' && onOpenShared}
			<button
				class="shared-report-btn"
				title="이 제안의 공유 공간 리포트 확인"
				onclick={() => {
					const parts = selected.path.split('/');
					const slug = selected.meta.slug || parts[2] || selected.meta.id;
					onOpenShared(slug);
				}}
			>
				🤝 공유 리포트
			</button>
		{/if}
	</nav>
	{#if detail}
		<nav class="detail-toc" aria-label="Document outline">
			{#each rendered.get(detail.path)?.headings ?? [] as h}
				<button onclick={() => onJump(detail.path, h.id)}>{h.title}</button>
			{/each}
		</nav>
	{/if}
</div>

<style>
	.bundle-header {
		max-width: 960px;
		margin: 0 auto 24px;
	}

	.bundle-header nav,
	.relations {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin: 16px 0;
		align-items: center;
	}

	button {
		cursor: pointer;
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		background: var(--bg-panel);
		padding: 8px 10px;
		text-align: left;
		font: inherit;
		color: var(--text-primary);
	}

	button:hover,
	button.active {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
	}

	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
		outline-offset: 2px;
	}

	.detail-toc button {
		font-size: 12px;
	}

	.shared-report-btn {
		background-color: var(--badge-bg);
		border: 1px dashed var(--border-btn) !important;
		color: var(--text-btn) !important;
		font-size: 13px;
		padding: 6px 12px;
		border-radius: 6px;
		cursor: pointer;
		margin-left: 8px;
	}

	.shared-report-btn:hover {
		background-color: var(--bg-btn) !important;
		border-style: solid !important;
		color: var(--text-primary) !important;
	}
</style>
