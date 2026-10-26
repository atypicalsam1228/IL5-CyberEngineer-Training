#!/usr/bin/env bash
# Idempotent: Deployment demo-app in demo, and a writable shell (sh) in its image for the Falco tests.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
oc exec -n demo deployment/demo-app -- sh -c 'true' || die "no working sh in the demo-app image"
