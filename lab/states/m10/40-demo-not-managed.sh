#!/usr/bin/env bash
# Idempotent: demo-app is not yet managed by Argo CD, so the namespace label M10 step 1 adds must be absent.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
if oc get namespace demo -o json | jq -e '.metadata.labels["argocd.argoproj.io/managed-by"] != null' >/dev/null; then
  oc label namespace demo argocd.argoproj.io/managed-by-
fi
