<script lang="ts">
	let {
		html,
		diagramAction
	}: {
		html: string;
		diagramAction?: (node: HTMLElement) => { destroy: () => void };
	} = $props();

	function actionProxy(node: HTMLElement) {
		return diagramAction?.(node);
	}
</script>

<article class="markdown-body" use:actionProxy>
	{@html html}
</article>

<style>
	.markdown-body {
		font-size: 15px;
		line-height: 1.7;
		color: var(--text-secondary);
	}

	.markdown-body :global(h1) {
		font-size: 26px;
		font-weight: 700;
		color: var(--text-primary);
		border-bottom: 1px solid var(--border-panel);
		padding-bottom: 8px;
		margin-top: 24px;
		margin-bottom: 16px;
	}

	.markdown-body :global(h2) {
		font-size: 20px;
		font-weight: 600;
		color: var(--text-primary);
		border-bottom: 1px solid var(--border-panel);
		padding-bottom: 6px;
		margin-top: 28px;
		margin-bottom: 14px;
	}

	.markdown-body :global(h3) {
		font-size: 16px;
		font-weight: 600;
		color: var(--text-primary);
		margin-top: 20px;
		margin-bottom: 10px;
	}

	.markdown-body :global(p) {
		margin-bottom: 16px;
	}

	.markdown-body :global(ul),
	.markdown-body :global(ol) {
		padding-left: 24px;
		margin-bottom: 16px;
	}

	.markdown-body :global(li) {
		margin-bottom: 6px;
	}

	.markdown-body :global(code) {
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
		font-size: 13px;
		background-color: var(--code-bg);
		color: var(--code-color);
		padding: 2px 6px;
		border-radius: 4px;
	}

	.markdown-body :global(pre) {
		background-color: var(--pre-bg);
		border: 1px solid var(--pre-border);
		border-radius: 8px;
		padding: 16px;
		overflow-x: auto;
		margin-bottom: 16px;
	}

	.markdown-body :global(pre code) {
		background: none;
		color: var(--pre-text);
		padding: 0;
	}

	.markdown-body :global(table) {
		width: 100%;
		border-collapse: collapse;
		margin-bottom: 20px;
	}

	.markdown-body :global(th),
	.markdown-body :global(td) {
		border: 1px solid var(--table-border);
		padding: 8px 12px;
		font-size: 13px;
	}

	.markdown-body :global(th) {
		background-color: var(--th-bg);
		color: var(--th-text);
		font-weight: 600;
	}

	.markdown-body :global(blockquote) {
		border-left: 4px solid #6366f1;
		padding-left: 14px;
		margin: 16px 0;
		color: var(--text-muted);
	}

	/* Mermaid Diagram Container */
	.markdown-body :global(.mermaid-diagram) {
		position: relative;
		display: flex;
		flex-direction: column;
		margin: 24px 0;
		padding: 12px 16px 16px;
		border-radius: 8px;
		background-color: var(--bg-panel);
		border: 1px solid var(--border-panel);
		transition: border-color 0.15s ease;
	}

	.markdown-body :global(.mermaid-diagram:hover) {
		border-color: var(--border-btn);
	}

	.markdown-body :global(.diagram-toolbar) {
		display: flex;
		justify-content: flex-end;
		margin-bottom: 8px;
	}

	.markdown-body :global(.diagram-action-btn) {
		background-color: var(--bg-btn);
		border: 1px solid var(--border-btn);
		color: var(--text-btn);
		padding: 3px 8px;
		border-radius: 5px;
		font-size: 11px;
		font-weight: 500;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 4px;
		transition: all 0.15s ease;
		opacity: 0.75;
	}

	.markdown-body :global(.mermaid-diagram:hover .diagram-action-btn) {
		opacity: 1;
	}

	.markdown-body :global(.diagram-action-btn:hover) {
		background-color: var(--btn-hover-bg);
		color: var(--text-primary);
	}

	.markdown-body :global(.diagram-svg-wrap) {
		display: flex;
		justify-content: center;
		overflow-x: auto;
		width: 100%;
	}

	.markdown-body :global(.diagram-svg-wrap svg) {
		max-width: 100%;
		height: auto;
	}
</style>

