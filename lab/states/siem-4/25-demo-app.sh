#!/usr/bin/env bash
# Idempotent: Deployment demo-app (label app=demo-app, service account demo-app, image with curl) in demo.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
oc exec -n demo deployment/demo-app -- curl --version >/dev/null || die "the demo-app image has no curl, which SIEM-4 needs"
