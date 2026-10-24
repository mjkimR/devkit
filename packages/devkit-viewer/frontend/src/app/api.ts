import { httpDataSource, type RepositoryDataSource } from '../lib/repository';

/** One repository `devkit viewer serve` registered. */
export interface RepositorySummary {
	id: string;
	default_branch: string;
}

const API = '/api/repos';

async function get<T>(url: string, signal?: AbortSignal): Promise<T> {
	const response = await fetch(url, { signal });
	if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
	return response.json();
}

export async function listRepositories(signal?: AbortSignal): Promise<RepositorySummary[]> {
	return (await get<{ repos: RepositorySummary[] }>(API, signal)).repos;
}

export const repositorySource = (id: string): RepositoryDataSource =>
	httpDataSource(`${API}/${encodeURIComponent(id)}`);

/** The repository kept in the address, so a reload or a shared link opens the same view. */
export function readLocation(hash: string): { repo: string } {
	const params = new URLSearchParams(hash.replace(/^#/, ''));
	return { repo: params.get('repo') ?? '' };
}

export const writeLocation = (repo: string) => `#${new URLSearchParams({ repo })}`;
