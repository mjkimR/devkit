import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/svelte';
import { afterEach, describe, expect, it } from 'vitest';
import SharedArtifactsView from './SharedArtifactsView.svelte';
import type { RepositoryDataSource, SharedArtifactMetadata } from '../../api/repository';

const mockArtifacts: SharedArtifactMetadata[] = [
	{
		generation_id: 'a1b2c3d4e5f600001111222233334444',
		kind: 'proposal-review',
		slug: 'alpha-feature',
		source_sha: '1234567890abcdef1234567890abcdef12345678',
		language: 'ko',
		content_sha256: 'fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321',
		content_type: 'text/markdown',
		byte_count: 120,
		created_at: new Date(Date.now() - 3600000).toISOString(),
		expires_at: new Date(Date.now() + 6 * 86400000).toISOString(),
		revision: 'fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321',
		artifact_uri: 'shared://ns/a1b2c3d4e5f600001111222233334444'
	},
	{
		generation_id: 'b2c3d4e5f6a100001111222233334444',
		kind: 'proposal-review',
		slug: 'beta-feature',
		source_sha: 'abcdef1234567890abcdef1234567890abcdef12',
		language: 'en',
		content_sha256: '0987654321fedcba0987654321fedcba0987654321fedcba0987654321fedcba',
		content_type: 'text/markdown',
		byte_count: 240,
		created_at: new Date(Date.now() - 7200000).toISOString(),
		expires_at: new Date(Date.now() + 5 * 86400000).toISOString(),
		revision: '0987654321fedcba0987654321fedcba0987654321fedcba0987654321fedcba',
		artifact_uri: 'shared://ns/b2c3d4e5f6a100001111222233334444'
	}
];

function createMockSource(artifacts: SharedArtifactMetadata[]): RepositoryDataSource {
	return {
		info: async () => ({ default_branch: 'main' }),
		tree: async () => ({ items: [] }),
		blob: async () => ({ path: '', content: '', encoding: 'utf-8' }),
		sharedList: async () => ({ artifacts }),
		sharedBlob: async (generationId: string) => {
			const item = artifacts.find((a) => a.generation_id === generationId);
			if (!item) throw new Error('Not found');
			return {
				metadata: item,
				content: `# Review for ${item.slug}\n\nThis is a mock report content.`,
				artifact_uri: item.artifact_uri || `shared://${item.generation_id}`
			};
		}
	};
}

describe('SharedArtifactsView', () => {
	afterEach(cleanup);

	it('renders empty guide state when no artifacts are found', async () => {
		const source = createMockSource([]);
		render(SharedArtifactsView, { props: { source } });

		await waitFor(() => {
			expect(screen.getByText('No shared artifacts in repository.')).toBeTruthy();
			expect(screen.getByText('Shared Space')).toBeTruthy();
		});
	});

	it('loads and lists artifacts, selecting the first by default', async () => {
		const source = createMockSource(mockArtifacts);
		const { container } = render(SharedArtifactsView, { props: { source, repoId: 'test-repo' } });

		await waitFor(() => {
			const list = container.querySelector('.artifact-list')!;
			expect(within(list as HTMLElement).getByText('alpha-feature')).toBeTruthy();
			expect(within(list as HTMLElement).getByText('beta-feature')).toBeTruthy();
			expect(screen.getByText('Review for alpha-feature')).toBeTruthy();
		});
	});

	it('switches selected artifact on click and toggles raw mode', async () => {
		const source = createMockSource(mockArtifacts);
		const { container } = render(SharedArtifactsView, { props: { source, repoId: 'test-repo' } });

		await waitFor(() => {
			const list = container.querySelector('.artifact-list')!;
			expect(within(list as HTMLElement).getByText('alpha-feature')).toBeTruthy();
		});

		const list = container.querySelector('.artifact-list')!;
		const betaCard = within(list as HTMLElement).getByText('beta-feature');
		await fireEvent.click(betaCard);

		await waitFor(() => {
			expect(screen.getByText('Review for beta-feature')).toBeTruthy();
		});

		const rawBtn = screen.getByText('Raw View');
		await fireEvent.click(rawBtn);

		await waitFor(() => {
			expect(screen.getByText('Markdown View')).toBeTruthy();
			expect(screen.getByText(/# Review for beta-feature/)).toBeTruthy();
		});
	});

	it('filters artifacts with the search input', async () => {
		const source = createMockSource(mockArtifacts);
		const { container } = render(SharedArtifactsView, { props: { source } });

		await waitFor(() => {
			const list = container.querySelector('.artifact-list')!;
			expect(within(list as HTMLElement).getByText('alpha-feature')).toBeTruthy();
			expect(within(list as HTMLElement).getByText('beta-feature')).toBeTruthy();
		});

		const searchInput = screen.getByPlaceholderText('Search slug, SHA, ID...');
		await fireEvent.input(searchInput, { target: { value: 'beta' } });

		await waitFor(() => {
			const list = container.querySelector('.artifact-list')!;
			expect(within(list as HTMLElement).queryByText('alpha-feature')).toBeNull();
			expect(within(list as HTMLElement).getByText('beta-feature')).toBeTruthy();
		});
	});

	it('toggles the right meta drawer', async () => {
		const source = createMockSource(mockArtifacts);
		render(SharedArtifactsView, { props: { source, repoId: 'test-repo' } });

		await waitFor(() => {
			expect(screen.getByText('Document Metadata')).toBeTruthy();
			expect(screen.getByText('Identification')).toBeTruthy();
		});

		const toggleBtn = screen.getByTitle('Close Metadata Drawer');
		await fireEvent.click(toggleBtn);

		await waitFor(() => {
			expect(screen.queryByText('Identification')).toBeNull();
		});

		const openBtn = screen.getByTitle('Open Metadata Drawer');
		await fireEvent.click(openBtn);

		await waitFor(() => {
			expect(screen.getByText('Identification')).toBeTruthy();
		});
	});

	it('renders an artifact whose frontmatter is invalid YAML as plain Markdown', async () => {
		const source = createMockSource([mockArtifacts[0]]);
		source.sharedBlob = async () => ({
			metadata: mockArtifacts[0],
			content: '---\nkey: [unclosed\n---\n# Body after bad frontmatter',
			artifact_uri: 'shared://x'
		});
		render(SharedArtifactsView, { props: { source, repoId: 'test-repo' } });

		await waitFor(() => {
			expect(screen.getByText('Body after bad frontmatter')).toBeTruthy();
		});
		expect(screen.queryByText('Loading artifact content...')).toBeNull();
	});

	it('shows the latest selection when an earlier detail request answers last', async () => {
		const [alpha, beta] = mockArtifacts;
		const source = createMockSource(mockArtifacts);
		source.sharedBlob = (generationId: string) => {
			const item = generationId === alpha.generation_id ? alpha : beta;
			return new Promise((resolve) =>
				setTimeout(
					() =>
						resolve({
							metadata: item,
							content: `# Review for ${item.slug}`,
							artifact_uri: `shared://${item.generation_id}`
						}),
					item === alpha ? 120 : 10
				)
			);
		};
		const { container } = render(SharedArtifactsView, { props: { source, repoId: 'test-repo' } });
		await waitFor(() => expect(container.querySelectorAll('.artifact-card').length).toBe(2));
		await fireEvent.click(container.querySelectorAll('.artifact-card')[1]);

		await new Promise((resolve) => setTimeout(resolve, 200));
		expect(container.querySelector('.detail-header h1')?.textContent).toBe('beta-feature');
	});

	it('does not keep showing the previous artifact when the new selection fails', async () => {
		const [alpha, beta] = mockArtifacts;
		const source = createMockSource([alpha, beta]);
		const load = source.sharedBlob!;
		source.sharedBlob = async (generationId: string, signal: AbortSignal) => {
			if (generationId === beta.generation_id) throw new Error('HTTP 500');
			return load(generationId, signal);
		};
		const { container } = render(SharedArtifactsView, { props: { source, repoId: 'test-repo' } });
		await waitFor(() =>
			expect(container.querySelector('.detail-header h1')?.textContent).toBe('alpha-feature')
		);
		await fireEvent.click(container.querySelectorAll('.artifact-card')[1]);

		await waitFor(() => expect(screen.getByText(/HTTP 500/)).toBeTruthy());
		expect(container.querySelector('.detail-header')).toBeNull();
	});

	it('stops loading when the selection clears while its detail is still loading', async () => {
		const pending = createMockSource([mockArtifacts[0]]);
		pending.sharedBlob = (_generationId: string, signal: AbortSignal) =>
			new Promise((_resolve, reject) =>
				signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')))
			);
		const { rerender } = render(SharedArtifactsView, {
			props: { source: pending, repoId: 'test-repo' }
		});
		await waitFor(() => expect(screen.getByText('Loading artifact content...')).toBeTruthy());

		await rerender({ source: createMockSource([]), repoId: 'test-repo' });

		await waitFor(() =>
			expect(screen.getByText('No shared artifacts in repository.')).toBeTruthy()
		);
		expect(screen.queryByText('Loading artifact content...')).toBeNull();
	});

	it('stops loading when the new source cannot read artifact details', async () => {
		const pending = createMockSource([mockArtifacts[0]]);
		pending.sharedBlob = (_generationId: string, signal: AbortSignal) =>
			new Promise((_resolve, reject) =>
				signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')))
			);
		const { rerender } = render(SharedArtifactsView, {
			props: { source: pending, repoId: 'test-repo' }
		});
		await waitFor(() => expect(screen.getByText('Loading artifact content...')).toBeTruthy());

		const listOnly = { ...createMockSource([mockArtifacts[0]]), sharedBlob: undefined };
		await rerender({ source: listOnly, repoId: 'test-repo' });

		await new Promise((resolve) => setTimeout(resolve, 20));
		expect(screen.queryByText('Loading artifact content...')).toBeNull();
	});

	it('encodes the repository and generation in the standalone review link', async () => {
		const source = createMockSource([mockArtifacts[0]]);
		const { container } = render(SharedArtifactsView, {
			props: { source, repoId: 'repo #1/x' }
		});
		await waitFor(() => expect(container.querySelector('a.action-btn')).not.toBeNull());
		expect(container.querySelector('a.action-btn')?.getAttribute('href')).toBe(
			`/review/repo%20%231%2Fx/${mockArtifacts[0].generation_id}`
		);
	});
});
