#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Installs the OADP operator (package redhat-oadp-operator) in openshift-adp.
# It does NOT create the DataProtectionApplication: that is M12 step 2.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_operator redhat-oadp-operator openshift-adp own
