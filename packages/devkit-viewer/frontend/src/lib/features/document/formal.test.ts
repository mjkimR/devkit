import { describe, expect, it } from 'vitest';
import {
	parseBlob,
	renderDocument,
	bookGroup,
	bookGroups,
	visibleReferences
} from '../../api/documents';
import { identityResolver } from '../../api/identity';
import { deriveReferences } from './references';
import { replacementStatements, deriveSupersession } from './supersession';
const doc = (path: string, id: string, body = '', meta = '') =>
	parseBlob(
		path,
		`---\nid: ${id}\ntitle: ${id}\nstatus: active\nsummary: "Example."\n${meta}---\n# [${id}] Title\n\n${body}`,
		'utf-8'
	);
describe.each([
	['DESIGN', 'designs', 'Designs'],
	['DOMAIN', 'domain', 'Domain'],
	['OPS', 'operations', 'Operations']
])('%s complete browser identity', (prefix, dir, group) => {
	it('groups global, registered and structural namespaces while excluding artifacts', () => {
		for (const root of ['docs', 'docs/packages/registered', 'docs/packages/structural'])
			expect(bookGroup(doc(`${root}/${dir}/${prefix}-x.md`, `${prefix}-x`))).toBe(group);
		expect(
			bookGroup(doc(`docs/${dir}/${prefix}-x/artifacts/example.md`, `${prefix}-forbidden`))
		).toBeNull();
		expect(bookGroup(doc(`docs/${dir}/README.md`, `${prefix}-readme`))).toBeNull();
	});
	it('resolves canonical before aliases and reports ambiguity, preserving retired targets', () => {
		const target = doc(
			`docs/${dir}/${prefix}-new.md`,
			`${prefix}-new`,
			'',
			`aliases: [${prefix}-old_name]\n`
		);
		target.meta.status = 'retired';
		const page = doc(
			'docs/a.md',
			'CAP-A-a',
			`See [${prefix}-old_name] and \`${prefix}-new\`.\n\n\`\`\`md\n[${prefix}-hidden]\n\`\`\`\n<!-- [${prefix}-comment] -->\n\n    [${prefix}-indented]`
		);
		expect(visibleReferences(page)).toEqual([`${prefix}-old_name`, `${prefix}-new`]);
		const html = renderDocument(page, [page, target]).html;
		expect(html.match(/data-doc-path=/g)).toHaveLength(2);
		expect(identityResolver([target]).resolve(`${prefix}-old_name`).document).toBe(target);
		const canonical = doc(`docs/${dir}/${prefix}-old_name.md`, `${prefix}-old_name`);
		expect(identityResolver([target, canonical]).resolve(`${prefix}-old_name`).document).toBe(
			canonical
		);
		expect(
			identityResolver([target, { ...target, path: 'docs/duplicate.md' }]).resolve(`${prefix}-new`)
				.unavailable
		).toBe('ambiguous');
	});
	it('shows current typed/prose graph from any indexed source and separates provenance/aliases', () => {
		const field = {
			DESIGN: 'related_designs',
			DOMAIN: 'related_domains',
			OPS: 'related_operations'
		}[prefix]!;
		const target = doc(
			`docs/${dir}/${prefix}-new.md`,
			`${prefix}-new`,
			'',
			`aliases: [${prefix}-old_name]\nrelated_capabilities: [CAP-A-owner]\nproposal: PROP-origin\n`
		);
		const incoming = doc(
			'docs/materials/MAT-evidence.md',
			'MAT-evidence',
			`See [${prefix}-old_name].`,
			`${field}: [${prefix}-new]\n`
		);
		const owner = doc('docs/capabilities/a/CAP-A-owner.md', 'CAP-A-owner');
		const refs = deriveReferences(target, [target, incoming, owner]);
		expect(refs.incoming.map((row) => row.field)).toEqual(['body', field]);
		expect(refs.outgoing.map((row) => row.id)).toEqual(['CAP-A-owner']);
		expect(refs.provenance[0].written).toBe('PROP-origin');
		expect(refs.issues).toEqual([]);
		incoming.meta[field] = [42, 'CAP-wrong'];
		expect(deriveReferences(target, [incoming, target]).issues).toHaveLength(2);
	});
	it('recognizes statement targets with underscores but keeps decision supersession UI interpretation separate', () => {
		const adr = doc(
			'docs/decisions/ADR-later.md',
			'ADR-later',
			`Supersedes in part \`${prefix}-under_score\`: Replacement.\n\n\`\`\`md\nSupersedes in part \`${prefix}-hidden\`: hidden\n\`\`\``,
			'supersedes: [ADR-earlier]\n'
		);
		expect(replacementStatements(adr)).toEqual([
			{ id: `${prefix}-under_score`, text: 'Replacement.' }
		]);
		expect(deriveSupersession(adr, [adr]).outgoing[0].id).toBe('ADR-earlier');
	});
});
it('uses the selected full group order', () =>
	expect(bookGroups).toEqual([
		'Overview',
		'Architecture',
		'Domain',
		'Capabilities',
		'Use Cases',
		'UX',
		'Designs',
		'Operations',
		'Steering',
		'Decisions',
		'Development'
	]));
it.each([
	['DESIGN', 'designs'],
	['DOMAIN', 'domain'],
	['OPS', 'operations']
])(
	'%s maintenance projections retain current parents, independent splits and cross-kind retirement',
	(prefix, dir) => {
		const old = doc(
			`docs/${dir}/${prefix}-old.md`,
			`${prefix}-old`,
			'Historical source at commit abc123: src/deleted.py.',
			''
		);
		old.meta.status = 'retired';
		const parent = doc(
			`docs/packages/registered/${dir}/${prefix}-new.md`,
			`${prefix}-new`,
			'',
			`aliases: [${prefix}-renamed]\n`
		);
		const detail = doc(`docs/packages/registered/${dir}/${prefix}-detail.md`, `${prefix}-detail`);
		const artifact = doc(
			`docs/packages/registered/${dir}/${prefix}-new/artifacts/invalid.md`,
			`${prefix}-forbidden`
		);
		const receiving = doc('docs/domain/DOMAIN-reclassified.md', 'DOMAIN-reclassified');
		old.body += '\n[DOMAIN-reclassified]';
		const resolver = identityResolver([old, parent, detail, artifact, receiving]);
		expect(resolver.resolve(`${prefix}-renamed`).document?.path).toBe(parent.path);
		expect(resolver.resolve(`${prefix}-forbidden`).document).toBeNull();
		expect(resolver.resolve(`${prefix}-detail`).document?.path).toBe(detail.path);
		expect(deriveReferences(old, [old, parent, detail, receiving]).outgoing[0].id).toBe(
			'DOMAIN-reclassified'
		);
		expect(old.meta.entrypoints).toBeUndefined();
		const historical = doc(
			`docs/materials/history/${dir}/${prefix}-new/artifacts/MAT-history.md`,
			'MAT-history'
		);
		expect(identityResolver([historical]).resolve('MAT-history').document).toBe(historical);
	}
);

it('retains malformed recursive metadata as explicit uncertainty without crashing the graph', () => {
	const subject = doc(
		'docs/designs/DESIGN-cycle.md',
		'DESIGN-cycle',
		'',
		'related_designs: &cycle [*cycle]\n'
	);
	expect(deriveReferences(subject, [subject]).issues.join(' ')).toContain('Recursive metadata');
});

it('uses reconcile_id identity for typed references from another indexed kind', () => {
	const target = doc('docs/designs/DESIGN-x.md', 'DESIGN-x');
	const source = parseBlob(
		'specs/month/unit/reconcile.md',
		'---\nreconcile_id: REC-example\nstatus: resolved\nrelated_designs: [DESIGN-x]\n---\n# Reconcile',
		'utf-8'
	);
	expect(identityResolver([source, target]).resolve('REC-example').document).toBe(source);
	expect(deriveReferences(target, [source, target]).incoming[0].id).toBe('REC-example');
});
