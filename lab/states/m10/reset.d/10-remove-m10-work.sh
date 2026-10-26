#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Removes what M10 steps 1 to 4 create. The demo-config repository content
# is kept (a merged pull request stays in its history); the start files make main match the running demo-app.
set -euo pipefail
. "$(dirname "$0")/../../_common/lib.sh"
oc delete applications.argoproj.io demo-app -n openshift-gitops --ignore-not-found
oc delete appprojects.argoproj.io demo -n openshift-gitops --ignore-not-found
oc delete secret demo-config-repo -n openshift-gitops --ignore-not-found
oc delete fileintegrity node-integrity -n openshift-file-integrity --ignore-not-found
if oc get argocd openshift-gitops -n openshift-gitops -o json | jq -e '.spec.rbac != null' >/dev/null; then
  oc patch argocd openshift-gitops -n openshift-gitops --type merge -p '{"spec":{"rbac":null}}'
fi
if [ -n "${GITEA_URL:-}" ] && [ -n "${GITEA_TOKEN:-}" ] && [ -n "${GITEA_USER:-}" ]; then
  gitea_call DELETE "/repos/$GITEA_USER/demo-config/branch_protections/main"
  case "$GITEA_CODE" in 204 | 404) ;; *) die "could not remove branch protection on demo-config main (HTTP $GITEA_CODE)" ;; esac
fi
