<script lang="ts">
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';
	import MarkdownArticle from '../document/MarkdownArticle.svelte';
	import RawViewer from '../document/RawViewer.svelte';
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
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	let kindFilter = $state('all');
	let rawMode = $state(false);
	let copiedUri = $state(false);

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

	let renderedHtml = $derived(
		selectedDetail?.content
			? DOMPurify.sanitize(marked.parse(selectedDetail.content, { async: false }) as string)
			: ''
	);

	function formatExpiry(expiresAt: string): { label: string; expired: boolean } {
		const diff = new Date(expiresAt).getTime() - Date.now();
		if (diff <= 0) return { label: '만료됨', expired: true };
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const days = Math.floor(hours / 24);
		if (days > 0) {
			const remHours = hours % 24;
			return { label: `${days}일 ${remHours}시간 남음`, expired: false };
		}
		if (hours > 0) return { label: `${hours}시간 남음`, expired: false };
		const mins = Math.floor(diff / (1000 * 60));
		return { label: `${mins}분 남음`, expired: false };
	}

	function formatBytes(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		const kb = (bytes / 1024).toFixed(1);
		return `${kb} KB`;
	}

	async function copyToClipboard(text: string) {
		try {
			await navigator.clipboard.writeText(text);
			copiedUri = true;
			setTimeout(() => {
				copiedUri = false;
			}, 2000);
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
				error = e.message || '공유 아티팩트 목록을 불러오지 못했습니다.';
			}
		} finally {
			loading = false;
		}
	}

	async function loadDetail(genId: string) {
		if (!source?.sharedBlob) return;
		detailLoading = true;
		const controller = new AbortController();
		try {
			const res = await source.sharedBlob(genId, controller.signal);
			selectedDetail = res;
		} catch (e: any) {
			if (e.name !== 'AbortError') {
				console.error('Failed to load shared artifact detail', e);
			}
		} finally {
			detailLoading = false;
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
		if (selectedId) {
			loadDetail(selectedId);
		} else {
			selectedDetail = null;
		}
	});
</script>

<div class="shared-view">
	<aside class="shared-sidebar">
		<div class="sidebar-header">
			<div class="title-row">
				<h2>공유 아티팩트</h2>
				<button class="icon-btn" title="새로고침" onclick={loadArtifacts}>
					<span class="refresh-icon" class:spin={loading}>↻</span>
				</button>
			</div>
			<div class="search-box">
				<input
					type="search"
					placeholder="슬러그, SHA, ID 검색..."
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
							{k === 'all' ? '전체' : k}
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<div class="artifact-list" role="list">
			{#if loading && artifacts.length === 0}
				<div class="empty-state">아티팩트를 조회하는 중...</div>
			{:else if error}
				<div class="error-state">{error}</div>
			{:else if filteredArtifacts.length === 0}
				<div class="empty-state">
					{#if artifacts.length === 0}
						저장소에 공유된 아티팩트가 없습니다.
					{:else}
						검색 조건에 맞는 아티팩트가 없습니다.
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
					<p>아티팩트 내용을 불러오는 중...</p>
				{:else}
					<div class="guide-box">
						<h3>공유 공간 (Shared Space)</h3>
						<p>
							작업 트리 간에 협업 중 생성된 7일 만료의 불변 아티팩트(예: proposal-review 리포트)를
							안전하게 공유하고 조회할 수 있습니다.
						</p>
						<div class="guide-tip">
							<strong>💡 안내:</strong> 좌측 목록에서 열람할 아티팩트를 선택하세요.
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
					</div>
					<div class="meta-pills">
						<span class="pill" title="Source commit">
							<strong>Commit:</strong> <code>{meta.source_sha}</code>
						</span>
						<span class="pill" title="Generation ID">
							<strong>Generation:</strong> <code>{meta.generation_id}</code>
						</span>
						<span class="pill" title="Created date">
							<strong>생성:</strong>
							{new Date(meta.created_at).toLocaleString()}
						</span>
						<span class="pill" class:expired={expiry.expired} title="Expiration">
							<strong>만료:</strong>
							{expiry.label}
						</span>
						<span class="pill">
							<strong>크기:</strong>
							{formatBytes(meta.byte_count)}
						</span>
						<span class="pill">
							<strong>언어:</strong>
							{meta.language.toUpperCase()}
						</span>
					</div>
				</div>

				<div class="detail-actions">
					{#if repoId}
						<a
							href={`/review/${repoId}/${meta.generation_id}`}
							target="_blank"
							rel="noopener noreferrer"
							class="action-btn"
							title="독립 HTML 페이지로 새 탭에서 열기"
						>
							↗ 새 탭에서 열기
						</a>
					{/if}
					<button
						class="action-btn"
						onclick={() => copyToClipboard(meta.artifact_uri || `shared://${meta.generation_id}`)}
						title="Logical URI 복사"
					>
						{copiedUri ? '✓ 복사됨' : 'URI 복사'}
					</button>
					<button
						class="action-btn"
						class:active={rawMode}
						onclick={() => {
							rawMode = !rawMode;
						}}
					>
						{rawMode ? 'Markdown 뷰' : 'Raw 보기'}
					</button>
				</div>
			</header>

			<div class="detail-body">
				{#if detailLoading}
					<div class="loading-overlay">내용을 읽는 중...</div>
				{:else if rawMode}
					<RawViewer content={selectedDetail.content} />
				{:else}
					<div class="article-wrapper">
						<MarkdownArticle html={renderedHtml} {diagramAction} />
					</div>
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
		width: 100%;
		background-color: var(--bg-viewport);
	}

	.shared-sidebar {
		width: 340px;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		background-color: var(--bg-sidebar);
		border-right: 1px solid var(--border-sidebar);
		overflow: hidden;
	}

	.sidebar-header {
		padding: 14px 16px 10px;
		border-bottom: 1px solid var(--border-sidebar);
		display: flex;
		flex-direction: column;
		gap: 10px;
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

	.kind-badge.proposal-review {
		background-color: rgba(99, 102, 241, 0.15);
		color: #818cf8;
		border: 1px solid rgba(99, 102, 241, 0.3);
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

	.expiry-tag.expired {
		color: #ef4444;
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
		padding: 18px 24px;
		border-bottom: 1px solid var(--border-panel);
		background-color: var(--bg-panel);
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		flex-wrap: wrap;
	}

	.detail-title-group {
		display: flex;
		flex-direction: column;
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
		font-size: 20px;
		font-weight: 700;
		color: var(--text-primary);
		word-break: break-all;
	}

	.meta-pills {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		font-size: 12px;
	}

	.pill {
		background-color: var(--bg-viewport);
		border: 1px solid var(--border-panel);
		padding: 2px 8px;
		border-radius: 4px;
		color: var(--text-secondary);
		display: inline-flex;
		align-items: center;
		gap: 4px;
	}

	.pill code {
		font-family: ui-monospace, SFMono-Regular, monospace;
		color: var(--code-color);
	}

	.pill.expired {
		color: #ef4444;
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
		gap: 4px;
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

	.detail-body {
		flex: 1;
		overflow-y: auto;
		padding: 24px 32px;
		min-height: 0;
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
</style>
