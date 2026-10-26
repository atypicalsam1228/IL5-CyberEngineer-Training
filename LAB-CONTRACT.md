# Lab Contract

What every module may assume about the lab. If a module needs something not listed here, add it to the module's `lab_needs` list and the lab build will provide it.

## Where learners work

Learners run every command inside `lab shell`, a prebuilt tools container (works the same on Mac and Windows). It has: oc, kubectl, jq, curl, git, openssl, terraform, aws, python3, cosign, trivy, kustomize, tkn (Tekton CLI), argocd, velero.

## Cluster

- One real OpenShift Container Platform single-node cluster per learner on AWS (commercial region), built with FIPS mode on. The learner is cluster-admin on their own cluster.
- Namespaces: `openshift-logging` (collector), `siem` (Loki, Grafana, Alloy), `chat` (Mattermost), `keycloak` (identity), `gitea` (in-lab git server), `openshift-gitops` (Argo CD), `kyverno`, `build` (pipelines), `demo` (sample workload named `demo-app`), `openshift-adp` (backup), `security-tools` (Trivy Operator, ClamAV, Falco).
- Free or low-cost tools only. Included with OpenShift: OpenShift Logging, OpenShift Pipelines (Tekton), OpenShift GitOps (Argo CD), Compliance Operator, File Integrity Operator, OADP (Velero). Open source: Loki, Grafana, Alloy, Mattermost, Keycloak, Gitea, Kyverno, Trivy, Cosign, ClamAV, Falco.
- Time comes from chrony on each node. Audit, infrastructure and application logs are the three log types.

## Pinned versions

- Kyverno 1.19.2 (Helm chart kyverno/kyverno 3.9.2, namespace `kyverno`), the current stable release on 2026-10-20. In 1.19 ClusterPolicy (kyverno.io/v1) is deprecated but fully supported; the Kyverno project plans to remove it in 1.20. M07 and M09 use ClusterPolicy, so the lab must not install 1.20 or later until both modules are rewritten for ValidatingPolicy / ImageValidatingPolicy (policies.kyverno.io/v1).
- Terraform AWS provider `~> 6.0` (terraform/versions.tf, M02, M06).
- Versions the module code was checked against on 2026-10-26 (pin these at lab build; Falco and ClamAV and Keycloak versions are not otherwise fixed by the lab): Keycloak 26.8.1, Falco 0.45.1, ClamAV 1.5.4. Gitea is not pinned yet.
- Grafana 13.2.4 (OSS), the current stable release checked on 2026-10-26 (GitHub release tagged Latest, published 13 October 2026; grafana.com/docs/grafana/latest/whatsnew/ lists 13.2 as the newest). Pin this at lab build and confirm with `GET /api/health`. Grafana documents the contact-point, notification-policy, template and mute-timing provisioning API endpoints, and the folder and data-source-by-name APIs, as deprecated (they still work); SIEM-2 and SIEM-3 use them. See reviews/ITEMS-5-7.md.
- Lab shell tools: Terraform 1.11 or newer and the Session Manager plugin are required; both are in the tools image (lab/image/versions.txt).
- Velero keeps backups for its default 720 hours (30 days). Lab backups expire after that; a learner returning after a month must take a new backup (M12).

## Learner AWS identity

`lab shell` receives the learner's own AWS credentials. Direct AWS calls in module exercises (M04, M06) run as that identity, not as the bastion role. terraform/iam_lab_exercise.tf provides the managed policy for the M04 calls; attach it to that identity.

## Reset points

Each module has `lab start <module>` (load the starting state) and `lab check <module>` (run the module's tests and print pass or fail). `lab reset <module>` returns to the starting state. A combined run simply continues from the previous module's end state.

## Environment variables set by the lab

VARS: LAB_ID AWS_REGION CLUSTER_NAME CLUSTER_API LOKI_URL LOKI_CA_FILE LOKI_USER LOKI_PASSWORD GRAFANA_URL GRAFANA_USER GRAFANA_PASSWORD MM_URL MM_WEBHOOK_URL KEYCLOAK_URL KEYCLOAK_ADMIN_USER KEYCLOAK_ADMIN_PASSWORD GITEA_URL GITEA_USER GITEA_TOKEN ARGOCD_URL REGISTRY_HOST BACKUP_BUCKET LOG_BUCKET ARTIFACTS_BUCKET BASTION_ID KMS_KEY_ARN VPC_ID

Passwords and tokens live only in these variables. Modules never ask the learner to type or save one.

Credentials are random per lab. `lab up` (lab/labcli/credentials.py) creates a fresh 32-character random KEYCLOAK_ADMIN_PASSWORD, GRAFANA_PASSWORD and LOKI_PASSWORD the first time and keeps them in the 0600 lab.env file (never in Terraform state or outputs, never printed, removed by `lab down`). There are no default passwords anywhere. The lab build must deploy Keycloak, Grafana and Loki with these values from lab.env. GITEA_TOKEN and MM_WEBHOOK_URL are issued by Gitea and Mattermost when the lab build deploys them; the lab build writes them to lab.env and must not use fixed values. The Gitea, Mattermost, Keycloak, Grafana and Loki deployment itself is not in this repository yet.

## Not allowed in modules

Real organization names, a fictional company or story, documents the learner must write, and numbers that are not traced to a source citation.
