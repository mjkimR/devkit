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
/** Branch metadata available from a host that supports branch enumeration. */
export interface RepositoryRefs {
	default_branch: string;
	branches: string[];
}

export interface SharedArtifactMetadata {
	generation_id: string;
	kind: string;
	slug: string;
	source_sha: string;
	language: string;
	content_sha256: string;
	content_type: string;
	byte_count: number;
	created_at: string;
	expires_at: string;
	revision: string;
	repository_namespace?: string;
	artifact_uri?: string;
}

export interface SharedArtifactDetail {
	metadata: SharedArtifactMetadata;
	content: string;
	artifact_uri: string;
}

export interface SharedArtifactsResponse {
	artifacts: SharedArtifactMetadata[];
}

/** Hosts own authentication and renewal; credentials never become element attributes. */
export interface RepositoryDataSource {
	info(signal: AbortSignal): Promise<any>;
	tree(path: string, ref: string, signal: AbortSignal): Promise<any>;
	/** Optional metadata-only recursive listing; hosts without it use directory discovery. */
	treeRecursive?(path: string, ref: string, signal: AbortSignal): Promise<any>;
	blob(path: string, ref: string, signal: AbortSignal): Promise<any>;
	/** Optional frontmatter-only section listing; bodies are fetched per visible page. */
	dashboardList?(
		section: string,
		ref: string,
		signal: AbortSignal
	): Promise<{
		items: RepositoryBlob[];
		errors: string[];
	}>;
	/** Optional branch metadata for hosts that expose it. */
	refs?(signal: AbortSignal): Promise<RepositoryRefs>;
	/** Optional: shared space artifacts (e.g. proposal reviews) */
	sharedList?(
		signal: AbortSignal,
		options?: { kind?: string; slug?: string }
	): Promise<SharedArtifactsResponse>;
	sharedBlob?(generationId: string, signal: AbortSignal): Promise<SharedArtifactDetail>;
}

export function httpDataSource(base: string): RepositoryDataSource {
	async function get<T>(endpoint: string, signal: AbortSignal): Promise<T> {
		const response = await fetch(`${base.replace(/\/+$/, '')}/${endpoint}`, { signal });
		if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		return response.json();
	}
	const query = (path: string) => new URLSearchParams({ path });
	return {
		info: (signal) => get('info', signal),
		dashboardList: (section, _ref, signal) => get(`dashboard-list?${query(section)}`, signal),
		tree: (path, _ref, signal) => get(`tree?${query(path)}`, signal),
		treeRecursive: (path, _ref, signal) => get(`tree?${query(path)}&recursive=true`, signal),
		blob: (path, _ref, signal) => get(`blob?${query(path)}`, signal),
		sharedList: (signal, options) => {
			const params = new URLSearchParams();
			if (options?.kind) params.set('kind', options.kind);
			if (options?.slug) params.set('slug', options.slug);
			const qs = params.toString() ? `?${params.toString()}` : '';
			return get(`shared${qs}`, signal);
		},
		sharedBlob: (generationId, signal) =>
			get(`shared?generation=${encodeURIComponent(generationId)}`, signal)
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
