<script lang="ts">
	import { ID_PATTERN, identityResolver, isArtifactPath } from '../../api/identity';
	import SupportingArtifact from '../document/SupportingArtifact.svelte';
	import { planningDataSource } from '../../api/planning';
	import { tick, untrack } from 'svelte';
	import { clearRepositoryCache } from '../../api/cache';
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
	import {
		cachedOverlay,
		loadPlanningBundle,
		loadPlanningOverlay,
		type PlanningOverlay
	} from '../../api/planning';
	import KnowledgeSidebar from './KnowledgeSidebar.svelte';
	import BundleHeader from './BundleHeader.svelte';
	import ChapterSection from './ChapterSection.svelte';
	import HandbookView from './HandbookView.svelte';

	let {
		view,
		source,
		branch,
		theme,
		requestedPath,
		requestedAnchor,
		onOpen,
		onLocation,
		diagrams,
		bookRequested = $bindable(false)
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
		/** The Living Spec book is computed only once requested; bind it to keep the request across mounts. */
		bookRequested?: boolean;
	} = $props();

	let documents = $state<RepositoryDocument[]>([]);
	let relationDocuments = $state<RepositoryDocument[]>([]);
	let errors = $state<string[]>([]);
	let loading = $state(false);
	let relationLoading = $state(false);
	let relationReload = $state(0);
	let loadedContext = $state.raw<{ source: RepositoryDataSource; branch: string } | null>(null);
	let query = $state('');
	let status = $state('');
	let priority = $state('');
	let size = $state('');
	let area = $state('');
	let namespace = $state('all');
	let includeCompleted = $state(false);
	let includeRetired = $state(false);
	let pinnedPath = $state('');
	let requestError = $state('');
	let activePath = $state('');
	let history = $state<
		{
			path: string;
			anchor: string;
			namespace: string;
			query: string;
			includeRetired: boolean;
			scroll: number;
		}[]
	>([]);
	let artifactFragment = $state('');
	let artifact = $state.raw<{
		path: string;
		parent: string;
		source: RepositoryDataSource;
		label: string;
		scroll: number;
	} | null>(null);
	$effect(() => {
		source;
		branch;
		artifact = null;
		history = [];
		pinnedPath = '';
		requestError = '';
		activePath = '';
	});
	let selectedPath = $state('');
	let detailPath = $state('');
	let currentAnchor = $state('');
	let root: HTMLElement;
	let resolvedRequest = '';

	// The reading tab shows the handbook until the book is requested; Proposals and Specs always index.
	const handbookMode = $derived(view === 'book' && !bookRequested);
	// Index latch: set by the first indexing view or the book request for this source and branch, never reset by a
	// view change, so Book, Proposals and Book again start one scan.
	let latched = $state.raw<{ source: RepositoryDataSource; branch: string } | null>(null);
	$effect(() => {
		if (!handbookMode && source && (latched?.source !== source || latched.branch !== branch))
			latched = { source, branch };
	});
	const indexed = $derived(
		Boolean(source) && latched?.source === source && latched?.branch === branch
	);

	$effect(() => {
		const repository = indexed ? source : null,
			ref = branch;
		relationReload;
		const keep = untrack(
			() => repository && loadedContext?.source === repository && loadedContext.branch === ref
		);
		const controller = new AbortController();
		if (!keep) {
			documents = [];
			relationDocuments = [];
			errors = [];
			resolvedRequest = '';
			selectedPath = '';
			detailPath = '';
			currentAnchor = '';
			loadedContext = null;
		}
		loading = Boolean(repository) && !keep;
		relationLoading = Boolean(repository);
		if (repository)
			void indexDocuments(repository, ref, controller.signal)
				.then((result) => {
					if (controller.signal.aborted) return;
					const subjects = keep ? untrack(() => documents) : [];
					relationDocuments = result.documents;
					documents = [
						...result.documents.map(
							(doc) => subjects.find((subject) => subject.path === doc.path) ?? doc
						),
						...subjects.filter(
							(subject) => !result.documents.some((doc) => doc.path === subject.path)
						)
					];
					errors = result.errors;
					loading = false;
					relationLoading = false;
					loadedContext = { source: repository, branch: ref };
				})
				.catch((error: unknown) => {
					if (!controller.signal.aborted) {
						errors = [String(error)];
						loadedContext = { source: repository, branch: ref };
						loading = false;
						relationLoading = false;
					}
				});
		return () => controller.abort();
	});
	function reloadRelations() {
		resolvedRequest = '';
		requestError = '';
		if (source) clearRepositoryCache(source);
		relationReload++;
	}

	// The Proposals tab overlays Planning proposals; the checkout index above never waits for them.
	let overlay = $state.raw<PlanningOverlay | undefined>();
	let overlayErrors = $state.raw<string[]>([]);
	$effect(() => {
		const repository = source,
			ref = branch,
			wanted = view === 'proposals';
		overlay = undefined;
		overlayErrors = [];
		if (!repository?.planningProposals || !wanted) return;
		const controller = new AbortController();
		const known = cachedOverlay(repository, ref);
		overlay = known;
		if (!known)
			void loadPlanningOverlay(repository, ref, controller.signal)
				.then((result) => {
					if (controller.signal.aborted) return;
					overlay = result;
					overlayErrors = result?.errors ?? [];
				})
				.catch((error: unknown) => {
					if (!controller.signal.aborted)
						overlayErrors = [
							`Planning overlay: ${error instanceof Error ? error.message : String(error)}`
						];
				});
		return () => controller.abort();
	});
	const overlayEntries = $derived(overlay?.entries ?? {});
	// Overlaid proposals replace their checkout copies in place; Planning-only ones join in path order.
	const merged = $derived.by(() => {
		const entries = Object.values(overlayEntries);
		if (!entries.length) return documents;
		const known = new Set(documents.map((d) => d.path));
		return [
			...documents.map((d) => overlayEntries[d.path]?.document ?? d),
			...entries.filter((e) => !known.has(e.document.path)).map((e) => e.document)
		].sort((a, b) => a.path.localeCompare(b.path, undefined, { numeric: true }));
	});
	const sourceLabels = $derived(
		Object.fromEntries(Object.entries(overlayEntries).map(([path, e]) => [path, e.source.label]))
	);

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
		merged.filter(
			(d) => namespace === 'all' || namespaceOf(d) === namespace || namespaceOf(d) === 'global'
		)
	);
	const ids = $derived(idIndex(merged));
	const book = $derived.by(() => {
		const matches = scoped.filter(
			(doc) =>
				(includeRetired ||
					doc.meta.status !== 'retired' ||
					!/^(?:DESIGN|DOMAIN|OPS)-/.test(String(doc.meta.id))) &&
				(!query ||
					`${doc.title} ${doc.meta.id ?? ''} ${Array.isArray(doc.meta.aliases) ? doc.meta.aliases.filter((value: unknown) => typeof value === 'string').join(' ') : ''} ${doc.meta.summary ?? ''} ${doc.body}`
						.toLowerCase()
						.includes(query.toLowerCase()))
		);
		const pinned = merged.find((doc) => doc.path === pinnedPath);
		if (pinned && !matches.some((doc) => doc.path === pinned.path)) matches.push(pinned);
		return bookGroups.flatMap((group) => matches.filter((doc) => bookGroup(doc) === group));
	});
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
	const selectedEntry = $derived(selected ? overlayEntries[selected.path] : undefined);
	// An overlaid proposal's bundle is read from its own Planning source, never from the checkout.
	let planningBundle = $state.raw<{
		key: string;
		documents: RepositoryDocument[];
		errors: string[];
	}>();
	const bundleKey = $derived(selectedEntry ? `${selectedEntry.source.id}\n${selected!.path}` : '');
	$effect(() => {
		const key = bundleKey,
			repository = source;
		planningBundle = undefined;
		const entry = untrack(() => selectedEntry);
		if (!key || !repository || !entry) return;
		const controller = new AbortController();
		void loadPlanningBundle(repository, entry, controller.signal).then((result) => {
			if (!controller.signal.aborted) planningBundle = { key, ...result };
		});
		return () => controller.abort();
	});
	const bundleSource = $derived(
		selectedEntry
			? planningBundle?.key === bundleKey && planningBundle.documents.length
				? planningBundle.documents
				: [selectedEntry.document]
			: documents
	);
	const bundle = $derived(
		selected
			? bundleSource
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
	const visibleDocs = $derived(
		view === 'book' ? (bookRequested ? book : []) : detail ? [detail] : []
	);
	const rendered = $derived(
		new Map(visibleDocs.map((doc) => [doc.path, renderDocument(doc, merged)]))
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

	// A request resolves once; a later overlay retries only a request no document matched yet.
	$effect(() => {
		const path = requestedPath,
			anchor = requestedAnchor,
			currentView = view,
			available = merged;
		if (loading || relationLoading || !loadedContext || handbookMode) return;
		untrack(() => {
			const key = `${currentView}\n${path}\n${anchor}`;
			if (resolvedRequest === key) return;
			const result = identityResolver(available).resolve(path);
			const doc = available.find((d) => d.path === path) ?? result.document;
			if (!doc) {
				if (path) {
					const reason = ID_PATTERN.test(path) ? result.unavailable : 'missing';
					requestError = `${path} — unavailable (${reason === 'missing' && errors.length ? 'index incomplete' : reason})`;
					if (currentView === 'book') resolvedRequest = key;
				}
				return;
			}
			requestError = '';
			if (currentView === 'book') pinnedPath = doc.path;
			resolvedRequest = key;
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
			// A tab switch before the next tick cancels the jump, so it never resolves in another view.
			void tick().then(() => {
				if (view === currentView) void jump(doc.path, anchor || documentAnchor(doc.path), false);
			});
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

	const shownErrors = $derived([
		...errors,
		...overlayErrors,
		...(planningBundle && planningBundle.key === bundleKey ? planningBundle.errors : [])
	]);
	const findDocument = (path: string) =>
		bundle.find((d) => d.path === path) ?? merged.find((d) => d.path === path);

	async function jump(
		path: string,
		anchor = documentAnchor(path),
		remember = true,
		originPath = activePath
	) {
		if (remember && originPath && originPath !== path)
			history.push({
				path: originPath,
				anchor: currentAnchor.startsWith(documentAnchor(originPath))
					? currentAnchor
					: documentAnchor(originPath),
				namespace,
				query,
				includeRetired,
				scroll: root?.querySelector('.reading-content')?.scrollTop ?? 0
			});
		if (view === 'book') pinnedPath = path;
		requestError = '';
		activePath = path;
		if (!visibleDocs.some((d) => d.path === path)) {
			const target = findDocument(path);
			if (!target) return;
			if (view === 'book' && bookGroup(target)) pinnedPath = path;
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
		onLocation(path, anchor, view, findDocument(path)?.meta ?? {});
	}

	async function openRelation(path: string, originPath = activePath) {
		if (view !== 'book') {
			onOpen(path);
			return;
		}
		const fresh = relationDocuments.find((doc) => doc.path === path);
		if (fresh) {
			documents = documents.some((doc) => doc.path === path)
				? documents.map((doc) => (doc.path === path ? fresh : doc))
				: [...documents, fresh];
			await tick();
		}
		await jump(path, documentAnchor(path), true, originPath);
	}

	function linkNavigation(node: HTMLElement) {
		node.addEventListener('click', followLink);
		return {
			destroy() {
				node.removeEventListener('click', followLink);
			}
		};
	}

	async function back() {
		const prior = history.pop();
		if (!prior) return;
		namespace = prior.namespace;
		query = prior.query;
		includeRetired = prior.includeRetired;
		await jump(prior.path, prior.anchor || documentAnchor(prior.path), false);
		await tick();
		const content = root.querySelector('.reading-content');
		if (content) content.scrollTop = prior.scroll;
	}
	function openArtifact(path: string, origin: string, fragment = '') {
		if (!source) return;
		const entry = view === 'book' ? undefined : selectedEntry;
		if (entry && !source.planningBlob) {
			requestError = `${path} — Planning source unavailable`;
			return;
		}
		artifactFragment = fragment;
		artifact = {
			path,
			parent: String(merged.find((doc) => doc.path === origin)?.meta.id ?? origin),
			source: entry ? planningDataSource(source, entry.source.id) : source,
			label: entry?.source.label ?? branch,
			scroll: root.querySelector('.reading-content')?.scrollTop ?? 0
		};
	}
	function followLink(event: MouseEvent) {
		if (event.defaultPrevented) return;
		const link = (event.target as Element).closest<HTMLAnchorElement>(
			'a[data-doc-path],a[data-repo-path]'
		);
		if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
		event.preventDefault();
		if (link.dataset.repoPath)
			openArtifact(
				link.dataset.repoPath,
				link.dataset.originPath ?? activePath,
				link.dataset.fragment
			);
		else
			void jump(
				link.dataset.docPath!,
				link.getAttribute('href')!.slice(1),
				true,
				link.dataset.originPath ?? activePath
			);
	}

	function select(doc: RepositoryDocument) {
		selectedPath = doc.path;
		detailPath = '';
		currentAnchor = '';
		onLocation(doc.path, '', view, doc.meta);
	}
</script>

<div class="knowledge" bind:this={root}>
	{#if source && handbookMode}
		<HandbookView
			{source}
			{branch}
			{theme}
			{requestedPath}
			{requestedAnchor}
			{diagrams}
			onRequestBook={() => {
				bookRequested = true;
			}}
			onLocation={(path, anchor, meta) => onLocation(path, anchor, view, meta)}
		/>
	{:else}
		{#if shownErrors.length}
			<details class="index-errors">
				<summary>{shownErrors.length} documents failed to load</summary>
				{#each shownErrors as error}
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
					bind:includeRetired
					bind:includeCompleted
					{book}
					{entries}
					sources={sourceLabels}
					{selected}
					{currentAnchor}
					{rendered}
					onJump={(path, anchor) => jump(path, anchor)}
					onSelect={select}
					onFiltersChanged={() => (pinnedPath = '')}
					onHandbook={() => {
						bookRequested = false;
					}}
				/>
				<main class="reading-content" use:linkNavigation>
					{#if artifact}<SupportingArtifact
							source={artifact.source}
							{branch}
							path={artifact.path}
							parent={artifact.parent}
							sourceLabel={artifact.label}
							fragment={artifactFragment}
							documents={merged}
							{diagrams}
							onBack={async () => {
								const scroll = artifact?.scroll ?? 0;
								artifact = null;
								await tick();
								const node = root.querySelector('.reading-content');
								if (node) node.scrollTop = scroll;
							}}
							onOpen={(path, fragment) => {
								if (merged.some((doc) => doc.path === path && !isArtifactPath(path))) {
									artifact = null;
									void jump(path, documentAnchor(path) + (fragment ? '--' + fragment : ''));
								} else if (artifact) {
									artifactFragment = fragment ?? '';
									if (path !== artifact.path) artifact = { ...artifact, path };
								}
							}}
						/>{/if}
					<div class:artifact-hidden={Boolean(artifact)}>
						{#if requestError}<p role="status">{requestError}</p>
							<button onclick={() => (requestError = '')}>Back to documents</button><button
								onclick={reloadRelations}>Reload documents</button
							>{/if}
						{#if history.length}<button onclick={back}>Back to previous document</button>{/if}
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
								sourceLabel={selectedEntry?.source.label}
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
								source={view !== 'book' && selectedEntry && source
									? planningDataSource(source, selectedEntry.source.id)
									: source}
								html={rendered.get(doc.path)?.html ?? ''}
								{branch}
								{theme}
								{lazyDiagrams}
								{trackHeading}
								sourceLabel={view === 'book' ? undefined : selectedEntry?.source.label}
								{onOpen}
								documents={relationDocuments}
								{relationLoading}
								relationErrors={errors}
								onReloadRelations={reloadRelations}
								onRelationOpen={(path) => openRelation(path, doc.path)}
							/>
						{/each}
						{#if !visibleDocs.length}
							<p class="empty">
								{view === 'book' ? 'No documents to display.' : 'Select an item from the list.'}
							</p>
						{/if}
					</div>
				</main>
			</div>
		{/if}
	{/if}
</div>

<style>
	.artifact-hidden {
		display: none;
	}
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
