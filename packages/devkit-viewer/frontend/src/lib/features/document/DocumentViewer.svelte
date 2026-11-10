<script lang="ts">
	import FrontmatterHeader from './FrontmatterHeader.svelte';
	import SupersessionSummary from './SupersessionSummary.svelte';
	import type { RepositoryDocument } from '../../api/documents';
	import MarkdownArticle from './MarkdownArticle.svelte';
	import RawViewer from './RawViewer.svelte';
	import EmptyPlaceholder from './EmptyPlaceholder.svelte';
	import type { Frontmatter } from './document-parser';

	let {
		currentBlob = null,
		loading = false,
		error = null,
		rawMode = false,
		theme = 'dark',
		diagramAction = undefined,
		relationSubject = null,
		relationDocuments = [],
		relationLoading = false,
		relationErrors = [],
		onRelationOpen = () => {},
		onReloadRelations = () => {}
	}: {
		currentBlob?: {
			path: string;
			content: string;
			frontmatter: Frontmatter | null;
			html: string;
		} | null;
		loading?: boolean;
		error?: string | null;
		rawMode?: boolean;
		theme?: 'dark' | 'light';
		diagramAction?: (node: HTMLElement) => { destroy: () => void };
		relationSubject?: RepositoryDocument | null;
		relationDocuments?: RepositoryDocument[];
		relationLoading?: boolean;
		relationErrors?: string[];
		onRelationOpen?: (path: string) => void;
		onReloadRelations?: () => void;
	} = $props();
</script>

<main class="content-viewport">
	{#if error}
		<div class="error-banner">
			<span class="error-icon">⚠️</span>
			<span>{error}</span>
		</div>
	{/if}

	{#if loading && !currentBlob}
		<div class="loading-placeholder">
			<div class="spinner"></div>
			<p>Fetching content...</p>
		</div>
	{:else if currentBlob}
		<div class="document-container">
			{#if currentBlob.frontmatter}
				<FrontmatterHeader frontmatter={currentBlob.frontmatter} />
			{/if}

			{#if rawMode}
				<RawViewer content={currentBlob.content} />
			{:else}
				{#if relationSubject}<SupersessionSummary
						subject={relationSubject}
						documents={relationDocuments}
						loading={relationLoading}
						errors={relationErrors}
						onOpen={onRelationOpen}
						onReload={onReloadRelations}
					/>{/if}
				{#key `${currentBlob.path}-${theme}`}
					<MarkdownArticle html={currentBlob.html} {diagramAction} />
				{/key}
			{/if}
		</div>
	{:else}
		<EmptyPlaceholder />
	{/if}
</main>

<style>
	.content-viewport {
		flex: 1;
		min-height: 0;
		height: 100%;
		overflow-y: auto;
		background-color: var(--bg-viewport);
		padding: 24px 32px 80px;
		position: relative;
	}

	.error-banner {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 10px 14px;
		background-color: #7f1d1d;
		border: 1px solid #b91c1c;
		border-radius: 6px;
		color: #fecaca;
		font-size: 13px;
		margin-bottom: 20px;
	}

	.loading-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 300px;
		color: var(--text-muted);
	}

	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid var(--border-btn);
		border-top-color: #6366f1;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin-bottom: 12px;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.document-container {
		max-width: 900px;
		margin: 0 auto;
	}
</style>
