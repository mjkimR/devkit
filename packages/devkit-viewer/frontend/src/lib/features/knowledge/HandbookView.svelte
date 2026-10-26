<script lang="ts">
	import { tick, untrack } from 'svelte';
	import type { RepositoryDataSource } from '../../api/repository';
	import type { RenderedDocument, RepositoryDocument } from '../../api/documents';
	import {
		HOME_PAGE,
		MANIFEST_PATH,
		fragmentTarget,
		initialLanguage,
		loadManifest,
		loadPage,
		loadVersion,
		pagePath,
		parsePagePath,
		rememberLanguage,
		renderHandbookPage,
		staleness,
		type HandbookManifest
	} from '../../api/handbook';

	let {
		source,
		branch,
		theme,
		requestedPath = '',
		requestedAnchor = '',
		diagrams,
		onRequestBook,
		onLocation
	}: {
		source: RepositoryDataSource;
		branch: string;
		theme: string;
		/** A host request for `handbook/<lang>/<page>`; any other path opens the home page. */
		requestedPath?: string;
		requestedAnchor?: string;
		diagrams: (node: HTMLElement) => { destroy: () => void };
		onRequestBook: () => void;
		onLocation: (path: string, anchor: string, meta: Record<string, any>) => void;
	} = $props();

	type State =
		| { kind: 'loading' }
		| { kind: 'absent' }
		| { kind: 'error'; message: string }
		| { kind: 'ready'; manifest: HandbookManifest };
	let manifestState = $state.raw<State>({ kind: 'loading' });
	let version = $state<string | null>(null);
	let lang = $state('en');
	let page = $state(HOME_PAGE);
	let pending = '';
	let resolvedRequest = '';
	let doc = $state.raw<RepositoryDocument | null>(null);
	let pageError = $state('');
	let pageLoading = $state(false);
	let content: HTMLElement | undefined = $state();

	const message = (error: unknown) => (error instanceof Error ? error.message : String(error));

	// The manifest decides the mode; VERSION is read only when it exists.
	$effect(() => {
		const repository = source,
			ref = branch;
		const controller = new AbortController();
		manifestState = { kind: 'loading' };
		version = null;
		doc = null;
		void loadManifest(repository, ref, controller.signal)
			.then((manifest) => {
				if (controller.signal.aborted) return;
				if (!manifest) {
					manifestState = { kind: 'absent' };
					return;
				}
				resolvedRequest = untrack(() => `${requestedPath}\n${requestedAnchor}`);
				const request = untrack(() => parsePagePath(requestedPath));
				if (request && manifest.langs.includes(request.lang)) {
					lang = request.lang;
					page = request.page;
					pending = untrack(() => requestedAnchor);
				} else {
					lang = initialLanguage(manifest.langs);
					page = HOME_PAGE;
				}
				manifestState = { kind: 'ready', manifest };
				void loadVersion(repository, ref, controller.signal).then((value) => {
					if (!controller.signal.aborted) version = value;
				});
			})
			.catch((error: unknown) => {
				if (!controller.signal.aborted) manifestState = { kind: 'error', message: message(error) };
			});
		return () => controller.abort();
	});

	const ready = $derived(manifestState.kind === 'ready');
	// A later host request for a handbook page opens it; the first one is applied with the manifest.
	$effect(() => {
		const key = `${requestedPath}\n${requestedAnchor}`;
		if (manifestState.kind !== 'ready' || key === untrack(() => resolvedRequest)) return;
		resolvedRequest = key;
		const request = parsePagePath(requestedPath);
		if (!request || !manifestState.manifest.langs.includes(request.lang)) return;
		const anchor = requestedAnchor;
		untrack(() => {
			if (request.lang === lang && request.page === page) return open(page, anchor);
			pending = anchor;
			lang = request.lang;
			page = request.page;
		});
	});
	$effect(() => {
		const repository = source,
			ref = branch,
			currentLang = lang,
			currentPage = page;
		if (!ready) return;
		const controller = new AbortController();
		pageLoading = true;
		pageError = '';
		void loadPage(repository, ref, currentLang, currentPage, controller.signal)
			.then(async (result) => {
				if (controller.signal.aborted) return;
				doc = result;
				pageLoading = false;
				await tick();
				if (controller.signal.aborted) return;
				const fragment = pending;
				pending = '';
				const target = content && fragmentTarget(content, fragment);
				if (target) target.scrollIntoView({ block: 'start', behavior: 'instant' });
				else content?.scrollTo?.({ top: 0 });
				onLocation(pagePath(currentLang, currentPage), fragment, result.meta);
			})
			.catch((error: unknown) => {
				if (controller.signal.aborted) return;
				doc = null;
				pageLoading = false;
				pageError = `Failed to load ${pagePath(currentLang, currentPage)}: ${message(error)}`;
			});
		return () => controller.abort();
	});

	const rendered = $derived<RenderedDocument | null>(doc ? renderHandbookPage(doc, lang) : null);
	const subheadings = $derived(rendered?.headings.filter((h) => h.level > 1 && h.level <= 3) ?? []);
	const noteState = $derived(
		manifestState.kind === 'ready' ? staleness(manifestState.manifest.tag, version) : 'absent'
	);

	function open(target: string, fragment = '') {
		if (target === page && doc) {
			const element = content && fragmentTarget(content, fragment);
			element?.scrollIntoView({ block: 'start', behavior: 'instant' });
			onLocation(pagePath(lang, page), fragment, doc.meta);
			return;
		}
		pending = fragment;
		page = target;
	}

	function switchLanguage(next: string) {
		rememberLanguage(next);
		lang = next;
	}

	function followLink(event: MouseEvent) {
		const link = (event.target as Element).closest<HTMLAnchorElement>('a');
		if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
		if (link.classList.contains('unavailable')) {
			event.preventDefault();
			return;
		}
		if (link.dataset.handbookPage === undefined) return;
		event.preventDefault();
		open(link.dataset.handbookPage, link.dataset.fragment ?? '');
	}
</script>

{#if manifestState.kind === 'loading'}
	<p role="status">Loading handbook…</p>
{:else if manifestState.kind !== 'ready'}
	<div class="handbook-missing">
		{#if manifestState.kind === 'absent'}
			<p class="handbook-absent">This repository has no <code>{MANIFEST_PATH}</code>.</p>
		{:else}
			<p class="handbook-error">Failed to read the handbook: {manifestState.message}</p>
		{/if}
		<p>The Living Spec book shows the current contracts under <code>docs/</code>.</p>
		<button class="book-control" onclick={onRequestBook}>Living Spec book</button>
	</div>
{:else}
	<div class="reading-layout">
		<aside class="outline" aria-label="Handbook contents">
			<div class="filters">
				<button class="book-control" onclick={onRequestBook}>Living Spec book</button>
				{#if manifestState.manifest.langs.length > 1}
					<label>
						Language
						<select
							aria-label="Language"
							value={lang}
							onchange={(e) => switchLanguage((e.currentTarget as HTMLSelectElement).value)}
						>
							{#each manifestState.manifest.langs as option}
								<option value={option}>{option}</option>
							{/each}
						</select>
					</label>
				{/if}
			</div>
			<button class:active={page === HOME_PAGE} onclick={() => open(HOME_PAGE)}>
				Handbook home
			</button>
			{#each subheadings as heading}
				<button
					class="subheading"
					style:padding-left={`${heading.level * 8}px`}
					onclick={() => open(page, heading.id)}
				>
					{heading.title}
				</button>
			{/each}
		</aside>
		<main class="reading-content handbook-content" bind:this={content}>
			<header class="handbook-header" data-staleness={noteState}>
				<p>
					{#if noteState === 'ahead'}
						Snapshot prepared for the upcoming release <code>{manifestState.manifest.tag}</code>
					{:else}
						Snapshot of <code>{manifestState.manifest.tag}</code>
					{/if}
					{#if manifestState.manifest.generated}
						· generated {manifestState.manifest.generated}
					{/if}
				</p>
				{#if noteState === 'behind'}
					<p class="handbook-note" role="note">
						This handbook describes <code>{manifestState.manifest.tag}</code>; this repository is at
						<code>{version}</code>. The Living Spec book shows the current contracts.
					</p>
				{/if}
			</header>
			{#if pageLoading}
				<p role="status">Loading {pagePath(lang, page)}…</p>
			{:else if pageError}
				<p class="handbook-error">{pageError}</p>
				<button onclick={() => open(HOME_PAGE)}>Handbook home</button>
			{:else if doc && rendered}
				{#key `${doc.path}-${branch}-${theme}-${doc.raw}`}
					<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
					<article class="markdown-body handbook-page" use:diagrams onclick={followLink}>
						{@html rendered.html}
					</article>
				{/key}
			{/if}
		</main>
	</div>
{/if}

<style>
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
	}

	.outline {
		overflow: auto;
		padding: 16px;
		border-right: 1px solid var(--border-panel);
	}

	.filters {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding-bottom: 12px;
		border-bottom: 1px solid var(--border-panel);
		margin-bottom: 12px;
	}

	label {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		font-size: 12px;
	}

	select {
		flex: 1;
		min-width: 0;
		padding: 6px 8px;
		font: inherit;
		font-size: 12px;
		color: var(--text-primary);
		border: 1px solid var(--border-input);
		background: var(--bg-input);
		border-radius: 6px;
	}

	button {
		cursor: pointer;
		font: inherit;
		color: var(--text-primary);
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		background: var(--bg-panel);
		padding: 8px 10px;
		text-align: left;
	}

	.outline > button {
		display: block;
		width: 100%;
		border: 0;
		margin: 3px 0;
		background: transparent;
	}

	button:hover,
	button.active,
	.outline > button.active,
	.outline > button:hover {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
	}

	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
		outline-offset: 2px;
	}

	.subheading {
		font-size: 12px;
		color: var(--text-muted);
	}

	.handbook-missing {
		max-width: 640px;
		margin: 80px auto;
		text-align: center;
		color: var(--text-secondary);
	}

	.handbook-header {
		max-width: 960px;
		margin: 0 auto 24px;
		padding-bottom: 12px;
		border-bottom: 1px solid var(--border-panel);
		font-size: 12px;
		color: var(--text-muted);
	}

	.handbook-note {
		padding: 8px 12px;
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		color: var(--text-secondary);
	}

	.handbook-error {
		color: var(--text-secondary);
		overflow-wrap: anywhere;
	}

	.handbook-page {
		max-width: 960px;
		margin: 0 auto;
		line-height: 1.8;
		overflow-wrap: anywhere;
	}

	.handbook-page :global([id]) {
		scroll-margin-top: 16px;
	}

	.handbook-page :global(a) {
		color: var(--tree-selected-text);
	}

	.handbook-page :global(a.unavailable) {
		color: var(--text-muted);
		text-decoration: line-through dotted;
		cursor: not-allowed;
	}

	.handbook-page :global(pre) {
		overflow: auto;
		background: var(--pre-bg);
		padding: 16px;
		border: 1px solid var(--pre-border);
		border-radius: 8px;
	}

	.handbook-page :global(code) {
		font-size: 0.9em;
		color: var(--code-color);
	}

	.handbook-page :global(table) {
		display: block;
		overflow: auto;
		border-collapse: collapse;
	}

	.handbook-page :global(th),
	.handbook-page :global(td) {
		border: 1px solid var(--table-border);
		padding: 8px 12px;
	}

	.handbook-page :global(blockquote) {
		border-left: 3px solid var(--border-panel);
		margin-left: 0;
		padding-left: 16px;
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
