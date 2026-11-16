import DOMPurify from 'dompurify';
import type { RepositoryDataSource } from './repository';

export const ARTIFACT_MAX_BYTES = 8 * 1024 * 1024;
export const IMAGE_LIMIT = 32;
export interface SupportingFile {
	path: string;
	bytes: Uint8Array;
	text: string | null;
	kind: 'markdown' | 'text' | 'image' | 'unsupported';
	mime: string;
}
export function blobBytes(content: string, encoding: string): Uint8Array {
	if (typeof content !== 'string') throw new Error('Blob content is not a string');
	if (content.length > ARTIFACT_MAX_BYTES * 2)
		throw new Error('Supporting file exceeds the 8 MiB preview limit');
	const bytes =
		encoding === 'utf-8'
			? new TextEncoder().encode(content)
			: encoding === 'base64'
				? Uint8Array.from(atob(content.replace(/\s/g, '')), (c) => c.charCodeAt(0))
				: (() => {
						throw new Error(`Unsupported encoding: ${encoding}`);
					})();
	if (bytes.length > ARTIFACT_MAX_BYTES)
		throw new Error('Supporting file exceeds the 8 MiB preview limit');
	return bytes;
}
export function textBytes(bytes: Uint8Array) {
	return new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
}
function safePath(path: string) {
	return Boolean(
		path &&
		!path.startsWith('/') &&
		!/[\\\u0000-\u001f]/.test(path) &&
		!path.split('/').some((part) => !part || part === '.' || part === '..' || part === '.git')
	);
}
export function classifyFile(path: string, bytes: Uint8Array): SupportingFile {
	const ext = path.split('.').at(-1)?.toLowerCase() ?? '';
	const images: Record<string, string> = {
		png: 'image/png',
		jpg: 'image/jpeg',
		jpeg: 'image/jpeg',
		gif: 'image/gif',
		webp: 'image/webp',
		avif: 'image/avif',
		svg: 'image/svg+xml'
	};
	let text: string | null = null;
	try {
		text = textBytes(bytes);
	} catch {
		/* Binary is retained without interpreting it as UTF-8. */
	}
	if (images[ext]) return { path, bytes, text, kind: 'image', mime: images[ext] };
	if (['md', 'markdown'].includes(ext)) {
		if (text === null) throw new Error('Markdown is not valid UTF-8');
		return { path, bytes, text, kind: 'markdown', mime: 'text/markdown' };
	}
	if (
		[
			'txt',
			'csv',
			'json',
			'yaml',
			'yml',
			'toml',
			'xml',
			'mmd',
			'mermaid',
			'dot',
			'log',
			'py',
			'ts',
			'js',
			'sh',
			'css',
			'sql'
		].includes(ext) &&
		text !== null
	)
		return { path, bytes, text, kind: 'text', mime: 'text/plain' };
	return { path, bytes, text, kind: 'unsupported', mime: 'application/octet-stream' };
}
export async function readSupportingFile(
	source: RepositoryDataSource,
	path: string,
	ref: string,
	signal: AbortSignal
): Promise<SupportingFile> {
	if (!safePath(path)) throw new Error(`Unavailable repository path: ${path}`);
	const blob = await source.blob(path, ref, signal);
	if (signal.aborted) throw new DOMException('Read cancelled', 'AbortError');
	return classifyFile(path, blobBytes(blob.content, blob.encoding));
}
export function fileUrl(file: SupportingFile, preview = false) {
	let bytes = file.bytes;
	if (preview && file.mime === 'image/svg+xml') {
		if (file.text === null) throw new Error('SVG is not valid UTF-8');
		const clean = DOMPurify.sanitize(file.text, {
			USE_PROFILES: { svg: true },
			FORBID_TAGS: ['foreignObject', 'script', 'style', 'image', 'animate', 'set']
		});
		const doc = new DOMParser().parseFromString(clean, 'image/svg+xml');
		if (doc.documentElement.tagName !== 'svg' || doc.querySelector('parsererror'))
			throw new Error('Invalid SVG image');
		for (const node of doc.querySelectorAll('*'))
			for (const attr of [...node.attributes]) {
				if (
					attr.name === 'style' ||
					(/^(?:href|xlink:href)$/.test(attr.name) && !attr.value.startsWith('#')) ||
					/url\(\s*['"]?(?!#)/i.test(attr.value)
				)
					node.removeAttribute(attr.name);
			}
		bytes = new TextEncoder().encode(new XMLSerializer().serializeToString(doc.documentElement));
	}
	return URL.createObjectURL(
		new Blob([new Uint8Array(bytes)], { type: preview ? file.mime : 'application/octet-stream' })
	);
}

/** Hydrates only tagged repository images. Cleanup cancels reads and revokes every created URL. */
export function repositoryImages(
	node: HTMLElement,
	context: { source: RepositoryDataSource | null; branch: string }
) {
	const controller = new AbortController();
	const urls: string[] = [];
	let budget = 16 * 1024 * 1024;
	const images = [...node.querySelectorAll<HTMLImageElement>('img[data-repo-image]')];
	let cursor = 0;
	async function worker() {
		while (!controller.signal.aborted && cursor < images.length) {
			const index = cursor++,
				image = images[index],
				path = image.dataset.repoImage!;
			const unavailable = (reason: string) => {
				if (controller.signal.aborted) return;
				image.removeAttribute('src');
				const label = document.createElement('span');
				label.textContent = `Image unavailable (${path}): ${reason}`;
				image.replaceWith(label);
			};
			if (!context.source || index >= IMAGE_LIMIT || budget <= 0) {
				unavailable('image preview limit or source unavailable');
				continue;
			}
			try {
				const file = await readSupportingFile(
					context.source,
					path,
					context.branch,
					controller.signal
				);
				if (controller.signal.aborted) return;
				if (file.kind !== 'image') throw new Error('Unsupported image format');
				if (file.bytes.length > budget) throw new Error('Image preview byte limit exceeded');
				budget -= file.bytes.length;
				const url = fileUrl(file, true);
				urls.push(url);
				image.src = url;
				image.onerror = () => unavailable('image could not be displayed');
			} catch (error) {
				unavailable(String(error));
			}
		}
	}
	for (let i = 0; i < Math.min(6, images.length); i++) void worker();
	return {
		destroy() {
			controller.abort();
			for (const url of urls) URL.revokeObjectURL(url);
		}
	};
}
