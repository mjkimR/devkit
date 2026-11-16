<script lang="ts">
	import DOMPurify from 'dompurify';

	let {
		svg,
		onclose
	}: {
		svg: string;
		onclose: () => void;
	} = $props();

	let zoomLevel = $state(1);

	function handleWheel(e: WheelEvent) {
		if (e.ctrlKey || e.metaKey) {
			e.preventDefault();
			const delta = e.deltaY < 0 ? 0.15 : -0.15;
			zoomLevel = Math.max(0.3, Math.min(4, +(zoomLevel + delta).toFixed(2)));
		}
	}

	$effect(() => {
		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape') onclose();
		};
		window.addEventListener('keydown', handleKey);
		return () => window.removeEventListener('keydown', handleKey);
	});
</script>

<div
	class="diagram-modal-backdrop"
	onclick={(e) => {
		if (e.target === e.currentTarget) onclose();
	}}
	onkeydown={(e) => {
		if (e.key === 'Escape') onclose();
	}}
	role="dialog"
	aria-modal="true"
	aria-label="Diagram Fullscreen View"
	tabindex="-1"
>
	<div class="diagram-modal-window">
		<div class="modal-header">
			<div class="modal-title">
				<span>📊 Mermaid Diagram</span>
			</div>
			<div class="modal-controls">
				<button
					class="modal-btn"
					onclick={() => (zoomLevel = Math.max(0.3, +(zoomLevel - 0.2).toFixed(1)))}
					title="Zoom out (Ctrl + wheel down)">➖</button
				>
				<span class="zoom-indicator">{Math.round(zoomLevel * 100)}%</span>
				<button
					class="modal-btn"
					onclick={() => (zoomLevel = Math.min(4, +(zoomLevel + 0.2).toFixed(1)))}
					title="Zoom in (Ctrl + wheel up)">➕</button
				>
				<button
					class="modal-btn reset-btn"
					onclick={() => (zoomLevel = 1)}
					title="Reset zoom (100%)">Reset</button
				>
				<button class="modal-btn close-btn" onclick={onclose} title="Close (ESC)">✕ Close</button>
			</div>
		</div>
		<div class="modal-content" onwheel={handleWheel}>
			<div class="modal-svg-canvas" style="transform: scale({zoomLevel});">
				{@html DOMPurify.sanitize(svg, {
					USE_PROFILES: { svg: true, svgFilters: true }
				})}
			</div>
		</div>
	</div>
</div>

<style>
	.diagram-modal-backdrop {
		position: fixed;
		inset: 0;
		z-index: 99999;
		background-color: rgba(0, 0, 0, 0.82);
		backdrop-filter: blur(8px);
		display: flex;
		flex-direction: column;
		padding: 16px;
		box-sizing: border-box;
		animation: fadeIn 0.15s ease;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.diagram-modal-window {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100%;
		background-color: var(--bg-viewport);
		border: 1px solid var(--border-header);
		border-radius: 10px;
		overflow: hidden;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
	}

	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 18px;
		background-color: var(--bg-header);
		border-bottom: 1px solid var(--border-header);
		flex-shrink: 0;
	}

	.modal-title {
		font-size: 13px;
		font-weight: 600;
		color: var(--text-primary);
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.modal-controls {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.modal-btn {
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
		justify-content: center;
	}

	.modal-btn:hover {
		background-color: var(--btn-hover-bg);
		color: var(--text-primary);
	}

	.modal-btn.close-btn {
		background-color: #dc2626;
		border-color: #ef4444;
		color: #ffffff;
		margin-left: 8px;
	}

	.modal-btn.close-btn:hover {
		background-color: #b91c1c;
	}

	.zoom-indicator {
		font-size: 12px;
		font-weight: 600;
		color: var(--text-muted);
		min-width: 44px;
		text-align: center;
		user-select: none;
	}

	.modal-content {
		flex: 1;
		overflow: auto;
		padding: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: var(--bg-panel);
	}

	.modal-svg-canvas {
		transform-origin: center center;
		transition: transform 0.1s ease-out;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.modal-svg-canvas :global(svg) {
		max-width: none !important;
		height: auto !important;
	}
</style>
