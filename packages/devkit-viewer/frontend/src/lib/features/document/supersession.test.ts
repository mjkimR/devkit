import { describe, expect, it } from 'vitest';
import { parseBlob } from '../../api/documents';
import { deriveSupersession, replacementStatements } from './supersession';
const doc = (id: string, fields = '', body = '', path = `docs/decisions/${id}.md`) =>
	parseBlob(path, `---\nid: ${id}\ntitle: ${id} title\n${fields}\n---\n${body}`, 'utf-8');

describe('decision supersession', () => {
	it('matches query direction, aliases, reciprocal whole status and statement text', () => {
		const earlier = doc(
			'ADR-old',
			'aliases: [ADR-alias]\nstatus: superseded\nsuperseded_by: ADR-new'
		);
		const later = doc(
			'ADR-new',
			'supersedes: [ADR-alias, ADR-missing]\nstatus: accepted',
			'Supersedes in part `ADR-alias`: first `clause`\nsecond clause.\n\nSupersedes in part `ADR-missing`: missing scope.'
		);
		const outgoing = deriveSupersession(later, [earlier, later]).outgoing;
		expect(outgoing.map((r) => [r.id, r.scope, r.text, r.path])).toEqual([
			['ADR-missing', 'partial', 'missing scope.', null],
			['ADR-old', 'whole', 'first `clause`\nsecond clause.', earlier.path]
		]);
		expect(deriveSupersession(earlier, [earlier, later]).incoming[0]).toMatchObject({
			id: 'ADR-new',
			scope: 'whole',
			status: 'accepted'
		});
	});

	it('retains ambiguous IDs and aliases without arbitrary links; declared IDs win aliases', () => {
		const one = doc('ADR-one', 'aliases: [ADR-alias, ADR-real]');
		const two = doc('ADR-two', 'aliases: [ADR-alias]');
		const real = doc('ADR-real');
		const later = doc('ADR-new', 'supersedes: [ADR-alias, ADR-real, ADR-dupe]');
		const duplicates = [doc('ADR-dupe', '', '', 'docs/a.md'), doc('ADR-dupe', '', '', 'docs/b.md')];
		const rows = deriveSupersession(later, [one, two, real, ...duplicates]).outgoing;
		expect(rows.find((r) => r.written === 'ADR-alias')).toMatchObject({
			path: null,
			unavailable: 'ambiguous'
		});
		expect(rows.find((r) => r.written === 'ADR-dupe')).toMatchObject({
			path: null,
			unavailable: 'ambiguous'
		});
		expect(rows.find((r) => r.written === 'ADR-real')?.path).toBe(real.path);
	});

	it('uses the exact displayed subject instead of its cached copy', () => {
		const earlier = doc('ADR-old');
		const stale = doc('ADR-new', 'supersedes: ADR-wrong', 'Supersedes in part `ADR-wrong`: stale.');
		const fresh = doc('ADR-new', 'supersedes: ADR-old', 'Supersedes in part `ADR-old`: displayed.');
		expect(deriveSupersession(fresh, [earlier, stale]).outgoing).toMatchObject([
			{ id: 'ADR-old', text: 'displayed.' }
		]);
	});

	it('shows PADR outgoing as proposed and excludes PADRs from applied incoming relations', () => {
		const earlier = doc('ADR-old');
		const planned = doc(
			'PADR-new',
			'supersedes: ADR-old',
			'Supersedes in part `ADR-old`: proposed.'
		);
		expect(deriveSupersession(planned, [earlier])).toMatchObject({
			proposed: true,
			outgoing: [{ id: 'ADR-old' }],
			incoming: []
		});
		expect(deriveSupersession(earlier, [earlier, planned]).incoming).toEqual([]);
	});

	it('does not create edges from body pointers and leaves absent replacement text null', () => {
		const old = doc('ADR-old', '', 'Superseded in part by `ADR-new`: old pointer.');
		const newer = doc('ADR-new', 'supersedes: ADR-old');
		expect(deriveSupersession(old, [old, newer]).incoming[0].text).toBeNull();
		expect(deriveSupersession(old, [old]).incoming).toEqual([]);
	});
});

describe('replacement statement source parity', () => {
	it.each([
		['plain multiline', 'Supersedes in part `ADR-old`: one\n two\n\nignored', 'one\ntwo'],
		[
			'list boundary',
			'- Supersedes in part `ADR-old`: one\n  continuation\n- next item',
			'one\ncontinuation'
		],
		['heading boundary', 'Supersedes in part `ADR-old`: one\n## Next', 'one'],
		['CRLF', 'Supersedes in part `ADR-old`: one\r\n two\r\n\r\nignored', 'one\ntwo'],
		['code boundary', 'Supersedes in part `ADR-old`: one\n```text\nnot scope\n```', 'one'],
		['inline markup', 'Supersedes in part `ADR-old`: **one** and `code`.', '**one** and `code`.']
	])('%s', (_name, body, expected) => {
		expect(replacementStatements(doc('ADR-new', '', body))).toEqual([
			{ id: 'ADR-old', text: expected }
		]);
	});
	it.each([
		'```md\nSupersedes in part `ADR-old`: hidden\n```',
		'~~~~\nSupersedes in part `ADR-old`: hidden\n~~~~',
		'    Supersedes in part `ADR-old`: hidden',
		'<!--\nSupersedes in part `ADR-old`: hidden\n-->',
		'~~Supersedes in part `ADR-old`: hidden~~',
		'``Supersedes in part `ADR-old`: hidden``',
		'`Supersedes in part\nADR-old: hidden`',
		'<!-- Supersedes in part `ADR-old`: hidden -->',
		'Supersedes in part `ADR-old` no colon'
	])('ignores hidden/non-statement %s', (body) => {
		expect(replacementStatements(doc('ADR-new', '', body))).toEqual([]);
	});
	it('keeps list-continuation statements visible rather than treating list indentation as code', () => {
		const body = '- prior item\n\n  Supersedes in part `ADR-old`: retained.\n';
		expect(replacementStatements(doc('ADR-new', '', body))[0]?.text).toBe('retained.');
	});
});

it('retains ambiguous incoming superseder identity without arbitrary navigation', () => {
	const old = doc('ADR-old');
	const later = [
		doc('ADR-new', 'supersedes: ADR-old', '', 'docs/a.md'),
		doc('ADR-new', 'supersedes: ADR-old', '', 'docs/b.md')
	];
	const rows = deriveSupersession(old, [old, ...later]).incoming;
	expect(rows).toHaveLength(2);
	expect(
		rows.every(
			(row) =>
				row.id === 'ADR-new' &&
				row.written === 'ADR-new' &&
				row.path === null &&
				row.unavailable === 'ambiguous'
		)
	).toBe(true);
});
it('resets indented code at fence boundaries exactly as Python visible_lines', () => {
	const body = '    code\n```\n```\n    Supersedes in part `ADR-old`: visible';
	expect(replacementStatements(doc('ADR-new', '', body))).toEqual([
		{ id: 'ADR-old', text: 'visible' }
	]);
});
