import type { RepositoryDocument } from '../../api/documents';
import { ID_PATTERN as idPattern, identityResolver, isArtifactPath } from '../../api/identity';
import { visibleLines } from '../../api/markdown';

export interface SupersessionRelation {
	id: string;
	written: string;
	path: string | null;
	title: string | null;
	status: string | null;
	scope: 'whole' | 'partial';
	text: string | null;
	unavailable: 'missing' | 'ambiguous' | null;
}
export interface Supersession {
	proposed: boolean;
	outgoing: SupersessionRelation[];
	incoming: SupersessionRelation[];
}
export const isDecision = (doc: RepositoryDocument | null | undefined) =>
	typeof doc?.meta.id === 'string' && !isArtifactPath(doc.path) && /^(ADR|PADR)-/.test(doc.meta.id);
const ids = (value: unknown): string[] =>
	typeof value === 'string'
		? [value.trim()]
		: Array.isArray(value)
			? value.filter((v): v is string => typeof v === 'string').map((v) => v.trim())
			: [];
const boundary = /^\s*(?:#{1,6}\s|[-+*]\s|\d+[.)]\s)/;

export function replacementStatements(doc: RepositoryDocument) {
	const lines = doc.body.split('\n'),
		visible = visibleLines(lines);
	const result: { id: string; text: string }[] = [];
	for (const [pos, line] of visible) {
		const match = line.match(/^\s*(?:[-+*]\s+|\d+[.)]\s+)?Supersedes in part `([^`]+)`:/);
		if (!match || !idPattern.test(match[1])) continue;
		const parts = [lines[pos].slice(match[0].length).trim()];
		for (let i = pos + 1; i < lines.length; i++) {
			const next = visible.get(i);
			if (!lines[i].trim() || next === undefined || boundary.test(next)) break;
			parts.push(lines[i].trim());
		}
		result.push({ id: match[1], text: parts.join('\n').trim() });
	}
	return result;
}

export function deriveSupersession(
	subject: RepositoryDocument,
	indexed: RepositoryDocument[]
): Supersession {
	const documents = [...indexed.filter((doc) => doc.path !== subject.path), subject];
	const resolver = identityResolver(documents);
	const candidates = resolver.candidates;
	const resolve = (id: string) => resolver.resolve(id).document;
	const canonical = (id: string) => resolve(id)?.meta.id ?? id;
	function row(
		written: string,
		earlier: RepositoryDocument | null,
		later: RepositoryDocument,
		other: RepositoryDocument | null
	): SupersessionRelation {
		const text =
			replacementStatements(later).find((s) => canonical(s.id) === (earlier?.meta.id ?? written))
				?.text ?? null;
		return {
			id: other?.meta.id ?? written,
			written,
			path: other?.path ?? null,
			title: other?.title ?? null,
			status: typeof other?.meta.status === 'string' ? other.meta.status : null,
			scope:
				earlier?.meta.status === 'superseded' &&
				canonical(String(earlier.meta.superseded_by ?? '')) === later.meta.id
					? 'whole'
					: 'partial',
			text,
			unavailable: other ? null : candidates(written).length > 1 ? 'ambiguous' : 'missing'
		};
	}
	const sort = (a: SupersessionRelation, b: SupersessionRelation) =>
		a.id.localeCompare(b.id) ||
		a.written.localeCompare(b.written) ||
		(a.path ?? '').localeCompare(b.path ?? '');
	return {
		proposed: String(subject.meta.id).startsWith('PADR-'),
		outgoing: ids(subject.meta.supersedes)
			.map((id) => {
				const earlier = resolve(id);
				return row(id, earlier, subject, earlier);
			})
			.sort(sort),
		incoming: String(subject.meta.id).startsWith('PADR-')
			? []
			: documents
					.filter(
						(doc) =>
							String(doc.meta.id).startsWith('ADR-') &&
							ids(doc.meta.supersedes).some((id) => canonical(id) === subject.meta.id)
					)
					.map((later) => row(later.meta.id, subject, later, resolve(later.meta.id)))
					.sort(sort)
	};
}
