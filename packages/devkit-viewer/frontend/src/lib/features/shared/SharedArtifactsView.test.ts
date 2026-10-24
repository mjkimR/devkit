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
			expect(screen.getByText('저장소에 공유된 아티팩트가 없습니다.')).toBeTruthy();
			expect(screen.getByText('공유 공간 (Shared Space)')).toBeTruthy();
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

		const rawBtn = screen.getByText('Raw 보기');
		await fireEvent.click(rawBtn);

		await waitFor(() => {
			expect(screen.getByText('Markdown 뷰')).toBeTruthy();
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

		const searchInput = screen.getByPlaceholderText('슬러그, SHA, ID 검색...');
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
			expect(screen.getByText('문서 메타 정보')).toBeTruthy();
			expect(screen.getByText('식별 정보')).toBeTruthy();
		});

		const toggleBtn = screen.getByTitle('메타 정보 서랍 닫기');
		await fireEvent.click(toggleBtn);

		await waitFor(() => {
			expect(screen.queryByText('식별 정보')).toBeNull();
		});

		const openBtn = screen.getByTitle('메타 정보 서랍 열기');
		await fireEvent.click(openBtn);

		await waitFor(() => {
			expect(screen.getByText('식별 정보')).toBeTruthy();
		});
	});
});
