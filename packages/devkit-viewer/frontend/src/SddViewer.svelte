<script lang="ts">
	import SupportingArtifact from './features/document/SupportingArtifact.svelte';
	import { hasFormalContext, isArtifactPath } from './api/identity';
	import {
		indexDocuments,
		parseBlob,
		renderDocument,
		documentAnchor,
		type DocumentIndex
	} from './api/documents';
	import { clearRepositoryCache } from './api/cache';
	import { isDecision } from './features/document/supersession';
	import { tick, untrack, type Snippet } from 'svelte';

	import KnowledgeViews from './features/knowledge/KnowledgeViews.svelte';
	import RoadmapView from './features/roadmap/RoadmapView.svelte';
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
		normalizeTree,
		type TreeItem,
		type RepositoryDataSource,
		type RepositoryInfo
	} from './api/repository';

	let {
		repoId = '',
		branch = 'main',
		theme = 'dark',
		dataSource,
		picker = undefined
	}: {
		repoId?: string;
		branch?: string;
		theme?: string;
		dataSource: RepositoryDataSource;
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

	// The page opens on the Dashboard; `book` is the Read tab.
	type ViewerView = 'dashboard' | 'files' | 'book' | 'proposals' | 'specs' | 'roadmap';
	let view = $state<ViewerView>('dashboard');
	let currentPath = $state('docs/');

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
	let fileAnchor = $state('');
	let hostEl: HTMLElement | null = null;
	let generation = 0;
	let repoInfo = $state<RepositoryInfo | null>(null);
	let fullscreenSvg = $state<string | null>(null);

	let fileSupport = $state<{
		path: string;
		parent: string;
		fragment: string;
		scroll?: number;
	} | null>(null);
	let relationIndex = $state<DocumentIndex>({ documents: [], errors: [] });
	let relationLoading = $state(false);
	let relationReload = $state(0);
	const relationSubject = $derived(
		currentBlob ? parseBlob(currentBlob.path, currentBlob.content, 'utf-8') : null
	);
	$effect(() => {
		const repository = source,
			currentBranch = branch,
			subject = relationSubject;
		const wanted =
			view === 'files' &&
			!rawMode &&
			!currentBlob?.path.startsWith('handbook/') &&
			(isDecision(subject) || hasFormalContext(subject));
		relationReload;
		const controller = new AbortController();
		relationIndex = { documents: [], errors: [] };
		relationLoading = Boolean(repository && wanted);
		if (repository && wanted)
			void indexDocuments(repository, currentBranch, controller.signal)
				.then((result) => {
					if (!controller.signal.aborted) {
						relationIndex = result;
						relationLoading = false;
					}
				})
				.catch((error: unknown) => {
					if (!controller.signal.aborted) {
						relationIndex = { documents: [], errors: [String(error)] };
						relationLoading = false;
					}
				});
		return () => controller.abort();
	});
	function reloadRelations() {
		if (source) clearRepositoryCache(source);
		relationReload++;
	}

	function openFullscreen(svg: string) {
		fullscreenSvg = svg;
	}

	function closeFullscreen() {
		fullscreenSvg = null;
	}

	const source = $derived(dataSource);

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

	// The document a Dashboard card opens; it applies to its own tab only.
	let knowledgeRequest = $state<{ path: string; anchor: string; view?: string }>({
		path: '',
		anchor: ''
	});
	// The Living Spec book is computed only on request; the request lives as long as this viewer, survives rail
	// switches and holds only for the source and branch it was made for, so a switch drops it in the same update,
	// before any view could index the new branch.
	let bookRequest = $state.raw<{ source: RepositoryDataSource; branch: string } | null>(null);
	const bookRequested = $derived(bookRequest?.source === source && bookRequest?.branch === branch);
	const setBookRequested = (requested: boolean) => {
		bookRequest = requested ? { source, branch } : null;
	};
	const requestFor = (current: string) =>
		!knowledgeRequest.view || knowledgeRequest.view === current
			? knowledgeRequest
			: { path: '', anchor: '' };

	// Only the current request may publish state.
	$effect(() => {
		const path = currentPath;
		const repository = source;
		branch;
		const id = ++generation;
		const controller = new AbortController();
		fileSupport = null;
		if (repository && view === 'files') {
			if (path.endsWith('/') || path === '') {
				void loadTree(path, repository, id, controller.signal);
			} else if (!/\.(?:md|markdown)$/i.test(path) || isArtifactPath(path)) {
				currentBlob = null;
				error = null;
				loading = false;
				fileSupport = { path, parent: '', fragment: untrack(() => fileAnchor) };
				void repository
					.tree(path.split('/').slice(0, -1).join('/'), controller.signal)
					.then((data) => {
						if (id === generation && !controller.signal.aborted) treeItems = normalizeTree(data);
					})
					.catch(() => {});
			} else {
				void loadBlob(path, repository, id, controller.signal);
			}
		}
		return () => controller.abort();
	});

	async function loadTree(
		path: string,
		repository: RepositoryDataSource,
		id: number,
		signal: AbortSignal
	) {
		loading = true;
		error = null;
		currentBlob = null;
		try {
			const cleanPath = path.replace(/\/+$/, '');
			const data = await repository.tree(cleanPath, signal);
			if (id !== generation || signal.aborted) return;
			treeItems = normalizeTree(data);
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
		id: number,
		signal: AbortSignal
	) {
		loading = true;
		error = null;
		currentBlob = null;
		try {
			const data = await repository.blob(path, signal);
			const parent = path.split('/').slice(0, -1).join('/');
			const siblings = await repository.tree(parent, signal);
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
			const parsedHtml = renderDocument(parseBlob(path, rawContent, 'utf-8'), []).html;
			currentBlob = {
				path,
				content: rawContent,
				frontmatter,
				html: parsedHtml
			};
		} catch (err: any) {
			if (id !== generation || signal.aborted) return;
			error = `Failed to load file (${path}): ${err.message}`;
		} finally {
			if (id === generation) loading = false;
		}
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
		fileAnchor = '';
		currentPath = isTree ? (path.endsWith('/') ? path : path + '/') : path;
	}

	function navigateParent() {
		fileAnchor = '';
		const parts = currentPath.replace(/\/+$/, '').split('/');
		if (parts.length > 1) {
			parts.pop();
			currentPath = parts.join('/') + '/';
		} else {
			currentPath = '';
		}
	}

	const currentHtml = $derived(
		relationSubject
			? renderDocument(relationSubject, [
					relationSubject,
					...relationIndex.documents.filter((doc) => doc.path !== relationSubject.path)
				]).html
			: (currentBlob?.html ?? '')
	);
	async function scrollFileFragment(fragment: string) {
		if (!fragment) return;
		const path = currentPath,
			currentBranch = branch,
			repository = source;
		await tick();
		if (
			view !== 'files' ||
			rawMode ||
			fileSupport ||
			path !== currentPath ||
			currentBranch !== branch ||
			repository !== source ||
			fragment !== fileAnchor
		)
			return;
		const target = [
			...(hostEl?.querySelectorAll<HTMLElement>('.content-viewport [id]') ?? [])
		].find((node) => node.id === fragment || node.id === documentAnchor(path) + '--' + fragment);
		target?.scrollIntoView({ block: 'start', behavior: 'instant' });
	}
	function navigateDocument(path: string, fragment = '') {
		fileAnchor = fragment;
		currentPath = path;
		void scrollFileFragment(fragment);
	}
	$effect(() => {
		currentHtml;
		currentBlob;
		fileAnchor;
		view;
		rawMode;
		if (currentBlob && fileAnchor && view === 'files' && !rawMode)
			void scrollFileFragment(fileAnchor);
	});
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
		hasCurrentBlob={Boolean(currentBlob) && !fileSupport}
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
							if (targetPath && targetView !== 'files')
								knowledgeRequest = { path: targetPath, anchor: '', view: targetView };
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
			{:else if view !== 'files'}
				<div class="knowledge-host">
					<KnowledgeViews
						{view}
						{bookRequested}
						onBookRequest={setBookRequested}
						{source}
						{branch}
						theme={themeState.current}
						requestedPath={requestFor(view).path}
						requestedAnchor={requestFor(view).anchor}
						diagrams={diagramRenderer}
						onOpen={(path) => {
							currentPath = path;
							view = 'files';
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
				{#if fileSupport}
					<SupportingArtifact
						{source}
						{branch}
						path={fileSupport.path}
						parent={fileSupport.parent}
						fragment={fileSupport.fragment}
						documents={relationIndex.documents}
						diagrams={diagramRenderer}
						onBack={async () => {
							if (fileSupport?.parent) {
								const scroll = fileSupport.scroll ?? 0;
								fileSupport = null;
								await tick();
								const node = hostEl?.querySelector('.content-viewport');
								if (node) node.scrollTop = scroll;
							} else navigateParent();
						}}
						onOpen={(path, fragment) => {
							if (
								relationIndex.documents.some((doc) => doc.path === path && !isArtifactPath(path))
							) {
								fileSupport = null;
								navigateDocument(path, fragment ?? '');
							} else if (fileSupport) {
								fileSupport.path = path;
								fileSupport.fragment = fragment ?? '';
							}
						}}
					/>
				{:else}
					<DocumentViewer
						{currentBlob}
						{source}
						{branch}
						renderedHtml={currentHtml}
						onSupportingOpen={(path, fragment) =>
							(fileSupport = {
								path,
								parent: currentBlob?.frontmatter?.id ?? currentPath,
								fragment,
								scroll: hostEl?.querySelector('.content-viewport')?.scrollTop ?? 0
							})}
						{loading}
						{error}
						{rawMode}
						theme={themeState.current}
						diagramAction={diagramRenderer}
						{relationSubject}
						relationDocuments={relationIndex.documents}
						relationFiles={relationIndex.files ?? []}
						{relationLoading}
						relationErrors={relationIndex.errors}
						onRelationOpen={navigateDocument}
						onReloadRelations={reloadRelations}
					/>
				{/if}
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
		scrollbar-width: thin;
		scrollbar-color: var(--border-btn) transparent;
	}

	.sdd-viewer-root :global(*)::-webkit-scrollbar {
		width: 8px;
		height: 8px;
	}

	.sdd-viewer-root :global(*)::-webkit-scrollbar-track {
		background: transparent;
	}

	.sdd-viewer-root :global(*)::-webkit-scrollbar-thumb {
		background-color: var(--border-btn);
		border-radius: 4px;
	}

	.sdd-viewer-root :global(*)::-webkit-scrollbar-thumb:hover {
		background-color: var(--btn-hover-bg);
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
