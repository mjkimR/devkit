import type { RepositoryDocument } from '../../api/documents';

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
	typeof doc?.meta.id === 'string' && /^(ADR|PADR)-/.test(doc.meta.id);
const ids = (value: unknown): string[] =>
	typeof value === 'string'
		? [value.trim()]
		: Array.isArray(value)
			? value.filter((v): v is string => typeof v === 'string').map((v) => v.trim())
			: [];
const idPattern =
	/^(?:CAP|UC|UX|ARCH|ADR|PROP|PADR|SPEC|PLAN|TASKS|REC|FB|MAT|MS)-[A-Za-z0-9][A-Za-z0-9_-]*$/;
const boundary = /^\s*(?:#{1,6}\s|[-+*]\s|\d+[.)]\s)/;
const marker = /^([ \t]*)([-*+]|[0-9]{1,9}[.)])([ \t]+|$)/;
const indent = (line: string) => {
	let n = 0;
	for (const ch of line) {
		if (ch === ' ') n++;
		else if (ch === '\t') n += 4 - (n % 4);
		else break;
	}
	return n;
};
const fenceRun = (line: string) => {
	const match = line.match(/^(`{3,}|~{3,})/);
	return match && !(match[1][0] === '`' && line.slice(match[1].length).includes('`'))
		? match[1]
		: '';
};
function closeRun(line: string, start: number, ch: string, width: number) {
	for (let i = start; i < line.length;) {
		if (line[i] !== ch) {
			i++;
			continue;
		}
		let end = i;
		while (line[end] === ch) end++;
		if (end - i === width) return i;
		i = end;
	}
	return -1;
}
function laterCloses(
	lines: string[],
	start: number,
	test: (line: string) => boolean,
	blocks = false
) {
	for (const line of lines.slice(start)) {
		if (!line.trim() || (indent(line) <= 3 && fenceRun(line.trim()))) return false;
		if (
			blocks &&
			(marker.test(line) ||
				(indent(line) <= 3 && (/^\s*<!--/.test(line) || /^ {0,3}#{1,6}(?:[ \t]|$)/.test(line))))
		)
			return false;
		if (test(line)) return true;
	}
	return false;
}

/** Port of the document query's visible-line rules; offsets stay aligned with the source. */
function visibleLines(lines: string[]): Map<number, string> {
	const visible = new Map<number, string>();
	let fence = '',
		blockComment = false,
		comment = false,
		codeSpan = 0;
	let inlineSpan: { ch: string; width: number } | null = null;
	let afterBlank = true,
		inIndented = false;
	const columns: number[] = [];
	for (let pos = 0; pos < lines.length; pos++) {
		const line = lines[pos].replace(/\r$/, ''),
			stripped = line.trim(),
			col = indent(line);
		const base = [...columns].reverse().find((n) => n <= col) ?? 0;
		let masked = line,
			prose = true,
			hidden = false;
		if (blockComment) {
			masked = ' '.repeat(line.length);
			blockComment = !line.includes('-->');
		} else if (!(comment || codeSpan) && fence) {
			inIndented = false;
			const run = col - base <= 3 ? fenceRun(stripped) : '';
			if (run[0] === fence[0] && run.length >= fence.length && !stripped.slice(run.length).trim())
				fence = '';
			hidden = true;
		} else if (!(comment || codeSpan) && !stripped) {
			afterBlank = true;
			hidden = true;
		} else if (
			!(comment || codeSpan) &&
			col >= 4 &&
			(inIndented || (afterBlank && !columns.length))
		) {
			inIndented = true;
			hidden = true;
		} else {
			if (!(comment || codeSpan)) {
				const list = col - base <= 3 ? line.match(marker) : null;
				if (list) {
					while (columns.length && columns.at(-1)! > col) columns.pop();
					const spaces = indent(list[3]);
					columns.push(col + list[2].length + (spaces >= 1 && spaces <= 4 ? spaces : 1));
				} else if (afterBlank || col === 0)
					while (columns.length && columns.at(-1)! > col) columns.pop();
				const run = col - base <= 3 ? fenceRun(stripped) : '';
				if (run) {
					inIndented = false;
					fence = run;
					hidden = true;
				} else if (col - base <= 3 && stripped.startsWith('<!--')) {
					masked = ' '.repeat(line.length);
					blockComment = !stripped.slice(4).includes('-->');
					prose = false;
				}
			}
			if (!hidden && prose) {
				const out = line.split('');
				const blank = (a: number, b: number) => {
					for (let i = a; i < b; i++) out[i] = ' ';
				};
				let i = 0;
				if (codeSpan) {
					const end = closeRun(line, 0, '`', codeSpan);
					if (end < 0) i = line.length;
					else {
						i = end + codeSpan;
						codeSpan = 0;
					}
				}
				while (i < line.length) {
					if (comment) {
						const end = line.indexOf('-->', i),
							stop = end < 0 ? line.length : end + 3;
						blank(i, stop);
						i = stop;
						comment = end < 0;
						continue;
					}
					if (line[i] === '\\') {
						i += 2;
						continue;
					}
					if (line[i] === '`') {
						let end = i;
						while (line[end] === '`') end++;
						const width = end - i,
							close = closeRun(line, end, '`', width);
						if (close >= 0) {
							i = close + width;
							continue;
						}
						if (laterCloses(lines, pos + 1, (s) => closeRun(s, 0, '`', width) >= 0, true)) {
							codeSpan = width;
							break;
						}
						i = end;
						continue;
					}
					if (
						line.startsWith('<!--', i) &&
						(line.indexOf('-->', i + 4) >= 0 ||
							laterCloses(lines, pos + 1, (s) => s.includes('-->'), true))
					) {
						comment = true;
						continue;
					}
					i++;
				}
				masked = out.join('');
			}
		}
		if (stripped) afterBlank = false;
		if (!hidden && stripped) inIndented = false;
		if (hidden) {
			inlineSpan = null;
			continue;
		}
		if (!stripped) continue;
		// Mask escapes, code and strikethrough after HTML/block scanning. Exact ID spans survive.
		const out = masked.split('');
		const blank = (a: number, b: number) => {
			for (let i = a; i < b; i++) out[i] = ' ';
		};
		let i = 0;
		if (inlineSpan) {
			const end = closeRun(masked, 0, inlineSpan.ch, inlineSpan.width);
			if (end < 0) {
				visible.set(pos, ' '.repeat(masked.length));
				continue;
			}
			blank(0, end + inlineSpan.width);
			i = end + inlineSpan.width;
			inlineSpan = null;
		}
		while (i < masked.length) {
			if (masked[i] === '\\' && i + 1 < masked.length) {
				blank(i, i + 2);
				i += 2;
				continue;
			}
			const ch = masked[i];
			if (ch === '`' || (ch === '~' && masked.startsWith('~~', i))) {
				let end = i;
				while (masked[end] === ch) end++;
				const width = end - i;
				if (ch === '~' && width !== 2) {
					i = end;
					continue;
				}
				const close = closeRun(masked, end, ch, width);
				if (close >= 0) {
					if (!(ch === '`' && width === 1 && idPattern.test(masked.slice(end, close))))
						blank(i, close + width);
					i = close + width;
					continue;
				}
				if (laterCloses(lines, pos + 1, (s) => closeRun(s, 0, ch, width) >= 0)) {
					blank(i, masked.length);
					inlineSpan = { ch, width };
					break;
				}
				i = end;
				continue;
			}
			if (ch === '[') {
				const end = masked.indexOf(']', i);
				if (end >= 0 && (masked[i - 1] === '!' || ['(', '[', ':'].includes(masked[end + 1])))
					blank(i, end + 1);
			}
			i++;
		}
		visible.set(pos, out.join(''));
	}
	return visible;
}

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
	const declared = new Map<string, RepositoryDocument[]>(),
		aliases = new Map<string, RepositoryDocument[]>();
	for (const doc of documents) {
		if (typeof doc.meta.id !== 'string') continue;
		for (const [map, keys] of [
			[declared, [doc.meta.id]],
			[aliases, ids(doc.meta.aliases)]
		] as const)
			for (const id of keys) map.set(id, [...(map.get(id) ?? []), doc]);
	}
	const candidates = (id: string) => declared.get(id) ?? aliases.get(id) ?? [];
	const resolve = (id: string) => (candidates(id).length === 1 ? candidates(id)[0] : null);
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
