#!/usr/bin/env bash
# NOT YET RUN ON A LIVE ACCOUNT. Read-only checks of what M02 assumes. Changes nothing.
# The cluster does not exist yet at M02, so this state has no cluster steps.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env LAB_ID AWS_REGION
aws sts get-caller-identity --query Arn --output text >/dev/null || die "no working AWS credentials in lab shell"
zones=$(aws route53 list-hosted-zones --output json | jq '[.HostedZones[] | select(.Config.PrivateZone == false)] | length')
[ "$zones" = 1 ] || die "M02 needs exactly one public Route 53 hosted zone; found $zones"
[ -s "$HOME/pull-secret.json" ] || die "Red Hat pull secret missing at $HOME/pull-secret.json (the lab supplies it)"
command -v ssh-keygen >/dev/null || die "ssh-keygen is not installed in lab shell"
date -u -d '+1 day' +%Y-%m-%d >/dev/null 2>&1 || die "GNU date is required (date -d)"
say "AWS identity, one public hosted zone, pull secret, ssh-keygen and GNU date are present"
