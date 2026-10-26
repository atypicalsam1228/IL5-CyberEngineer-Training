"""Terraform argv builders, warnings, and output handling for lab up/down."""
from __future__ import annotations

import json

from labcli.environment import CONTAINER_TERRAFORM, CONTAINER_WORKSPACE, CONTRACT_VARS

STATE_PATH = f"{CONTAINER_WORKSPACE}/.lab/terraform.tfstate"
_CHDIR = f"-chdir={CONTAINER_TERRAFORM}"

COST_WARNING = """\
COST WARNING: 'lab up' builds a real OpenShift cluster and supporting
resources in your AWS account (compute, NAT gateway, Elastic IP, load
balancing, KMS key, S3 storage). They are billed until they are destroyed.
When you stop working, run 'lab down'. Closing this window does NOT stop
the charges."""

DESTROY_WARNING = """\
==================================================================
WARNING: 'lab down' DESTROYS your whole lab in AWS.
Everything in the cluster, the KMS key and the buckets will be removed.
Run it whenever you stop working: the lab bills until it is destroyed.
=================================================================="""

DOWN_FAILED = """\
!!! THE LAB MAY STILL BE RUNNING AND STILL BILLING !!!
Destroy did not finish. Run 'lab down' again. If it keeps failing, open the
AWS console and delete the resources tagged with your lab id by hand."""


def init_argv() -> tuple[str, ...]:
    return ("terraform", _CHDIR, "init", "-input=false")


def apply_argv() -> tuple[str, ...]:
    return ("terraform", _CHDIR, "apply", "-input=false", "-auto-approve", f"-state={STATE_PATH}")


def destroy_argv() -> tuple[str, ...]:
    return ("terraform", _CHDIR, "destroy", "-input=false", "-auto-approve", f"-state={STATE_PATH}")


def output_argv() -> tuple[str, ...]:
    return ("terraform", _CHDIR, "output", "-json", f"-state={STATE_PATH}")


def outputs_to_env(raw_json: str) -> dict[str, str]:
    """Map terraform outputs onto contract variable names. Ignores everything else."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    allowed = set(CONTRACT_VARS)
    result: dict[str, str] = {}
    for key, entry in data.items():
        name = str(key).upper()
        if name in allowed and isinstance(entry, dict) and "value" in entry:
            result[name] = str(entry["value"])
    return result
