<script lang="ts">
	let { content }: { content: string } = $props();
</script>

<pre class="raw-content"><code>{content}</code></pre>

<style>
	.raw-content {
		background-color: var(--pre-bg);
		border: 1px solid var(--pre-border);
		border-radius: 8px;
		padding: 20px;
		overflow-x: auto;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
		font-size: 13px;
		line-height: 1.6;
		color: var(--pre-text);
	}
</style>
