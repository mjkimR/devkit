<script lang="ts">
	import { tick } from 'svelte';
	import type { RepositoryDataSource } from '../../api/repository';
	import {
		readSupportingFile,
		fileUrl,
		repositoryImages,
		type SupportingFile
	} from '../../api/artifacts';
	import { parseBlob, renderDocument, type RepositoryDocument } from '../../api/documents';
	import RawViewer from './RawViewer.svelte';
	import MarkdownArticle from './MarkdownArticle.svelte';
	let {
		source,
		branch,
		path,
		parent = '',
		sourceLabel = '',
		documents = [],
		fragment = '',
		onBack = () => {},
		onOpen = () => {},
		diagrams = () => ({ destroy() {} })
	}: {
		source: RepositoryDataSource | null;
		branch: string;
		path: string;
		parent?: string;
		sourceLabel?: string;
		documents?: RepositoryDocument[];
		fragment?: string;
		onBack?: () => void;
		onOpen?: (path: string, fragment?: string) => void;
		diagrams?: (node: HTMLElement) => { destroy: () => void };
	} = $props();
	let file = $state.raw<SupportingFile | null>(null),
		error = $state(''),
		loading = $state(false),
		raw = $state(false),
		retry = $state(0);
	let preview = $state(''),
		download = $state('');
	let root: HTMLElement;
	const repositorySource = $derived(source),
		repositoryPath = $derived(path),
		repositoryBranch = $derived(branch);
	$effect(() => {
		const repository = repositorySource,
			target = repositoryPath,
			ref = repositoryBranch;
		retry;
		const controller = new AbortController();
		let urls: string[] = [];
		file = null;
		error = '';
		loading = true;
		preview = '';
		download = '';
		raw = false;
		if (repository)
			void readSupportingFile(repository, target, ref, controller.signal)
				.then(async (result) => {
					if (controller.signal.aborted) return;
					file = result;
					download = fileUrl(result);
					urls.push(download);
					if (result.kind === 'image') {
						preview = fileUrl(result, true);
						urls.push(preview);
					}
					loading = false;
				})
				.catch((reason) => {
					if (!controller.signal.aborted) {
						error = String(reason);
						loading = false;
					}
				});
		else {
			loading = false;
			error = 'Repository source unavailable';
		}
		return () => {
			controller.abort();
			urls.forEach((url) => URL.revokeObjectURL(url));
		};
	});
	const rendered = $derived.by(() => {
		if (file?.kind !== 'markdown' || file.text === null) return { html: '', error: '' };
		try {
			return {
				html: renderDocument(parseBlob(path, file.text, 'utf-8'), documents).html,
				error: ''
			};
		} catch (error) {
			return { html: '', error: String(error) };
		}
	});
	const html = $derived(rendered.html);
	$effect(() => {
		const requested = fragment,
			content = file;
		html;
		if (!requested || !content || raw) return;
		let cancelled = false;
		void tick().then(() => {
			if (cancelled || file !== content || fragment !== requested) return;
			root?.querySelectorAll('[id]').forEach((node) => {
				if (node.id.endsWith('--' + requested) || node.id === requested)
					node.scrollIntoView({ block: 'start' });
			});
		});
		return () => {
			cancelled = true;
		};
	});

	function assets(node: HTMLElement) {
		const a = repositoryImages(node, { source, branch }),
			d = diagrams(node);
		return {
			destroy() {
				a.destroy();
				d.destroy();
			}
		};
	}
	function links(node: HTMLElement) {
		node.addEventListener('click', follow);
		return {
			destroy() {
				node.removeEventListener('click', follow);
			}
		};
	}
	function follow(event: MouseEvent) {
		const link = (event.target as Element).closest<HTMLAnchorElement>(
			'a[data-doc-path],a[data-repo-path]'
		);
		if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
		event.preventDefault();
		onOpen(link.dataset.docPath ?? link.dataset.repoPath!, link.dataset.fragment ?? '');
	}
</script>

<section class="supporting-artifact" bind:this={root}>
	<header>
		<button onclick={onBack}>Back{parent ? ' to ' + parent : ''}</button>
		<h2>{path}</h2>
		<p>Source: {sourceLabel || branch}</p>
		{#if fragment}<small>Requested fragment: {fragment}</small>{/if}
	</header>
	{#if loading}<p role="status">Loading supporting file…</p>{/if}
	{#if error}<p role="status">File unavailable: {path} — {error}</p>
		<button onclick={() => retry++}>Retry file</button>{/if}
	{#if file}
		<p>Format: {file.mime}</p>
		{#if file.text !== null}<button onclick={() => (raw = !raw)}
				>{raw ? 'Rendered' : 'View raw'}</button
			>{/if}
		{#if download}<a href={download} download={path.split('/').at(-1)}>Download file</a>{/if}
		{#if raw && file.text !== null}<RawViewer content={file.text} />
		{:else if file.kind === 'image' && preview}<img src={preview} alt={path} />
		{:else if file.kind === 'markdown' && rendered.error}<p role="status">
				Markdown preview unavailable: {rendered.error}. View raw or download the source.
			</p>
		{:else if file.kind === 'markdown'}<div aria-label="Supporting Markdown" use:links>
				{#key html}<MarkdownArticle {html} diagramAction={assets} />{/key}
			</div>
		{:else if file.kind === 'text'}<RawViewer content={file.text ?? ''} />
		{:else}<p>
				Unsupported preview format for {path}. Download the available bytes or inspect readable raw
				source.
			</p>{/if}
	{/if}
</section>

<style>
	.supporting-artifact {
		flex: 1;
		min-width: 0;
		overflow: auto;
		box-sizing: border-box;
		padding: 20px;
		overflow-wrap: anywhere;
	}
	img {
		max-width: 100%;
		height: auto;
	}
	button,
	a {
		margin: 8px;
		color: var(--text-primary);
		font: inherit;
	}
	button {
		background: var(--bg-panel);
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		padding: 8px;
		cursor: pointer;
	}
</style>
