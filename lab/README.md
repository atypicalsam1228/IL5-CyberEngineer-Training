# lab: IL5 training lab command

One command-line tool for the hands-on modules. Works on Mac and Windows.

## Install

1. Install Python 3.10 or newer and either podman or docker.
2. Build the tools image with `python lab.py build-image` (see image/README.md). It holds oc, kubectl, jq, curl, git, openssl, terraform, aws,
   python3, cosign, trivy, kustomize, tkn, argocd, velero, session-manager-plugin. Set `LAB_IMAGE` to its name
   (default: `il5-lab-tools:latest`).
3. Run the tool from this folder: `python lab.py <command>`
   Or install it: `pip install ./lab` and then run `lab <command>`.
4. Put your AWS credentials in your normal environment (for example AWS_PROFILE).
   They are passed into the container by name. Passwords and tokens are never printed.

## Commands

| Command | What it does |
|---|---|
| `lab modules` | List modules in the recommended order. |
| `lab up` | Build your lab in AWS with Terraform. Costs money. Asks you to type `yes`. |
| `lab down` | Destroy your lab. Run it every time you stop. Asks you to type `destroy`. |
| `lab shell` | Open the tools container with your workspace and lab variables. |
| `lab start <module>` | Load the module's starting state (example: `lab start siem-1`). |
| `lab reset <module>` | Return the module to its starting state. |
| `lab check <module>` | Run the module's tests. Prints PASS or FAIL for each, with expected and actual output. Exit code is 1 if any fail. |
| `lab build-image` | Build the tools container image locally from `image/Dockerfile`. |
| `lab status` | Show engine, workspace, which lab variables are set, modules applied. |

Every command that changes something accepts `--dry-run`, which prints what would run and
changes nothing. `up` and `down` also accept `--yes` to skip the question.

## Cost: read this

`lab up` creates billable AWS resources. They keep billing until `lab down` finishes.
Closing your laptop does not stop them. After `lab down`, confirm in the AWS console that
nothing tagged with your lab id remains.

## How check works

Each module's verify commands run in the tools container (or directly if you are already
inside `lab shell`). If the module's expected output starts with "Example only", the check
compares the stable labels on each expected line (the text before a colon or tab) and
ignores values and placeholders. Otherwise it compares the output exactly, ignoring
spacing. A few tests need a manual step (for example saving a file first); the module text
says so.

## Settings (optional environment variables)

`LAB_IMAGE`, `LAB_ENGINE` (podman or docker), `LAB_WORKSPACE` (default `~/lab-workspace`),
`LAB_STATES_DIR`, `LAB_TERRAFORM_DIR`, `LAB_GENERATORS_DIR`.

## For maintainers

Module data and tests are read from `../generators/content` (read only). Start states live
in `states/<module-id>/`: ordered `.sh` scripts (idempotent) and `.yaml` manifests
(`oc apply`), `reset.d/` for reset-only steps, `README.md`, and `TODO.md` where the lab
build must still supply something. Run tests: `pytest --cov=labcli`.
