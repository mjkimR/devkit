// Cold-load probe: headless Chrome over CDP against a running `devkit viewer serve`.
// Usage: node coldload-probe.mjs <viewer-url> <repo-id> <runs> <out.json> [<tab label>] [<readiness selector>]
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const [url, repo, runsArg, out, tabArg, readyArg] = process.argv.slice(2);
const runs = Number(runsArg || 3);
const here = dirname(fileURLToPath(import.meta.url));
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const port = 9333;
const profile = mkdtempSync(join(here, 'chrome-'));
const proc = spawn(chrome, [
	'--headless=new',
	`--remote-debugging-port=${port}`,
	`--user-data-dir=${profile}`,
	'--no-first-run',
	'--disable-extensions',
	'--window-size=1400,900',
	'about:blank'
]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let version;
for (let i = 0; i < 50 && !version; i++) {
	try {
		version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
	} catch {
		await sleep(200);
	}
}

async function session() {
	const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
	const ws = new WebSocket(target.webSocketDebuggerUrl);
	await new Promise((r) => ws.addEventListener('open', r, { once: true }));
	let id = 0;
	const pending = new Map();
	ws.addEventListener('message', (e) => {
		const msg = JSON.parse(e.data);
		if (msg.id && pending.has(msg.id)) {
			pending.get(msg.id)(msg);
			pending.delete(msg.id);
		}
	});
	const send = (method, params = {}) =>
		new Promise((resolve, reject) => {
			const n = ++id;
			pending.set(n, (m) => (m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result)));
			ws.send(JSON.stringify({ id: n, method, params }));
		});
	const evaluate = async (expression) => {
		const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
		if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
		return r.result.value;
	};
	return {
		send,
		evaluate,
		close: async () => {
			ws.close();
			await fetch(`http://127.0.0.1:${port}/json/close/${target.id}`);
		}
	};
}

async function metrics(s) {
	const { metrics } = await s.send('Performance.getMetrics');
	return Object.fromEntries(metrics.map((m) => [m.name, m.value]));
}

// Click a rail tab and wait until the knowledge view has finished loading and shows `ready`.
const scenario = (tab, ready) => `(async () => {
  const until = (f, limit = 120000) => new Promise((resolve, reject) => {
    const start = performance.now();
    (function poll() { const v = f(); if (v) return resolve(v); if (performance.now() - start > limit) return reject(new Error('timeout')); requestAnimationFrame(poll); })();
  });
  await until(() => document.querySelector('button[aria-label="${tab}"]'));
  performance.setResourceTimingBufferSize(10000);
  performance.clearResourceTimings();
  const t0 = performance.now();
  document.querySelector('button[aria-label="${tab}"]').click();
  await until(() => document.querySelector('.knowledge'));
  const tLoaded = await until(() => !document.querySelector('.knowledge [role="status"]') && performance.now());
  const tReady = await until(() => (${ready}) && performance.now());
  // Main thread quiet: two consecutive 100 ms timers each firing within 20 ms of schedule.
  let quiet = 0, tQuiet = 0;
  while (quiet < 2) { const s = performance.now(); await new Promise((r) => setTimeout(r, 100)); const late = performance.now() - s - 100; if (late < 20) { quiet++; if (quiet === 1) tQuiet = s; } else quiet = 0; }
  const api = performance.getEntriesByType('resource').filter((e) => e.name.includes('/api/'));
  return {
    loaded_ms: Math.round(tLoaded - t0),
    first_content_ms: Math.round(tReady - t0),
    main_thread_quiet_ms: Math.round(tQuiet - t0),
    api_requests: api.length,
    blob_requests: api.filter((e) => e.name.includes('/blob?')).length,
    api_bytes: api.reduce((n, e) => n + (e.transferSize || e.encodedBodySize || 0), 0),
    chapters: document.querySelectorAll('.reading-content section.chapter').length
  };
})()`;

// The handbook first read: manifest plus one page through the existing blob endpoint.
const handbook = `(async () => {
  const base = '/api/repos/${repo}/blob?path=';
  const t0 = performance.now();
  const manifest = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob((await (await fetch(base + 'handbook/manifest.json')).json()).content), c => c.charCodeAt(0))));
  const t1 = performance.now();
  const page = await (await fetch(base + 'handbook/en/README.md')).json();
  const t2 = performance.now();
  return { manifest_ms: Math.round(t1 - t0), page_ms: Math.round(t2 - t1), page_bytes: page.size, tag: manifest.tag, langs: manifest.langs };
})()`;

const results = { url, repo, runs, chrome: version?.Browser, scenarios: {} };
const cases = {
	book: [
		tabArg || 'Book',
		readyArg
			? `document.querySelector(${JSON.stringify(readyArg)})`
			: "document.querySelectorAll('.reading-content section.chapter').length > 0"
	],
	proposals: ['Proposals', "document.querySelector('.reading-layout')"]
};
for (const [name, [tab, ready]] of Object.entries(cases)) {
	results.scenarios[name] = [];
	for (let i = 0; i < runs; i++) {
		const s = await session();
		await s.send('Performance.enable');
		await s.send('Page.enable');
		await s.send('Network.enable');
		await s.send('Network.setCacheDisabled', { cacheDisabled: true });
		await s.send('Page.navigate', { url: `${url}#repo=${encodeURIComponent(repo)}` });
		await sleep(500);
		// Let the dashboard finish its own loading first so it does not overlap the measured tab.
		await s.evaluate(`new Promise((resolve) => { (function poll() { if (document.querySelector('button[aria-label="${tab}"]')) setTimeout(resolve, 3000); else setTimeout(poll, 50); })(); })`);
		const before = await metrics(s);
		const r = await s.evaluate(scenario(tab, ready));
		let after = await metrics(s);
		if (name === 'book') {
			await s.evaluate(`document.querySelector('button[aria-label="Dashboard"]').click(); new Promise((r) => setTimeout(r, 500))`);
			const b2 = await metrics(s);
			const w = await s.evaluate(scenario(tab, ready));
			const a2 = await metrics(s);
			r.warm_index_cached = { first_content_ms: w.first_content_ms, blob_requests: w.blob_requests, script_ms: Math.round((a2.ScriptDuration - b2.ScriptDuration) * 1000), task_ms: Math.round((a2.TaskDuration - b2.TaskDuration) * 1000) };
		}
		r.script_ms_total_page = Math.round((after.ScriptDuration - before.ScriptDuration) * 1000);
		r.task_ms_total_page = Math.round((after.TaskDuration - before.TaskDuration) * 1000);
		r.dom_nodes = after.Nodes;
		r.js_heap_mb = Math.round(after.JSHeapUsedSize / 1e6);
		results.scenarios[name].push(r);
		console.log(name, i, JSON.stringify(r));
		await s.close();
	}
}
results.scenarios.handbook = [];
for (let i = 0; i < runs; i++) {
	const s = await session();
	await s.send('Page.enable');
	await s.send('Page.navigate', { url: `${url}#repo=${encodeURIComponent(repo)}` });
	await sleep(1500);
	const r = await s.evaluate(handbook);
	results.scenarios.handbook.push(r);
	console.log('handbook', i, JSON.stringify(r));
	await s.close();
}
writeFileSync(out, JSON.stringify(results, null, 2) + '\n');
proc.kill();
process.exit(0);
