#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Installs OpenShift GitOps (package openshift-gitops-operator; it creates the
# ArgoCD resource openshift-gitops in namespace openshift-gitops) and the File Integrity Operator in
# openshift-file-integrity. Creates NO Argo CD application, project, repository secret or FileIntegrity.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_operator openshift-gitops-operator openshift-gitops-operator all
wait_until "ArgoCD openshift-gitops" oc get argocd openshift-gitops -n openshift-gitops
wait_until "Argo CD repo server" oc get deployment openshift-gitops-repo-server -n openshift-gitops
oc rollout status deployment/openshift-gitops-repo-server -n openshift-gitops --timeout=240s
ensure_operator file-integrity-operator openshift-file-integrity own
