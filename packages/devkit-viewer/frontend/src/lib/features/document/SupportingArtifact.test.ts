import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import SupportingArtifact from './SupportingArtifact.svelte';
import { planningDataSource } from '../../api/planning';
import type { RepositoryDataSource } from '../../api/repository';
const repository = (content: string, encoding = 'utf-8'): RepositoryDataSource => ({
	info: async () => ({}),
	tree: async () => [],
	blob: vi.fn(async () => ({ content, encoding }))
});
beforeEach(() => {
	URL.createObjectURL = vi.fn(() => `blob:test-${Math.random()}`);
	URL.revokeObjectURL = vi.fn();
	Element.prototype.scrollIntoView = vi.fn();
});
afterEach(() => cleanup());
it('keeps Planning reads in the selected source and never falls back to checkout', async () => {
	const source = repository('CHECKOUT SECRET');
	source.planningBlob = vi.fn(async () => ({ content: 'PLANNING DATA', encoding: 'utf-8' }));
	const view = render(SupportingArtifact, {
		source: planningDataSource(source, 'planning:one'),
		branch: 'feature',
		path: 'docs/proposals/PROP-one/materials/data.csv',
		sourceLabel: 'Planning one'
	});
	await screen.findByText('PLANNING DATA');
	expect(source.blob).not.toHaveBeenCalled();
	expect(source.planningBlob).toHaveBeenCalledWith(
		'planning:one',
		'docs/proposals/PROP-one/materials/data.csv',
		expect.anything()
	);
	source.planningBlob = vi.fn(async () => {
		throw new Error('Planning source unavailable');
	});
	await view.rerender({
		source: planningDataSource(source, 'planning:missing'),
		branch: 'feature',
		path: 'docs/proposals/PROP-one/materials/data.csv'
	});
	await screen.findByText(/File unavailable:.*Planning source unavailable/);
	expect(source.blob).not.toHaveBeenCalled();
});
it('shows binary images and disposes preview/download URLs on source replacement and unmount', async () => {
	const first = repository(
		'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/iZk9HQAAAABJRU5ErkJggg==',
		'base64'
	);
	const view = render(SupportingArtifact, { source: first, branch: 'old', path: 'docs/chart.png' });
	await screen.findByRole('img', { name: 'docs/chart.png' });
	expect(URL.createObjectURL).toHaveBeenCalledTimes(2);
	await view.rerender({ source: repository('a,b'), branch: 'new', path: 'docs/data.csv' });
	await screen.findByText('a,b');
	expect(URL.revokeObjectURL).toHaveBeenCalledTimes(2);
	view.unmount();
	expect(URL.revokeObjectURL).toHaveBeenCalledTimes(3);
});
it('ignores a late prior-source blob after cancellation', async () => {
	let release!: (value: any) => void;
	const first = {
		...repository(''),
		blob: vi.fn(
			(_path: string, _ref: string, _signal: AbortSignal) =>
				new Promise<any>((resolve) => (release = resolve))
		)
	};
	const view = render(SupportingArtifact, { source: first, branch: 'old', path: 'docs/old.csv' });
	await waitFor(() => expect(first.blob).toHaveBeenCalledTimes(1));
	await view.rerender({ source: repository('NEW DATA'), branch: 'new', path: 'docs/new.csv' });
	await screen.findByText('NEW DATA');
	release({ content: 'OLD DATA', encoding: 'utf-8' });
	await new Promise((resolve) => setTimeout(resolve, 0));
	expect(screen.queryByText('OLD DATA')).toBeNull();
	expect(first.blob.mock.calls[0][2].aborted).toBe(true);
});
it('shows unsupported bytes with download and contextual Back, but no fabricated readable raw', async () => {
	const onBack = vi.fn();
	render(SupportingArtifact, {
		source: repository(btoa(String.fromCharCode(255, 254)), 'base64'),
		branch: 'main',
		path: 'docs/data.bin',
		parent: 'DESIGN-parent',
		onBack
	});
	await screen.findByText(/Unsupported preview format/);
	expect(screen.getByRole('link', { name: 'Download file' })).toBeTruthy();
	expect(screen.queryByRole('button', { name: 'View raw' })).toBeNull();
	await fireEvent.click(screen.getByRole('button', { name: 'Back to DESIGN-parent' }));
	expect(onBack).toHaveBeenCalledOnce();
});
it('retains missing path/fragment and retries without inventing available bytes', async () => {
	let missing = true;
	const source = {
		...repository(''),
		blob: vi.fn(async () => {
			if (missing) throw new Error('HTTP 404');
			return { content: 'Restored', encoding: 'utf-8' };
		})
	};
	render(SupportingArtifact, {
		source,
		branch: 'main',
		path: 'docs/missing.csv',
		fragment: 'row 2'
	});
	await screen.findByText(/File unavailable: docs\/missing.csv/);
	expect(screen.queryByRole('link', { name: 'Download file' })).toBeNull();
	expect(screen.getByText('Requested fragment: row 2')).toBeTruthy();
	missing = false;
	await fireEvent.click(screen.getByRole('button', { name: 'Retry file' }));
	await screen.findByText('Restored');
});
it('shares Markdown/Mermaid rendering, source-relative links and raw controls', async () => {
	const diagrams = vi.fn(() => ({ destroy: vi.fn() })),
		onOpen = vi.fn();
	render(SupportingArtifact, {
		source: repository('# Example\n\n```mermaid\ngraph TD\nA-->B\n```\n\n[More](more.csv#row%202)'),
		branch: 'main',
		path: 'docs/designs/DESIGN-x/artifacts/example.md',
		diagrams,
		onOpen
	});
	await screen.findByRole('heading', { name: 'Example' });
	expect(document.querySelector('.language-mermaid')?.textContent).toContain('A-->B');
	expect(diagrams).toHaveBeenCalledOnce();
	await fireEvent.click(screen.getByRole('link', { name: 'More' }));
	expect(onOpen).toHaveBeenCalledWith('docs/designs/DESIGN-x/artifacts/more.csv', 'row 2');
	await fireEvent.click(screen.getByRole('button', { name: 'View raw' }));
	expect(document.querySelector('pre')?.textContent).toContain('```mermaid');
	await fireEvent.click(screen.getByRole('button', { name: 'Rendered' }));
	await screen.findByRole('heading', { name: 'Example' });
});
it('retains raw/download when supporting Markdown has malformed frontmatter', async () => {
	render(SupportingArtifact, {
		source: repository('---\nid: [broken\n---\nExample'),
		branch: 'main',
		path: 'docs/designs/DESIGN-x/artifacts/example.md'
	});
	await screen.findByText(/Markdown preview unavailable/);
	expect(screen.getByRole('link', { name: 'Download file' })).toBeTruthy();
	await fireEvent.click(screen.getByRole('button', { name: 'View raw' }));
	expect(document.querySelector('pre')?.textContent).toContain('id: [broken');
});
