<script lang="ts">
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';
	import type { Snippet } from 'svelte';

	import KnowledgeViews from './KnowledgeViews.svelte';
	import RoadmapView from './RoadmapView.svelte';
	import SharedArtifactsView from './features/shared/SharedArtifactsView.svelte';
	import DashboardView from './features/dashboard/DashboardView.svelte';
	import ViewerHeader from './components/shared/ViewerHeader.svelte';
	import NavigationRail from './components/shared/NavigationRail.svelte';
	import FileExplorer from './features/explorer/FileExplorer.svelte';
	import DocumentViewer from './features/document/DocumentViewer.svelte';
	import FullscreenDiagramModal from './features/diagrams/FullscreenDiagramModal.svelte';
	import { createDiagramRenderer } from './features/diagrams/mermaid';
	import {
		parseFrontmatterAndMarkdown,
		type Frontmatter
	} from './features/document/document-parser';
	import { ThemeState } from './state/theme.svelte';
	import {
		httpDataSource,
		normalizeTree,
		type TreeItem,
		type RepositoryDataSource,
		type RepositoryInfo
	} from './api/repository';

	let {
		repoId = '',
		apiBase = '',
		branch = 'main',
		initialPath = 'docs/',
		initialView = 'files',
		initialAnchor = '',
		theme = 'dark',
		dataSource = undefined,
		onselectpath = undefined,
		picker = undefined
	}: {
		repoId?: string;
		apiBase?: string;
		branch?: string;
		initialPath?: string;
		initialView?: string;
		initialAnchor?: string;
		theme?: string;
		dataSource?: RepositoryDataSource;
		onselectpath?: (path: string) => void;
		picker?: Snippet;
	} = $props();

	const themeState = new ThemeState();

	$effect(() => {
		themeState.sync(theme);
	});

	$effect(() => {
		if (hostEl) {
			hostEl.setAttribute('data-theme', themeState.current);
		}
	});

	let view = $state<'dashboard' | 'files' | 'book' | 'proposals' | 'specs' | 'roadmap' | 'shared'>(
		'dashboard'
	);
	let currentPath = $state('docs/');
	let selectedSharedSlug = $state('');

	$effect(() => {
		view = ['dashboard', 'book', 'proposals', 'specs', 'roadmap', 'shared'].includes(initialView)
			? (initialView as typeof view)
			: 'dashboard';
	});

	let treeItems = $state<TreeItem[]>([]);
	let currentBlob = $state<{
		path: string;
		content: string;
		frontmatter: Frontmatter | null;
		html: string;
	} | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let rawMode = $state(false);
	let hostEl: HTMLElement | null = null;
	let generation = 0;
	let repoInfo = $state<RepositoryInfo | null>(null);
	let fullscreenSvg = $state<string | null>(null);

	function openFullscreen(svg: string) {
		fullscreenSvg = svg;
	}

	function closeFullscreen() {
		fullscreenSvg = null;
	}

	const source = $derived(dataSource ?? (apiBase ? httpDataSource(apiBase) : null));

	$effect(() => {
		const repository = source;
		const controller = new AbortController();
		repoInfo = null;
		if (repository) {
			void repository
				.info(controller.signal)
				.then((info: any) => {
					if (!controller.signal.aborted) repoInfo = info;
				})
				.catch((err: any) => {
					if (!controller.signal.aborted)
						error = `Failed to load repository info: ${err?.message ?? err}`;
				});
		}
		return () => controller.abort();
	});

	$effect(() => {
		currentPath = initialPath;
	});

	// Only the current request may publish state or events.
	$effect(() => {
		const path = currentPath;
		const repository = source;
		const ref = branch;
		const id = ++generation;
		const controller = new AbortController();
		if (repository && view === 'files') {
			if (path.endsWith('/') || path === '') {
				void loadTree(path, repository, ref, id, controller.signal);
			} else {
				void loadBlob(path, repository, ref, id, controller.signal);
			}
		}
		return () => controller.abort();
	});

	async function loadTree(
		path: string,
		repository: RepositoryDataSource,
		ref: string,
		id: number,
		signal: AbortSignal
	) {
		loading = true;
		error = null;
		currentBlob = null;
		try {
			const cleanPath = path.replace(/\/+$/, '');
			const data = await repository.tree(cleanPath, ref, signal);
			if (id !== generation || signal.aborted) return;
			treeItems = normalizeTree(data);
			dispatchPathChange(path);
		} catch (err: any) {
			if (id !== generation || signal.aborted) return;
			error = `Failed to load tree (${path}): ${err.message}`;
		} finally {
			if (id === generation) loading = false;
		}
	}

	async function loadBlob(
		path: string,
		repository: RepositoryDataSource,
		ref: string,
		id: number,
		signal: AbortSignal
	) {
		loading = true;
		error = null;
		currentBlob = null;
		try {
			const data = await repository.blob(path, ref, signal);
			const parent = path.split('/').slice(0, -1).join('/');
			const siblings = await repository.tree(parent, ref, signal);
			if (id !== generation || signal.aborted) return;
			treeItems = normalizeTree(siblings);
			let rawContent: string;
			if (data.encoding === 'base64') {
				rawContent = new TextDecoder('utf-8', { fatal: true }).decode(
					Uint8Array.from(atob(data.content.replace(/\s/g, '')), (c) => c.charCodeAt(0))
				);
			} else if (data.encoding === 'utf-8') {
				rawContent = data.content;
			} else {
				throw new Error(`Unsupported encoding: ${data.encoding}`);
			}
			const { frontmatter, content } = parseFrontmatterAndMarkdown(rawContent);
			const parsedHtml = DOMPurify.sanitize(
				marked.parse(content, { gfm: true, breaks: true }) as string,
				{ USE_PROFILES: { html: true } }
			);
			currentBlob = {
				path,
				content: rawContent,
				frontmatter,
				html: parsedHtml
			};
			dispatchPathChange(path);
			dispatchItemSelected(path, frontmatter);
		} catch (err: any) {
			if (id !== generation || signal.aborted) return;
			error = `Failed to load file (${path}): ${err.message}`;
		} finally {
			if (id === generation) loading = false;
		}
	}

	function dispatchPathChange(path: string) {
		const event = new CustomEvent('sdd:path-change', {
			detail: { path, repoId, branch },
			bubbles: true,
			composed: true
		});
		hostEl?.dispatchEvent(event);
	}

	function dispatchItemSelected(path: string, frontmatter: Frontmatter | null) {
		onselectpath?.(path);
		const event = new CustomEvent('sdd:item-selected', {
			detail: { path, frontmatter, repoId, branch },
			bubbles: true,
			composed: true
		});
		hostEl?.dispatchEvent(event);
	}

	const diagramRenderer = $derived(
		createDiagramRenderer(
			() => themeState.current,
			openFullscreen,
			(msg) => {
				error = msg;
			}
		)
	);

	function navigateTo(path: string, isTree: boolean) {
		currentPath = isTree ? (path.endsWith('/') ? path : path + '/') : path;
	}

	function navigateParent() {
		const parts = currentPath.replace(/\/+$/, '').split('/');
		if (parts.length > 1) {
			parts.pop();
			currentPath = parts.join('/') + '/';
		} else {
			currentPath = '';
		}
	}

	const breadcrumbs = $derived(currentPath ? currentPath.split('/').filter(Boolean) : []);
</script>

<div class="sdd-viewer-root" class:theme-light={themeState.current === 'light'} bind:this={hostEl}>
	<ViewerHeader
		{repoId}
		{repoInfo}
		{branch}
		{view}
		{breadcrumbs}
		{currentPath}
		hasCurrentBlob={Boolean(currentBlob)}
		bind:rawMode
		theme={themeState.current}
		{picker}
		onnavigate={navigateTo}
		ontoggletheme={() => themeState.toggle()}
	/>

	<div class="viewer-body">
		<NavigationRail bind:view />

		<div class="view-stage">
			{#if view === 'dashboard'}
				<div class="knowledge-host">
					<DashboardView
						{source}
						{branch}
						{repoId}
						onNavigate={(targetView, targetPath) => {
							if (targetPath) currentPath = targetPath;
							view = targetView;
						}}
					/>
				</div>
			{:else if view === 'roadmap'}
				<div class="knowledge-host">
					<RoadmapView
						{source}
						{branch}
						onOpen={(path) => {
							currentPath = path;
							view = 'files';
						}}
					/>
				</div>
			{:else if view === 'shared'}
				<div class="knowledge-host">
					<SharedArtifactsView
						{source}
						{repoId}
						initialSlug={selectedSharedSlug}
						diagramAction={diagramRenderer}
					/>
				</div>
			{:else if view !== 'files'}
				<div class="knowledge-host">
					<KnowledgeViews
						{view}
						{source}
						{branch}
						theme={themeState.current}
						requestedPath={initialPath}
						requestedAnchor={initialAnchor}
						diagrams={diagramRenderer}
						onOpen={(path) => {
							currentPath = path;
							view = 'files';
						}}
						onLocation={(path, anchor, selectedView, frontmatter) => {
							dispatchItemSelected(path, frontmatter);
							hostEl?.dispatchEvent(
								new CustomEvent('sdd:path-change', {
									detail: { path, anchor, view: selectedView, repoId, branch },
									bubbles: true,
									composed: true
								})
							);
						}}
					/>
				</div>
			{/if}

			<div class="viewer-layout" class:hidden={view !== 'files'}>
				<FileExplorer
					{treeItems}
					{currentPath}
					currentBlobPath={currentBlob?.path ?? ''}
					{loading}
					onnavigate={navigateTo}
					onparent={navigateParent}
				/>
				<DocumentViewer
					{currentBlob}
					{loading}
					{error}
					{rawMode}
					theme={themeState.current}
					diagramAction={diagramRenderer}
				/>
			</div>
		</div>
	</div>

	{#if fullscreenSvg}
		<FullscreenDiagramModal svg={fullscreenSvg} onclose={closeFullscreen} />
	{/if}
</div>

<style>
	*,
	*::before,
	*::after {
		box-sizing: border-box;
	}

	.sdd-viewer-root {
		--bg-header: #1e293b;
		--border-header: #334155;
		--bg-sidebar: #111827;
		--border-sidebar: #1f2937;
		--bg-viewport: #0b0f17;
		--bg-panel: #111827;
		--border-panel: #1f2937;
		--text-primary: #f8fafc;
		--text-secondary: #d1d5db;
		--text-muted: #94a3b8;
		--text-dim: #6b7280;
		--bg-input: #1f2937;
		--border-input: #374151;
		--bg-btn: #334155;
		--border-btn: #475569;
		--text-btn: #e2e8f0;
		--btn-hover-bg: #475569;
		--tree-hover-bg: #1f2937;
		--tree-selected-bg: #1e1b4b;
		--tree-selected-text: #818cf8;
		--code-bg: #1e293b;
		--code-color: #38bdf8;
		--pre-bg: #111827;
		--pre-border: #1f2937;
		--pre-text: #e5e7eb;
		--table-border: #374151;
		--th-bg: #1f2937;
		--th-text: #f9fafb;
		--badge-bg: #1f2937;
		--badge-text: #9ca3af;
		--branch-bg: #334155;
		--branch-text: #94a3b8;

		display: flex;
		flex-direction: column;
		height: 100%;
		width: 100%;
		background-color: var(--bg-viewport);
		color: var(--text-secondary);
	}

	.sdd-viewer-root.theme-light {
		--bg-header: #ffffff;
		--border-header: #e2e8f0;
		--bg-sidebar: #f8fafc;
		--border-sidebar: #e2e8f0;
		--bg-viewport: #ffffff;
		--bg-panel: #f8fafc;
		--border-panel: #e2e8f0;
		--text-primary: #0f172a;
		--text-secondary: #334155;
		--text-muted: #64748b;
		--text-dim: #94a3b8;
		--bg-input: #ffffff;
		--border-input: #cbd5e1;
		--bg-btn: #f1f5f9;
		--border-btn: #cbd5e1;
		--text-btn: #334155;
		--btn-hover-bg: #e2e8f0;
		--tree-hover-bg: #f1f5f9;
		--tree-selected-bg: #e0e7ff;
		--tree-selected-text: #4338ca;
		--code-bg: #f1f5f9;
		--code-color: #0284c7;
		--pre-bg: #f8fafc;
		--pre-border: #e2e8f0;
		--pre-text: #1e293b;
		--table-border: #e2e8f0;
		--th-bg: #f1f5f9;
		--th-text: #0f172a;
		--badge-bg: #f1f5f9;
		--badge-text: #475569;
		--branch-bg: #f1f5f9;
		--branch-text: #475569;
	}

	.viewer-body {
		display: flex;
		flex: 1;
		min-height: 0;
		height: 100%;
		overflow: hidden;
	}

	.view-stage {
		flex: 1;
		min-width: 0;
		min-height: 0;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.knowledge-host {
		flex: 1;
		min-height: 0;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.viewer-layout {
		display: flex;
		flex: 1;
		min-height: 0;
		height: 100%;
		overflow: hidden;
	}

	.viewer-layout.hidden {
		display: none;
	}
</style>
