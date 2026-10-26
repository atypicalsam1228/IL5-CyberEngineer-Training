"""Official overview links and lab-use blurbs for the tools each module uses.

Links were fetched and confirmed when written. Red Hat links point at the OpenShift 4.22 docs.
"""

B = "https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/"
TOOLS = {
    "OpenShift Container Platform": (B + "overview/ocp-overview", "A Kubernetes container platform for running and managing containerized applications."),
    "oc": (B + "cli_tools/openshift-cli-oc", "The OpenShift command-line tool for creating and managing applications and projects from a terminal."),
    "openshift-install": (B + "installing_on_aws/installing-methods-aws", "The installer that provisions the cluster's AWS infrastructure and builds the cluster."),
    "OpenShift FIPS support": (B + "installation_overview/installing-fips", "FIPS mode makes core components use RHEL cryptographic libraries submitted to NIST for FIPS validation. It can only be set at install time."),
    "Security context constraints (SCC)": (B + "authentication_and_authorization/managing-pod-security-policies", "Cluster rules that control what a pod may do and which user IDs, host access and volumes it may use."),
    "NetworkPolicy": (B + "network_security/network-policy", "Rules for which pods may talk to which. Once a policy selects a pod, it accepts only what the policies allow."),
    "Service Mesh 3": ("https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh/3.4/html/about/ossm-about-openshift-service-mesh", "An Istio-based layer that adds encrypted service identity, traffic policy and telemetry between components without code changes."),
    "OpenShift Logging": (B + "logging/index", "Collects, forwards and stores cluster log data. (Loki as the store is described in the Logging 6.x docs, not on this page.)"),
    "Compliance Operator": (B + "security_and_compliance/compliance-operator", "Checks cluster configuration against standards and benchmarks. It is not an auditor."),
    "File Integrity Operator": (B + "security_and_compliance/file-integrity-operator", "Runs file integrity checks (AIDE) on cluster nodes and logs files that changed."),
    "OpenShift Pipelines (Tekton)": (B + "pipelines/index", "Kubernetes-native CI/CD built on Tekton."),
    "tkn": (B + "cli_tools/pipelines-cli-tkn", "Command-line tool for managing pipelines, runs and tasks."),
    "OpenShift GitOps (Argo CD)": (B + "gitops/index", "Deploys what a git repository says should be running, using Argo CD."),
    "OADP (Velero)": (B + "backup_and_restore/oadp-application-backup-and-restore", "Backs up applications, their resources and persistent volumes. Not a disaster-recovery tool for etcd or Operators."),
    "Terraform": ("https://developer.hashicorp.com/terraform/intro", "Describes infrastructure in text files, then creates, updates and tracks it."),
    "AWS CLI": ("https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html", "Runs AWS actions from a shell instead of the browser console."),
    "Amazon S3 Object Lock": ("https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html", "Makes stored objects write-once-read-many so they cannot be deleted or overwritten for a set time."),
    "AWS KMS": ("https://docs.aws.amazon.com/kms/latest/developerguide/overview.html", "Creates and controls encryption keys, held in FIPS-validated hardware."),
    "Amazon VPC": ("https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html", "A logically isolated virtual network for AWS resources."),
    "AWS Budgets": ("https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html", "Tracks spend against a budget and can notify when it is exceeded."),
    "AWS Systems Manager Session Manager": ("https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html", "Shell access to instances with no open inbound ports, bastion or SSH keys. (The page says this legacy page is deprecated on Dec 31, 2026.)"),
    "Keycloak": ("https://www.keycloak.org/documentation", "Open-source identity server for sign-in, multi-factor authentication and access control."),
    "Grafana Loki": ("https://grafana.com/docs/loki/latest/", "Log storage that indexes only labels and keeps compressed log data in object storage."),
    "Grafana": ("https://grafana.com/docs/grafana/latest/", "Dashboards, log browsing and alerting."),
    "Grafana Alloy": ("https://grafana.com/docs/alloy/latest/", "A collector that gathers, processes and ships logs and metrics."),
    "LogQL": ("https://grafana.com/docs/loki/latest/query/", "Loki's query language for searching and filtering logs."),
    "Prometheus": ("https://prometheus.io/docs/introduction/overview/", "Records numeric measurements over time and can alert on them."),
    "Kyverno": ("https://kyverno.io/docs/", "A policy engine that checks and enforces rules on Kubernetes resources."),
    "Trivy": ("https://trivy.dev/", "Scans images, code and clusters for known flaws and misconfigurations."),
    "Trivy Operator": ("https://aquasecurity.github.io/trivy-operator/latest/", "Runs Trivy inside the cluster continuously and stores findings as cluster resources."),
    "Cosign": ("https://docs.sigstore.dev/cosign/signing/overview/", "Signs container images and verifies the signature."),
    "Gitea": ("https://docs.gitea.com/", "A lightweight self-hosted git server."),
    "ClamAV": ("https://docs.clamav.net/", "Open-source antivirus with a daemon, command-line scanner and signature updater."),
    "Falco": ("https://falco.org/docs/", "Watches system calls and alerts in real time when a rule detects suspicious behavior."),
    "Velero": ("https://velero.io/docs/", "Backs up and restores Kubernetes resources and persistent volumes."),
    "Mattermost": ("https://docs.mattermost.com/developers/integrate/webhooks/incoming", "Open-source team chat. Incoming webhooks let tools post messages into a channel."),
    "jq": ("https://jqlang.org/", "Command-line JSON processor."),
    "curl": ("https://curl.se/docs/manpage.html", "Command-line tool for transferring data over URLs, used here to call web endpoints."),
    "OpenSSL": ("https://docs.openssl.org/master/man1/openssl/", "Command-line tool for keys, certificates and testing TLS connections."),
    "Git": ("https://git-scm.com/about", "Version control that stores repository history."),
    "Podman / Docker": ("https://docs.podman.io/en/latest/", "Runs containers. Docker alternative: https://docs.docker.com/get-started/docker-overview/"),
    "Python 3": ("https://docs.python.org/3/tutorial/introduction.html", "General-purpose language, used here for small helper scripts."),
}
_MODULES = [
    ("M00", "Keyboard Survival and Machine Check", [("Podman / Docker", "Runs the lab shell container, so every command behaves the same on Mac and Windows."), ("oc", "Learners run their first cluster commands."), ("Git", "First clone, commit and diff.")]),
    ("M02", "Lab Build with Terraform", [("Terraform", "Creates the lab's AWS resources from code."), ("AWS CLI", "Checks what Terraform built."), ("AWS KMS", "Creates the key used to encrypt lab storage."), ("Amazon VPC", "The isolated network the cluster is built in."), ("AWS Budgets", "Sets a spend alert on the learner's lab."), ("openshift-install", "Builds the single-node cluster."), ("jq", "Reads JSON output.")]),
    ("SIEM-1", "Collect Audit Logs", [("OpenShift Logging", "Collects audit, infrastructure and application logs and forwards them."), ("Grafana Loki", "Receives and stores the forwarded logs."), ("Grafana", "Used to browse the logs and confirm they arrive."), ("oc", "Applies the log forwarding configuration.")]),
    ("SIEM-2", "Store and Protect Audit Logs", [("Grafana Loki", "Configured for retention and protected storage."), ("Amazon S3 Object Lock", "Makes stored logs tamper-resistant (write-once-read-many)."), ("AWS KMS", "Encrypts the log bucket."), ("Grafana", "Shows storage and log status.")]),
    ("SIEM-3", "Detect and Alert", [("Grafana", "Hosts the alert rules."), ("LogQL", "The query that spots the event in the logs."), ("Mattermost", "Receives the alert message in a chat channel.")]),
    ("SIEM-4", "Respond to an Incident", [("Mattermost", "Where the alert arrives and the response is coordinated."), ("Grafana Loki", "Searched to trace what happened."), ("Grafana", "Used to view the query results."), ("oc", "Used to contain the affected workload.")]),
    ("M12", "Backup and Recovery", [("OADP (Velero)", "Backs up the demo application and its data, then restores it."), ("Velero", "The command-line client for running and checking backups."), ("AWS KMS", "Encrypts the backup bucket.")]),
    ("M08", "Vulnerability Management", [("Trivy", "Scans images for known flaws."), ("Trivy Operator", "Scans workloads in the cluster continuously and records findings."), ("jq", "Filters scan results.")]),
    ("M05", "Identity and Multi-Factor Sign-In", [("Keycloak", "Provides sign-in, multi-factor authentication and account rules."), ("OpenSSL", "Inspects the certificates used for card-style sign-in."), ("curl", "Calls sign-in endpoints."), ("Python 3", "Small helper script.")]),
    ("M06", "Privileged Access and Session Audit", [("AWS Systems Manager Session Manager", "Gives audited shell access with no open inbound ports."), ("Terraform", "Creates the access setup."), ("Grafana Loki", "Receives session records."), ("Grafana", "Used to review them.")]),
    ("M11", "Malware and Runtime Detection", [("ClamAV", "Scans uploaded files for malware."), ("Falco", "Detects suspicious behavior inside running containers."), ("Grafana Loki", "Receives the alerts for review.")]),
    ("M07", "Hardening and Policy as Code", [("Compliance Operator", "Scans the cluster against a hardening benchmark."), ("Kyverno", "Blocks resources that break a written policy."), ("Git", "Policies are kept as files in version control.")]),
    ("M04", "FIPS Cryptography and Keys", [("OpenShift FIPS support", "Shows how FIPS mode is checked on the running cluster."), ("AWS KMS", "Key creation, rotation and use."), ("OpenSSL", "Tests which TLS versions and ciphers a service accepts."), ("AWS CLI", "Reads key settings.")]),
    ("M03", "Boundary and Default-Deny", [("NetworkPolicy", "Blocks all traffic between pods except what is allowed."), ("Service Mesh 3", "Encrypts traffic between internal components."), ("curl", "Tests that blocked paths are blocked and allowed paths work.")]),
    ("M09", "Secure Release Pipeline", [("OpenShift Pipelines (Tekton)", "Runs the build, test, scan and sign steps."), ("tkn", "Starts and watches pipeline runs."), ("Gitea", "Holds the application source."), ("Trivy", "Fails the build on serious findings."), ("Cosign", "Signs the built image."), ("Kyverno", "Refuses unsigned images.")]),
    ("M10", "GitOps and Change Control", [("OpenShift GitOps (Argo CD)", "Applies only what is approved in git."), ("Gitea", "Holds the approved configuration and review."), ("File Integrity Operator", "Detects changes made outside the approved path."), ("Git", "Reviewed commits are the change record.")]),
    ("CAP", "Capstone: One Workload, Five Controls", [("OpenShift GitOps (Argo CD)", "Deploys the capstone workload from an approved git change."), ("Gitea", "Holds the reviewed change that Argo CD applies."), ("NetworkPolicy", "Blocks all traffic in the project except one listed flow."), ("Kyverno", "Refuses images that are not signed."), ("OpenShift Logging", "Carries the project's records to the SIEM."), ("Grafana Loki", "Searched to prove the records arrived."), ("Git", "Branch, commit and pull request for the change.")]),
]

_CURATED = {mid: [(n, TOOLS[n][0], TOOLS[n][1], use) for n, use in items] for mid, _title, items in _MODULES}

# Shared tools are added only when the module's own `tools` list names them.
_SHARED = [
    ("OpenShift Container Platform", "openshift container platform", "The cluster every command in this module runs against."),
    ("oc", "oc", "Runs the cluster commands in each step."),
    ("AWS CLI", "aws", "Reads and checks AWS resources from the shell."),
    ("jq", "jq", "Picks fields out of JSON output."),
    ("curl", "curl", "Calls web endpoints to test behavior."),
    ("Git", "git", "Tracks and reviews file changes."),
]


def tool_rows(module: dict) -> list[tuple[str, str, str, str]]:
    """Rows (name, url, what it is, used here) for one module, without duplicates."""
    rows = list(_CURATED.get(module["id"], []))
    have = {r[0] for r in rows}
    listed = [t.lower() for t in module["tools"]]
    for name, needle, use in _SHARED:
        if name in have:
            continue
        if any(t == needle or t.startswith(needle + " ") or t.startswith(needle + "(") for t in listed):
            url, what = TOOLS[name]
            rows.append((name, url, what, use))
    return rows
