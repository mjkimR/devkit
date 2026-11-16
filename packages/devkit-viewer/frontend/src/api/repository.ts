export interface TreeItem {
	name: string;
	path: string;
	type: string;
	size?: number;
	sha?: string;
}

export type TreeResponse = TreeItem[] | { items?: TreeItem[] } | { items?: any[] } | any;
export interface RepositoryInfo {
	default_branch: string;
	repo_id?: string;
	[key: string]: any;
}
export interface RepositoryBlob {
	path: string;
	content: string;
	encoding: string;
	[key: string]: any;
}
/** A Planning source: a `plan-<slug>` worktree or local branch. */
export interface PlanningSource {
	id: string;
	kind: 'worktree' | 'branch';
	label: string;
	slug: string;
}
/** Each source's `docs/proposals/PROP-<slug>/proposal.md`, read after the checkout. */
export interface PlanningProposals {
	sources: PlanningSource[];
	items: (RepositoryBlob & { source: string })[];
	errors: string[];
}

/** The local server's read-only API for one registered repository (`devkit viewer serve`). */
export interface RepositoryDataSource {
	info(signal: AbortSignal): Promise<any>;
	tree(path: string, signal: AbortSignal): Promise<any>;
	/** Metadata of every descendant in one response. */
	treeRecursive(path: string, signal: AbortSignal): Promise<any>;
	blob(path: string, signal: AbortSignal): Promise<any>;
	/** Frontmatter-only listing of one dashboard section. */
	dashboardList(
		section: string,
		signal: AbortSignal
	): Promise<{
		items: RepositoryBlob[];
		errors: string[];
	}>;
	/** The Planning overlay of proposals. */
	planningProposals(signal: AbortSignal): Promise<PlanningProposals>;
	/** Recursive metadata listing inside a Planning source's proposal directory. */
	planningTree(source: string, path: string, signal: AbortSignal): Promise<any>;
	/** One file of a Planning source's proposal directory. */
	planningBlob(source: string, path: string, signal: AbortSignal): Promise<any>;
}

/** The reads the document scanner and the supporting reader use: the checkout or one Planning source. */
export type FileSource = Pick<RepositoryDataSource, 'tree' | 'treeRecursive' | 'blob'>;

export function httpDataSource(base: string): RepositoryDataSource {
	async function get<T>(endpoint: string, signal: AbortSignal): Promise<T> {
		const response = await fetch(`${base.replace(/\/+$/, '')}/${endpoint}`, { signal });
		if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		return response.json();
	}
	const query = (path: string) => new URLSearchParams({ path });
	return {
		info: (signal) => get('info', signal),
		dashboardList: (section, signal) => get(`dashboard-list?${query(section)}`, signal),
		tree: (path, signal) => get(`tree?${query(path)}`, signal),
		treeRecursive: (path, signal) => get(`tree?${query(path)}&recursive=true`, signal),
		blob: (path, signal) => get(`blob?${query(path)}`, signal),
		planningProposals: (signal) => get('planning-proposals', signal),
		planningTree: (source, path, signal) =>
			get(`tree?${new URLSearchParams({ path, recursive: 'true', source })}`, signal),
		planningBlob: (source, path, signal) =>
			get(`blob?${new URLSearchParams({ path, source })}`, signal)
	};
}

export function normalizeTree(response: TreeResponse): TreeItem[] {
	const items = Array.isArray(response) ? response : (response?.items ?? []);
	return items
		.map((item: any) => ({
			...item,
			type: item.type === 'dir' ? 'tree' : item.type === 'file' ? 'blob' : item.type
		}))
		.sort((a: any, b: any) =>
			a.type !== b.type ? (a.type === 'tree' ? -1 : 1) : a.name.localeCompare(b.name)
		);
}
