#!/usr/bin/env bash
# Public development command; the built-wheel scenarios live with the e2e tests.
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
exec bash "$root/tests/e2e/smoke.sh" "$@"
