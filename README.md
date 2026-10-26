# IL5 CyberEngineer Training

A hands-on training program that teaches information security analysts to implement, and prove, the security tooling an Impact Level 5 (IL5) cloud system must have. Learners build each control on their own real OpenShift cluster in AWS, then run a test that shows the control works and a test that shows the failure when it is removed.

STATUS: DRAFT. Every module is written, validated and rendered, and the lab command-line tool passes its unit tests. Nothing has been run against a live cluster yet. Commands follow vendor documentation and are validated (`--dry-run=server`, `oc explain`, `--help`) before they are applied, but expect field-name corrections on the first live run.

## 1. Goal of the training

Analysts who have never typed a cluster command should finish able to:

1. Stand up a hardened, FIPS-mode OpenShift cluster from code and detect when it drifts from that code.
2. Collect, store, search, alert on and respond to audit records (a working SIEM).
3. Enforce identity, least privilege, encryption, network default-deny, hardening, vulnerability, malware, release, change and backup controls with real tools.
4. Prove each control with a positive test (it works) and a negative test (break it on purpose and watch it fail).
5. Put five controls around one workload and pass a nine-check score (the capstone).

The target is skill, not paperwork. The learner writes no documents. Everything is a command, a configuration applied to the lab, or a check, and the cluster holds the record.

Every module maps to NIST SP 800-53 Rev 5 controls and, where the value is assigned there, to the FedRAMP baseline and the DoD Cloud Computing SRG. Where a framework leaves a parameter organization-defined, the module says so and states the value the lab chooses. Every cited quotation is checked against the source text by the validator.

## 2. Who it is for

Information security analysts with little keyboard experience. Module M00 teaches the terminal, `oc`, `git` and reading YAML and errors before any security work begins. Each technical term is defined where it first appears and again in the module glossary.

## 3. How to use the training

### Requirements
- A laptop (Mac or Windows) with Python 3.10 or newer and podman or docker.
- An AWS account you may spend in, with your credentials in the normal environment (for example `AWS_PROFILE`). Use a lab account, not a production one: some exercises change account-level defaults.
- A Red Hat pull secret for OpenShift, as M02 explains.
- A budget. The author's estimate is about $18 per learner for a full run; it is an estimate, not a quote. The lab sets a budget alarm and a destroy-after date.

### The lab command
All hands-on work goes through one tool, `lab` (see `lab/README.md`). Every command that changes something accepts `--dry-run`.

| Command | What it does |
|---|---|
| `lab modules` | List modules in the recommended order |
| `lab build-image` | Build the tools container (oc, kubectl, jq, curl, git, openssl, terraform, aws, python3, cosign, trivy, kustomize, tkn, argocd, velero) |
| `lab up` | Build your lab in AWS with Terraform. Costs money |
| `lab shell` | Open the tools container with your workspace and lab variables. Run every module command inside it |
| `lab start <module>` | Load the module's starting state |
| `lab check <module>` | Run the module's tests and print PASS or FAIL with expected and actual output |
| `lab reset <module>` | Return the module to its starting state |
| `lab status` | Show engine, workspace and which modules are applied |
| `lab down` | Destroy your lab. Run it every time you stop |

### Working a module
1. Read **Why This Matters**: the requirement in plain words, the control mapping table, and the investigation questions already answered for each control. This is reading and is not timed.
2. Read **The Tools** (what each tool is, why it is used, how the pieces fit together).
3. Do **Implement**: at most five steps. Each step gives the reason, commands with a line-by-line table, an action and a checkpoint.
4. Do **Verify**: at least one positive and one negative test with the expected output.
5. Run `lab check <module>`.

Timed work is 55 to 75 minutes per module (hands-on plus verify). Work in the recommended order, or start any module alone with `lab start <module>`; a combined run continues from the previous module's end state.

### Two modes
- **Ready Lab**: prebuilt starting state; you implement the module's steps.
- **Architect**: each module has a brief; you design and build it yourself, then run the same checks.

### Stopping
Run `lab down` whenever you stop. Closing the laptop does not stop AWS billing. Afterwards confirm in the AWS console that nothing tagged with your lab id remains. Compliance-locked log objects cannot be deleted early; see SIEM-2.

## 4. Recommended order and module descriptions

Seventeen modules, in this order:
M00, M02, SIEM-1, SIEM-2, SIEM-3, SIEM-4, M12, M08, M05, M06, M11, M07, M04, M03, M09, M10, CAP.

Files are in `modules/` as `.docx` and `.md`, each with `img/` diagrams: one main diagram and one image per step that shows the picture building up.

### M00 Keyboard Survival and Machine Check (55 min)
No security control. Teaches the terminal, `lab shell`, asking the cluster questions with `oc`, saving work with `git`, reading YAML, and reading errors without panic. Includes a check that your laptop can run the lab. Negative test: make three mistakes on purpose and read the errors.

### M02 Lab Build with Terraform (CM-2, CM-6) (70 min)
Build your own lab as infrastructure as code: an encrypted, versioned state bucket, a customer-managed key with rotation, a network, a budget alarm, and a single-node OpenShift cluster with FIPS mode on. The files become the baseline; a plan after apply shows no drift. Negative test: turn key rotation off by hand and watch Terraform detect it.

### SIEM-1 Collect Audit Logs (AU-2, AU-3, AU-8, AU-12) (65 min)
Give the log collector a limited identity, forward audit, infrastructure and application logs to Loki, and confirm each type arrives. Positive tests: one audit record answers the six AU-3 questions; clocks are synchronized and timestamps show the millisecond and UTC. Negative test: remove the audit permission and watch the records stop.

### SIEM-2 Store and Protect Audit Logs (AU-9, AU-11, AU-4, AU-5) (70 min)
Move Loki to encrypted S3 with Object Lock, create auditor and ordinary identities, show the retention periods the lab sets, warn before storage fills, and keep records when the connection to Loki fails. Negative tests: an ordinary user cannot read or delete logs; a locked object cannot be deleted even with administrator cloud rights; stopping Loki loses no records.

### SIEM-3 Detect and Alert (SI-4, SI-4(5), AU-6) (70 min)
Connect Grafana alerting to a Mattermost channel, write pattern rules (failed logins, privilege changes), alert when a log type goes silent (closing the SIEM-1 gap), alert when a node clock loses synchronization, and set up the review routine. Negative test: stop the collector and the missing-logs alert fires.

### SIEM-4 Respond to an Incident (IR-4, IR-5, IR-6) (65 min)
Take an alert from Mattermost, open an incident channel, analyze and mark a simulated compromised workload, contain it (isolate the pod, cordon the node, scale down), remove the stolen permission, recover, and post the reports. No document is written; the channel and the cluster hold the record.

### M12 Backup and Recovery (CP-9, CP-10) (65 min)
Point OADP (Velero) at the encrypted bucket, schedule a backup, take one, and restore it into a fresh project. A backup that has never been restored is only a hope. Negative test: data written after the last backup is lost.

### M08 Vulnerability Management (RA-5, SI-2, CA-5) (70 min)
Scan a known-vulnerable image with Trivy, let Trivy Operator scan the running workload, read findings by severity, set the fix deadline, and track an unfixed flaw as a plan-of-action item inside the cluster. Tests: the vulnerable image fails the gate; a minimal, patched image passes; the item closes once fixed.

### M05 Identity and Multi-Factor Sign-In (IA-2, IA-5, AC-2, AC-7, AC-11) (65 min)
Make Keycloak the identity provider OpenShift trusts, require a one-time code, add certificate sign-in that stands in for a smart card, lock accounts after wrong passwords, and expire idle sessions. Negative tests: password alone is refused; no certificate means no sign-in; wrong passwords lock the account; an idle session times out.

### M06 Privileged Access and Session Audit (AC-6, AC-17, AU-14) (65 min)
Create administrator, developer and auditor roles and prove each with `oc auth can-i`; build a jump host with no open SSH port reachable only through Session Manager; send session records to the SIEM. Negative tests: a developer cannot do an administrator action; SSH from the internet is not possible.

### M11 Malware and Runtime Detection (SI-3, SI-4) (65 min)
ClamAV scans uploads and runs a daily scheduled scan that quarantines infected files; Falco watches runtime behavior (for example a shell opened in a container) and its events reach Loki. Negative test: disable the rule and the event is not raised.

### M07 Hardening and Policy as Code (CM-6, CM-7, CM-2) (70 min)
Scan the cluster against the DISA STIG with the Compliance Operator and fix a failing setting; enforce least functionality with Kyverno so over-privileged workloads are refused; record the baseline. Negative tests: non-compliant pods are denied; a failing hardening rule stays failed until fixed.

### M04 FIPS Cryptography and Keys (SC-13, SC-12, SC-28) (65 min)
Read the platform's cryptographic state, set the TLS profile, turn on etcd encryption, rotate the customer-managed key, and encrypt volumes and the backup bucket with it. Negative tests: a non-approved algorithm is refused on the FIPS node; the router refuses a weak cipher; a disabled key cannot decrypt (cryptographic erase).

### M03 Boundary and Default-Deny (SC-7, AC-4, CA-3, SC-8) (65 min)
Answers one question: is traffic protected only at the boundary, or also between internal components? Deny everything by default, allow only listed flows with NetworkPolicy, encrypt the allowed flow with mutual TLS (Service Mesh 3), and check every row of the ports, protocols and services table. Negative tests: a disallowed flow is blocked; plain-text traffic between internal components is refused.

### M09 Secure Release Pipeline (SA-11, SI-7, SR-3) (65 min)
Build a Tekton pipeline that tests code, scans the image with Trivy, records a software bill of materials, and signs the image with Cosign; Kyverno then refuses any unsigned image. Negative tests: an image with a critical finding fails the gate; an unsigned image is denied.

### M10 GitOps and Change Control (CM-3, CM-5, SI-7) (70 min)
Make git the single source of truth: Argo CD deploys what git says and reverts manual changes, Gitea refuses direct pushes to the approved branch, Argo CD roles limit who can sync, and the File Integrity Operator watches node files. Negative tests: a manual change is reverted; an unapproved push is rejected; a viewer cannot sync; a changed node file is detected.

### CAP Capstone: One Workload, Five Controls (AC-6, CM-3, SC-7, AU-12, SI-7) (75 min)
No new tool. Put least-privilege access, deployment only through approved git changes, default-deny networking, SIEM records and signed-image-only admission around one fresh workload using what you built earlier. `lab check cap` runs nine checks (five positive, four negative) and prints a score with a one-line fix for each failure.

## 5. Repository layout

| Path | What it holds |
|---|---|
| `modules/` | Rendered modules (`.docx`, `.md`) and `img/` diagrams |
| `generators/` | Module content (`content/<id>.py`), the renderer (`render.py`), the validator (`validate.py`) and the diagram system (`module_diagrams.py`) |
| `lab/` | The `lab` command-line tool, tests, tools image and per-module start states |
| `terraform/` | Lab infrastructure for one learner, a sweeper for expired labs, and scripts. Read `terraform/README.md` before applying anything |
| `LAB-CONTRACT.md` | What every module may assume about the lab: namespaces, tools, pinned versions, environment variables |
| `BUILD-BRIEF.md` | The module schema and writing rules |
| `DIAGRAM-CHECKLIST.md` | Rules every diagram must pass |
| `REVIEW-BRIEF.md`, `REVIEW-CHECKLIST.md` | How modules are reviewed |

## 6. Building and checking the content

From `generators/`:

    python validate.py --all     # citations, ASCII, banned words, commands, variables
    python render.py --all       # writes modules/*.docx, *.md and img/*.png

The validator checks every cited quotation against the framework source text, so the framework documents must be available locally; without them the citation checks cannot run. Diagrams need Graphviz.

From `lab/`: `pytest --cov=labcli`.

## 7. Rules the content follows

- Citations come only from NIST, FedRAMP and the DoD Cloud Computing SRG. No real organization, program or internal document is named or quoted.
- Where a control leaves a value organization-defined, the lab chooses one and says so.
- Free or low-cost tools only (listed in `LAB-CONTRACT.md`).
- The learner writes no documents.
- Every term is defined inline at first use.

## 8. Known open items

- Nothing has run on a live cluster; all modules are DRAFT.
- The tools image has not been built (needs a running container engine).
- Installer IAM is not yet scoped to cluster ARNs (needs a live install).
- Kyverno is pinned to 1.19.2. M07 and M09 use ClusterPolicy, which the Kyverno project plans to remove in 1.20; both modules must move to ValidatingPolicy / ImageValidatingPolicy before the pin is raised.
- Cosign signing-config migration (M09), Grafana provisioning endpoints deprecated but working (SIEM-2, SIEM-3), M08 clock fix and the SIEM-3 clear-audit-log test are unverified.
- Diagram residuals: M05 arrows converge at the certificate box; M07 has one long arrow across the diagram.
- Terraform: `lab up` has not been applied; see "Not verified" in `terraform/README.md`.
