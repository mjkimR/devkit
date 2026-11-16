import { fireEvent, screen, waitFor } from '@testing-library/svelte';

/**
 * Opens a file in the Files tab the way a reader does: the Files rail entry, the `docs` crumb when a file is shown,
 * then the file's entry in the listing. The fixture's `tree` must list the file under `docs`.
 */
export async function openFile(path: string) {
	const files = screen.getByRole('button', { name: 'Files' });
	if (files.getAttribute('aria-pressed') !== 'true') await fireEvent.click(files);
	const crumb = [...document.querySelectorAll<HTMLButtonElement>('.crumb-btn')].find(
		(button) => button.textContent?.trim() === 'docs'
	);
	if (crumb) await fireEvent.click(crumb);
	const node = await waitFor(() => {
		const found = [...document.querySelectorAll<HTMLButtonElement>('.tree-node')].find(
			(button) => button.querySelector('.node-name')?.textContent === path.split('/').at(-1)
		);
		if (!found) throw new Error(`no tree entry for ${path}`);
		return found;
	});
	await fireEvent.click(node);
}
