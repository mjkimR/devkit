import DOMPurify from 'dompurify';

export function createDiagramRenderer(
	getTheme: () => 'dark' | 'light',
	onOpenFullscreen: (svg: string) => void,
	onError?: (msg: string) => void
) {
	return function renderDiagrams(node: HTMLElement) {
		let active = true;
		void (async () => {
			const diagrams = node.querySelectorAll<HTMLElement>('pre > code.language-mermaid');
			if (!diagrams.length) return;
			const { default: mermaid } = await import('mermaid');
			const isDark = getTheme() === 'dark';
			mermaid.initialize({
				startOnLoad: false,
				securityLevel: 'strict',
				htmlLabels: false,
				flowchart: { htmlLabels: false },
				theme: isDark ? 'dark' : 'default',
				themeVariables: isDark
					? {
							darkMode: true,
							background: '#111827',
							mainBkg: '#1e293b',
							primaryColor: '#1e293b',
							primaryTextColor: '#f8fafc',
							primaryBorderColor: '#475569',
							lineColor: '#94a3b8',
							textColor: '#e2e8f0',
							edgeLabelBackground: '#1e293b',
							tertiaryColor: '#0f172a',
							tertiaryTextColor: '#f8fafc',
							nodeBorder: '#475569',
							clusterBkg: '#0f172a',
							clusterBorder: '#334155'
						}
					: {
							darkMode: false,
							background: '#f8fafc',
							mainBkg: '#ffffff',
							primaryColor: '#ffffff',
							primaryTextColor: '#0f172a',
							primaryBorderColor: '#cbd5e1',
							lineColor: '#334155',
							textColor: '#1e293b',
							edgeLabelBackground: '#ffffff',
							nodeBorder: '#cbd5e1',
							clusterBkg: '#f1f5f9',
							clusterBorder: '#cbd5e1'
						}
			});
			for (const code of diagrams) {
				if (!active) return;
				const container = document.createElement('div');
				container.style.position = 'absolute';
				container.style.visibility = 'hidden';
				document.body.append(container);
				try {
					const { svg } = await mermaid.render(
						`sdd-${crypto.randomUUID()}`,
						code.textContent || '',
						container
					);
					if (active) {
						const diagram = document.createElement('div');
						diagram.className = 'mermaid-diagram';

						const toolbar = document.createElement('div');
						toolbar.className = 'diagram-toolbar';

						const expandBtn = document.createElement('button');
						expandBtn.type = 'button';
						expandBtn.className = 'diagram-action-btn';
						expandBtn.title = 'View diagram fullscreen';
						expandBtn.innerHTML = `⛶ Fullscreen`;
						expandBtn.addEventListener('click', () => {
							onOpenFullscreen(svg);
						});

						toolbar.appendChild(expandBtn);

						const svgWrap = document.createElement('div');
						svgWrap.className = 'diagram-svg-wrap';
						svgWrap.innerHTML = DOMPurify.sanitize(svg, {
							USE_PROFILES: { svg: true, svgFilters: true }
						});

						diagram.appendChild(toolbar);
						diagram.appendChild(svgWrap);
						code.parentElement?.replaceWith(diagram);
					}
				} catch (err) {
					if (active) code.parentElement?.setAttribute('title', `Mermaid: ${String(err)}`);
				} finally {
					container.remove();
				}
			}
		})().catch((err) => {
			if (active && onError) onError(`Failed to load diagram: ${String(err)}`);
		});
		return {
			destroy() {
				active = false;
			}
		};
	};
}
