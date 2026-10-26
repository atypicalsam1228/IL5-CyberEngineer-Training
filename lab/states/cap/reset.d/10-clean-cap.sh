#!/usr/bin/env bash
# Remove everything the capstone created. Idempotent.
set -u
oc delete applications.argoproj.io cap-app -n openshift-gitops --ignore-not-found --wait=false
oc delete appprojects.argoproj.io cap -n openshift-gitops --ignore-not-found
oc delete secret cap-config-repo -n openshift-gitops --ignore-not-found
oc delete namespace cap-demo --ignore-not-found --wait=true --timeout=300s
if oc get clusterpolicy require-signed-images > /dev/null 2>&1; then
  NEW=$(oc get clusterpolicy require-signed-images -o json | jq -c '[.spec.rules[0].match.any[0].resources.namespaces[] | select(. != "cap-demo")]')
  oc patch clusterpolicy require-signed-images --type json -p "[{\"op\":\"replace\",\"path\":\"/spec/rules/0/match/any/0/resources/namespaces\",\"value\":$NEW}]"
fi
# Recreate the repository from scratch so the next run starts on a clean main.
curl -s -o /dev/null -X DELETE -H "Authorization: token $GITEA_TOKEN" "$GITEA_URL/api/v1/repos/$GITEA_USER/cap-config"
echo "capstone cleaned"
