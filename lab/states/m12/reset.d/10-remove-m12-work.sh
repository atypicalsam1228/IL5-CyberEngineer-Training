#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Removes what M12 steps 2 to 5 create: the DataProtectionApplication,
# the demo-daily schedule, the demo-manual-1 backup, the demo-restore-1 restore and the demo-restored
# namespace. Backup files already written to the bucket expire under the bucket's own rules.
set -euo pipefail
oc delete dataprotectionapplication dpa-demo -n openshift-adp --ignore-not-found
oc delete schedules.velero.io demo-daily -n openshift-adp --ignore-not-found
oc delete restores.velero.io demo-restore-1 -n openshift-adp --ignore-not-found
oc delete backups.velero.io demo-manual-1 -n openshift-adp --ignore-not-found
oc delete namespace demo-restored --ignore-not-found
