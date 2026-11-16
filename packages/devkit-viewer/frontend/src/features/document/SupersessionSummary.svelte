<script lang="ts">
	import type { RepositoryDocument } from '../../api/documents';
	import { documentAnchor } from '../../api/documents';
	import { deriveSupersession, isDecision } from './supersession';
	let {
		subject,
		documents = [],
		loading = false,
		errors = [],
		onOpen,
		onReload
	}: {
		subject: RepositoryDocument;
		documents?: RepositoryDocument[];
		loading?: boolean;
		errors?: string[];
		onOpen: (path: string) => void;
		onReload: () => void;
	} = $props();
	const relations = $derived(deriveSupersession(subject, documents));
	const groups = $derived([
		{
			title: relations.proposed ? 'Proposed supersession' : 'Supersedes',
			rows: relations.outgoing
		},
		...(relations.proposed ? [] : [{ title: 'Superseded by', rows: relations.incoming }])
	]);
</script>

{#if isDecision(subject)}
	<section class="supersession-summary" aria-label="Decision supersession" aria-busy={loading}>
		<div class="summary-heading">
			<h3>Supersession relations</h3>
			<button onclick={onReload} disabled={loading}>Reload relations</button>
		</div>
		{#if loading}<p role="status">Loading supersession relations…</p>{/if}
		{#if errors.length}
			<p class="incomplete" role="status">Incomplete — some documents could not be read.</p>
			<details>
				<summary>Source failures</summary>{#each errors as error}<p>{error}</p>{/each}
			</details>
		{/if}
		{#each groups as group}
			<div class="relation-group">
				<h4>{group.title}</h4>
				{#each group.rows as row}
					<div class="relation-row">
						{#if row.path}
							<a
								href={`#${documentAnchor(row.path)}`}
								onclick={(event) => {
									if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
									event.preventDefault();
									event.stopPropagation();
									onOpen(row.path!);
								}}>{row.id}{row.title ? ` — ${row.title}` : ''}</a
							>
						{:else}<span>{row.id} ({row.unavailable} target)</span>{/if}
						<p class="relation-meta">
							{row.status ?? 'Unknown status'} · {relations.proposed ? 'proposed ' : ''}{row.scope}
						</p>
						<p class="replacement-text">{row.text ?? 'Replacement scope not recorded'}</p>
					</div>
				{:else}{#if !loading}
						<p class="empty">
							{errors.length
								? group.title === 'Superseded by'
									? 'No incoming relations found in the documents read'
									: 'No outgoing relations found in the documents read'
								: 'None recorded'}
						</p>
					{/if}{/each}
			</div>
		{/each}
	</section>
{/if}

<style>
	.supersession-summary {
		margin: 20px 0;
		padding: 16px;
		border: 1px solid var(--border-panel);
		border-radius: 8px;
		color: var(--text-primary);
	}
	.summary-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		flex-wrap: wrap;
	}
	h3,
	h4 {
		margin: 0 0 8px;
	}
	h3 {
		font-size: 16px;
	}
	h4 {
		font-size: 14px;
	}
	.relation-group {
		margin-top: 12px;
	}
	.relation-row {
		margin: 12px 0;
		overflow-wrap: anywhere;
	}
	p {
		margin: 6px 0;
	}
	.relation-meta,
	.empty {
		color: var(--text-muted);
		font-size: 13px;
	}
	.replacement-text {
		white-space: pre-wrap;
		line-height: 1.6;
	}
	.incomplete {
		color: var(--text-secondary);
	}
	a {
		color: var(--tree-selected-text);
	}
	button {
		font: inherit;
		color: var(--text-primary);
		background: var(--bg-panel);
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		padding: 6px 10px;
		cursor: pointer;
	}
	button:disabled {
		opacity: 0.6;
		cursor: default;
	}
	a:focus-visible,
	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
		outline-offset: 2px;
	}
</style>
