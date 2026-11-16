import type { RepositoryDataSource } from '../api/repository';

const absent = (path: string) => Promise.reject(new Error(`HTTP 404: Not Found (${path})`));

/** A local data source for tests: every member a test does not name answers as an empty repository. */
export function testSource<T extends Partial<RepositoryDataSource>>(
	members: T
): RepositoryDataSource & T {
	return {
		info: async () => ({ default_branch: 'main' }),
		tree: async () => ({ items: [] }),
		treeRecursive: async () => ({ items: [] }),
		blob: (path: string) => absent(path),
		dashboardList: async () => ({ items: [], errors: [] }),
		planningProposals: async () => ({ sources: [], items: [], errors: [] }),
		planningTree: async () => ({ items: [] }),
		planningBlob: (_source: string, path: string) => absent(path),
		...members
	};
}
