import { ID_PATTERN as idPattern } from './identity';

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
export function visibleLines(lines: string[]): Map<number, string> {
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
