#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Start state for M04: encryption off, TLS profiles unset.
set -euo pipefail
oc patch apiserver cluster --type=merge -p '{"spec":{"encryption":{"type":"identity"},"tlsSecurityProfile":null}}'
oc patch ingresscontroller default -n openshift-ingress-operator --type=merge -p '{"spec":{"tlsSecurityProfile":null}}'
