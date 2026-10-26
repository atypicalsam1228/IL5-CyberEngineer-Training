"""M10: GitOps and Change Control (CM-3, CM-5, SI-7)."""

NIST = "nist-sp-800-53r5-full.md"
FEDRAMP = "fedramp-high-baseline.md"

RBAC_PATCH = """spec:
  rbac:
    defaultPolicy: ""
    scopes: "[groups]"
    policy: |
      g, system:cluster-admins, role:admin
      g, cluster-admins, role:admin
      p, role:demo-viewer, applications, get, demo/*, allow
      p, role:demo-deployer, applications, get, demo/*, allow
      p, role:demo-deployer, applications, sync, demo/*, allow
      g, demo-viewers, role:demo-viewer
      g, demo-deployers, role:demo-deployer
"""

FIO_YAML = """apiVersion: fileintegrity.openshift.io/v1alpha1
kind: FileIntegrity
metadata:
  name: node-integrity
  namespace: openshift-file-integrity
spec:
  nodeSelector:
    node-role.kubernetes.io/master: ""
  config:
    gracePeriod: 30
"""

PROTECT_BODY = (
    "'{\"rule_name\":\"main\",\"enable_push\":false,\"required_approvals\":1,"
    "\"enable_approvals_whitelist\":true,\"approvals_whitelist_username\":[\"lab-reviewer\"],"
    "\"block_on_rejected_reviews\":true,\"dismiss_stale_approvals\":true,\"block_admin_merge_override\":true}'"
)

MODULE = {
    "id": "M10",
    "slug": "GitOpsChange",
    "title": "GitOps and Change Control",
    "draft": (
        "Commands follow the Red Hat OpenShift GitOps, Argo CD, Gitea and File Integrity Operator documentation but have not yet run in the lab. "
        "The argocd flags and the Gitea branch protection fields are checked with --help and a read-back before they are relied on. "
        "Gitea branch protection uses rule_name because branch_name is deprecated, and block_admin_merge_override so an administrator token cannot merge without the approval. The merge call uses the lowercase key do. "
        "Confirm before relying on them: that the push in test 3 is refused for the administrator token (the Gitea source has no administrator exemption for push, but check with a live push), that argocd core mode finds the instance Redis and repo server (if app list fails, set ARGOCD_REDIS_NAME to the Redis service name of the instance, as with ARGOCD_REPO_SERVER_NAME), and that the node status results list keeps one entry per condition, so the test selects the newest Failed entry and prints zero for counts the operator omits. The exact text of the Gitea push rejection and of the file integrity result can differ between releases, so the expected output is an example."
    ),
    "controls": ["CM-3", "CM-5", "SI-7"],
    "mentions": ["CM-4", "CM-6", "AC-6", "SI-4", "SA-11"],
    "unit_values_ok": ["30 seconds", "120 seconds"],
    "minutes": {"hands_on": 45, "verify": 25},
    "tools": [
        "OpenShift GitOps (Argo CD)",
        "Gitea (in-lab git server)",
        "File Integrity Operator",
        "oc",
        "argocd",
        "git",
        "curl",
        "jq",
    ],
    "diagrams": [
        {
            "id": "flow",
            "title": "Git is the only door to production",
            "caption": "A change reaches the demo-app deployment only after review and merge into main. Argo CD then applies it and undoes anything done by hand. The File Integrity Operator watches the node files underneath. Each step below adds one part, drawn with thick lines.",
            "per_step": True,
            "rankdir": "LR",
            "step_notes": {
                1: "Argo CD reads the main branch and keeps the demo-app deployment matching it, undoing hand changes.",
                2: "A role policy limits who may sync in Argo CD. The viewer role can only look.",
                3: "Gitea protects main. A change can enter only through a pull request with one approval.",
                4: "The File Integrity Operator compares the node files with a baseline on a repeating schedule.",
            },
            "zones": [
                {"id": "lab", "label": "Your lab", "kind": "boundary"},
                {"id": "gitea", "label": "Gitea, repository demo-config", "parent": "lab", "kind": "group"},
                {"id": "gitops", "label": "Project openshift-gitops", "parent": "lab", "kind": "group"},
                {"id": "demo", "label": "Project demo", "parent": "lab", "kind": "group"},
                {"id": "node", "label": "Cluster node", "parent": "lab", "kind": "group"},
            ],
            "nodes": [
                {"id": "pr", "title": "Pull request", "sub": "One approval needed", "zone": "gitea", "kind": "ok", "s": 3},
                {"id": "main", "title": "Branch main", "sub": "The approved source", "zone": "gitea"},
                {"id": "app", "title": "Argo CD application", "sub": "Sync and self-heal", "zone": "gitops", "kind": "ok", "s": 1},
                {"id": "roles", "title": "Role policy", "sub": "Viewer cannot sync", "zone": "gitops", "kind": "warn", "s": 2},
                {"id": "dep", "title": "Demo application", "sub": "Deployment demo-app", "zone": "demo"},
                {"id": "fio", "title": "File Integrity Operator", "sub": "Runs AIDE", "zone": "node", "kind": "ok", "s": 4},
                {"id": "files", "title": "Node files", "sub": "Operating system", "zone": "node"},
            ],
            "edges": [
                {"a": "pr", "b": "main", "label": "Merge after approval", "kind": "ok", "flat": True, "s": 3},
                {"a": "main", "b": "app", "n": 1, "label": "Read", "s": 1},
                {"a": "app", "b": "dep", "n": 2, "label": "Apply and revert", "kind": "ok", "s": 1},
                {"a": "roles", "b": "app", "label": "Limits sync", "flat": True, "s": 2},
                {"a": "fio", "b": "files", "label": "Compare with baseline", "flat": True, "s": 4},
            ],
            "reading": [
                "A change enters main only through a pull request with one approval.",
                "Argo CD reads main (flow 1) and applies it to the demo-app deployment, reverting changes made by hand (flow 2).",
                "The role policy decides who may sync in Argo CD. The viewer role cannot.",
                "The File Integrity Operator compares the files on the node with a baseline and reports Failed when one changes.",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)", "M09 Secure Release Pipeline (signed demo-app image)"],
    "lab_needs": [
        "Gitea repository demo-config under GITEA_USER with a deployment.yaml (Deployment demo-app, replicas: 1, running the signed image from M09) and a service file on branch main. Gitea user lab-reviewer has write access to it, and GITEA_TOKEN belongs to an administrator so the lab can act as that user for a review.",
        "Argo CD from OpenShift GitOps runs in openshift-gitops with the ArgoCD resource named openshift-gitops. The argocd command works in core mode, and the Argo CD repo server trusts the Gitea certificate.",
        "File Integrity Operator is installed and watching namespace openshift-file-integrity.",
        "The lab shell has a git credential helper that supplies GITEA_USER and GITEA_TOKEN for GITEA_URL, a configured git name and email, and trusts the Gitea certificate.",
        "Deployment demo-app already runs in namespace demo and is not yet managed by Argo CD.",
    ],
    "lab": {
        "start": "lab start m10",
        "env": ["GITEA_URL", "GITEA_USER", "GITEA_TOKEN"],
        "checks": [
            "Argo CD application demo-app is Synced and Healthy, with automated sync and self-heal on.",
            "A reviewed pull request merged into main changes the running replica count.",
            "A manual scale in the demo namespace is reverted by Argo CD.",
            "A direct push to main is rejected by Gitea.",
            "Argo CD policy gives the viewer role no sync permission, and the File Integrity scan reports Failed after a file is added on a node.",
        ],
    },
    "requirement": (
        "An IL5 system must change only through a controlled, recorded process, and only the right people may make those changes. "
        "This module makes git the single source of truth for what runs in production. Argo CD (a GitOps tool: software that "
        "continuously compares the cluster with the configuration kept in git and makes the cluster match) deploys what git says and "
        "undoes anything done by hand. Gitea (the in-lab git server) refuses direct changes to the approved branch. "
        "The File Integrity Operator then watches the operating system files on the nodes for changes that no process approved."
    ),
    "mapping": [
        {
            "control": "CM-3 Configuration Change Control",
            "plain": "Changes are reviewed and approved with security in mind, made through a defined process, recorded, and watched.",
            "source": "NIST",
            "covered": "Steps 1 and 3 make git the only way to deploy and require an approved pull request. Tests 1 to 3 show a reviewed change deploying, a hand change reverted, and a direct push refused.",
            "cite": [
                {"file": NIST, "quote": "Review proposed configuration-controlled changes to the system and approve or disapprove"},
                {"file": NIST, "quote": "Document configuration change decisions associated with the system;"},
                {"file": NIST, "quote": "Implement approved configuration-controlled changes to the system;"},
            ],
        },
        {
            "control": "CM-5 Access Restrictions for Change",
            "plain": "Only qualified, authorized people can make changes, and the restriction is enforced by the system.",
            "source": "NIST; FedRAMP",
            "covered": "Step 2 limits who can sync in Argo CD. Step 3 limits who can change main in Gitea. Tests 3 and 4 prove both.",
            "cite": [
                {"file": NIST, "quote": "Define, document, approve, and enforce physical and logical access restrictions"},
                {"file": NIST, "quote": "Automatically generate audit records of the enforcement actions."},
                {"file": FEDRAMP, "quote": "CM-5 (5) (b) [at least quarterly]"},
            ],
        },
        {
            "control": "SI-7 Software, Firmware, and Information Integrity",
            "plain": "Use tools that detect unauthorized changes to software and information, and act when one is found.",
            "source": "NIST; FedRAMP",
            "covered": "Step 4 turns on file integrity monitoring for the nodes. Test 5 changes a file and shows the scan fail.",
            "cite": [
                {"file": NIST, "quote": "Employ integrity verification tools to detect unauthorized changes to the following software"},
                {"file": FEDRAMP, "quote": "SI-7 (1)-3 [at least monthly]"},
                {"file": NIST, "quote": "Perform an integrity check of [Assignment: organization-defined software, firmware, and"},
            ],
        },
    ],
    "intent": [
        {
            "control": "CM-3 Configuration Change Control",
            "feared": "Someone changes production directly, outside review, and nobody can say who did it, who approved it, or why.",
            "scope": "Every configuration the system team controls, including application deployment settings and platform settings kept as files.",
            "question": "Is what runs in production exactly what an approved change says should run?",
            "evidence": "The merge record showing review and approval, the git history of every change, and Argo CD showing the cluster matches git.",
            "sufficient": "Changes are proposed, reviewed with security impact in mind, approved, then applied automatically from git. The lab prohibits direct pushes to the main branch and reverts unauthorized changes to the baseline automatically.",
            "tieoff": "Reverted changes are visible in Argo CD history and in audit logs, so the person who made a hand change can be found.",
            "tool": "Argo CD applies only what is in git and reverts the rest (Step 1). Gitea refuses unapproved changes to main (Step 3).",
        },
        {
            "control": "CM-5 Access Restrictions for Change",
            "feared": "Anyone with a login, or one person acting alone, can alter production.",
            "scope": "Who can change the deployment configuration, the git repository that holds it, and the tool that applies it.",
            "question": "Who can change production, and can that person approve their own change?",
            "evidence": "The Argo CD role policy, the Gitea branch protection settings, and the tests that show each denial.",
            "sufficient": "Only authorized roles can sync, role membership comes from groups, and a second authorized person must approve a merge. The lab assigns these through role-based access control and requires approval from at least one other authorized team member.",
            "tieoff": "Someone reviews role membership on a schedule. FedRAMP sets the review of privileges to change production (CM-5(5)(b)) at least quarterly, and the lab reviews elevated privilege accounts quarterly.",
            "tool": "The Argo CD role policy (Step 2) and the Gitea branch protection rule (Step 3).",
        },
        {
            "control": "SI-7 Software, Firmware, and Information Integrity",
            "feared": "Files on a node are altered by malware or an administrator, and the change is never noticed.",
            "scope": "The operating system files and settings on the cluster nodes. Container images are covered in module M09.",
            "question": "If a system file on a node changed an hour ago, would anything have noticed?",
            "evidence": "The monitoring resource, the scan results for each node, and a scan that reports a change.",
            "sufficient": "A tool compares monitored files with a known-good baseline on a repeating schedule and reports any difference. The lab uses file integrity monitoring that watches critical operating system files and configuration.",
            "tieoff": "In production a violation sends an alert to the log stack and notifies the cybersecurity team. This module reads the result by hand. A later module wires the alert.",
            "tool": "The File Integrity Operator runs AIDE (a file comparison tool) on each node (Step 4). Test 5 proves it sees a change.",
        },
    ],
    "architect": (
        "Design the change path before building it. Decide what lives in git, which branch is the approved one, who may approve, "
        "who may sync in Argo CD, what the cluster should do when someone changes it by hand, and how you will detect a change "
        "to a node that no one approved. Then build it and run the tests."
    ),
    "terms": [
        ("GitOps", "Running a system from configuration kept in git, with a tool that keeps the system matching git."),
        ("Argo CD", "The GitOps tool that compares the cluster with git and applies the difference."),
        ("Sync", "Making the cluster match git."),
        ("Drift", "A difference between what git says and what is actually running."),
        ("Self-heal", "Argo CD undoing drift automatically."),
        ("Branch protection", "A Gitea rule that limits who can change a branch and how."),
        ("Pull request", "A proposed change that others review before it joins a branch."),
        ("RBAC", "Role-based access control: permissions are given to roles, and people get roles."),
        ("File integrity monitoring", "Comparing files with a known-good record to detect changes."),
        ("AIDE", "Advanced Intrusion Detection Environment: the file comparison tool the operator runs on each node."),
    ],
    "concepts": [
        {
            "heading": "2.1 Why git is the only door",
            "paras": [
                "What is this? Configuration is the set of files that decide how the system behaves, such as how many copies of an application run and which image they use. Change control means each change to that configuration is requested, reviewed, approved and recorded.",
                "Why? If anyone can change the cluster directly, review is optional and the record is incomplete. If the cluster accepts changes only from git, and git accepts changes only after approval, every change is reviewed and every change is recorded in the history.",
            ],
            "table": {
                "headers": ["Layer", "Control", "What it stops"],
                "rows": [
                    ("Gitea branch protection", "No direct push to main, one approval needed", "An unreviewed change entering the approved source"),
                    ("Argo CD sync and self-heal", "The cluster follows git and reverts anything else", "A hand change surviving in production"),
                    ("Argo CD roles", "Only named roles can sync", "An unauthorized person forcing a change"),
                    ("File Integrity Operator", "Node files are compared with a baseline", "A change made below the cluster, on the node itself"),
                ],
            },
        },
        {
            "heading": "2.2 How Argo CD works",
            "paras": [
                "An Argo CD Application names a git repository, a folder in it, and a destination namespace (a named workspace in the cluster). Argo CD reads the files, compares them with the live objects, and reports Synced or OutOfSync.",
                "With automated sync, Argo CD applies git changes on its own. Drift is any difference between git and the live cluster. Self-heal means Argo CD also undoes drift caused by changes made directly in the cluster. Prune means it deletes cluster objects that were removed from git. An AppProject limits which repositories an application may read and which namespaces it may write to.",
            ],
            "diagram": (
                "Developer --> branch --> pull request --> approval --> merge to main\n"
                "                                                          |\n"
                "                                                          v\n"
                "                                                    Gitea (main)\n"
                "                                                          |\n"
                "                                              Argo CD reads and compares\n"
                "                                                          |\n"
                "                       hand change in cluster ----> reverted to match git"
            ),
        },
        {
            "heading": "2.3 File integrity on nodes",
            "paras": [
                "Argo CD protects what runs in the cluster. It cannot see the files of the operating system underneath. The File Integrity Operator fills that gap. It runs AIDE on every node, takes a baseline (a record of file sizes, permissions and checksums when the node was known to be good), and compares on a repeating schedule.",
                "A scan result is Succeeded when nothing differs, Failed when a monitored file was added, changed or removed, and Errored when the scanner itself broke.",
            ],
            "production": "In the real environment FedRAMP sets the SI-7(1) integrity check to at least monthly, and a Failed result raises an alert to the security team. The lab uses a short interval so you can see a result in a few minutes.",
        },
    ],
    "steps": [
        {
            "title": "Connect Argo CD to Gitea and deploy by git (CM-3)",
            "why": (
                "This makes git the source of truth. You give Argo CD a read credential for the configuration repository, create an "
                "AppProject (a boundary that limits what an application may read and where it may write), then create the application "
                "with automated sync, self-heal and prune turned on. The namespace label tells the OpenShift GitOps instance it may manage "
                "that namespace."
            ),
            "blocks": [
                {
                    "code": (
                        "oc config set-context --current --namespace openshift-gitops\n"
                        "export ARGOCD_REPO_SERVER_NAME=openshift-gitops-repo-server\n"
                        "argocd app list --core\n"
                        "argocd app create --help | grep -e self-heal -e auto-prune -e sync-policy\n"
                        "argocd proj create --help | grep -e dest -e src"
                    ),
                    "lines": [
                        ("oc config set-context --current --namespace", "Makes openshift-gitops your default project (a project is a named workspace in the cluster)."),
                        ("export ARGOCD_REPO_SERVER_NAME", "Tells the argocd command the name of the repo server in this installation."),
                        ("argocd app list --core", "Runs argocd in core mode, which talks to the cluster directly with your login, so no separate Argo CD password is needed. An empty list is correct."),
                        ("--help | grep", "Confirms your argocd release has the flags used below."),
                    ],
                },
                {
                    "code": (
                        "oc create secret generic demo-config-repo -n openshift-gitops \\\n"
                        "  --from-literal=type=git \\\n"
                        "  --from-literal=url=\"$GITEA_URL/$GITEA_USER/demo-config.git\" \\\n"
                        "  --from-literal=username=\"$GITEA_USER\" \\\n"
                        "  --from-literal=password=\"$GITEA_TOKEN\"\n"
                        "oc label secret demo-config-repo -n openshift-gitops argocd.argoproj.io/secret-type=repository"
                    ),
                    "lines": [
                        ("type=git, url", "Describes the repository to Argo CD."),
                        ("username, password", "The Gitea credential, taken from lab variables so you never type it."),
                        ("secret-type=repository", "The label Argo CD looks for to treat a secret as a repository credential."),
                    ],
                },
                {
                    "code": (
                        "argocd proj create demo --core --description \"Demo application\" \\\n"
                        "  --dest https://kubernetes.default.svc,demo \\\n"
                        "  --src \"$GITEA_URL/$GITEA_USER/demo-config.git\"\n"
                        "oc label namespace demo argocd.argoproj.io/managed-by=openshift-gitops\n"
                        "argocd app create demo-app --core --project demo \\\n"
                        "  --repo \"$GITEA_URL/$GITEA_USER/demo-config.git\" \\\n"
                        "  --path . --revision main \\\n"
                        "  --dest-server https://kubernetes.default.svc --dest-namespace demo \\\n"
                        "  --sync-policy automated --self-heal --auto-prune\n"
                        "argocd app wait demo-app --core --sync --health --timeout 120\n"
                        "argocd app get demo-app --core"
                    ),
                    "lines": [
                        ("argocd proj create demo --dest ... --src ...", "Makes a project that may read only this repository and write only to the demo namespace."),
                        ("oc label namespace demo", "Allows the OpenShift GitOps instance to manage the demo namespace."),
                        ("--repo, --path, --revision", "Where the configuration lives: this repository, the top folder, the main branch."),
                        ("--dest-server, --dest-namespace", "Where it is applied: this cluster, the demo namespace."),
                        ("--sync-policy automated", "Apply git changes without a person clicking sync."),
                        ("--self-heal", "Undo changes made directly in the cluster."),
                        ("--auto-prune", "Delete cluster objects that were removed from git."),
                        ("argocd app wait", "Waits until the application is Synced and Healthy."),
                    ],
                },
            ],
            "tip": "The Argo CD application is also configuration. In the real environment it is kept as a file in git too, so changes to it are reviewed like any other change (CM-3).",
            "action": "Run the three blocks in order.",
            "checkpoint": "argocd app get shows Sync Status Synced and Health Status Healthy.",
        },
        {
            "title": "Limit who can change production in Argo CD (CM-5)",
            "why": (
                "By default a person who signs in may get more access than they need. You replace that with a role policy. "
                "Role-based access control (RBAC) gives permissions to roles, and people get roles through group membership. "
                "Here one role can only look, one role can look and sync, and anyone else gets nothing. The cluster administrator "
                "groups keep full access so you cannot lock yourself out. Argo CD reads the policy from the ArgoCD resource, so you patch that resource."
            ),
            "blocks": [
                {
                    "lang": "yaml",
                    "code": RBAC_PATCH,
                    "lines": [
                        ("defaultPolicy: \"\"", "A signed-in person with no role gets no access."),
                        ("scopes: \"[groups]\"", "Argo CD reads role membership from the groups in the sign-in token."),
                        ("g, system:cluster-admins, role:admin", "Keeps full access for the cluster administrator groups."),
                        ("p, role:demo-viewer ... get", "The viewer role may read applications in the demo project."),
                        ("p, role:demo-deployer ... sync", "The deployer role may read and sync applications in the demo project."),
                        ("g, demo-viewers, role:demo-viewer", "Members of the group demo-viewers get the viewer role."),
                    ],
                },
                {
                    "code": (
                        "oc get argocd -n openshift-gitops\n"
                        "oc patch argocd openshift-gitops -n openshift-gitops --type merge --patch-file argocd-rbac.yaml --dry-run=server\n"
                        "oc patch argocd openshift-gitops -n openshift-gitops --type merge --patch-file argocd-rbac.yaml\n"
                        "oc get configmap argocd-rbac-cm -n openshift-gitops -o jsonpath='{.data.policy\\.csv}'"
                    ),
                    "lines": [
                        ("oc get argocd", "Shows the Argo CD instance resource you are about to change."),
                        ("--dry-run=server", "Asks the cluster to check the patch without saving it."),
                        ("oc patch --type merge --patch-file", "Merges only the rbac settings into the existing resource and leaves the rest alone."),
                        ("argocd-rbac-cm", "The configuration map the operator writes the policy into. Reading it back proves the change landed."),
                    ],
                },
            ],
            "security": "Anyone with Kubernetes access to the Argo CD namespace can act as an Argo CD administrator and bypass these roles. Keep that access limited to the cluster administrators.",
            "action": "Save the YAML as argocd-rbac.yaml, dry-run it, apply it, and read the policy back.",
            "checkpoint": "The policy text lists role:demo-viewer and role:demo-deployer.",
        },
        {
            "title": "Protect the approved branch in Gitea (CM-3, CM-5)",
            "why": (
                "A branch is a line of work in git, and main is the branch Argo CD deploys. Branch protection is a Gitea rule on a branch. "
                "This rule turns off direct pushes to main for everyone, so the only way in is a pull request (a proposed change that "
                "others review before it joins the branch). It requires one approval, and only the listed reviewer's approval counts. "
                "It also makes administrators follow the rule, because Gitea otherwise lets a repository administrator merge without the approval. This is dual authorization (two-person control), and the lab applies it in Gitea."
            ),
            "blocks": [
                {
                    "code": (
                        "curl -s -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Content-Type: application/json\" \\\n"
                        "  \"$GITEA_URL/api/v1/repos/$GITEA_USER/demo-config/branch_protections\" \\\n"
                        "  -d " + PROTECT_BODY + " | jq '{rule_name, enable_push, required_approvals}'\n"
                        "curl -s -H \"Authorization: token $GITEA_TOKEN\" \\\n"
                        "  \"$GITEA_URL/api/v1/repos/$GITEA_USER/demo-config/branch_protections/main\" | jq '{enable_push, required_approvals, approvals_whitelist_username, block_admin_merge_override}'"
                    ),
                    "lines": [
                        ("curl -X POST .../branch_protections", "Creates the protection rule through the Gitea API (the web interface for programs)."),
                        ("Authorization: token $GITEA_TOKEN", "Uses the lab token from a variable, so nothing secret is typed."),
                        ("enable_push false", "Nobody can push directly to main."),
                        ("required_approvals 1", "A pull request needs one approval before it can merge."),
                        ("approvals_whitelist_username", "Only this reviewer's approval counts, so the author cannot approve their own change."),
                        ("block_on_rejected_reviews, dismiss_stale_approvals", "A rejected review blocks the merge, and a new commit voids older approvals."),
                        ("block_admin_merge_override", "Administrators follow the same rule. Without it Gitea lets a repository administrator merge without the approval."),
                        ("curl .../branch_protections/main", "Reads the rule back so you can see what was saved."),
                    ],
                }
            ],
            "action": "Run the commands and read the saved rule.",
            "checkpoint": "The read-back shows enable_push false, required_approvals 1, the reviewer name, and block_admin_merge_override true.",
        },
        {
            "title": "Watch node files with the File Integrity Operator (SI-7)",
            "why": (
                "Git and Argo CD control what runs in the cluster, not the operating system files on the node underneath. A FileIntegrity "
                "resource tells the operator to run AIDE on the node, take a baseline, and compare on a schedule. The pause between scans "
                "is the gracePeriod, set short here so you can see a result quickly. FedRAMP sets the SI-7(1) integrity check to at least monthly."
            ),
            "blocks": [
                {
                    "lang": "yaml",
                    "code": FIO_YAML,
                    "lines": [
                        ("kind: FileIntegrity", "The operator resource that starts file integrity scanning."),
                        ("nodeSelector master", "Scans the control plane node. On a single-node cluster this is the only node, and one resource avoids scanning it twice."),
                        ("gracePeriod: 30", "Seconds to wait between scans. A lab-only value. The operator default is much longer."),
                    ],
                },
                {
                    "code": (
                        "oc apply -f node-integrity.yaml --dry-run=server\n"
                        "oc apply -f node-integrity.yaml\n"
                        "oc get fileintegrities -n openshift-file-integrity\n"
                        "sleep 120\n"
                        "oc get fileintegritynodestatuses -n openshift-file-integrity"
                    ),
                    "lines": [
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc get fileintegrities", "Shows the monitoring resource. Its phase moves from Initializing to Active."),
                        ("sleep 120", "Gives the operator time to build the baseline and run the first scan."),
                        ("fileintegritynodestatuses", "One result per node. The first good result says Succeeded."),
                    ],
                },
            ],
            "note": "If no result appears yet, wait and run the last command again. Building the baseline takes a few minutes.",
            "action": "Save the YAML as node-integrity.yaml, validate it, apply it, and read the node result.",
            "checkpoint": "The node status shows Succeeded.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "A reviewed git change deploys",
            "why": "Make a change the right way: on a branch, through a pull request, with an approval, then merged. Argo CD should apply it with no one running a deploy command.",
            "code": (
                "git clone \"$GITEA_URL/$GITEA_USER/demo-config.git\"\n"
                "cd demo-config\n"
                "git checkout -b scale-up\n"
                "sed -i 's/replicas: 1/replicas: 2/' deployment.yaml\n"
                "git commit -am \"Scale demo-app to two replicas\"\n"
                "git push origin scale-up\n"
                "PR=$(curl -s -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Content-Type: application/json\" \"$GITEA_URL/api/v1/repos/$GITEA_USER/demo-config/pulls\" -d '{\"head\":\"scale-up\",\"base\":\"main\",\"title\":\"Scale demo-app to two replicas\"}' | jq -r '.number')\n"
                "curl -s -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Sudo: lab-reviewer\" -H \"Content-Type: application/json\" \"$GITEA_URL/api/v1/repos/$GITEA_USER/demo-config/pulls/$PR/reviews\" -d '{\"event\":\"APPROVED\"}' | jq -r '.state'\n"
                "curl -s -o /dev/null -w \"%{http_code}\\n\" -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Content-Type: application/json\" \"$GITEA_URL/api/v1/repos/$GITEA_USER/demo-config/pulls/$PR/merge\" -d '{\"do\":\"merge\"}'\n"
                "argocd app get demo-app --core --refresh > /dev/null\n"
                "argocd app wait demo-app --core --sync --health --timeout 120\n"
                "oc get deployment demo-app -n demo -o jsonpath='{.spec.replicas}{\"\\n\"}'"
            ),
            "expect": (
                "Example only.\n"
                "APPROVED\n"
                "200\n"
                "2"
            ),
            "checkpoint": "The review is APPROVED, the merge returns 200, and the running deployment shows 2 replicas without anyone applying it by hand.",
        },
        {
            "kind": "negative",
            "title": "A manual cluster change is reverted",
            "why": "Change production directly, the way an administrator in a hurry might. Self-heal should put it back to what git says.",
            "code": (
                "oc scale deployment/demo-app -n demo --replicas=5\n"
                "oc get deployment demo-app -n demo -o jsonpath='{.spec.replicas}{\"\\n\"}'\n"
                "sleep 30\n"
                "oc get deployment demo-app -n demo -o jsonpath='{.spec.replicas}{\"\\n\"}'\n"
                "argocd app get demo-app --core | grep -e 'Sync Status' -e 'Health Status'"
            ),
            "expect": (
                "Example only.\n"
                "deployment.apps/demo-app scaled\n"
                "5\n"
                "2\n"
                "Sync Status:        Synced to main (3f9a1c2)\n"
                "Health Status:      Healthy"
            ),
            "checkpoint": "The count reads 5 right after your change and 2 after the wait, and the application is Synced to main again. If it still reads 5, wait a little longer and read it again.",
        },
        {
            "kind": "negative",
            "title": "An unapproved push to main is rejected",
            "why": "Try to put a change straight onto the approved branch with no review. Gitea should refuse it before it is stored.",
            "code": (
                "git checkout main\n"
                "git pull origin main\n"
                "sed -i 's/replicas: 2/replicas: 3/' deployment.yaml\n"
                "git commit -am \"Unapproved change straight to main\"\n"
                "git push origin main\n"
                "git reset --hard HEAD~1\n"
                "oc get deployment demo-app -n demo -o jsonpath='{.spec.replicas}{\"\\n\"}'"
            ),
            "expect": (
                "Example only. The wording depends on your Gitea release.\n"
                "remote: Gitea: Not allowed to push to protected branch main\n"
                "To https://gitea.lab.internal/student/demo-config.git\n"
                " ! [remote rejected] main -> main (pre-receive hook declined)\n"
                "error: failed to push some refs\n"
                "2"
            ),
            "checkpoint": "The push is rejected with a protected branch message, and the running replica count is still 2.",
        },
        {
            "kind": "negative",
            "title": "A viewer cannot sync",
            "why": "Ask Argo CD's own policy engine what each role may do. This checks the roles you set in Step 2 without needing a second login.",
            "code": (
                "argocd admin settings rbac can role:demo-viewer sync applications demo/demo-app --namespace openshift-gitops\n"
                "argocd admin settings rbac can role:demo-deployer sync applications demo/demo-app --namespace openshift-gitops"
            ),
            "expect": (
                "No\n"
                "Yes"
            ),
            "checkpoint": "The viewer role gets No and the deployer role gets Yes.",
        },
        {
            "kind": "negative",
            "title": "A changed node file is detected",
            "why": "Add a file to the node's operating system, the way an intruder or an unapproved administrator might. The next file integrity scan should report Failed.",
            "code": (
                "NODE=$(oc get nodes -o jsonpath='{.items[0].metadata.name}')\n"
                "oc debug node/$NODE -- chroot /host touch /etc/fio-lab-test\n"
                "sleep 120\n"
                "oc get fileintegritynodestatuses -n openshift-file-integrity -o json | jq '[.items[].results[] | select(.condition==\"Failed\")] | sort_by(.lastProbeTime) | last | {condition, filesAdded: (.filesAdded // 0), filesChanged: (.filesChanged // 0), filesRemoved: (.filesRemoved // 0)}'\n"
                "oc debug node/$NODE -- chroot /host rm /etc/fio-lab-test\n"
                "oc annotate fileintegrities/node-integrity -n openshift-file-integrity file-integrity.openshift.io/re-init="
            ),
            "expect": (
                "Example only. Counts will differ.\n"
                "{\n"
                "  \"condition\": \"Failed\",\n"
                "  \"filesAdded\": 1,\n"
                "  \"filesChanged\": 1,\n"
                "  \"filesRemoved\": 0\n"
                "}"
            ),
            "checkpoint": "The condition is Failed and at least one file is counted as added. If it still says Succeeded, wait and run the oc get line again. The last command accepts the node as good again by rebuilding the baseline.",
        },
    ],
    "glossary": [
        ("Application (Argo CD)", "The Argo CD object that links a git folder to a cluster namespace."),
        ("AppProject", "An Argo CD boundary that limits which repositories and namespaces an application may use."),
        ("Baseline", "The known-good record that later scans are compared against."),
        ("Branch", "A line of work in git. The main branch is the approved one."),
        ("Namespace", "A named workspace in the cluster."),
        ("Prune", "Delete cluster objects that were removed from git."),
    ],
    "next": "That completes the track. The capstone, scored by lab check, brings the modules together.",
}
