import { describe, expect, it } from 'vitest';
import { normalizeTree } from './repository';

describe('normalizeTree', () => {
	it('keeps the server item types and lists directories before files by name', () => {
		const items = normalizeTree({
			items: [
				{ name: 'b.md', path: 'docs/b.md', type: 'blob' },
				{ name: 'z', path: 'docs/z', type: 'tree' },
				{ name: 'a.md', path: 'docs/a.md', type: 'blob' },
				{ name: 'c', path: 'docs/c', type: 'tree' }
			]
		});
		expect(items.map((item) => [item.name, item.type])).toEqual([
			['c', 'tree'],
			['z', 'tree'],
			['a.md', 'blob'],
			['b.md', 'blob']
		]);
	});

	it('accepts a bare item array and an empty response', () => {
		expect(normalizeTree([{ name: 'x', path: 'x', type: 'blob' }])).toHaveLength(1);
		expect(normalizeTree({})).toEqual([]);
	});
});
