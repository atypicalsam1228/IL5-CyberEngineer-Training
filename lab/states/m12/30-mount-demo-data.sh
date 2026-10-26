#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Mounts the claim demo-data at /data in demo-app (a merge by name, so a
# second run changes nothing) and waits until the claim is Bound and demo-app is ready.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
oc patch deployment demo-app -n demo --type strategic -p '{"spec":{"template":{"spec":{
  "volumes":[{"name":"demo-data","persistentVolumeClaim":{"claimName":"demo-data"}}],
  "containers":[{"name":"demo-app","volumeMounts":[{"name":"demo-data","mountPath":"/data"}]}]}}}}'
oc rollout status deployment/demo-app -n demo --timeout=240s
bound() { [ "$(oc get pvc demo-data -n demo -o jsonpath='{.status.phase}')" = Bound ]; }
wait_until "claim demo-data to be Bound" bound
oc exec -n demo deployment/demo-app -- sh -c 'touch /data/.lab-write-test && rm /data/.lab-write-test' ||
  die "/data is not writable by demo-app (check the storage class and fsGroup)"
