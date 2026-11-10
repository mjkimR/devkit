import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import { afterEach, expect, it, vi } from 'vitest';
import { parseBlob } from '../../api/documents';
import SupersessionSummary from './SupersessionSummary.svelte';
afterEach(cleanup);
const old = parseBlob(
	'docs/old.md',
	'---\nid: ADR-old\ntitle: Old\nstatus: accepted\n---\n# Old',
	'utf-8'
);
const later = parseBlob(
	'docs/new.md',
	'---\nid: ADR-new\ntitle: "<img src=x onerror=alert(1)>"\nsupersedes: ADR-old\nstatus: accepted\n---\nSupersedes in part `ADR-old`: <script>bad()</script>',
	'utf-8'
);
it('escapes relation metadata/text and exposes keyboard-operable navigation/reload', async () => {
	const onOpen = vi.fn(),
		onReload = vi.fn();
	render(SupersessionSummary, { subject: old, documents: [old, later], onOpen, onReload });
	const link = screen.getByRole('link', { name: /ADR-new/ });
	expect(link.textContent).toContain('<img');
	expect(
		document.querySelector('.supersession-summary img, .supersession-summary script')
	).toBeNull();
	expect(screen.getByText('<script>bad()</script>')).toBeTruthy();
	await fireEvent.click(link);
	expect(onOpen).toHaveBeenCalledWith('docs/new.md');
	await fireEvent.click(screen.getByRole('button', { name: 'Reload relations' }));
	expect(onReload).toHaveBeenCalledOnce();
});
it('distinguishes incomplete empty lists and keeps failed paths visible', () => {
	render(SupersessionSummary, {
		subject: old,
		errors: ['docs/fail.md: denied'],
		onOpen: vi.fn(),
		onReload: vi.fn()
	});
	expect(screen.getByText(/Incomplete/)).toBeTruthy();
	expect(screen.getByText('docs/fail.md: denied')).toBeTruthy();
	expect(screen.queryByText('None recorded')).toBeNull();
	expect(screen.getByText('No incoming relations found in the documents read')).toBeTruthy();
});
it('shows proposed outgoing only and no broken target link', () => {
	const planned = parseBlob(
		'docs/p.md',
		'---\nid: PADR-test\nsupersedes: ADR-missing\n---\n# Proposed',
		'utf-8'
	);
	render(SupersessionSummary, { subject: planned, onOpen: vi.fn(), onReload: vi.fn() });
	expect(screen.getByText('Proposed supersession')).toBeTruthy();
	expect(screen.queryByText('Superseded by')).toBeNull();
	expect(screen.getByText('ADR-missing (missing target)')).toBeTruthy();
	expect(screen.getByText('Replacement scope not recorded')).toBeTruthy();
	expect(screen.queryByRole('link')).toBeNull();
});
