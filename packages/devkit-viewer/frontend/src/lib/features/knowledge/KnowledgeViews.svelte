<script lang="ts">
	import { tick, untrack } from 'svelte';
	import type { RepositoryDataSource } from '../../api/repository';
	import {
		indexDocuments,
		taskProgress,
		renderDocument,
		documentAnchor,
		bookGroup,
		bookGroups,
		namespaceOf,
		idIndex,
		type RepositoryDocument
	} from '../../api/documents';
	import KnowledgeSidebar from './KnowledgeSidebar.svelte';
	import BundleHeader from './BundleHeader.svelte';
	import ChapterSection from './ChapterSection.svelte';

	let {
		view,
		source,
		branch,
		theme,
		requestedPath,
		requestedAnchor,
		onOpen,
		onLocation,
		diagrams
	}: {
		view: 'book' | 'proposals' | 'specs';
		theme: string;
		requestedPath: string;
		requestedAnchor: string;
		source: RepositoryDataSource | null;
		branch: string;
		onOpen: (path: string) => void;
		onLocation: (path: string, anchor: string, view: string, meta: Record<string, any>) => void;
		diagrams: (node: HTMLElement) => { destroy: () => void };
	} = $props();

	let documents = $state<RepositoryDocument[]>([]);
	let errors = $state<string[]>([]);
	let loading = $state(false);
	let query = $state('');
	let status = $state('');
	let priority = $state('');
	let size = $state('');
	let area = $state('');
	let namespace = $state('all');
	let includeCompleted = $state(false);
	let selectedPath = $state('');
	let detailPath = $state('');
	let currentAnchor = $state('');
	let root: HTMLElement;

	$effect(() => {
		const repository = source,
			ref = branch;
		const controller = new AbortController();
		documents = [];
		errors = [];
		loading = Boolean(repository);
		selectedPath = '';
		detailPath = '';
		currentAnchor = '';
		if (repository)
			void indexDocuments(repository, ref, controller.signal).then((result) => {
				if (controller.signal.aborted) return;
				documents = result.documents;
				errors = result.errors;
				loading = false;
			});
		return () => controller.abort();
	});

	$effect(() => {
		view;
		query = '';
		status = '';
		priority = '';
		size = '';
		area = '';
		selectedPath = '';
		detailPath = '';
		currentAnchor = '';
	});

	const namespaces = $derived([...new Set(documents.map(namespaceOf))].sort());
	const scoped = $derived(
		documents.filter(
			(d) => namespace === 'all' || namespaceOf(d) === namespace || namespaceOf(d) === 'global'
		)
	);
	const ids = $derived(idIndex(documents));
	const book = $derived(
		bookGroups.flatMap((group) => scoped.filter((d) => bookGroup(d) === group))
	);
	const candidates = $derived(
		scoped.filter((d) =>
			view === 'proposals'
				? /^docs\/proposals\/PROP-[^/]+\/proposal\.md$/.test(d.path)
				: /^specs\/\d{4}-\d{2}\/[^/]+\/spec\.md$/.test(d.path)
		)
	);
	const statuses = $derived(
		[...new Set(candidates.map((d) => String(d.meta.status ?? 'unknown')))].sort()
	);
	const areas = $derived(
		[...new Set(candidates.map((d) => String(d.meta.target_area ?? '')).filter(Boolean))].sort()
	);
	const entries = $derived(
		candidates.filter(
			(d) =>
				(view !== 'specs' || includeCompleted || d.meta.status !== 'completed') &&
				(!status || String(d.meta.status ?? 'unknown') === status) &&
				(!priority || d.meta.priority === priority) &&
				(!size || d.meta.size === size) &&
				(!area || d.meta.target_area === area) &&
				(!query ||
					`${d.title} ${d.meta.id ?? ''} ${d.meta.target_area ?? ''}`
						.toLowerCase()
						.includes(query.toLowerCase()))
		)
	);
	const selected = $derived(entries.find((d) => d.path === selectedPath));
	const bundle = $derived(
		selected
			? documents
					.filter((d) =>
						d.path.startsWith(selected.path.slice(0, selected.path.lastIndexOf('/') + 1))
					)
					.sort((a, b) => {
						const order = [
							'proposal.md',
							'spec.md',
							'target-docs.md',
							'plan.md',
							'tasks.md',
							'reconcile.md'
						];
						const rank = (d: RepositoryDocument) => {
							const i = order.indexOf(d.path.split('/').at(-1)!);
							return i < 0 ? 99 : i;
						};
						return rank(a) - rank(b) || a.path.localeCompare(b.path);
					})
			: []
	);
	const detail = $derived(bundle.find((d) => d.path === detailPath) ?? selected);
	const visibleDocs = $derived(view === 'book' ? book : detail ? [detail] : []);
	const rendered = $derived(
		new Map(visibleDocs.map((doc) => [doc.path, renderDocument(doc, documents)]))
	);
	const taskDoc = $derived(bundle.find((d) => d.path.endsWith('/tasks.md')));
	const taskChecks = $derived(taskProgress(taskDoc?.body ?? ''));
	const relations = $derived(
		selected
			? ['related_capabilities', 'related_usecases'].flatMap((key) =>
					Array.isArray(selected.meta[key]) ? selected.meta[key] : []
				)
			: []
	);

	$effect(() => {
		const path = requestedPath,
			anchor = requestedAnchor,
			currentView = view;
		if (loading || !documents.length) return;
		untrack(() => {
			const doc = documents.find((d) => d.path === path);
			if (!doc) return;
			if (currentView !== 'book') {
				const entry = candidates.find((d) =>
					path.startsWith(d.path.slice(0, d.path.lastIndexOf('/') + 1))
				);
				if (!entry) return;
				if (entry.meta.status === 'completed') includeCompleted = true;
				namespace = 'all';
				status = '';
				query = '';
				priority = '';
				size = '';
				area = '';
				selectedPath = entry.path;
				detailPath = path;
			}
			void tick().then(() => jump(path, anchor || documentAnchor(path)));
		});
	});

	function lazyDiagrams(node: HTMLElement) {
		let cleanup: { destroy: () => void } | undefined;
		const observer = new IntersectionObserver(
			(entries) => {
				if (entries.some((e) => e.isIntersecting)) {
					cleanup = diagrams(node);
					observer.disconnect();
				}
			},
			{ root: root?.querySelector('.reading-content'), rootMargin: '200px' }
		);
		observer.observe(node);
		return {
			destroy() {
				observer.disconnect();
				cleanup?.destroy();
			}
		};
	}

	function trackHeading(node: HTMLElement) {
		const observer = new IntersectionObserver(
			(entries) => {
				const visible = entries.filter((e) => e.isIntersecting);
				if (visible.length) currentAnchor = visible[0].target.id;
			},
			{ root: root?.querySelector('.reading-content'), rootMargin: '0px 0px -70% 0px' }
		);
		node.querySelectorAll('[id]').forEach((heading) => observer.observe(heading));
		return {
			destroy() {
				observer.disconnect();
			}
		};
	}

	async function jump(path: string, anchor = documentAnchor(path)) {
		if (!visibleDocs.some((d) => d.path === path)) {
			const target = documents.find((d) => d.path === path);
			if (!target) return;
			if (view === 'book' && bookGroup(target)) namespace = 'all';
			else if (
				selected &&
				path.startsWith(selected.path.slice(0, selected.path.lastIndexOf('/') + 1))
			)
				detailPath = path;
			else {
				onOpen(path);
				return;
			}
			await tick();
		}
		const element = root.querySelectorAll<HTMLElement>('[id]');
		const destination = [...element].find((el) => el.id === anchor);
		if (!destination) return;
		destination.scrollIntoView({ block: 'start', behavior: 'instant' });
		currentAnchor = anchor;
		onLocation(path, anchor, view, documents.find((d) => d.path === path)?.meta ?? {});
	}

	function linkNavigation(node: HTMLElement) {
		node.addEventListener('click', followLink);
		return {
			destroy() {
				node.removeEventListener('click', followLink);
			}
		};
	}

	function followLink(event: MouseEvent) {
		const link = (event.target as Element).closest<HTMLAnchorElement>('a[data-doc-path]');
		if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
		event.preventDefault();
		void jump(link.dataset.docPath!, link.getAttribute('href')!.slice(1));
	}

	function select(doc: RepositoryDocument) {
		selectedPath = doc.path;
		detailPath = '';
		currentAnchor = '';
		onLocation(doc.path, '', view, doc.meta);
	}
</script>

<div class="knowledge" bind:this={root}>
	{#if errors.length}
		<details class="index-errors">
			<summary>{errors.length} documents failed to load</summary>
			{#each errors as error}
				<p>{error}</p>
			{/each}
		</details>
	{/if}
	{#if loading}
		<p role="status">Loading documents…</p>
	{:else if !source}
		<p>Connect a repository to browse documents.</p>
	{:else}
		<div class="reading-layout">
			<KnowledgeSidebar
				{view}
				bind:namespace
				{namespaces}
				bind:query
				bind:status
				{statuses}
				bind:priority
				bind:size
				bind:area
				{areas}
				bind:includeCompleted
				{book}
				{entries}
				{selected}
				{currentAnchor}
				{rendered}
				onJump={(path, anchor) => jump(path, anchor)}
				onSelect={select}
			/>
			<main class="reading-content" use:linkNavigation>
				{#if view !== 'book' && selected}
					<BundleHeader
						{selected}
						{bundle}
						{detail}
						{taskChecks}
						{relations}
						{ids}
						{rendered}
						{view}
						{onOpen}
						onLocation={(path, anchor, meta) => onLocation(path, anchor, view, meta)}
						onJump={(path, headingId) => jump(path, headingId)}
						onSelectDetail={(path) => {
							detailPath = path;
							currentAnchor = '';
						}}
					/>
				{/if}
				{#each visibleDocs as doc (doc.path)}
					<ChapterSection
						{doc}
						html={rendered.get(doc.path)?.html ?? ''}
						{branch}
						{theme}
						{lazyDiagrams}
						{trackHeading}
						{onOpen}
					/>
				{/each}
				{#if !visibleDocs.length}
					<p class="empty">
						{view === 'book' ? 'No documents to display.' : 'Select an item from the list.'}
					</p>
				{/if}
			</main>
		</div>
	{/if}
</div>

<style>
	.knowledge {
		display: flex;
		flex-direction: column;
		min-height: 0;
		height: 100%;
		color: var(--text-primary);
	}

	.reading-layout {
		display: grid;
		grid-template-columns: 280px minmax(0, 1fr);
		flex: 1;
		min-height: 0;
		height: 100%;
		overflow: hidden;
	}

	.reading-content {
		overflow-y: auto;
		padding: 24px clamp(16px, 4vw, 64px) 80px;
		scroll-behavior: smooth;
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

	@media (max-width: 760px) {
		.reading-layout {
			grid-template-columns: 200px minmax(0, 1fr);
		}
		.reading-content {
			padding: 16px;
		}
	}

	@media (max-width: 520px) {
		.reading-layout {
			grid-template-columns: 1fr;
			grid-template-rows: 180px minmax(0, 1fr);
		}
	}
</style>
