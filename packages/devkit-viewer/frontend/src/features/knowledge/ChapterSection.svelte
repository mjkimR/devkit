<script lang="ts">
	import type { RepositoryDocument } from '../../api/documents';
	import { documentAnchor, bookGroup } from '../../api/documents';
	import RawViewer from '../document/RawViewer.svelte';
	import FormalReferences from '../document/FormalReferences.svelte';
	import { repositoryImages } from '../../api/artifacts';
	import type { FileSource, TreeItem } from '../../api/repository';
	import { isFormal, formalArea } from '../../api/identity';
	import SupersessionSummary from '../document/SupersessionSummary.svelte';
	import { isDecision } from '../document/supersession';

	let {
		doc,
		source = null,
		html,
		branch,
		theme,
		lazyDiagrams,
		trackHeading,
		sourceLabel = undefined,
		onOpen,
		documents = [],
		files = [],
		onSupportingOpen = () => {},
		relationLoading = false,
		relationErrors = [],
		onRelationOpen = onOpen,
		onReloadRelations = () => {}
	}: {
		doc: RepositoryDocument;
		source?: FileSource | null;
		html: string;
		branch: string;
		theme: string;
		lazyDiagrams: (node: HTMLElement) => { destroy: () => void };
		trackHeading: (node: HTMLElement) => { destroy: () => void };
		/** The Planning source a document was read from; the Files tab would show the checkout copy instead. */
		sourceLabel?: string;
		onOpen: (path: string) => void;
		documents?: RepositoryDocument[];
		files?: TreeItem[];
		onSupportingOpen?: (path: string) => void;
		relationLoading?: boolean;
		relationErrors?: string[];
		onRelationOpen?: (path: string) => void;
		onReloadRelations?: () => void;
	} = $props();

	let raw = $state(false);
	function assets(node: HTMLElement) {
		const images = repositoryImages(node, { source, branch }),
			diagrams = lazyDiagrams(node);
		return {
			destroy() {
				images.destroy();
				diagrams.destroy();
			}
		};
	}
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

<section class="chapter" id={documentAnchor(doc.path)} use:trackHeading>
	<header>
		<div>
			<span class="chapter-group"
				>{bookGroup(doc) ?? fileLabel(doc.path)}{formalArea(doc)
					? ' · ' + formalArea(doc)
					: ''}</span
			>
			<h2>{doc.title}</h2>
			<small>{doc.meta.id ? doc.meta.id + ' · ' : ''}{doc.path}</small>
			{#if isDecision(doc) || isFormal(doc)}<span class="decision-status"
					>{typeof doc.meta.status === 'string' ? doc.meta.status : 'Unknown status'}</span
				>{/if}
		</div>
		{#if sourceLabel}
			<span class="source-badge" title="Planning source">{sourceLabel}</span>
		{:else}
			<button onclick={() => (raw = !raw)}>{raw ? 'Rendered' : 'View raw'}</button>
		{/if}
	</header>
	{#if !raw}<FormalReferences
			subject={doc}
			{files}
			{onSupportingOpen}
			{documents}
			loading={relationLoading}
			errors={relationErrors}
			onOpen={onRelationOpen}
			onReload={onReloadRelations}
		/><SupersessionSummary
			subject={doc}
			{documents}
			loading={relationLoading}
			errors={relationErrors}
			onOpen={onRelationOpen}
			onReload={onReloadRelations}
		/>
	{/if}
	{#if raw}<RawViewer content={doc.raw} />{:else}
		{#key `${doc.path}-${branch}-${theme}-${doc.raw}-${html}`}
			<article class="markdown-body" use:assets use:trackHeading>
				{@html html}
			</article>
		{/key}
	{/if}
</section>

<style>
	.chapter {
		max-width: 960px;
		margin: 0 auto 48px;
		scroll-margin-top: 16px;
	}

	.chapter header {
		display: flex;
		justify-content: space-between;
		align-items: start;
		gap: 16px;
		padding-bottom: 20px;
		border-bottom: 1px solid var(--border-panel);
	}

	.decision-status {
		display: inline-block;
		margin-left: 8px;
		font-size: 12px;
		color: var(--text-secondary);
	}

	.chapter h2 {
		font-size: 24px;
		margin: 8px 0;
	}

	.chapter small,
	.chapter-group {
		color: var(--text-muted);
		overflow-wrap: anywhere;
	}

	.chapter-group {
		font-size: 12px;
	}

	.source-badge {
		flex-shrink: 0;
		font-size: 12px;
		font-family: ui-monospace, SFMono-Regular, monospace;
		padding: 4px 8px;
		border-radius: 6px;
		border: 1px solid var(--border-panel);
		color: var(--text-secondary);
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

	button:hover {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
	}

	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
		outline-offset: 2px;
	}

	.markdown-body {
		line-height: 1.8;
		overflow-wrap: anywhere;
		content-visibility: auto;
		contain-intrinsic-size: auto 600px;
	}

	.markdown-body :global([id]) {
		scroll-margin-top: 16px;
	}

	.markdown-body :global(a) {
		color: var(--tree-selected-text);
	}

	.markdown-body :global(pre) {
		overflow: auto;
		background: var(--pre-bg);
		padding: 16px;
		border: 1px solid var(--pre-border);
		border-radius: 8px;
	}

	.markdown-body :global(code) {
		font-size: 0.9em;
		color: var(--code-color);
	}

	.markdown-body :global(table) {
		display: block;
		overflow: auto;
		border-collapse: collapse;
	}

	.markdown-body :global(th),
	.markdown-body :global(td) {
		border: 1px solid var(--table-border);
		padding: 8px 12px;
	}

	.markdown-body :global(img),
	.markdown-body :global(svg) {
		max-width: 100%;
		height: auto;
	}

	.markdown-body :global(blockquote) {
		border-left: 3px solid var(--border-panel);
		margin-left: 0;
		padding-left: 16px;
		color: var(--text-muted);
	}
</style>
