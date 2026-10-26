#!/usr/bin/env bash
# Idempotent: namespace demo and Deployment demo-app. M06 step 1 binds the developer role in demo.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
