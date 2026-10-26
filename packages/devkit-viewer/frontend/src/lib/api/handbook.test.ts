import DOMPurify from 'dompurify';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	fragmentTarget,
	initialLanguage,
	isAbsent,
	loadManifest,
	loadVersion,
	rememberLanguage,
	renderHandbookPage,
	staleness
} from './handbook';
import { parseBlob } from './documents';
import type { RepositoryDataSource } from './repository';

const source = (files: Record<string, string>, failure?: Error): RepositoryDataSource => ({
	info: async () => ({ default_branch: 'main' }),
	tree: vi.fn(async () => ({ items: [] })),
	blob: vi.fn(async (path: string) => {
		if (failure) throw failure;
		if (!(path in files)) throw new Error('HTTP 404: Not Found');
		return { path, content: files[path], encoding: 'utf-8' };
	})
});
const signal = new AbortController().signal;

afterEach(() => {
	localStorage.clear();
	vi.unstubAllGlobals();
});

describe('handbook reads', () => {
	it('treats only an HTTP 404 rejection as an absent manifest', async () => {
		expect(isAbsent(new Error('HTTP 404: Not Found'))).toBe(true);
		expect(isAbsent(new Error('HTTP 4040'))).toBe(false);
		expect(await loadManifest(source({}), 'main', signal)).toBeNull();
		await expect(
			loadManifest(source({}, new Error('HTTP 500: Server Error')), 'main', signal)
		).rejects.toThrow('HTTP 500');
		await expect(
			loadManifest(source({ 'handbook/manifest.json': '{' }), 'main', signal)
		).rejects.toThrow('not valid JSON');
		await expect(
			loadManifest(
				source({ 'handbook/manifest.json': '{"tag": "v1.0.0", "langs": ["ko"]}' }),
				'main',
				signal
			)
		).rejects.toThrow('"langs" including "en"');
		expect(
			await loadManifest(
				source({
					'handbook/manifest.json': '{"tag": "v1.0.0", "langs": ["en"], "generated": "2026-10-26"}'
				}),
				'main',
				signal
			)
		).toEqual({ tag: 'v1.0.0', langs: ['en'], generated: '2026-10-26', repository: undefined });
	});

	it('reads VERSION as major.minor.patch, else absent', async () => {
		expect(await loadVersion(source({ VERSION: '0.1.3\n' }), 'main', signal)).toBe('0.1.3');
		expect(await loadVersion(source({ VERSION: 'next' }), 'main', signal)).toBeNull();
		expect(await loadVersion(source({}), 'main', signal)).toBeNull();
	});

	it('orders the manifest tag against v<VERSION>', () => {
		expect(staleness('v0.1.4', '0.1.3')).toBe('ahead');
		expect(staleness('v0.1.4', '0.1.4')).toBe('equal');
		expect(staleness('v0.1.4', '0.1.5')).toBe('behind');
		expect(staleness('v0.1.4', '0.2.0')).toBe('behind');
		expect(staleness('v0.10.0', '0.9.9')).toBe('ahead');
		expect(staleness('v0.1.4', null)).toBe('absent');
		expect(staleness('release-4', '0.1.4')).toBe('absent');
	});
});

describe('handbook language', () => {
	it('prefers the stored choice, then the browser language, then en', () => {
		vi.stubGlobal('navigator', { languages: ['ko-KR', 'en-US'], language: 'ko-KR' });
		expect(initialLanguage(['en', 'ko'])).toBe('ko');
		expect(initialLanguage(['en', 'ja'])).toBe('en');
		rememberLanguage('ja');
		expect(initialLanguage(['en', 'ja'])).toBe('ja');
		expect(initialLanguage(['en', 'ko'])).toBe('ko');
		vi.stubGlobal('navigator', { languages: ['fr'], language: 'fr' });
		localStorage.clear();
		expect(initialLanguage(['en', 'ko'])).toBe('en');
	});
});

describe('handbook page rendering', () => {
	const page = (lang: string, body: string) =>
		parseBlob(`handbook/${lang}/journeys/x.md`, `---\ntitle: X\n---\n${body}`, 'utf-8');

	it('relies on DOMPurify for ids and on post-sanitize rewriting for target and rel', () => {
		// The settings of the existing Markdown path keep id and rel but drop target, so the renderer sets both.
		const clean = DOMPurify.sanitize(
			'<a id="journeys"></a><a href="https://x.test" target="_blank" rel="opener">x</a>',
			{ USE_PROFILES: { html: true } }
		);
		expect(clean).toBe('<a id="journeys"></a><a href="https://x.test" rel="opener">x</a>');
	});

	it('keeps raw id anchors and opens external links in a new browsing context', () => {
		const { html } = renderHandbookPage(
			page(
				'ko',
				'<a id="journeys"></a>\n\n## 여정\n\n[src](https://github.com/o/r/blob/v1/docs/a.md) <a href="https://x.test" target="_self" onclick="alert(1)">x</a>\n'
			),
			'ko'
		);
		const root = document.createElement('div');
		root.innerHTML = html;
		expect(root.querySelector('a#journeys')).not.toBeNull();
		expect(root.querySelector('h2')?.id).toBe('handbook--여정');
		const external = [...root.querySelectorAll('a[href^="https:"]')];
		expect(external).toHaveLength(2);
		for (const link of external) {
			expect(link.getAttribute('target')).toBe('_blank');
			expect(link.getAttribute('rel')).toBe('noopener noreferrer');
			expect(link.getAttribute('onclick')).toBeNull();
		}
	});

	it('opens pages of the same language and marks every other relative link unavailable', () => {
		const { html, headings } = renderHandbookPage(
			page(
				'en',
				'# X\n\n## Steps\n\n## Steps\n\n[home](../README.md#journeys) [peer](y.md) [here](#steps) [docs](../../../docs/a.md) [ko](../../ko/README.md) [img](../logo.png)\n'
			),
			'en'
		);
		expect(headings.map((h) => h.id)).toEqual([
			'handbook--x',
			'handbook--steps',
			'handbook--steps-1'
		]);
		const root = document.createElement('div');
		root.innerHTML = html;
		const links = [...root.querySelectorAll('a')];
		expect(links.map((a) => [a.textContent, a.dataset.handbookPage, a.dataset.fragment])).toEqual([
			['home', 'README.md', 'journeys'],
			['peer', 'journeys/y.md', ''],
			['here', 'journeys/x.md', 'steps'],
			['docs', undefined, undefined],
			['ko', undefined, undefined],
			['img', undefined, undefined]
		]);
		for (const link of links.slice(3)) {
			expect(link.hasAttribute('href')).toBe(false);
			expect(link.classList.contains('unavailable')).toBe(true);
		}
	});

	it('resolves a fragment to an exact id first, then to the heading slug', () => {
		const root = document.createElement('div');
		root.innerHTML =
			'<a id="journeys"></a><h2 id="handbook--journeys">J</h2><h2 id="handbook--areas">A</h2>';
		expect(fragmentTarget(root, 'journeys')?.tagName).toBe('A');
		expect(fragmentTarget(root, 'areas')?.id).toBe('handbook--areas');
		expect(fragmentTarget(root, 'missing')).toBeNull();
		expect(fragmentTarget(root, '')).toBeNull();
	});
});
