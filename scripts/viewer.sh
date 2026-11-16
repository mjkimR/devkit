#!/usr/bin/env bash
# Frontend commands of the devkit-viewer package (packages/devkit-viewer/frontend); they need Node and npm:
#   viewer.sh install   npm ci
#   viewer.sh lint      prettier --check
#   viewer.sh check     svelte-check, warnings fail
#   viewer.sh test      vitest
#   viewer.sh probe DIR [ARGS...]
#                       vitest on the *.test.ts files under the absolute directory DIR outside src/ (a reviewer's
#                       throwaway probes), with the package's config and its dependencies resolved from the package;
#                       ARGS go to vitest
#   viewer.sh build     rebuild the committed page into src/devkit_viewer/static/ (artifact viewer-assets)
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../packages/devkit-viewer/frontend"

action=${1:?Expected an action: install, lint, check, test, probe or build}
if [[ $action != install && ! -d node_modules ]]; then
    echo "error: viewer frontend dependencies are not installed (no packages/devkit-viewer/frontend/node_modules); run \`just viewer install\` first" >&2
    exit 2
fi
case "$action" in
    install) npm ci --no-audit --no-fund ;;
    lint) npm run --silent lint ;;
    check) npm run --silent check ;;
    test) npm run --silent test ;;
    probe)
        dir=${2:?Expected the absolute directory of the probe tests}
        if [[ $dir != /* || ! -d $dir ]]; then
            echo "error: probe directory must be an existing absolute path: $dir" >&2
            exit 2
        fi
        dir=$(cd "$dir" && pwd -P)
        # vitest has no include flag, so a config beside the probes extends the package's: it collects DIR's tests and
        # resolves every dependency the package declares from the package, as a test under src/ would.
        config="$dir/.viewer-probe.vitest.config.mts"
        trap 'rm -f "$config"' EXIT
        cat >"$config" <<'CONFIG'
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
const root = process.env.VIEWER_PROBE_ROOT!;
const { default: base } = await import(join(root, 'vite.config.ts'));
const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const dedupe = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies, ...pkg.peerDependencies });
export default {
	...base,
	root,
	resolve: { ...base.resolve, dedupe },
	test: { ...base.test, dir: process.env.VIEWER_PROBE_DIR, include: ['**/*.test.ts'] }
};
CONFIG
        VIEWER_PROBE_ROOT=$PWD VIEWER_PROBE_DIR=$dir npx --no-install vitest run --config "$config" "${@:3}"
        ;;
    build) npm run --silent build:app ;;
    *) echo "Unknown action: $action" >&2; exit 2 ;;
esac
