import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { RepositoryDataSource } from './repository';
import {
	headingSlug,
	parseBlob,
	resolvePath,
	type Heading,
	type RenderedDocument,
	type RepositoryDocument
} from './documents';

/** `handbook/manifest.json` of `CAP-DLV-release-handbook`; only the fields the viewer shows. */
export interface HandbookManifest {
	tag: string;
	langs: string[];
	generated?: string;
	repository?: string;
}
export type Staleness = 'ahead' | 'equal' | 'behind' | 'absent';

export const MANIFEST_PATH = 'handbook/manifest.json';
export const HOME_PAGE = 'README.md';
const LANGUAGE_KEY = 'sdd-handbook-lang';
const HEADING_PREFIX = 'handbook--';

/** A host signals an absent file by rejecting with a message that starts with `HTTP 404` (`CAP-VIEW-repository-viewer` §6). */
export const isAbsent = (error: unknown) =>
	/^HTTP 404(?:\b|:)/.test(error instanceof Error ? error.message : String(error));

const text = (blob: { content: string; encoding: string }, path: string) =>
	parseBlob(path, blob.content, blob.encoding).raw;

/** The manifest, or `null` when the repository has none; any other failure rejects. */
export async function loadManifest(
	source: RepositoryDataSource,
	ref: string,
	signal: AbortSignal
): Promise<HandbookManifest | null> {
	let blob;
	try {
		blob = await source.blob(MANIFEST_PATH, ref, signal);
	} catch (error) {
		if (isAbsent(error)) return null;
		throw error;
	}
	let value: any;
	try {
		value = JSON.parse(text(blob, MANIFEST_PATH));
	} catch (error) {
		throw new Error(`${MANIFEST_PATH} is not valid JSON: ${(error as Error).message}`);
	}
	if (
		!value ||
		typeof value !== 'object' ||
		typeof value.tag !== 'string' ||
		!Array.isArray(value.langs) ||
		!value.langs.every((lang: unknown) => typeof lang === 'string') ||
		!value.langs.includes('en')
	)
		throw new Error(`${MANIFEST_PATH} needs a string "tag" and "langs" including "en"`);
	return {
		tag: value.tag,
		langs: value.langs,
		generated: typeof value.generated === 'string' ? value.generated : undefined,
		repository: typeof value.repository === 'string' ? value.repository : undefined
	};
}

const VERSION_PATTERN = /^v?(\d+)\.(\d+)\.(\d+)$/;

/** The repository's `VERSION`, or `null` when it is absent, unreadable or not `major.minor.patch`. */
export async function loadVersion(
	source: RepositoryDataSource,
	ref: string,
	signal: AbortSignal
): Promise<string | null> {
	try {
		const value = text(await source.blob('VERSION', ref, signal), 'VERSION').trim();
		return VERSION_PATTERN.test(value) && !value.startsWith('v') ? value : null;
	} catch {
		return null;
	}
}

/** The manifest tag ordered against `v<VERSION>` (`ADR-handbook-staleness-from-version`). */
export function staleness(tag: string, version: string | null): Staleness {
	const a = tag.match(VERSION_PATTERN),
		b = version?.match(VERSION_PATTERN);
	if (!a || !b) return 'absent';
	for (let i = 1; i <= 3; i++) {
		const diff = Number(a[i]) - Number(b[i]);
		if (diff) return diff > 0 ? 'ahead' : 'behind';
	}
	return 'equal';
}

/** The remembered language if listed, else the browser language if listed, else `en`. */
export function initialLanguage(langs: string[]): string {
	let stored: string | null = null;
	try {
		stored = typeof localStorage === 'undefined' ? null : localStorage.getItem(LANGUAGE_KEY);
	} catch {
		stored = null;
	}
	if (stored && langs.includes(stored)) return stored;
	const browser =
		typeof navigator === 'undefined' ? [] : (navigator.languages ?? [navigator.language]);
	for (const tag of browser) {
		const lang = String(tag ?? '')
			.toLowerCase()
			.split('-')[0];
		if (langs.includes(lang)) return lang;
	}
	return 'en';
}

export function rememberLanguage(lang: string) {
	try {
		localStorage?.setItem(LANGUAGE_KEY, lang);
	} catch {
		// Storage may be unavailable (private mode); the choice then lasts for the mount only.
	}
}

export const pagePath = (lang: string, page: string) => `handbook/${lang}/${page}`;

/** `handbook/<lang>/<page>` split into its language and page, or `null` for another path. */
export function parsePagePath(path: string): { lang: string; page: string } | null {
	const match = path.match(/^handbook\/([^/]+)\/(.+\.md)$/);
	return match ? { lang: match[1], page: match[2] } : null;
}

export async function loadPage(
	source: RepositoryDataSource,
	ref: string,
	lang: string,
	page: string,
	signal: AbortSignal
): Promise<RepositoryDocument> {
	const path = pagePath(lang, page);
	const blob = await source.blob(path, ref, signal);
	return parseBlob(path, blob.content, blob.encoding);
}

/**
 * One handbook page through the Markdown and DOMPurify path, without the Living Spec index. Links are rewritten after
 * sanitization: pages of the same language open in the tab, external links open a new browsing context, and every
 * other relative link is unavailable.
 */
export function renderHandbookPage(doc: RepositoryDocument, lang: string): RenderedDocument {
	const wrapper = document.createElement('div');
	wrapper.innerHTML = DOMPurify.sanitize(
		marked.parse(doc.body, { gfm: true, breaks: true }) as string,
		{ USE_PROFILES: { html: true } }
	);
	const headings: Heading[] = [];
	const counts = new Map<string, number>();
	for (const node of wrapper.querySelectorAll('h1,h2,h3,h4,h5,h6')) {
		const title = node.textContent ?? '';
		const slug = headingSlug(title) || 'section';
		const n = counts.get(slug) ?? 0;
		counts.set(slug, n + 1);
		node.id = `${HEADING_PREFIX}${slug}${n ? `-${n}` : ''}`;
		headings.push({ id: node.id, title, level: Number(node.tagName.slice(1)) });
	}
	const root = `handbook/${lang}/`;
	for (const a of wrapper.querySelectorAll<HTMLAnchorElement>('a[href]')) {
		const href = a.getAttribute('href')!;
		if (/^https?:/i.test(href)) {
			a.setAttribute('target', '_blank');
			a.setAttribute('rel', 'noopener noreferrer');
			continue;
		}
		if (/^[a-z][a-z\d+.-]*:/i.test(href)) continue;
		const resolved = resolvePath(doc.path, href);
		if (resolved && resolved.path.startsWith(root) && resolved.path.endsWith('.md')) {
			a.dataset.handbookPage = resolved.path.slice(root.length);
			a.dataset.fragment = resolved.fragment;
			continue;
		}
		a.removeAttribute('href');
		a.classList.add('unavailable');
		a.setAttribute('aria-disabled', 'true');
		a.setAttribute('title', `Not part of the handbook: ${href}`);
	}
	return { html: wrapper.innerHTML, headings };
}

/** The element a fragment names: an element with that exact `id`, else the prefixed heading slug. */
export function fragmentTarget(root: ParentNode, fragment: string): HTMLElement | null {
	if (!fragment) return null;
	const elements = [...root.querySelectorAll<HTMLElement>('[id]')];
	return (
		elements.find((el) => el.id === fragment) ??
		elements.find((el) => el.id === `${HEADING_PREFIX}${fragment}`) ??
		elements.find((el) => el.id === `${HEADING_PREFIX}${headingSlug(fragment)}`) ??
		null
	);
}
