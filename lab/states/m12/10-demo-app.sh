#!/usr/bin/env bash
# Idempotent: namespace demo and Deployment demo-app (image with sh and cat).
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
