import { marked } from 'marked';
import DOMPurify from 'dompurify';
import {
	ID_SOURCE,
	ID_PATTERN,
	documentId,
	identityResolver,
	isArtifactPath,
	formalArea
} from './identity';
import { visibleLines } from './markdown';
import { parseFrontmatter } from './frontmatter';
import {
	normalizeTree,
	type FileSource,
	type RepositoryDataSource,
	type TreeItem
} from './repository';
import { cachedResult, cacheGeneration, cacheResult } from './cache';

export interface RepositoryDocument {
	path: string;
	meta: Record<string, any>;
	body: string;
	raw: string;
	title: string;
}
export interface Heading {
	id: string;
	title: string;
	level: number;
}
export interface RenderedDocument {
	html: string;
	headings: Heading[];
}
export const documentAnchor = (path: string) => `doc-${encodeURIComponent(path)}`;
export const headingSlug = (title: string) =>
	title
		.toLowerCase()
		.trim()
		.replace(/[^\p{L}\p{N}\s_-]/gu, '')
		.replace(/\s+/g, '-');

export function parseBlob(path: string, content: string, encoding: string): RepositoryDocument {
	const raw =
		encoding === 'utf-8'
			? content
			: encoding === 'base64'
				? new TextDecoder('utf-8', { fatal: true }).decode(
						Uint8Array.from(atob(content.replace(/\s/g, '')), (c) => c.charCodeAt(0))
					)
				: (() => {
						throw new Error(`Unsupported encoding: ${encoding}`);
					})();
	const parsed = parseFrontmatter(raw);
	const meta = parsed.meta ?? {};
	const body = parsed.body;
	const title =
		typeof meta.title === 'string'
			? meta.title
			: (body.match(/^#\s+(.+)$/m)?.[1] ?? path.split('/').at(-1)!);
	return { path, meta, body, raw, title };
}

export interface DocumentIndex {
	documents: RepositoryDocument[];
	errors: string[];
	/** Source tree inventory, collected during the same scan without reading supporting blobs. */
	files?: TreeItem[];
}

/** One recursive listing per root, then the selected bodies through six continuous workers. */
export async function scanDocuments(
	source: FileSource,
	signal: AbortSignal,
	roots: string[],
	select: (item: TreeItem) => boolean = (item) => item.name.endsWith('.md')
): Promise<DocumentIndex> {
	type Job = { path: string; kind: 'tree' | 'blob' };
	const jobs: Job[] = roots.map((path) => ({ path, kind: 'tree' }));
	const seen = new Set<string>();
	const documents: RepositoryDocument[] = [];
	const files = new Map<string, TreeItem>();
	const errors: string[] = [];
	await new Promise<void>((resolve) => {
		let active = 0;
		function pump() {
			if (signal.aborted) jobs.length = 0;
			while (active < 6 && jobs.length) {
				const job = jobs.shift()!;
				const key = `${job.kind}:${job.path}`;
				if (seen.has(key)) continue;
				seen.add(key);
				active++;
				void (async () => {
					try {
						if (job.kind === 'tree') {
							const items = normalizeTree(await source.treeRecursive(job.path, signal));
							for (const item of items) {
								if (
									!item.path.startsWith(`${job.path}/`) ||
									item.path.split('/').some((p) => p === '..' || p === '.')
								)
									continue;
								if (item.type !== 'blob') continue;
								files.set(item.path, item);
								if (select(item)) jobs.push({ path: item.path, kind: 'blob' });
							}
						} else {
							const blob = await source.blob(job.path, signal);
							documents.push(parseBlob(job.path, blob.content, blob.encoding));
						}
					} catch (error) {
						const message = error instanceof Error ? error.message : String(error);
						if (!signal.aborted) errors.push(`${job.path}: ${message}`);
					} finally {
						active--;
						pump();
					}
				})();
			}
			if (!active && !jobs.length) resolve();
		}
		pump();
	});
	return {
		documents: documents.sort((a, b) => a.path.localeCompare(b.path, undefined, { numeric: true })),
		errors,
		files: [...files.values()].sort((a, b) => a.path.localeCompare(b.path))
	};
}

export async function indexDocuments(
	source: RepositoryDataSource,
	branch: string,
	signal: AbortSignal
): Promise<DocumentIndex> {
	const cached = cachedResult<DocumentIndex>(source, branch, 'documents');
	if (cached && !signal.aborted) return cached;
	const generation = cacheGeneration(source);
	const result = await scanDocuments(
		source,
		signal,
		['docs', 'specs'],
		(item) => item.name.endsWith('.md') && !isArtifactPath(item.path)
	);
	if (!signal.aborted && !result.errors.length)
		cacheResult(source, branch, 'documents', result, generation);
	return result;
}

export function idIndex(documents: RepositoryDocument[]) {
	const resolver = identityResolver(documents);
	return new Map(
		[...resolver.keys].flatMap((id) => {
			const doc = resolver.resolve(id).document;
			return doc ? [[id, doc] as const] : [];
		})
	);
}

export function visibleReferences(doc: RepositoryDocument): string[] {
	const refs: string[] = [];
	for (const line of visibleLines(doc.body.split('\n')).values()) {
		const pattern = new RegExp('`(' + ID_SOURCE + ')`|\\[(' + ID_SOURCE + ')\\]', 'g');
		for (const match of line.matchAll(pattern)) {
			const id = match[1] ?? match[2];
			if (line.trimStart().startsWith('# ') && id === documentId(doc)) continue;
			refs.push(id);
		}
	}
	return [...new Set(refs)];
}

export function resolvePath(origin: string, href: string) {
	if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(href)) return null;
	const [pathname, rawFragment = ''] = href.split('#');
	let fragment: string;
	try {
		fragment = decodeURIComponent(rawFragment);
	} catch {
		return null;
	}
	let decoded: string;
	try {
		decoded = decodeURIComponent(pathname);
	} catch {
		return null;
	}
	if (/[\\\u0000-\u001f]/.test(decoded) || decoded.split('/').includes('.git')) return null;
	const parts = decoded
		? decoded.startsWith('/')
			? []
			: origin.split('/').slice(0, -1)
		: origin.split('/');
	for (const part of decoded.split('/')) {
		if (!part || part === '.') continue;
		if (part === '..') {
			if (!parts.length) return null;
			parts.pop();
		} else parts.push(part);
	}
	return { path: parts.join('/'), fragment };
}

export function renderDocument(
	doc: RepositoryDocument,
	documents: RepositoryDocument[]
): RenderedDocument {
	const wrapper = document.createElement('div');
	// Sanitize in DOMPurify's inert document before assigning HTML: relative images must never hit the viewer origin.
	DOMPurify.addHook('afterSanitizeAttributes', (node) => {
		const element = node as Element;
		for (const name of [
			'data-doc-path',
			'data-repo-path',
			'data-repo-image',
			'data-repo-image-fragment',
			'data-origin-path',
			'data-fragment',
			'srcset'
		])
			element.removeAttribute?.(name);
		if (node.nodeName !== 'IMG') return;
		const image = node as Element;
		image.removeAttribute('srcset');
		const src = image.getAttribute('src');
		if (!src || /^https?:/i.test(src)) return;
		image.removeAttribute('src');
		const resolved = resolvePath(doc.path, src);
		if (resolved) {
			image.setAttribute('data-repo-image', resolved.path);
			image.setAttribute(
				'data-repo-image-fragment',
				src.includes('#') ? src.slice(src.indexOf('#') + 1) : ''
			);
		} else image.setAttribute('alt', `Unavailable image: ${src}`);
	});
	try {
		wrapper.innerHTML = DOMPurify.sanitize(
			marked.parse(doc.body, { gfm: true, breaks: true }) as string,
			{ USE_PROFILES: { html: true }, FORBID_TAGS: ['video', 'audio', 'source', 'track'] }
		);
	} finally {
		DOMPurify.removeHook('afterSanitizeAttributes');
	}
	const headings: Heading[] = [];
	const counts = new Map<string, number>();
	for (const node of wrapper.querySelectorAll('h1,h2,h3,h4,h5,h6')) {
		const rawTitle = node.textContent ?? '';
		const selfPrefix = `[${doc.meta.id}]`;
		const title =
			node.tagName === 'H1' && typeof doc.meta.id === 'string' && rawTitle.startsWith(selfPrefix)
				? rawTitle.slice(selfPrefix.length).trim()
				: rawTitle;
		if (title !== rawTitle) node.textContent = title;
		const slug = node.id || headingSlug(rawTitle) || 'section';
		const n = counts.get(slug) ?? 0;
		counts.set(slug, n + 1);
		const id = `${documentAnchor(doc.path)}--${slug}${n ? `-${n}` : ''}`;
		node.id = id;
		headings.push({ id, title, level: Number(node.tagName.slice(1)) });
	}
	for (const node of wrapper.querySelectorAll<HTMLElement>('[id]'))
		if (!/^H[1-6]$/.test(node.tagName)) node.id = documentAnchor(doc.path) + '--' + node.id;
	const byId = idIndex(documents);
	function linkNode(node: HTMLElement, target: RepositoryDocument, fragment = '') {
		node.setAttribute('href', `#${documentAnchor(target.path)}${fragment ? `--${fragment}` : ''}`);
		node.dataset.docPath = target.path;
		node.dataset.originPath = doc.path;
		node.dataset.fragment = fragment;
	}
	for (const a of wrapper.querySelectorAll<HTMLAnchorElement>('a[href]')) {
		const href = a.getAttribute('href')!;
		const byReference = byId.get(href) ?? byId.get(href.replace(/^\[|\]$/g, ''));
		const resolved = resolvePath(doc.path, href);
		const target = byReference ?? (resolved && documents.find((d) => d.path === resolved.path));
		if (target && !isArtifactPath(target.path))
			linkNode(a, target, byReference ? '' : resolved!.fragment);
		else if (ID_PATTERN.test(href)) {
			a.removeAttribute('href');
			a.title = `Unavailable reference: ${href}`;
		} else if (resolved) {
			a.setAttribute('href', '#');
			a.dataset.repoPath = resolved.path;
			a.dataset.fragment = resolved.fragment;
			a.dataset.originPath = doc.path;
		} else if (!/^(?:https?:|mailto:)/i.test(href)) {
			a.removeAttribute('href');
			a.title = `Unavailable repository path: ${href}`;
		}
	}
	for (const image of wrapper.querySelectorAll<HTMLImageElement>('img[src]')) {
		const href = image.getAttribute('src')!;
		const resolved = resolvePath(doc.path, href);
		if (resolved) {
			image.removeAttribute('src');
			image.dataset.repoImage = resolved.path;
			image.dataset.repoImageFragment = href.includes('#') ? href.slice(href.indexOf('#') + 1) : '';
		} else if (!/^https?:/i.test(href)) {
			image.removeAttribute('src');
			image.alt = `Unavailable image: ${href}`;
		}
	}
	// ID references occur both as [ID] prose and exact inline code; fenced code is untouched.
	const walker = document.createTreeWalker(wrapper, NodeFilter.SHOW_TEXT);
	const nodes: Text[] = [];
	while (walker.nextNode()) nodes.push(walker.currentNode as Text);
	for (const node of nodes) {
		const parent = node.parentElement;
		if (!parent || parent.closest('a,pre,h1,h2,h3,h4,h5,h6')) continue;
		const value = node.textContent ?? '';
		const exactCode = parent.tagName === 'CODE' && byId.has(value);
		const pattern = exactCode ? /^(.*)$/g : new RegExp(`\\[(${ID_SOURCE})\\]`, 'g');
		let match: RegExpExecArray | null;
		let cursor = 0;
		const replacement = document.createDocumentFragment();
		while ((match = pattern.exec(value))) {
			const target = byId.get(match[1]);
			if (!target) continue;
			replacement.append(value.slice(cursor, match.index));
			const a = document.createElement('a');
			a.textContent = match[0];
			linkNode(a, target);
			replacement.append(a);
			cursor = match.index + match[0].length;
		}
		if (cursor) {
			replacement.append(value.slice(cursor));
			node.replaceWith(replacement);
		}
	}
	return { html: wrapper.innerHTML, headings };
}

// Steering documents are ID-free project background, not a document kind, so the group is a viewer literal: every
// file under docs/steering/ and a package glossary (docs/packages/<name>/glossary.md).
const STEERING = 'Steering';

export function bookGroup(doc: RepositoryDocument) {
	const path = doc.path.replace(/^docs\/packages\/[^/]+\//, 'docs/');
	if (
		!path.startsWith('docs/') ||
		/\/(proposals|materials)\//.test(path) ||
		/\/README\.md$/i.test(path) ||
		isArtifactPath(path)
	)
		return null;
	if (path.startsWith('docs/steering/') || /^docs\/packages\/[^/]+\/glossary\.md$/.test(doc.path))
		return STEERING;
	for (const [directory, title] of [
		['architecture', 'Architecture'],
		['domain', 'Domain'],
		['designs', 'Designs'],
		['operations', 'Operations'],
		['capabilities', 'Capabilities'],
		['usecases', 'Use Cases'],
		['ux', 'UX'],
		['decisions', 'Decisions'],
		['development', 'Development']
	]) {
		if (path.startsWith(`docs/${directory}/`)) return title;
	}
	return 'Overview';
}
export const bookGroups = [
	'Overview',
	'Architecture',
	'Domain',
	'Capabilities',
	'Use Cases',
	'UX',
	'Designs',
	'Operations',
	STEERING,
	'Decisions',
	'Development'
];
export function byBookArea(documents: RepositoryDocument[]) {
	return [...documents].sort(
		(a, b) => formalArea(a).localeCompare(formalArea(b)) || a.path.localeCompare(b.path)
	);
}
export const namespaceOf = (doc: RepositoryDocument) =>
	doc.path.match(/^docs\/packages\/([^/]+)\//)?.[1] ?? String(doc.meta.namespace ?? 'global');

// Markdown list tokens exclude checkbox examples inside fenced code.
export function taskProgress(body: string) {
	let total = 0,
		checked = 0;
	function visit(tokens: any[]) {
		for (const token of tokens) {
			if (token.type === 'list')
				for (const item of token.items) {
					if (item.task) {
						total++;
						if (item.checked) checked++;
					}
					visit(item.tokens ?? []);
				}
			else if (token.type === 'blockquote') visit(token.tokens ?? []);
		}
	}
	visit(marked.lexer(body));
	return { total, checked };
}
