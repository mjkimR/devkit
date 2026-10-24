import type { RepositoryDataSource } from './repository';

export const CACHE_TTL_MS = 30_000;
const MAX_ENTRIES = 8;
type Entry = { value: unknown; expires: number };
const caches = new WeakMap<RepositoryDataSource, Map<string, Entry>>();
const keyOf = (ref: string, purpose: string) => JSON.stringify([ref, purpose]);

export function cachedResult<T>(
	source: RepositoryDataSource,
	ref: string,
	purpose: string
): T | undefined {
	const cache = caches.get(source);
	const key = keyOf(ref, purpose);
	const entry = cache?.get(key);
	if (!entry) return undefined;
	if (entry.expires <= Date.now()) {
		cache!.delete(key);
		return undefined;
	}
	return entry.value as T;
}

// The map identity is a generation token: refresh also rejects writes from older scans.
export function cacheGeneration(source: RepositoryDataSource) {
	let cache = caches.get(source);
	if (!cache) {
		cache = new Map();
		caches.set(source, cache);
	}
	return cache;
}
export function cacheResult<T>(
	source: RepositoryDataSource,
	ref: string,
	purpose: string,
	value: T,
	generation: ReturnType<typeof cacheGeneration>,
	expires = Date.now() + CACHE_TTL_MS
) {
	if (caches.get(source) !== generation) return;
	const key = keyOf(ref, purpose);
	generation.delete(key);
	generation.set(key, { value, expires });
	while (generation.size > MAX_ENTRIES) generation.delete(generation.keys().next().value!);
}
export function clearRepositoryCache(source: RepositoryDataSource) {
	caches.delete(source);
}
