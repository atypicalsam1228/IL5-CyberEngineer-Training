#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. ASSUMPTION TO CONFIRM LIVE: the registry at REGISTRY_HOST accepts the
# Gitea user and token (true for the Gitea built-in registry). Creates, only the lab-side credentials:
#   registry-pull in namespace kyverno (so Kyverno can read signatures)
#   registry-credentials in namespace build, linked to service account pipeline (buildah, Trivy, Cosign)
# The learner's own secrets (cosign-signing, cosign-public, gitea-clone) are NOT created here.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env REGISTRY_HOST GITEA_USER GITEA_TOKEN
make_registry_secret() { # namespace name
  oc create secret docker-registry "$2" -n "$1" --docker-server="$REGISTRY_HOST" \
    --docker-username="$GITEA_USER" --docker-password="$GITEA_TOKEN" --dry-run=client -o yaml | oc apply -f - >/dev/null
}
make_registry_secret kyverno registry-pull
make_registry_secret build registry-credentials
oc annotate secret registry-credentials -n build "tekton.dev/docker-0=$REGISTRY_HOST" --overwrite >/dev/null
oc secrets link pipeline registry-credentials -n build
