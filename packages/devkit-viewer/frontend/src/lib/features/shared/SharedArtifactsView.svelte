<script lang="ts">
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';
	import MarkdownArticle from '../document/MarkdownArticle.svelte';
	import RawViewer from '../document/RawViewer.svelte';
	import { parseFrontmatterAndMarkdown } from '../document/document-parser';
	import type {
		RepositoryDataSource,
		SharedArtifactDetail,
		SharedArtifactMetadata
	} from '../../api/repository';

	let {
		source = null,
		repoId = '',
		initialSlug = '',
		diagramAction = undefined
	}: {
		source?: RepositoryDataSource | null;
		repoId?: string;
		initialSlug?: string;
		diagramAction?: (node: HTMLElement) => { destroy: () => void };
	} = $props();

	let artifacts = $state<SharedArtifactMetadata[]>([]);
	let selectedId = $state<string | null>(null);
	let selectedDetail = $state<SharedArtifactDetail | null>(null);
	let loading = $state(false);
	let detailLoading = $state(false);
	let detailError = $state<string | null>(null);
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	let kindFilter = $state('all');
	let rawMode = $state(false);
	let copiedUri = $state(false);
	let drawerOpen = $state(true);
	let copiedField = $state<string | null>(null);

	let kinds = $derived(['all', ...Array.from(new Set(artifacts.map((a) => a.kind)))]);

	let filteredArtifacts = $derived(
		artifacts.filter((item) => {
			if (kindFilter !== 'all' && item.kind !== kindFilter) return false;
			if (!searchQuery.trim()) return true;
			const q = searchQuery.toLowerCase().trim();
			return (
				item.slug.toLowerCase().includes(q) ||
				item.generation_id.toLowerCase().includes(q) ||
				item.source_sha.toLowerCase().includes(q)
			);
		})
	);

	let parsedDoc = $derived.by(() => {
		const text = selectedDetail?.content ?? '';
		if (!text) return { frontmatter: null, content: '' };
		try {
			return parseFrontmatterAndMarkdown(text);
		} catch {
			// Invalid frontmatter YAML: show the whole artifact as Markdown rather than failing the view.
			return { frontmatter: null, content: text };
		}
	});

	let renderedHtml = $derived(
		parsedDoc.content
			? DOMPurify.sanitize(marked.parse(parsedDoc.content, { async: false }) as string)
			: ''
	);

	let parsedFrontmatter = $derived(parsedDoc.frontmatter);

	function formatExpiry(expiresAt: string): { label: string; expired: boolean } {
		const diff = new Date(expiresAt).getTime() - Date.now();
		if (diff <= 0) return { label: 'Expired', expired: true };
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const days = Math.floor(hours / 24);
		if (days > 0) {
			const remHours = hours % 24;
			return { label: `${days}d ${remHours}h left`, expired: false };
		}
		if (hours > 0) return { label: `${hours}h left`, expired: false };
		const mins = Math.floor(diff / (1000 * 60));
		return { label: `${mins}m left`, expired: false };
	}

	function formatBytes(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		const kb = (bytes / 1024).toFixed(1);
		return `${kb} KB`;
	}

	async function copyToClipboard(text: string, fieldName = 'uri') {
		try {
			await navigator.clipboard.writeText(text);
			if (fieldName === 'uri') {
				copiedUri = true;
				setTimeout(() => {
					copiedUri = false;
				}, 2000);
			} else {
				copiedField = fieldName;
				setTimeout(() => {
					copiedField = null;
				}, 2000);
			}
		} catch (e) {
			console.error('Failed to copy', e);
		}
	}

	async function loadArtifacts() {
		if (!source?.sharedList) {
			artifacts = [];
			selectedId = null;
			selectedDetail = null;
			return;
		}
		loading = true;
		error = null;
		const controller = new AbortController();
		try {
			const res = await source.sharedList(controller.signal);
			artifacts = res.artifacts ?? [];
			if (artifacts.length > 0) {
				const matching = initialSlug
					? artifacts.find(
							(a) =>
								a.slug === initialSlug || a.slug.toLowerCase().includes(initialSlug.toLowerCase())
						)
					: null;
				if (matching) {
					selectedId = matching.generation_id;
				} else if (!selectedId || !artifacts.some((a) => a.generation_id === selectedId)) {
					selectedId = artifacts[0].generation_id;
				}
			} else {
				selectedId = null;
				selectedDetail = null;
			}
		} catch (e: any) {
			if (e.name !== 'AbortError') {
				error = e.message || 'Failed to load shared artifacts.';
			}
		} finally {
			loading = false;
		}
	}

	// Only the request for the current selection may change the detail; a superseded one is aborted and ignored.
	async function loadDetail(genId: string, signal: AbortSignal) {
		if (!source?.sharedBlob) {
			detailLoading = false;
			return;
		}
		selectedDetail = null;
		detailError = null;
		detailLoading = true;
		const current = () => !signal.aborted && genId === selectedId;
		try {
			const res = await source.sharedBlob(genId, signal);
			if (current()) selectedDetail = res;
		} catch (e: any) {
			if (current() && e.name !== 'AbortError') {
				console.error('Failed to load shared artifact detail', e);
				detailError = e.message || 'Failed to load the shared artifact.';
			}
		} finally {
			if (current()) detailLoading = false;
		}
	}

	$effect(() => {
		if (source) {
			loadArtifacts();
		}
	});

	$effect(() => {
		if (initialSlug && artifacts.length > 0) {
			const matching = artifacts.find(
				(a) => a.slug === initialSlug || a.slug.toLowerCase().includes(initialSlug.toLowerCase())
			);
			if (matching) {
				selectedId = matching.generation_id;
			}
		}
	});

	$effect(() => {
		const genId = selectedId;
		if (!genId) {
			selectedDetail = null;
			detailError = null;
			detailLoading = false;
			return;
		}
		const controller = new AbortController();
		loadDetail(genId, controller.signal);
		return () => controller.abort();
	});
</script>

<div class="shared-view">
	<aside class="shared-sidebar">
		<div class="sidebar-header">
			<div class="title-row">
				<h2>Shared Artifacts</h2>
				<button class="icon-btn" title="Refresh" onclick={loadArtifacts}>
					<span class="refresh-icon" class:spin={loading}>↻</span>
				</button>
			</div>
			<div class="search-box">
				<input
					type="search"
					placeholder="Search slug, SHA, ID..."
					bind:value={searchQuery}
					aria-label="Search shared artifacts"
				/>
			</div>
			{#if kinds.length > 2}
				<div class="kinds-filter">
					{#each kinds as k}
						<button
							class="kind-tab"
							class:active={kindFilter === k}
							onclick={() => {
								kindFilter = k;
							}}
						>
							{k === 'all' ? 'All' : k}
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<div class="artifact-list" role="list">
			{#if loading && artifacts.length === 0}
				<div class="empty-state">Loading artifacts...</div>
			{:else if error}
				<div class="error-state">{error}</div>
			{:else if filteredArtifacts.length === 0}
				<div class="empty-state">
					{#if artifacts.length === 0}
						No shared artifacts in repository.
					{:else}
						No matching artifacts found.
					{/if}
				</div>
			{:else}
				{#each filteredArtifacts as item (item.generation_id)}
					{@const expiry = formatExpiry(item.expires_at)}
					<button
						class="artifact-card"
						class:selected={selectedId === item.generation_id}
						onclick={() => {
							selectedId = item.generation_id;
						}}
					>
						<div class="card-top">
							<span class="kind-badge {item.kind}">{item.kind}</span>
							<span class="lang-badge">{item.language.toUpperCase()}</span>
						</div>
						<div class="card-slug" title={item.slug}>{item.slug}</div>
						<div class="card-meta">
							<span class="commit-sha" title={`Commit: ${item.source_sha}`}>
								{item.source_sha.slice(0, 7)}
							</span>
							<span class="expiry-tag" class:expired={expiry.expired}>
								{expiry.label}
							</span>
							<span class="bytes">{formatBytes(item.byte_count)}</span>
						</div>
					</button>
				{/each}
			{/if}
		</div>
	</aside>

	<section class="shared-content">
		{#if !selectedId || !selectedDetail}
			<div class="detail-empty">
				{#if detailLoading}
					<p>Loading artifact content...</p>
				{:else if detailError}
					<div class="error-state">{detailError}</div>
				{:else}
					<div class="guide-box">
						<h3>Shared Space</h3>
						<p>Safely view immutable artifacts shared across worktrees with a 7-day expiration.</p>
						<div class="guide-tip">
							<strong>💡 Tip:</strong> Select an artifact from the list on the left.
						</div>
					</div>
				{/if}
			</div>
		{:else}
			{@const meta = selectedDetail.metadata}
			{@const expiry = formatExpiry(meta.expires_at)}
			<header class="detail-header">
				<div class="detail-title-group">
					<div class="detail-title-row">
						<span class="kind-badge {meta.kind}">{meta.kind}</span>
						<h1>{meta.slug}</h1>
						<span
							class="expiry-tag-compact"
							class:expired={expiry.expired}
							title={`Expires: ${new Date(meta.expires_at).toLocaleString()}`}
						>
							{expiry.label}
						</span>
					</div>
				</div>

				<div class="detail-actions">
					{#if repoId}
						<a
							href={`/review/${encodeURIComponent(repoId)}/${encodeURIComponent(meta.generation_id)}`}
							target="_blank"
							rel="noopener noreferrer"
							class="action-btn"
							title="Open in new tab as standalone HTML page"
						>
							↗ Open in New Tab
						</a>
					{/if}
					<button
						class="action-btn"
						onclick={() =>
							copyToClipboard(meta.artifact_uri || `shared://${meta.generation_id}`, 'uri')}
						title="Copy Logical URI"
					>
						{copiedUri ? '✓ Copied' : 'Copy URI'}
					</button>
					<button
						class="action-btn"
						class:active={rawMode}
						onclick={() => {
							rawMode = !rawMode;
						}}
					>
						{rawMode ? 'Markdown View' : 'Raw View'}
					</button>
					<button
						class="action-btn drawer-toggle"
						class:active={drawerOpen}
						onclick={() => {
							drawerOpen = !drawerOpen;
						}}
						title={drawerOpen ? 'Close Metadata Drawer' : 'Open Metadata Drawer'}
					>
						<span class="btn-icon">ℹ️</span>
						<span>Metadata</span>
					</button>
				</div>
			</header>

			<div class="detail-main">
				<div class="detail-body">
					{#if detailLoading}
						<div class="loading-overlay">Loading content...</div>
					{:else if rawMode}
						<RawViewer content={selectedDetail.content} />
					{:else}
						<div class="article-wrapper">
							<MarkdownArticle html={renderedHtml} {diagramAction} />
						</div>
					{/if}
				</div>

				{#if drawerOpen}
					<aside class="meta-drawer" aria-label="Document Metadata">
						<div class="drawer-header">
							<h3>Document Metadata</h3>
							<button
								class="drawer-close-btn"
								onclick={() => {
									drawerOpen = false;
								}}
								title="Close Drawer"
								aria-label="Close Drawer"
							>
								✕
							</button>
						</div>

						<div class="drawer-content">
							<section class="drawer-section">
								<h4 class="section-title">Identification</h4>
								<div class="drawer-field">
									<span class="field-label">Kind</span>
									<span class="field-value">
										<span class="kind-badge {meta.kind}">{meta.kind}</span>
									</span>
								</div>
								<div class="drawer-field">
									<span class="field-label">Slug</span>
									<span class="field-value selectable-text">{meta.slug}</span>
								</div>
								<div class="drawer-field">
									<span class="field-label">Generation ID</span>
									<div class="copyable-row">
										<code class="code-val" title={meta.generation_id}>{meta.generation_id}</code>
										<button
											class="copy-icon-btn"
											onclick={() => copyToClipboard(meta.generation_id, 'gen')}
											title="Copy Generation ID"
										>
											{copiedField === 'gen' ? '✓' : '📋'}
										</button>
									</div>
								</div>
								<div class="drawer-field">
									<span class="field-label">Source Commit SHA</span>
									<div class="copyable-row">
										<code class="code-val" title={meta.source_sha}>{meta.source_sha}</code>
										<button
											class="copy-icon-btn"
											onclick={() => copyToClipboard(meta.source_sha, 'sha')}
											title="Copy Commit SHA"
										>
											{copiedField === 'sha' ? '✓' : '📋'}
										</button>
									</div>
								</div>
							</section>

							<section class="drawer-section">
								<h4 class="section-title">Lifecycle & Attributes</h4>
								<div class="drawer-field">
									<span class="field-label">Created At</span>
									<span class="field-value">{new Date(meta.created_at).toLocaleString()}</span>
								</div>
								<div class="drawer-field">
									<span class="field-label">Expires At</span>
									<div class="field-value-group">
										<span class="expiry-tag" class:expired={expiry.expired}>{expiry.label}</span>
										<span class="field-sub">{new Date(meta.expires_at).toLocaleString()}</span>
									</div>
								</div>
								<div class="drawer-field">
									<span class="field-label">Language</span>
									<span class="field-value">
										<span class="lang-badge">{meta.language.toUpperCase()}</span>
									</span>
								</div>
								<div class="drawer-field">
									<span class="field-label">Content Size</span>
									<span class="field-value"
										>{formatBytes(meta.byte_count)} ({meta.byte_count.toLocaleString()} bytes)</span
									>
								</div>
								<div class="drawer-field">
									<span class="field-label">Content Hash (SHA-256)</span>
									<div class="copyable-row">
										<code class="code-val" title={meta.content_sha256}>
											{meta.content_sha256.slice(0, 16)}...
										</code>
										<button
											class="copy-icon-btn"
											onclick={() => copyToClipboard(meta.content_sha256, 'hash')}
											title="Copy Full Hash"
										>
											{copiedField === 'hash' ? '✓' : '📋'}
										</button>
									</div>
								</div>
							</section>

							<section class="drawer-section">
								<h4 class="section-title">Shared Space URI</h4>
								<div class="drawer-field">
									<div class="copyable-row uri-box">
										<code class="code-val uri-code"
											>{meta.artifact_uri || `shared://${meta.generation_id}`}</code
										>
										<button
											class="copy-icon-btn"
											onclick={() =>
												copyToClipboard(
													meta.artifact_uri || `shared://${meta.generation_id}`,
													'drawer-uri'
												)}
											title="Copy URI"
										>
											{copiedField === 'drawer-uri' ? '✓' : '📋'}
										</button>
									</div>
								</div>
							</section>

							{#if parsedFrontmatter && Object.keys(parsedFrontmatter).length > 0}
								<section class="drawer-section">
									<h4 class="section-title">Document Frontmatter</h4>
									{#each Object.entries(parsedFrontmatter) as [key, value]}
										<div class="drawer-field">
											<span class="field-label">{key}</span>
											<span class="field-value selectable-text">
												{typeof value === 'object' ? JSON.stringify(value) : String(value)}
											</span>
										</div>
									{/each}
								</section>
							{/if}
						</div>
					</aside>
				{/if}
			</div>
		{/if}
	</section>
</div>

<style>
	.shared-view {
		display: flex;
		flex: 1;
		min-height: 0;
		height: 100%;
		width: 100%;
		overflow: hidden;
		background-color: var(--bg-viewport);
	}

	.shared-sidebar {
		width: 320px;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		height: 100%;
		min-height: 0;
		overflow: hidden;
		background-color: var(--bg-sidebar);
		border-right: 1px solid var(--border-sidebar);
	}

	.sidebar-header {
		padding: 14px 16px 10px;
		border-bottom: 1px solid var(--border-sidebar);
		display: flex;
		flex-direction: column;
		gap: 10px;
		flex-shrink: 0;
	}

	.title-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.title-row h2 {
		margin: 0;
		font-size: 15px;
		font-weight: 600;
		color: var(--text-primary);
	}

	.icon-btn {
		background: none;
		border: 1px solid transparent;
		color: var(--text-muted);
		border-radius: 4px;
		padding: 4px 6px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.icon-btn:hover {
		background-color: var(--bg-btn);
		color: var(--text-primary);
	}

	.refresh-icon {
		font-size: 14px;
		display: inline-block;
	}

	.refresh-icon.spin {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		100% {
			transform: rotate(360deg);
		}
	}

	.search-box input {
		width: 100%;
		box-sizing: border-box;
		background-color: var(--bg-input);
		border: 1px solid var(--border-input);
		color: var(--text-primary);
		padding: 6px 10px;
		border-radius: 6px;
		font-size: 13px;
	}

	.kinds-filter {
		display: flex;
		gap: 6px;
		overflow-x: auto;
		padding-bottom: 2px;
	}

	.kind-tab {
		background: none;
		border: 1px solid var(--border-btn);
		color: var(--text-muted);
		padding: 3px 8px;
		border-radius: 4px;
		font-size: 12px;
		cursor: pointer;
		white-space: nowrap;
	}

	.kind-tab.active {
		background-color: var(--bg-btn);
		color: var(--text-primary);
		font-weight: 600;
	}

	.artifact-list {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
		padding: 8px;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.artifact-card {
		background: none;
		border: 1px solid transparent;
		border-radius: 6px;
		padding: 10px 12px;
		text-align: left;
		cursor: pointer;
		transition: background-color 0.15s ease;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.artifact-card:hover {
		background-color: var(--tree-hover-bg);
	}

	.artifact-card.selected {
		background-color: var(--tree-selected-bg);
		border-color: var(--tree-selected-text);
	}

	.card-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.kind-badge {
		font-size: 11px;
		padding: 2px 6px;
		border-radius: 4px;
		font-weight: 600;
		text-transform: uppercase;
		background-color: var(--bg-btn);
		color: var(--text-btn);
	}

	.lang-badge {
		font-size: 10px;
		padding: 1px 4px;
		border-radius: 3px;
		background-color: var(--badge-bg);
		color: var(--badge-text);
		font-weight: 700;
	}

	.card-slug {
		font-size: 13px;
		font-weight: 600;
		color: var(--text-primary);
		word-break: break-all;
	}

	.card-meta {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 11px;
		color: var(--text-dim);
	}

	.commit-sha {
		font-family: ui-monospace, SFMono-Regular, monospace;
		background-color: var(--code-bg);
		color: var(--code-color);
		padding: 1px 4px;
		border-radius: 3px;
	}

	.expiry-tag {
		font-size: 11px;
	}

	.expiry-tag.expired {
		color: #ef4444;
	}

	.expiry-tag-compact {
		font-size: 11px;
		padding: 2px 8px;
		border-radius: 4px;
		background-color: var(--badge-bg);
		color: var(--text-muted);
		border: 1px solid var(--border-panel);
	}

	.expiry-tag-compact.expired {
		color: #ef4444;
		border-color: #ef4444;
	}

	.empty-state,
	.error-state {
		padding: 24px 16px;
		text-align: center;
		font-size: 13px;
		color: var(--text-muted);
	}

	.error-state {
		color: #ef4444;
	}

	.shared-content {
		flex: 1;
		min-width: 0;
		min-height: 0;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		background-color: var(--bg-viewport);
	}

	.detail-empty {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 32px;
		color: var(--text-muted);
	}

	.guide-box {
		max-width: 520px;
		padding: 24px;
		border-radius: 8px;
		border: 1px solid var(--border-panel);
		background-color: var(--bg-panel);
		text-align: center;
	}

	.guide-box h3 {
		margin-top: 0;
		color: var(--text-primary);
		font-size: 18px;
	}

	.guide-box p {
		line-height: 1.6;
		margin-bottom: 16px;
	}

	.guide-tip {
		font-size: 13px;
		color: var(--text-dim);
	}

	.detail-header {
		padding: 14px 24px;
		border-bottom: 1px solid var(--border-panel);
		background-color: var(--bg-panel);
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 16px;
		flex-wrap: wrap;
		flex-shrink: 0;
	}

	.detail-title-group {
		display: flex;
		align-items: center;
		gap: 8px;
		min-width: 0;
	}

	.detail-title-row {
		display: flex;
		align-items: center;
		gap: 10px;
		flex-wrap: wrap;
	}

	.detail-title-row h1 {
		margin: 0;
		font-size: 18px;
		font-weight: 700;
		color: var(--text-primary);
		word-break: break-all;
	}

	.detail-actions {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
	}

	.action-btn {
		background-color: var(--bg-btn);
		border: 1px solid var(--border-btn);
		color: var(--text-btn);
		padding: 6px 12px;
		border-radius: 6px;
		font-size: 13px;
		cursor: pointer;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 5px;
		font-weight: 500;
	}

	.action-btn:hover {
		background-color: var(--btn-hover-bg);
		color: var(--text-primary);
	}

	.action-btn.active {
		background-color: var(--tree-selected-bg);
		border-color: var(--tree-selected-text);
		color: var(--tree-selected-text);
	}

	.btn-icon {
		font-size: 12px;
	}

	.detail-main {
		flex: 1;
		min-height: 0;
		height: 100%;
		display: flex;
		overflow: hidden;
	}

	.detail-body {
		flex: 1;
		min-height: 0;
		min-width: 0;
		overflow-y: auto;
		padding: 24px 32px 80px;
		scroll-behavior: smooth;
	}

	.article-wrapper {
		max-width: 860px;
		margin: 0 auto;
	}

	.loading-overlay {
		padding: 32px;
		text-align: center;
		color: var(--text-muted);
	}

	/* Right Drawer Styles */
	.meta-drawer {
		width: 330px;
		flex-shrink: 0;
		border-left: 1px solid var(--border-panel);
		background-color: var(--bg-panel);
		display: flex;
		flex-direction: column;
		height: 100%;
		min-height: 0;
		overflow: hidden;
		box-sizing: border-box;
	}

	.drawer-header {
		padding: 14px 18px;
		border-bottom: 1px solid var(--border-panel);
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-shrink: 0;
	}

	.drawer-header h3 {
		margin: 0;
		font-size: 14px;
		font-weight: 600;
		color: var(--text-primary);
	}

	.drawer-close-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		font-size: 14px;
		cursor: pointer;
		padding: 4px;
		border-radius: 4px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.drawer-close-btn:hover {
		background-color: var(--bg-btn);
		color: var(--text-primary);
	}

	.drawer-content {
		flex: 1;
		overflow-y: auto;
		padding: 16px 18px 40px;
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.drawer-section {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.section-title {
		margin: 0;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-dim);
		border-bottom: 1px solid var(--border-sidebar);
		padding-bottom: 4px;
	}

	.drawer-field {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.field-label {
		font-size: 11px;
		color: var(--text-muted);
		font-weight: 500;
	}

	.field-value {
		font-size: 13px;
		color: var(--text-secondary);
		word-break: break-all;
	}

	.field-value.selectable-text {
		font-weight: 600;
		color: var(--text-primary);
	}

	.field-value-group {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.field-sub {
		font-size: 11px;
		color: var(--text-dim);
	}

	.copyable-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 6px;
		background-color: var(--bg-viewport);
		border: 1px solid var(--border-panel);
		border-radius: 5px;
		padding: 4px 8px;
	}

	.code-val {
		font-family: ui-monospace, SFMono-Regular, monospace;
		font-size: 12px;
		color: var(--code-color);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		flex: 1;
	}

	.uri-box {
		padding: 6px 8px;
	}

	.uri-code {
		white-space: normal;
		word-break: break-all;
		font-size: 11px;
	}

	.copy-icon-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		font-size: 12px;
		padding: 2px 4px;
		border-radius: 3px;
		flex-shrink: 0;
	}

	.copy-icon-btn:hover {
		background-color: var(--bg-btn);
		color: var(--text-primary);
	}
</style>
