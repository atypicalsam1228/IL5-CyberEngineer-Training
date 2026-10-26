#!/usr/bin/env bash
# Remove the Kyverno policies created in M07 (names from the M07 module).
set -euo pipefail
oc delete clusterpolicy disallow-privileged-containers require-run-as-nonroot disallow-latest-tag --ignore-not-found
