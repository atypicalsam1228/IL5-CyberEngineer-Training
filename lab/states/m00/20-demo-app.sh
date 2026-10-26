#!/usr/bin/env bash
# Idempotent: Deployment demo-app (namespace demo) running at the start state.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
