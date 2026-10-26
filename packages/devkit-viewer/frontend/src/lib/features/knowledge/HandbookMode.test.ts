import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import KnowledgeViews from './KnowledgeViews.svelte';
import type { RepositoryDataSource } from '../../api/repository';
import { bookGroup, bookGroups, documentAnchor, parseBlob } from '../../api/documents';

const doc = (id: string, title: string) =>
	`---\nid: ${id}\ntitle: ${title}\nstatus: active\n---\n# ${title}\n`;
const living: Record<string, string> = {
	'docs/README.md': '# Docs\n',
	'docs/steering/glossary.md': '---\ntitle: Glossary\nsummary: Terms.\n---\n# Glossary\n',
	'docs/development/dev.md': '# Dev notes\n',
	'docs/decisions/2026-10/ADR-a.md': doc('ADR-a', 'Decision A'),
	'docs/usecases/UC-a.md': doc('UC-a', 'Use case A'),
	'docs/capabilities/x/CAP-a.md': doc('CAP-a', 'Capability A'),
	'docs/architecture/ARCH-a.md': doc('ARCH-a', 'Architecture A'),
	'docs/overview.md': '# Overview\n',
	'docs/materials/m.md': '# Material\n',
	'docs/proposals/PROP-a/proposal.md':
		'---\nid: PROP-a\ntitle: Proposal A\nstatus: draft\n---\n# Proposal A\n',
	'specs/2026-10/20261026-a/spec.md': '---\nid: SPEC-a\ntitle: Spec A\nstatus: planned\n---\n# A\n'
};
const page = (title: string, body: string) => `---\ntitle: ${title}\n---\n# ${title}\n\n${body}`;
const handbook: Record<string, string> = {
	'handbook/manifest.json': JSON.stringify({
		tag: 'v0.1.4',
		source_commit: 'abc',
		repository: 'o/r',
		langs: ['en', 'ko'],
		generated: '2026-10-26'
	}),
	VERSION: '0.1.4\n',
	'handbook/en/README.md': page(
		'devkit handbook',
		'Start with [Concepts](concepts.md) or [a journey](journeys/x.md).\n\nSource: [ARCH](https://github.com/o/r/blob/v0.1.4/docs/a.md), outside: [docs](../../docs/a.md), [gone](missing.md).\n\n## Journeys\n\nList.\n\n## Areas\n\nTable.\n'
	),
	'handbook/en/concepts.md': page('Concepts', 'See the [journeys](README.md#journeys).\n'),
	'handbook/en/journeys/x.md': page('Journey X', '## Steps\n\nDo it.\n'),
	'handbook/ko/README.md': page(
		'devkit 핸드북',
		'[개념](concepts.md)\n\n<a id="journeys"></a>\n\n## 여정\n\n목록.\n'
	),
	'handbook/ko/concepts.md': page('개념', '[여정](README.md#journeys)을 보십시오.\n'),
	'handbook/ko/journeys/x.md': page('여정 X', '## 단계\n')
};

function repository(files: Record<string, string>, manifestFailure?: string) {
	const listing = (path: string) => ({
		items: Object.keys(files)
			.filter((file) => file.startsWith(`${path}/`))
			.map((file) => ({ name: file.split('/').at(-1)!, path: file, type: 'blob' }))
	});
	const source = {
		info: async () => ({ default_branch: 'main' }),
		tree: vi.fn(async (path: string) => listing(path)),
		treeRecursive: vi.fn(async (path: string) => listing(path)),
		blob: vi.fn(async (path: string) => {
			if (path === 'handbook/manifest.json' && manifestFailure) throw new Error(manifestFailure);
			if (!(path in files)) throw new Error('HTTP 404: Not Found');
			return { path, content: files[path], encoding: 'utf-8' };
		})
	} satisfies RepositoryDataSource;
	return source;
}
type Source = ReturnType<typeof repository>;
const blobs = (source: Source) => source.blob.mock.calls.map(([path]) => path);
const scans = (source: Source) =>
	[...source.tree.mock.calls, ...source.treeRecursive.mock.calls].map(([path]) => path);

const props = (source: RepositoryDataSource, extra: Record<string, unknown> = {}) => ({
	view: 'book' as const,
	source,
	branch: 'main',
	theme: 'dark',
	requestedPath: '',
	requestedAnchor: '',
	onOpen: vi.fn(),
	onLocation: vi.fn(),
	diagrams: () => ({ destroy() {} }),
	...extra
});
const pageTitle = () => document.querySelector('.handbook-page h1')?.textContent;

beforeEach(() => {
	Element.prototype.scrollIntoView = vi.fn();
	vi.stubGlobal(
		'IntersectionObserver',
		class {
			observe() {}
			disconnect() {}
		}
	);
	vi.stubGlobal('navigator', { languages: ['en-US'], language: 'en-US' });
});
afterEach(() => {
	cleanup();
	localStorage.clear();
	vi.unstubAllGlobals();
});

describe('reading tab: handbook first', () => {
	it('opens the handbook within the read budget and renders no chapter', async () => {
		const source = repository({ ...living, ...handbook });
		render(KnowledgeViews, props(source));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		await waitFor(() =>
			expect(document.querySelector('.handbook-header')?.getAttribute('data-staleness')).toBe(
				'equal'
			)
		);
		expect(document.querySelector('.handbook-header')?.textContent).toContain('v0.1.4');
		expect(document.querySelector('.handbook-header')?.textContent).toContain('2026-10-26');
		expect(blobs(source).sort()).toEqual([
			'VERSION',
			'handbook/en/README.md',
			'handbook/manifest.json'
		]);
		expect(scans(source)).toEqual([]);
		expect(document.querySelector('section.chapter')).toBeNull();
		expect(screen.getByRole('button', { name: 'Handbook home' })).toBeTruthy();
		expect(screen.getByRole('button', { name: 'Journeys' })).toBeTruthy();
	});

	it('shows the absence and the book control after one read', async () => {
		const source = repository(living);
		render(KnowledgeViews, props(source));
		await screen.findByText(/This repository has no/);
		expect(document.querySelector('.handbook-absent code')?.textContent).toBe(
			'handbook/manifest.json'
		);
		expect(screen.getByRole('button', { name: 'Living Spec book' })).toBeTruthy();
		expect(blobs(source)).toEqual(['handbook/manifest.json']);
		expect(scans(source)).toEqual([]);
	});

	it.each([
		['HTTP 500: Server Error', undefined, 'HTTP 500'],
		[undefined, '{', 'not valid JSON'],
		[undefined, '{"tag": "v1.0.0", "langs": ["ko"]}', '"langs" including "en"']
	])('shows a manifest failure with the control (%s %s)', async (failure, content, shown) => {
		const files = content ? { ...living, 'handbook/manifest.json': content } : living;
		const source = repository(files, failure);
		render(KnowledgeViews, props(source));
		await waitFor(() =>
			expect(document.querySelector('.handbook-error')?.textContent).toContain(shown)
		);
		expect(screen.getByRole('button', { name: 'Living Spec book' })).toBeTruthy();
		expect(scans(source)).toEqual([]);
	});

	it.each([
		['0.1.3', 'ahead', 'upcoming release', false],
		['0.1.4', 'equal', 'Snapshot of', false],
		['0.1.5', 'behind', 'Snapshot of', true],
		[undefined, 'absent', 'Snapshot of', false],
		['next', 'absent', 'Snapshot of', false]
	])('VERSION %s renders the %s header', async (version, state, text, note) => {
		const files: Record<string, string> = { ...handbook };
		if (version === undefined) delete files.VERSION;
		else files.VERSION = `${version}\n`;
		render(KnowledgeViews, props(repository(files)));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		const header = document.querySelector('.handbook-header')!;
		await waitFor(() => expect(header.getAttribute('data-staleness')).toBe(state));
		expect(header.textContent).toContain(text);
		expect(header.textContent).toContain('v0.1.4');
		const shown = header.querySelector('.handbook-note');
		expect(Boolean(shown)).toBe(note);
		if (note) {
			expect(shown!.textContent).toContain('0.1.5');
			expect(shown!.textContent).toContain('Living Spec book shows the current contracts');
			expect(shown!.getAttribute('role')).toBe('note');
		}
	});
});

describe('reading tab: the book on request', () => {
	const expectedChapters = () => {
		const documents = Object.entries(living).map(([path, raw]) => parseBlob(path, raw, 'utf-8'));
		return bookGroups.flatMap((group) =>
			documents
				.filter((d) => bookGroup(d) === group)
				.sort((a, b) => a.path.localeCompare(b.path, undefined, { numeric: true }))
				.map((d) => documentAnchor(d.path))
		);
	};

	it('computes nothing before the control, also after Proposals indexed, and scans once', async () => {
		const source = repository({ ...living, ...handbook });
		const view = render(KnowledgeViews, props(source));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		expect(blobs(source).filter((p) => /^(docs|specs)\//.test(p))).toEqual([]);

		await view.rerender(props(source, { view: 'proposals' }));
		await screen.findByText('Proposal A');
		const indexed = source.blob.mock.calls.length;

		await view.rerender(props(source, { view: 'book' }));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		expect(document.querySelector('section.chapter')).toBeNull();
		expect(
			blobs(source)
				.slice(indexed)
				.filter((p) => /^(docs|specs)\//.test(p))
		).toEqual([]);

		await fireEvent.click(screen.getByRole('button', { name: 'Living Spec book' }));
		await waitFor(() =>
			expect(document.querySelectorAll('section.chapter').length).toBeGreaterThan(0)
		);
		expect(scans(source).filter((p) => p === 'docs')).toEqual(['docs']);
		expect(scans(source).filter((p) => p === 'specs')).toEqual(['specs']);
	});

	it('renders the same chapters in the same order once computed', async () => {
		const source = repository({ ...living, ...handbook });
		render(KnowledgeViews, props(source, { bookRequested: true }));
		await waitFor(() =>
			expect(document.querySelectorAll('section.chapter').length).toBeGreaterThan(0)
		);
		expect([...document.querySelectorAll('section.chapter')].map((s) => s.id)).toEqual(
			expectedChapters()
		);
		expect(blobs(source)).not.toContain('handbook/manifest.json');
	});

	it('returns to the handbook from the book without dropping the index', async () => {
		const source = repository({ ...living, ...handbook });
		render(KnowledgeViews, props(source, { bookRequested: true }));
		await waitFor(() =>
			expect(document.querySelectorAll('section.chapter').length).toBeGreaterThan(0)
		);
		await fireEvent.click(screen.getByRole('button', { name: 'Handbook' }));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		expect(document.querySelector('section.chapter')).toBeNull();
		await fireEvent.click(screen.getByRole('button', { name: 'Living Spec book' }));
		await waitFor(() =>
			expect(document.querySelectorAll('section.chapter').length).toBeGreaterThan(0)
		);
		expect(scans(source).filter((p) => p === 'docs')).toEqual(['docs']);
	});
});

describe('reading tab: handbook navigation', () => {
	const link = (text: string) =>
		[...document.querySelectorAll<HTMLAnchorElement>('.handbook-page a')].find(
			(a) => a.textContent === text
		)!;

	it('follows pages of the language, refuses links that leave it and opens sources externally', async () => {
		const source = repository(handbook);
		const view = props(source);
		render(KnowledgeViews, view);
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		const external = link('ARCH');
		expect(external.getAttribute('target')).toBe('_blank');
		expect(external.getAttribute('rel')).toBe('noopener noreferrer');

		const before = source.blob.mock.calls.length;
		await fireEvent.click(link('docs'));
		expect(link('docs').classList.contains('unavailable')).toBe(true);
		expect(source.blob.mock.calls.length).toBe(before);

		await fireEvent.click(link('a journey'));
		await waitFor(() => expect(pageTitle()).toBe('Journey X'));
		expect(blobs(source).slice(before)).toEqual(['handbook/en/journeys/x.md']);
		expect(view.onLocation).toHaveBeenLastCalledWith(
			'handbook/en/journeys/x.md',
			'',
			'book',
			expect.objectContaining({ title: 'Journey X' })
		);

		await fireEvent.click(screen.getByRole('button', { name: 'Handbook home' }));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		await fireEvent.click(link('gone'));
		await screen.findByText(/Failed to load handbook\/en\/missing\.md/);
		const homes = screen.getAllByRole('button', { name: 'Handbook home' });
		expect(homes.length).toBe(2);
		await fireEvent.click(homes[1]);
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
	});

	it.each([
		['en', 'H2', 'handbook--journeys'],
		['ko', 'A', 'journeys']
	])('scrolls a cross-page fragment in %s', async (lang, tag, id) => {
		localStorage.setItem('sdd-handbook-lang', lang);
		render(KnowledgeViews, props(repository(handbook)));
		await waitFor(() => expect(document.querySelector('.handbook-page h1')).not.toBeNull());
		await fireEvent.click(link(lang === 'en' ? 'Concepts' : '개념'));
		await waitFor(() => expect(link(lang === 'en' ? 'journeys' : '여정')).toBeTruthy());
		const scroll = vi.mocked(Element.prototype.scrollIntoView);
		scroll.mockClear();
		await fireEvent.click(link(lang === 'en' ? 'journeys' : '여정'));
		await waitFor(() => expect(scroll).toHaveBeenCalled());
		const target = scroll.mock.contexts.at(-1) as HTMLElement;
		expect([target.tagName, target.id]).toEqual([tag, id]);
	});

	it('switches language on the same page and remembers it', async () => {
		const source = repository(handbook);
		render(KnowledgeViews, props(source));
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		await fireEvent.click(link('a journey'));
		await waitFor(() => expect(pageTitle()).toBe('Journey X'));
		await fireEvent.change(screen.getByRole('combobox', { name: 'Language' }), {
			target: { value: 'ko' }
		});
		await waitFor(() => expect(pageTitle()).toBe('여정 X'));
		expect(blobs(source).at(-1)).toBe('handbook/ko/journeys/x.md');
		expect(localStorage.getItem('sdd-handbook-lang')).toBe('ko');

		cleanup();
		render(KnowledgeViews, props(repository(handbook)));
		await waitFor(() => expect(pageTitle()).toBe('devkit 핸드북'));
	});

	it('starts with the browser language when nothing is stored', async () => {
		vi.stubGlobal('navigator', { languages: ['ko-KR'], language: 'ko-KR' });
		render(KnowledgeViews, props(repository(handbook)));
		await waitFor(() => expect(pageTitle()).toBe('devkit 핸드북'));
	});
});

describe('book groups: steering documents', () => {
	const group = (path: string) => bookGroup(parseBlob(path, '# Page\n', 'utf-8'));

	it('groups every steering file and a package glossary under Steering', () => {
		expect(group('docs/steering/glossary.md')).toBe('Steering');
		expect(group('docs/steering/product.md')).toBe('Steering');
		expect(group('docs/packages/example/glossary.md')).toBe('Steering');
		expect(bookGroups).toContain('Steering');
		expect(bookGroups).not.toContain('Glossary');
	});

	it('no longer treats docs/glossary.md specially', () => {
		expect(group('docs/glossary.md')).toBe('Overview');
	});
});
