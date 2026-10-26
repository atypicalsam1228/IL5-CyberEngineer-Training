#!/usr/bin/env bash
# Idempotent: create the empty rules config map only if it is absent.
set -euo pipefail
oc get namespace security-tools >/dev/null
oc get configmap falco-custom-rules -n security-tools >/dev/null 2>&1 || oc create configmap falco-custom-rules -n security-tools
