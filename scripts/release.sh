#!/usr/bin/env bash
# Build the release assets for a version tag:
#   release.sh vX.Y.Z
# Checks that the tag is vX.Y.Z and names the devkit package's version, builds a
# wheel of every workspace package into dist/release/, writes SHA256SUMS there
# and the release notes (install commands for this tag) to dist/release-notes.md.
# The devkit-embed model wheel is not rebuilt: the notes point at the release
# that ships it, pinned in the devkit package's [tool.uv.sources].
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

tag=${1:?Expected a version tag such as v0.1.0}
if [[ ! "$tag" =~ ^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "error: $tag is not a vX.Y.Z version tag" >&2
    exit 1
fi
version=${tag#v}
devkit_version=$(awk -F'"' '/^version[[:space:]]*=/ { print $2; exit }' packages/devkit/pyproject.toml)
if [ "$devkit_version" != "$version" ]; then
    echo "error: $tag does not match the devkit version $devkit_version in packages/devkit/pyproject.toml" >&2
    exit 1
fi

out=dist/release
rm -rf "$out"
mkdir -p "$out"
modules=$(list_modules)
model_url=$(model_wheel_url)
for module in $modules; do
    uv build --package "$module" --wheel --out-dir "$out" >/dev/null
done
(cd "$out" && shasum -a 256 -- *.whl > SHA256SUMS)

repository=${GITHUB_REPOSITORY:-$(git remote get-url origin | sed -E 's#^(git@github\.com:|https://github\.com/)##; s#\.git$##')}
base="https://github.com/$repository/releases/download/$tag"
devkit_wheel=$(basename "$out"/agt_devkit-*.whl)
advisory_wheel=$(basename "$out"/devkit_advisory-*.whl)
cat > dist/release-notes.md <<EOF
## Install

\`\`\`bash
# devkit (requires devkit-advisory of the same version)
uv add --dev "agt-devkit @ $base/$devkit_wheel" "devkit-advisory @ $base/$advisory_wheel"

# devkit with dense and hybrid search (adds numpy, tokenizers and the 15 MB embedding model)
uv add --dev "agt-devkit[search] @ $base/$devkit_wheel" "devkit-advisory @ $base/$advisory_wheel" "devkit-embed @ $model_url"

# devkit.advisory alone, as a runtime dependency of a library or service (standard library only)
uv add "devkit-advisory @ $base/$advisory_wheel"
\`\`\`

Checksums: \`SHA256SUMS\`.
EOF

echo "[RELEASE: $tag assets=$out]"
cat "$out/SHA256SUMS"
