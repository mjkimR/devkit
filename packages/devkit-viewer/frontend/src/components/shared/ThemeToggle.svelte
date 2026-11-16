<script lang="ts">
	let {
		theme = 'dark',
		ontoggle
	}: {
		theme: 'dark' | 'light';
		ontoggle: () => void;
	} = $props();
</script>

<button
	class="theme-toggle-btn"
	title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
	onclick={ontoggle}
>
	{theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
</button>

<style>
	.theme-toggle-btn {
		background-color: var(--bg-btn);
		border: 1px solid var(--border-btn);
		color: var(--text-btn);
		padding: 4px 10px;
		border-radius: 6px;
		font-size: 12px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
		display: inline-flex;
		align-items: center;
		gap: 4px;
	}

	.theme-toggle-btn:hover {
		background-color: var(--btn-hover-bg);
		color: var(--text-primary);
	}
</style>
