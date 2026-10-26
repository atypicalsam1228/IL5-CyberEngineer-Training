#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Namespace build, OpenShift Pipelines (package openshift-pipelines-operator-rh,
# which also installs the openshift-pipelines tasks), and a check that Kyverno (lab-provided) is present.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_operator openshift-pipelines-operator-rh openshift-operators global
ensure_namespace build
oc get namespace kyverno >/dev/null || die "namespace kyverno is missing (the lab build installs Kyverno)"
wait_until "service account pipeline in build" oc get serviceaccount pipeline -n build
for task in git-clone buildah openshift-client; do
  wait_until "task $task in openshift-pipelines" oc get task "$task" -n openshift-pipelines
done
