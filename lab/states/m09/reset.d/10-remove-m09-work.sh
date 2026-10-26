#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Removes what M09 steps 1 to 4 create. Images already pushed to the
# registry stay (a registry cleanup is a lab-build job).
set -euo pipefail
oc delete clusterpolicy require-signed-images --ignore-not-found
oc delete pipelinerun --all -n build --ignore-not-found
oc delete pipeline secure-release -n build --ignore-not-found
oc delete pvc source-pvc -n build --ignore-not-found
oc delete secret cosign-signing gitea-clone -n build --ignore-not-found
oc delete secret cosign-public -n kyverno --ignore-not-found
oc get rolebinding -n demo -o json |
  jq -r '.items[] | select(any(.subjects[]?; .kind == "ServiceAccount" and .name == "pipeline" and .namespace == "build")) | select(.roleRef.name == "edit") | .metadata.name' |
  while read -r name; do oc delete rolebinding "$name" -n demo --ignore-not-found; done
oc delete pod unsigned-test -n demo --ignore-not-found
