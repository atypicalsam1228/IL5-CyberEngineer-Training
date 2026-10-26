#!/usr/bin/env bash
# Idempotent: Deployment demo-app (container name demo-app) in demo. If it already exists (for example
# from an earlier module) it is kept. Starting it from the image signed by the lab build is a lab-build
# step that needs the registry and Cosign (see TODO.md); until then it runs the base image.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
oc get deployment demo-app -n demo -o json | jq -e 'any(.spec.template.spec.containers[]; .name == "demo-app")' >/dev/null ||
  die "demo-app has no container named demo-app (the pipeline deploy task sets that container's image)"
