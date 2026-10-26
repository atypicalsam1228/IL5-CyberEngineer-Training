#!/usr/bin/env bash
# Idempotent: Deployment demo-app running in demo. After M09 it is the signed image; if M09 was skipped
# it is the base image. Either way it is NOT managed by Argo CD yet (see 40-demo-not-managed.sh).
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
