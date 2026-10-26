"""CAP: Capstone. Combine earlier controls on one fresh workload, scored by `lab check cap`."""

FEDRAMP = "fedramp-high-baseline.md"
NIST = "nist-sp-800-53r5-full.md"
SRG = "u-cloud-computing-mission-owner-os-srg-v1r3-manual-xccdf.md"

# Search window starts when the project was created, so records from an earlier attempt cannot count.
START_LINE = (
    "START=\"$(date -d \"$(oc get namespace cap-demo -o jsonpath='{.metadata.creationTimestamp}')\" +%s)000000000\"\n"
)
# Audit records of network policies created in cap-demo (read as JSON, verb create only).
AUDIT_QUERY = (
    "--data-urlencode 'query={log_type=\"audit\"} |= \"cap-demo\" |= \"networkpolicies\" | json | verb=\"create\"'"
)

LOKI_CURL = (
    "curl -sG --cacert \"$LOKI_CA_FILE\" -u \"$LOKI_USER:$LOKI_PASSWORD\" \"$LOKI_URL/loki/api/v1/query_range\" "
    "--data-urlencode \"start=$START\" --data-urlencode 'limit=1' "
)

MODULE = {
    "id": "CAP",
    "slug": "Capstone",
    "title": "Capstone: One Workload, Five Controls",
    "draft": (
        "Live-lab-only items, none yet run in the lab: (1) the demo image is assumed to answer HTTP on port 8080, so "
        "confirm that port with oc get deployment demo-app -n demo -o yaml before Step 2 and change the port in the "
        "Step 2 and Step 3 files if it differs; (2) the registry pull secret is assumed to be named registry-pull in "
        "the kyverno project and to be a Docker config secret; (3) Loki is assumed to accept the LOKI_USER and "
        "LOKI_PASSWORD read that SIEM-1 used, and the label name kubernetes_namespace_name is the one SIEM-3 and "
        "the malware module used; (4) the Kyverno refusal wording 'was blocked due to the following policies' "
        "matches the Kyverno documentation, but the exact text can differ in your Kyverno release, so Check 8 also "
        "requires the policy name; (5) how fast Argo CD reverts a manual change depends on the Argo CD release, so "
        "Check 4 waits before it reads the answer; (6) the Gitea review and merge calls use the Sudo header, which "
        "needs an administrator token, and the Gitea version the lab runs is not pinned in the lab contract; "
        "(7) the audit search in Step 4 and Check 7 assumes each audit record is stored as JSON with a verb field, "
        "as shown in SIEM-1. Every apply is first checked with a server dry run."
    ),
    "scored": True,
    "controls": ["AC-6", "CM-3", "SC-7", "AU-12", "SI-7"],
    "mentions": ["AC-4", "CM-5", "AU-2", "AU-3", "SC-8", "CP-9"],
    "unit_values_ok": ["45 seconds", "30 seconds"],
    "minutes": {"hands_on": 50, "verify": 25},
    "tools": [
        "OpenShift Container Platform",
        "OpenShift GitOps (Argo CD)",
        "Gitea",
        "NetworkPolicy",
        "Kyverno",
        "OpenShift Logging",
        "Grafana Loki",
        "oc",
        "curl",
        "jq",
        "Git",
    ],
    "diagrams": [
        {
            "id": "flow",
            "title": "One workload under five controls",
            "caption": (
                "A new project holds one workload. Each step adds one control around it: a limited identity, "
                "deployment from git with a signed image, a default-deny network, records in the SIEM, and a "
                "rule that refuses unsigned images. New parts are drawn with thick lines."
            ),
            "per_step": True,
            "rankdir": "LR",
            "step_notes": {
                1: "The project cap-demo is created, and one limited identity may manage deployments inside it and nowhere else.",
                2: "Argo CD deploys the workload from an approved git change. The image is the signed one the release pipeline built.",
                3: "Default-deny blocks everything. The client may reach the workload on one port, and the other pod may not.",
                4: "The collector reads the project's records and sends them to Loki, so you can search them.",
                5: "Kyverno now checks every image in cap-demo and refuses the unsigned test pod. The signed workload is still admitted.",
            },
            "zones": [
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "ns", "label": "Project cap-demo", "parent": "cluster", "kind": "group"},
                {"id": "gitops", "label": "Change control", "parent": "cluster", "kind": "group"},
                {"id": "platform", "label": "Platform services", "parent": "cluster", "kind": "group"},
                {"id": "siem", "label": "Project siem", "parent": "cluster", "kind": "group"},
            ],
            "nodes": [
                {"id": "role", "title": "Deployer identity", "sub": "Manages this project only", "zone": "ns", "kind": "warn", "s": 1},
                {"id": "app", "title": "Workload", "sub": "Signed image, port 8080", "zone": "ns", "kind": "ok", "s": 2},
                {"id": "client", "title": "Client pod", "sub": "Allowed one flow", "zone": "ns", "s": 3},
                {"id": "other", "title": "Other pod", "sub": "Not allowed", "zone": "ns", "s": 3},
                {"id": "unsigned", "title": "Unsigned test pod", "sub": "Refused at start", "zone": "ns", "kind": "bad", "s": 5},
                {"id": "git", "title": "Approved git change", "sub": "Gitea repository", "zone": "gitops", "s": 2},
                {"id": "argo", "title": "Argo CD", "sub": "Applies what git says", "zone": "gitops", "s": 2},
                {"id": "collector", "title": "Collector", "sub": "Reads project logs", "zone": "platform", "s": 4},
                {"id": "kyverno", "title": "Kyverno", "sub": "Checks image signatures", "zone": "platform", "kind": "warn", "s": 5},
                {"id": "loki", "title": "Loki", "sub": "Stores and searches", "zone": "siem", "kind": "ok", "s": 4},
            ],
            "edges": [
                {"a": "role", "b": "app", "label": "May manage", "kind": "warn", "s": 2},
                {"a": "git", "b": "argo", "n": 1, "label": "Pulls", "s": 2},
                {"a": "argo", "b": "app", "n": 2, "label": "Deploys", "kind": "ok", "s": 2, "beside": True},
                {"a": "client", "b": "app", "label": "Allowed", "kind": "ok", "s": 3},
                {"a": "other", "b": "app", "label": "Blocked", "kind": "bad", "s": 3},
                {"a": "collector", "b": "client", "label": "Reads logs", "s": 4, "minlen": 2},
                {"a": "collector", "b": "loki", "label": "Sends", "kind": "ok", "s": 4},
                {"a": "kyverno", "b": "unsigned", "label": "Refuses unsigned", "kind": "bad", "s": 5},
            ],
            "reading": [
                "A change approved in git is pulled by Argo CD, which deploys the workload into the project (flows 1 and 2).",
                "The deployer identity may manage things inside the project only.",
                "The client pod may reach the workload. The other pod is blocked.",
                "The collector reads the project's logs and sends them to Loki.",
                "Kyverno refuses a pod whose image is not signed.",
            ],
        },
    ],
    "prereq": [
        "Module 0 (terminal and git basics)",
        "Module 2 (lab running)",
        "SIEM-1 and SIEM-2 (logs reach Loki)",
        "M06 (roles), M03 (default-deny), M09 (signed image and policy), M10 (GitOps)",
    ],
    "lab_needs": [
        "End state of the earlier modules: audit and application logs reach Loki (SIEM-1), Kyverno policy require-signed-images exists (M09), Argo CD runs in openshift-gitops and trusts the Gitea certificate (M10), and demo-app in project demo runs the signed image.",
        "Gitea repository cap-config under GITEA_USER with a README on branch main. Branch main is protected: pushes are refused and one approval from Gitea user lab-reviewer is required. Provided by lab start cap.",
        "Secret registry-pull in project kyverno holds a Docker config for REGISTRY_HOST (from the release pipeline module), so it can be copied to cap-demo to pull the signed image.",
        "The demo-app image answers HTTP on port 8080 (live-lab-only: confirm before Step 2).",
        "The cluster can pull registry.access.redhat.com/ubi9/ubi-minimal, which is the image for the two test pods.",
    ],
    "lab": {
        "start": "lab start cap",
        "env": ["LOKI_URL", "LOKI_CA_FILE", "LOKI_USER", "LOKI_PASSWORD", "GITEA_URL", "GITEA_USER", "GITEA_TOKEN"],
        "checks": [
            "The deployer identity can manage deployments in cap-demo and nothing outside it.",
            "Argo CD reports the workload Synced and Healthy, it came from a merged and approved pull request, and a manual change is reverted.",
            "The one allowed flow works and every other flow is blocked.",
            "The workload's application records and the audit record of the network policy are found in Loki.",
            "An unsigned image is refused and a signed one is admitted.",
        ],
    },
    "requirement": (
        "An IL5 system is not secure because each tool works alone. It is secure when the controls hold "
        "together on one real workload. This capstone has no new tool and no new theory. You take one fresh "
        "workload in a new project and put five controls around it using what you built in earlier modules: "
        "least-privilege access, deployment only through approved git changes, default-deny networking, records "
        "in the SIEM, and admission of signed images only. Then `lab check cap` runs nine checks and prints a "
        "score. Each check passes or fails on its own and prints a one-line fix."
    ),
    "mapping": [
        {
            "control": "AC-6 Least Privilege",
            "plain": "The identity that deploys to the project gets only the access it needs inside that project.",
            "source": "NIST; FedRAMP",
            "covered": "Step 1 creates the role. Checks 1 and 2 prove what it can and cannot do.",
            "cite": [
                {"file": NIST, "quote": "Employ the principle of least privilege, allowing only authorized accesses for users"},
                {"file": FEDRAMP, "quote": "ensuring that the processes have access to systems and operate at privilege levels no higher than necessary to accomplish organizational missions or business functions"},
            ],
        },
        {
            "control": "CM-3 Configuration Change Control",
            "plain": "Changes reach the system only through a reviewed, approved and recorded path.",
            "source": "NIST; FedRAMP",
            "covered": "Step 2 deploys through a reviewed git change and Argo CD. Checks 3 and 4 prove the deployment is in sync and a manual change is undone.",
            "cite": [
                {"file": NIST, "quote": "Review proposed configuration-controlled changes to the system and approve or disapprove"},
                {"file": FEDRAMP, "quote": "Document configuration change decisions associated with the system;"},
                {"file": FEDRAMP, "quote": "Implement approved configuration-controlled changes to the system;"},
            ],
        },
        {
            "control": "SC-7 Boundary Protection",
            "plain": "Traffic is controlled at the edge and also between internal components, and anything not on the allowed list is blocked.",
            "source": "NIST; DoD SRG",
            "covered": "Step 3 applies default-deny and one allowed flow. Checks 5 and 6 test the allowed flow and three blocked ones.",
            "cite": [
                {"file": NIST, "quote": "Deny network communications traffic by default and allow network communications traffic by exception"},
                {"file": SRG, "quote": "Mission Owners must disable or restrict unused or unnecessary physical and logical ports/protocols on information systems."},
            ],
        },
        {
            "control": "AU-12 Audit Record Generation",
            "plain": "The workload and the actions on it produce records, and the records reach the central store.",
            "source": "NIST; FedRAMP",
            "covered": "Step 4 finds the workload's records and an audit record in Loki. Check 7 proves both arrived.",
            "cite": [
                {"file": NIST, "quote": "Provide audit record generation capability for the event types the system is capable of"},
                {"file": FEDRAMP, "quote": "AU-12 (a) [all information system and network components where audit capability is deployed/available]"},
            ],
        },
        {
            "control": "SI-7 Software, Firmware, and Information Integrity",
            "plain": "Software is checked for unauthorized change before it runs, and a failed check stops it.",
            "source": "NIST; FedRAMP",
            "covered": "Step 5 extends the signature policy to the project. Check 8 shows an unsigned image refused and Check 9 shows the signed workload admitted.",
            "cite": [
                {"file": NIST, "quote": "Employ integrity verification tools to detect unauthorized changes to the following software"},
                {"file": FEDRAMP, "quote": "Take the following actions when unauthorized changes to the software, firmware, and information are detected"},
            ],
        },
    ],
    "intent": [
        {
            "control": "AC-6 Least Privilege",
            "feared": "A pipeline or developer identity can do far more than its job needs, so one stolen token can change the whole cluster.",
            "scope": "Every identity that deploys to or runs in the project.",
            "question": "If this identity were stolen today, what is the worst it could do, and does that stop at the project boundary?",
            "evidence": "The role and its binding, plus a can-i test for what the identity may and may not do.",
            "sufficient": "The identity holds only the actions its job needs, and only inside its own project. In this lab, application teams may change resources only within the namespaces assigned to their team.",
            "tieoff": "Someone reviews the binding when the team or its job changes.",
            "tool": "A Role and RoleBinding (Step 1) and `oc auth can-i` (Checks 1 and 2).",
        },
        {
            "control": "CM-3 Configuration Change Control",
            "feared": "A change reaches the running system without review, or someone alters it by hand and nobody notices.",
            "scope": "Everything deployed into the project.",
            "question": "Can I show who approved the change that is running now, and what happens if someone edits it by hand?",
            "evidence": "The merged and approved change in git, the Argo CD status, and the result of a manual edit.",
            "sufficient": "Changes enter by an approved git change, the system applies it automatically, and a manual edit is put back. In this lab, direct pushes to the main branch are prohibited and Argo CD applies approved baselines.",
            "tieoff": "Reviewers are named, and the protected branch rule is kept in place.",
            "tool": "Gitea branch protection, a pull request, and an Argo CD application with self-heal (Step 2).",
        },
        {
            "control": "SC-7 Boundary Protection",
            "feared": "A compromised pod reaches anything else in the system because nothing inside is blocked.",
            "scope": "Traffic between pods in the project and from them to the rest of the cluster.",
            "question": "Is traffic protected only at the boundary, or also between internal components?",
            "evidence": "The policies, one successful test of the allowed flow, and failed tests of the others.",
            "sufficient": "Everything is denied by default and each allowed flow is listed with one port. The NIST text says to deny by default and allow by exception.",
            "tieoff": "A new flow is added to the list through change control before it is allowed.",
            "tool": "NetworkPolicy (Step 3) and `curl` from two test pods (Checks 5 and 6).",
        },
        {
            "control": "AU-12 Audit Record Generation",
            "feared": "A new workload runs and nobody can see what it did, because its records never reach the SIEM.",
            "scope": "Application records from the workload and audit records of actions on the project.",
            "question": "For a workload created today, can an analyst find its records in the SIEM, and the record of who changed its network rules?",
            "evidence": "A search result from Loki for each of the two record types.",
            "sufficient": "Records from the new project arrive without extra setup, because the collector already reads all projects.",
            "tieoff": "Someone notices when a new project stops producing records. The detection module adds that alert.",
            "tool": "The collector and Loki built in SIEM-1 and SIEM-2, searched with LogQL (Step 4).",
        },
        {
            "control": "SI-7 Software, Firmware, and Information Integrity",
            "feared": "A tampered or unapproved image runs in the project because nothing checks where it came from.",
            "scope": "Every image started in the project.",
            "question": "If someone tries to run an image the pipeline never signed, what stops it?",
            "evidence": "The policy, the refusal of an unsigned image, and the admission of the signed workload.",
            "sufficient": "Signatures are checked before any application starts, and a failed check aborts the start.",
            "tieoff": "The signing key and the policy are owned by named people and kept in git.",
            "tool": "The Kyverno policy from the release pipeline module, extended to this project (Step 5).",
        },
    ],
    "architect": (
        "Draw the project before building it. List the one identity and what it may touch, the one flow "
        "the network must allow and its port, the two kinds of record you expect in the SIEM, and the one "
        "image source you trust. Note the order, because a rule that refuses unsigned images also refuses "
        "your own unsigned test pods once it is on. Then build in the step order and run `lab check cap`."
    ),
    "terms": [
        ("Capstone", "A final exercise that combines skills from earlier modules instead of teaching a new one."),
        ("Least privilege", "Giving an identity only the access its job needs."),
        ("Default-deny", "A network rule set where everything is blocked unless a rule allows it."),
        ("Admission control", "A check the cluster runs on a new pod before it is allowed to start."),
        ("Self-heal (Argo CD)", "Argo CD puts back what git says when someone changes the cluster by hand."),
        ("Perimeter-only protection", "Controls that protect traffic only where it enters or leaves the system, with nothing between internal components."),
    ],
    "concepts": [
        {
            "heading": "2.1 How the capstone works",
            "paras": [
                "What is this? One new project named cap-demo holds one workload (a program the cluster keeps running). You apply five controls to it, one per step, in the same order the earlier modules taught them.",
                "Why? Controls rarely fail on their own. They fail where they meet: a policy that blocks your own test pod, a network rule that blocks the log collector, a role that is too wide for the pipeline. The capstone makes those meetings visible.",
                "How is it scored? `lab check cap` runs nine checks. Each prints PASS or FAIL. A FAIL prints the expected and actual output and a one-line fix. The last line is your score. The checks run commands against your cluster; there is no hidden answer key.",
            ],
            "table": {
                "headers": ["Check", "Control", "What it proves"],
                "rows": [
                    ("1 and 2", "AC-6", "The identity can deploy in cap-demo and is refused everywhere else"),
                    ("3 and 4", "CM-3", "Argo CD reports the workload in sync, and a manual change is undone"),
                    ("5 and 6", "SC-7", "The one allowed flow works and three others are blocked"),
                    ("7", "AU-12", "Application records and an audit record are in Loki"),
                    ("8 and 9", "SI-7", "An unsigned image is refused and the signed workload is admitted"),
                ],
            },
        },
        {
            "heading": "2.2 Order matters",
            "paras": [
                "The signature rule in Step 5 applies to every pod in the project. Once it is on, the unsigned test pods you used in Steps 3 and 4 could no longer be created. So you create them first, apply the rule last, and use the rule's refusal of an unsigned pod as Check 8.",
                "Before Step 3 the project has perimeter-only protection: anything inside it can talk to anything else. The network rule in Step 3 blocks outbound traffic from every pod, including the name lookup that finds the workload by its service name. The first rule you write therefore allows name lookups, and the second allows the one real flow.",
            ],
        },
    ],
    "steps": [
        {
            "title": "Create the project and a limited deployer identity (AC-6)",
            "why": "Start with who may act. A role is a list of allowed actions, and a role binding gives that list to one identity. This identity may manage deployments and services in cap-demo only, which is least privilege: it cannot create projects or read anything outside cap-demo.",
            "blocks": [
                {
                    "code": (
                        "oc get deployment demo-app -n demo\n"
                        "oc get clusterpolicy require-signed-images\n"
                        "oc create namespace cap-demo"
                    ),
                    "lines": [
                        ("oc get deployment demo-app -n demo", "Confirms the signed workload from the release pipeline module exists. You copy its image in Step 2."),
                        ("oc get clusterpolicy require-signed-images", "Confirms the signature policy from the release pipeline module exists. You extend it in Step 5."),
                        ("oc create namespace cap-demo", "Creates the new project (a named workspace in the cluster)."),
                    ],
                },
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: v1\n"
                        "kind: ServiceAccount\n"
                        "metadata:\n"
                        "  name: cap-deployer\n"
                        "  namespace: cap-demo\n"
                        "---\n"
                        "apiVersion: rbac.authorization.k8s.io/v1\n"
                        "kind: Role\n"
                        "metadata:\n"
                        "  name: cap-deployer\n"
                        "  namespace: cap-demo\n"
                        "rules:\n"
                        "  - apiGroups: [\"apps\"]\n"
                        "    resources: [\"deployments\"]\n"
                        "    verbs: [\"get\", \"list\", \"watch\", \"create\", \"update\", \"patch\", \"delete\"]\n"
                        "  - apiGroups: [\"\"]\n"
                        "    resources: [\"services\", \"pods\"]\n"
                        "    verbs: [\"get\", \"list\", \"watch\", \"create\", \"update\", \"patch\", \"delete\"]\n"
                        "---\n"
                        "apiVersion: rbac.authorization.k8s.io/v1\n"
                        "kind: RoleBinding\n"
                        "metadata:\n"
                        "  name: cap-deployer\n"
                        "  namespace: cap-demo\n"
                        "roleRef:\n"
                        "  apiGroup: rbac.authorization.k8s.io\n"
                        "  kind: Role\n"
                        "  name: cap-deployer\n"
                        "subjects:\n"
                        "  - kind: ServiceAccount\n"
                        "    name: cap-deployer\n"
                        "    namespace: cap-demo"
                    ),
                    "lines": [
                        ("kind: ServiceAccount", "The identity for a program instead of a person."),
                        ("kind: Role ... rules", "The allowed actions: manage deployments, services and pods, in cap-demo only. A Role is limited to one project; a ClusterRole is not."),
                        ("kind: RoleBinding", "Gives the Role to the service account."),
                    ],
                },
                {
                    "code": (
                        "oc apply -f cap-identity.yaml --dry-run=server\n"
                        "oc apply -f cap-identity.yaml\n"
                        "oc auth can-i create deployments -n cap-demo --as=system:serviceaccount:cap-demo:cap-deployer"
                    ),
                    "lines": [
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc apply -f", "Saves the three resources."),
                        ("oc auth can-i ... --as=...", "Asks the cluster whether the identity may do the action. The answer is yes or no."),
                    ],
                },
            ],
            "action": "Save the YAML as cap-identity.yaml, then run the three command groups.",
            "checkpoint": "The last command prints yes.",
        },
        {
            "title": "Deploy the signed workload through git and Argo CD (CM-3, SI-7)",
            "why": "Nothing is created by hand. You put the workload definition in git, a second person approves the change, and Argo CD applies it. The image is the exact signed one that demo-app already runs, so it passes the signature check in Step 5. The main branch of cap-config is protected, so a direct push is refused, as this lab requires. Argo CD gets its own project that allows only this repository and only the cap-demo destination, so even a mistake in the application cannot deploy anywhere else.",
            "blocks": [
                {
                    "code": (
                        "oc label namespace cap-demo argocd.argoproj.io/managed-by=openshift-gitops\n"
                        "oc get secret registry-pull -n kyverno -o json | jq '{apiVersion, kind, type, data, metadata: {name: \"registry-pull\"}}' | oc apply -n cap-demo -f -\n"
                        "oc secrets link default registry-pull --for=pull -n cap-demo\n"
                        "oc create secret generic cap-config-repo -n openshift-gitops \\\n"
                        "  --from-literal=type=git \\\n"
                        "  --from-literal=url=\"$GITEA_URL/$GITEA_USER/cap-config.git\" \\\n"
                        "  --from-literal=username=\"$GITEA_USER\" \\\n"
                        "  --from-literal=password=\"$GITEA_TOKEN\"\n"
                        "oc label secret cap-config-repo -n openshift-gitops argocd.argoproj.io/secret-type=repository"
                    ),
                    "lines": [
                        ("oc label namespace ... managed-by", "Tells Argo CD it may manage this project."),
                        ("oc get secret registry-pull ... | jq ... | oc apply", "Copies the registry pull secret into cap-demo, keeping only its name and contents."),
                        ("oc secrets link default registry-pull --for=pull", "Lets pods in cap-demo use that secret to pull the signed image."),
                        ("oc create secret generic cap-config-repo", "Gives Argo CD the address and login for the git repository. The token comes from the lab variable, so you never type it."),
                        ("argocd.argoproj.io/secret-type=repository", "The label that makes Argo CD treat the secret as a repository login."),
                    ],
                },
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: apps/v1\n"
                        "kind: Deployment\n"
                        "metadata:\n"
                        "  name: cap-app\n"
                        "  namespace: cap-demo\n"
                        "spec:\n"
                        "  replicas: 1\n"
                        "  selector:\n"
                        "    matchLabels:\n"
                        "      app: cap-app\n"
                        "  template:\n"
                        "    metadata:\n"
                        "      labels:\n"
                        "        app: cap-app\n"
                        "    spec:\n"
                        "      securityContext:\n"
                        "        runAsNonRoot: true\n"
                        "        seccompProfile:\n"
                        "          type: RuntimeDefault\n"
                        "      containers:\n"
                        "        - name: cap-app\n"
                        "          image: ${CAP_IMAGE}\n"
                        "          ports:\n"
                        "            - containerPort: 8080\n"
                        "          securityContext:\n"
                        "            allowPrivilegeEscalation: false\n"
                        "            capabilities:\n"
                        "              drop: [\"ALL\"]\n"
                        "---\n"
                        "apiVersion: v1\n"
                        "kind: Service\n"
                        "metadata:\n"
                        "  name: cap-app\n"
                        "  namespace: cap-demo\n"
                        "spec:\n"
                        "  selector:\n"
                        "    app: cap-app\n"
                        "  ports:\n"
                        "    - port: 8080\n"
                        "      targetPort: 8080"
                    ),
                    "lines": [
                        ("image: ${CAP_IMAGE}", "A placeholder. The next block fills it with the signed image reference from demo-app."),
                        ("runAsNonRoot ... drop ALL", "Runs the workload with no extra rights, as the hardening module's policies expect."),
                        ("kind: Service", "Gives the workload a stable name, cap-app, on port 8080. The network step allows traffic to it."),
                    ],
                },
                {
                    "code": (
                        "export CAP_IMAGE=$(oc get deployment demo-app -n demo -o jsonpath='{.spec.template.spec.containers[0].image}')\n"
                        "echo \"$CAP_IMAGE\" | grep '@sha256:' || echo \"STOP: the image is not pinned by digest\"\n"
                        "git clone \"$GITEA_URL/$GITEA_USER/cap-config.git\"\n"
                        "envsubst < cap-app.tpl.yaml > cap-config/cap-app.yaml\n"
                        "cd cap-config\n"
                        "git checkout -b add-cap-app\n"
                        "git add cap-app.yaml\n"
                        "git commit -m \"Add cap-app\"\n"
                        "git push origin add-cap-app\n"
                        "git push origin HEAD:main\n"
                        "cd .."
                    ),
                    "lines": [
                        ("export CAP_IMAGE=$(oc get deployment demo-app ...)", "Reads the signed image reference (name plus digest) that demo-app runs."),
                        ("echo ... | grep ...", "Prints the image only if its reference contains a digest (the fixed fingerprint after the at sign). If you see STOP, do not go on: Step 5 needs the digest form."),
                        ("git clone", "Copies the repository to the lab shell. The lab supplies the git login."),
                        ("envsubst < cap-app.tpl.yaml > cap-config/cap-app.yaml", "Writes the final file with the real image filled in."),
                        ("git checkout -b add-cap-app", "Starts a branch for the change, because main is protected."),
                        ("git commit -m ... / git push origin add-cap-app", "Records the change and sends the branch to Gitea."),
                        ("git push origin HEAD:main", "Tries to push straight to main. Gitea refuses it, which is the point. Expect a line saying the branch is protected."),
                        ("cd ..", "Returns to the folder that holds your saved files, so the later blocks find them.")
                    ],
                },
                {
                    "code": (
                        "PR=$(curl -s -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Content-Type: application/json\" \"$GITEA_URL/api/v1/repos/$GITEA_USER/cap-config/pulls\" -d '{\"head\":\"add-cap-app\",\"base\":\"main\",\"title\":\"Add cap-app\"}' | jq -r '.number')\n"
                        "echo \"pull request number: $PR\"\n"
                        "curl -s -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Sudo: lab-reviewer\" -H \"Content-Type: application/json\" \"$GITEA_URL/api/v1/repos/$GITEA_USER/cap-config/pulls/$PR/reviews\" -d '{\"event\":\"APPROVED\"}' | jq -r '.state'\n"
                        "curl -s -o /dev/null -w \"%{http_code}\\n\" -X POST -H \"Authorization: token $GITEA_TOKEN\" -H \"Content-Type: application/json\" \"$GITEA_URL/api/v1/repos/$GITEA_USER/cap-config/pulls/$PR/merge\" -d '{\"do\":\"merge\"}'"
                    ),
                    "lines": [
                        ("pulls ... | jq -r '.number'", "Opens a pull request (a request to merge the branch into main) and keeps its number."),
                        ("Sudo: lab-reviewer ... reviews", "Approves it as the reviewer account. In real work a different person approves; the lab gives you a reviewer so you can finish alone."),
                        ("pulls/$PR/merge", "Merges the approved change. 200 means it worked."),
                    ],
                },
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: argoproj.io/v1alpha1\n"
                        "kind: AppProject\n"
                        "metadata:\n"
                        "  name: cap\n"
                        "  namespace: openshift-gitops\n"
                        "spec:\n"
                        "  description: Capstone workload\n"
                        "  sourceRepos:\n"
                        "    - ${GITEA_URL}/${GITEA_USER}/cap-config.git\n"
                        "  destinations:\n"
                        "    - server: https://kubernetes.default.svc\n"
                        "      namespace: cap-demo\n"
                        "---\n"
                        "apiVersion: argoproj.io/v1alpha1\n"
                        "kind: Application\n"
                        "metadata:\n"
                        "  name: cap-app\n"
                        "  namespace: openshift-gitops\n"
                        "spec:\n"
                        "  project: cap\n"
                        "  source:\n"
                        "    repoURL: ${GITEA_URL}/${GITEA_USER}/cap-config.git\n"
                        "    targetRevision: main\n"
                        "    path: .\n"
                        "  destination:\n"
                        "    server: https://kubernetes.default.svc\n"
                        "    namespace: cap-demo\n"
                        "  syncPolicy:\n"
                        "    automated:\n"
                        "      prune: true\n"
                        "      selfHeal: true"
                    ),
                    "lines": [
                        ("kind: AppProject", "A dedicated Argo CD project (a rule set for one application). It allows exactly one source repository and one destination project, instead of the default Argo CD project, which allows any repository and any destination."),
                        ("project: cap", "Puts the application under that project."),
                        ("repoURL ... targetRevision: main", "Watch the main branch of cap-config."),
                        ("destination ... namespace: cap-demo", "Apply what is found there into cap-demo."),
                        ("automated ... selfHeal: true", "Apply changes on their own, and put back anything changed by hand."),
                    ],
                },
                {
                    "code": (
                        "oc explain applications.spec.syncPolicy.automated --api-version=argoproj.io/v1alpha1\n"
                        "envsubst < cap-argo.yaml | oc apply --dry-run=server -f -\n"
                        "envsubst < cap-argo.yaml | oc apply -f -\n"
                        "oc wait applications.argoproj.io/cap-app -n openshift-gitops --for=jsonpath='{.status.sync.status}'=Synced --timeout=180s\n"
                        "oc rollout status deployment/cap-app -n cap-demo --timeout=180s"
                    ),
                    "lines": [
                        ("oc explain application.spec.syncPolicy.automated", "Prints the fields your Argo CD release accepts. If a name differs, use the one it shows."),
                        ("envsubst < cap-argo.yaml | oc apply", "Fills in the git address from the lab variables, then saves the Argo CD project and the application."),
                        ("oc wait applications.argoproj.io/cap-app ... Synced", "Waits until Argo CD reports the cluster matches git."),
                        ("oc rollout status deployment/cap-app", "Waits until the workload pod is running."),
                    ],
                },
            ],
            "note": "Save the first YAML as cap-app.tpl.yaml and the second as cap-argo.yaml, both in the folder where you run the commands, not inside the cloned cap-config folder. The push to main in the third block is meant to fail; if it succeeds, branch protection is missing on cap-config, so tell the lab maintainer.",
            "security": "The signed image is pinned by digest (a fixed fingerprint of the exact image), so Step 5 can verify it. A tag can be moved to different content; a digest cannot.",
            "action": "Run each block in order. Read the refusal from the push to main.",
            "checkpoint": "The application is Synced and one cap-app pod is running.",
        },
        {
            "title": "Deny all traffic and allow one flow (SC-7)",
            "why": "Add two test pods: client, which will be allowed to call the workload, and other, which will not. Then block everything and open one path. The first policy denies all incoming and outgoing traffic for every pod. The second allows name lookups, because pods cannot find cap-app by name without them. The last two allow only client to call cap-app on port 8080. This answers the question: is traffic protected only at the boundary, or also between internal components?",
            "blocks": [
                {
                    "code": (
                        "oc run client -n cap-demo --image=registry.access.redhat.com/ubi9/ubi-minimal --labels=app=client -- sh -c 'while true; do echo cap-marker-client; sleep 30; done'\n"
                        "oc run other -n cap-demo --image=registry.access.redhat.com/ubi9/ubi-minimal --labels=app=other -- sleep infinity\n"
                        "oc wait --for=condition=Ready pod/client pod/other -n cap-demo --timeout=120s\n"
                        "oc exec -n cap-demo pod/other -- curl -s -o /dev/null -m 5 -w '%{http_code}\\n' http://cap-app:8080"
                    ),
                    "lines": [
                        ("oc run client ... --labels=app=client", "Starts a test pod. Its loop writes a marker line every 30 seconds, so Step 4 has something to find."),
                        ("oc run other ... --labels=app=other", "Starts a second test pod that will stay blocked."),
                        ("oc wait --for=condition=Ready", "Waits until both pods are running."),
                        ("oc exec ... curl ... cap-app:8080", "The starting problem: before any policy, the pod that should not reach the workload can. Any number except 000 means it connected."),
                    ],
                },
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: networking.k8s.io/v1\n"
                        "kind: NetworkPolicy\n"
                        "metadata:\n"
                        "  name: default-deny-all\n"
                        "  namespace: cap-demo\n"
                        "spec:\n"
                        "  podSelector: {}\n"
                        "  policyTypes:\n"
                        "    - Ingress\n"
                        "    - Egress\n"
                        "---\n"
                        "apiVersion: networking.k8s.io/v1\n"
                        "kind: NetworkPolicy\n"
                        "metadata:\n"
                        "  name: allow-dns\n"
                        "  namespace: cap-demo\n"
                        "spec:\n"
                        "  podSelector: {}\n"
                        "  policyTypes:\n"
                        "    - Egress\n"
                        "  egress:\n"
                        "    - to:\n"
                        "        - namespaceSelector:\n"
                        "            matchLabels:\n"
                        "              kubernetes.io/metadata.name: openshift-dns\n"
                        "      ports:\n"
                        "        - protocol: UDP\n"
                        "          port: 53\n"
                        "        - protocol: TCP\n"
                        "          port: 53\n"
                        "        - protocol: UDP\n"
                        "          port: 5353\n"
                        "        - protocol: TCP\n"
                        "          port: 5353\n"
                        "---\n"
                        "apiVersion: networking.k8s.io/v1\n"
                        "kind: NetworkPolicy\n"
                        "metadata:\n"
                        "  name: client-to-app\n"
                        "  namespace: cap-demo\n"
                        "spec:\n"
                        "  podSelector:\n"
                        "    matchLabels:\n"
                        "      app: client\n"
                        "  policyTypes:\n"
                        "    - Egress\n"
                        "  egress:\n"
                        "    - to:\n"
                        "        - podSelector:\n"
                        "            matchLabels:\n"
                        "              app: cap-app\n"
                        "      ports:\n"
                        "        - protocol: TCP\n"
                        "          port: 8080\n"
                        "---\n"
                        "apiVersion: networking.k8s.io/v1\n"
                        "kind: NetworkPolicy\n"
                        "metadata:\n"
                        "  name: app-from-client\n"
                        "  namespace: cap-demo\n"
                        "spec:\n"
                        "  podSelector:\n"
                        "    matchLabels:\n"
                        "      app: cap-app\n"
                        "  policyTypes:\n"
                        "    - Ingress\n"
                        "  ingress:\n"
                        "    - from:\n"
                        "        - podSelector:\n"
                        "            matchLabels:\n"
                        "              app: client\n"
                        "      ports:\n"
                        "        - protocol: TCP\n"
                        "          port: 8080"
                    ),
                    "lines": [
                        ("default-deny-all", "Selects every pod and lists both directions with no rules, so nothing is allowed."),
                        ("allow-dns", "Lets every pod send name lookups to the cluster DNS service on its ports."),
                        ("client-to-app", "Lets only pods labeled app=client send traffic to pods labeled app=cap-app, on port 8080 only."),
                        ("app-from-client", "The matching rule on the receiving side. Both sides must allow a flow."),
                    ],
                },
                {
                    "code": (
                        "oc explain networkpolicy.spec.egress.to\n"
                        "oc apply -f cap-network.yaml --dry-run=server\n"
                        "oc apply -f cap-network.yaml\n"
                        "oc get networkpolicy -n cap-demo"
                    ),
                    "lines": [
                        ("oc explain ...", "Prints the fields your cluster accepts."),
                        ("--dry-run=server", "Checks the file without saving it."),
                        ("oc get networkpolicy", "Lists the four policies you applied."),
                    ],
                },
            ],
            "action": "Run the first block and note the starting answer. Save the YAML as cap-network.yaml and run the third block.",
            "checkpoint": "Four policies are listed.",
        },
        {
            "title": "Find the workload's records in the SIEM (AU-12)",
            "why": "A workload that cannot be searched cannot be investigated. The collector from SIEM-1 already reads every project, so nothing needs configuring. Prove it: search Loki for the marker the client pod writes, and for the audit record of your network policy change. Loki finds streams by label, so you name the project in the label and filter the text after it.",
            "blocks": [
                {
                    "code": (
                        "sleep 60\n"
                        + START_LINE
                        + "curl -s --cacert \"$LOKI_CA_FILE\" -u \"$LOKI_USER:$LOKI_PASSWORD\" \"$LOKI_URL/loki/api/v1/label/kubernetes_namespace_name/values\" | jq -c .\n"
                        + LOKI_CURL
                        + "--data-urlencode 'query={log_type=\"application\", kubernetes_namespace_name=\"cap-demo\"} |= \"cap-marker-client\"' | jq '.data.result | length'\n"
                        + LOKI_CURL
                        + AUDIT_QUERY + " | jq '.data.result | length'"
                    ),
                    "lines": [
                        ("sleep 60", "Gives the collector time to send the first records."),
                        ("START=...", "Sets the start of the search window to the moment cap-demo was created. Records from an earlier attempt, before the project existed, cannot be counted, and the search still works if you come back later."),
                        ("label/kubernetes_namespace_name/values", "Lists the project names Loki holds records for. cap-demo must be in the list."),
                        ("query={log_type=\"application\", ...}", "Searches application records from cap-demo that contain the marker."),
                        ("query={log_type=\"audit\"} |= \"cap-demo\" |= \"networkpolicies\" | json | verb=\"create\"", "Searches audit records that mention cap-demo and network policies, reads each record as JSON, and keeps only the ones whose verb is create. This is the record of who created the policies in Step 3."),
                        ("jq '.data.result | length'", "Counts the matching streams. 1 or more means found; 0 means none."),
                    ],
                }
            ],
            "note": "The label name kubernetes_namespace_name is the one earlier modules used. If cap-demo is missing from the list, run the label query again and use the name your Logging release shows. Loki answers the label-values query for a default recent window unless you give a start, so a new project can take a minute to appear.",
            "action": "Run the block and read the two counts.",
            "checkpoint": "Both counts are 1 or more.",
        },
        {
            "title": "Admit only signed images in the project (SI-7)",
            "why": "The signature policy from the release pipeline module covers only the demo project. Add cap-demo to it. From now on every pod in cap-demo must carry a valid signature, so the workload (signed) is admitted and the unsigned image is refused. This step comes last because the rule would have refused your own test pods.",
            "blocks": [
                {
                    "code": (
                        "oc get clusterpolicy require-signed-images -o jsonpath='{.spec.rules[0].match.any[0].resources.namespaces}{\"\\n\"}'\n"
                        "oc patch clusterpolicy require-signed-images --type json -p '[{\"op\":\"add\",\"path\":\"/spec/rules/0/match/any/0/resources/namespaces/-\",\"value\":\"cap-demo\"}]' --dry-run=server\n"
                        "oc patch clusterpolicy require-signed-images --type json -p '[{\"op\":\"add\",\"path\":\"/spec/rules/0/match/any/0/resources/namespaces/-\",\"value\":\"cap-demo\"}]'\n"
                        "oc get clusterpolicy require-signed-images -o jsonpath='{.spec.rules[0].match.any[0].resources.namespaces}{\"\\n\"}'"
                    ),
                    "lines": [
                        ("oc get clusterpolicy ... namespaces", "Prints the projects the policy covers. Run before and after."),
                        ("--type json -p '[{\"op\":\"add\" ...}]'", "Adds cap-demo to the end of that list without touching the rest of the policy."),
                        ("--dry-run=server", "Checks the change without saving it."),
                    ],
                },
                {
                    "code": (
                        "sleep 10\n"
                        "oc run unsigned-test -n cap-demo --image=registry.access.redhat.com/ubi9/ubi-minimal --restart=Never -- sleep 60\n"
                        "oc get pod unsigned-test -n cap-demo"
                    ),
                    "lines": [
                        ("sleep 10", "Gives Kyverno a moment to load the changed policy before the test."),
                        ("oc run unsigned-test ... ubi-minimal", "Tries to start a pod from an image nobody signed."),
                        ("oc get pod unsigned-test", "Shows the pod does not exist, because the cluster refused it."),
                    ],
                },
            ],
            "tip": "Read the refusal text. It names the policy and the rule that blocked the pod, which is the first thing an administrator checks when a pod will not start.",
            "action": "Add the project to the policy, then try the unsigned pod.",
            "checkpoint": "The unsigned pod is refused and the list now includes cap-demo.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "Check 1: The deployer identity can manage deployments in its own project",
            "hint": "Fix: re-apply cap-identity.yaml (Step 1) and check the Role lists deployments in apps and that the RoleBinding names cap-deployer in cap-demo.",
            "why": "AC-6. The identity needs the access its job requires.",
            "code": (
                "SA=system:serviceaccount:cap-demo:cap-deployer\n"
                "echo \"create deployments in cap-demo: $(oc auth can-i create deployments -n cap-demo --as=$SA 2>/dev/null)\""
            ),
            "expect": "create deployments in cap-demo: yes",
            "checkpoint": "The answer is yes.",
        },
        {
            "kind": "negative",
            "title": "Check 2: The same identity is refused everywhere else",
            "hint": "Fix: the identity is too wide. Remove any ClusterRoleBinding or RoleBinding for cap-deployer outside cap-demo (oc get clusterrolebinding,rolebinding -A | grep cap-deployer).",
            "why": "AC-6. Least privilege is proven by what is refused, not by what works. The first line is a control: if the identity does not exist, every answer is no, so the control must say yes for the three no answers to mean anything.",
            "code": (
                "SA=system:serviceaccount:cap-demo:cap-deployer\n"
                "echo \"control, create deployments in cap-demo: $(oc auth can-i create deployments -n cap-demo --as=$SA 2>/dev/null)\"\n"
                "echo \"create deployments in demo: $(oc auth can-i create deployments -n demo --as=$SA 2>/dev/null)\"\n"
                "echo \"read secrets in openshift-config: $(oc auth can-i get secrets -n openshift-config --as=$SA 2>/dev/null)\"\n"
                "echo \"create namespaces: $(oc auth can-i create namespaces --as=$SA 2>/dev/null)\""
            ),
            "expect": (
                "control, create deployments in cap-demo: yes\n"
                "create deployments in demo: no\n"
                "read secrets in openshift-config: no\n"
                "create namespaces: no"
            ),
            "checkpoint": "The control line says yes and the three other answers are no.",
        },
        {
            "kind": "positive",
            "title": "Check 3: The workload is in sync, healthy, and came from an approved pull request",
            "hint": "Fix: redo Step 2. Open a pull request, have it approved by lab-reviewer and merge it into main, apply cap-argo.yaml, then run oc get applications.argoproj.io cap-app -n openshift-gitops to read the status.",
            "why": "CM-3. The running workload must match the approved git change. The last line reads Gitea: a merged pull request must carry an approval from lab-reviewer, so a workload that was applied some other way does not pass.",
            "code": (
                "oc get applications.argoproj.io cap-app -n openshift-gitops -o jsonpath='{.status.sync.status} {.status.health.status}{\"\\n\"}'\n"
                "oc get deployment cap-app -n cap-demo -o jsonpath='{.status.readyReplicas}{\"\\n\"}'\n"
                "API=\"$GITEA_URL/api/v1/repos/$GITEA_USER/cap-config\"\n"
                "MERGED='[.[] | select(.merged == true)] | .[0].number // empty'\n"
                "APPROVED='[.[] | select(.state == \"APPROVED\" and .user.login == \"lab-reviewer\")] | length'\n"
                "PRN=$(curl -s -H \"Authorization: token $GITEA_TOKEN\" \"$API/pulls?state=closed\" | jq -r \"$MERGED\")\n"
                "NAP=$(curl -s -H \"Authorization: token $GITEA_TOKEN\" \"$API/pulls/$PRN/reviews\" | jq \"$APPROVED\")\n"
                "test -n \"$PRN\" && test \"${NAP:-0}\" -ge 1 && echo \"merged pull request approved: yes\" || echo \"merged pull request approved: no\""
            ),
            "expect": (
                "Synced Healthy\n"
                "1\n"
                "merged pull request approved: yes"
            ),
            "checkpoint": "The first line is Synced Healthy, the second is 1, and the third says yes.",
        },
        {
            "kind": "negative",
            "title": "Check 4: A manual change is reverted by Argo CD",
            "hint": "Fix: self-heal is off or slow. Confirm syncPolicy.automated.selfHeal is true in cap-argo.yaml, then apply it again.",
            "why": "CM-3. A change made outside git must not last. The first line proves the manual change was accepted, so a rejected change cannot pass by accident.",
            "code": (
                "oc scale deployment/cap-app -n cap-demo --replicas=3\n"
                "sleep 45\n"
                "AFTER=$(oc get deployment cap-app -n cap-demo -o jsonpath='{.spec.replicas}')\n"
                "oc scale deployment/cap-app -n cap-demo --replicas=1 > /dev/null\n"
                "echo \"replicas after the wait: $AFTER\""
            ),
            "expect": (
                "deployment.apps/cap-app scaled\n"
                "replicas after the wait: 1"
            ),
            "checkpoint": "The scale command confirms the manual change, and the count is back to 1 after the wait. The check puts the count back to 1 itself afterwards, so a failed check leaves nothing changed.",
        },
        {
            "kind": "positive",
            "title": "Check 5: The one allowed flow works",
            "hint": "Fix: check client-to-app and app-from-client in cap-network.yaml use the labels app=client and app=cap-app and port 8080, and that allow-dns exists.",
            "why": "SC-7. The listed flow must still work after default-deny.",
            "code": (
                "CODE=$(oc exec -n cap-demo pod/client -- curl -s -o /dev/null -m 5 -w '%{http_code}' http://cap-app:8080)\n"
                "test \"$CODE\" != \"000\" && echo reachable || echo blocked"
            ),
            "expect": "reachable",
            "checkpoint": "The answer is reachable.",
        },
        {
            "kind": "negative",
            "title": "Check 6: Every flow that is not listed is blocked",
            "hint": "Fix: a policy is too open, or the allowed flow is broken. Run oc get networkpolicy -n cap-demo and confirm default-deny-all exists and no policy allows the other pod. If the first line says blocked, fix Check 5 first.",
            "why": "SC-7. Anything not on the list must fail. 000 means no connection was made. The first line is a control: a closed port also prints 000, so the allowed flow must work for the 000 answers to mean blocked by policy.",
            "code": (
                "CODE=$(oc exec -n cap-demo pod/client -- curl -s -o /dev/null -m 5 -w '%{http_code}' http://cap-app:8080 2>/dev/null)\n"
                "test -n \"$CODE\" && test \"$CODE\" != \"000\" && echo \"control, allowed flow: reachable\" || echo \"control, allowed flow: blocked\"\n"
                "echo \"other to app: $(oc exec -n cap-demo pod/other -- curl -s -o /dev/null -m 5 -w '%{http_code}' http://cap-app:8080 2>/dev/null)\"\n"
                "echo \"client to API: $(oc exec -n cap-demo pod/client -- curl -sk -o /dev/null -m 5 -w '%{http_code}' https://kubernetes.default.svc:443 2>/dev/null)\"\n"
                "echo \"other to API: $(oc exec -n cap-demo pod/other -- curl -sk -o /dev/null -m 5 -w '%{http_code}' https://kubernetes.default.svc:443 2>/dev/null)\""
            ),
            "expect": (
                "control, allowed flow: reachable\n"
                "other to app: 000\n"
                "client to API: 000\n"
                "other to API: 000"
            ),
            "checkpoint": "The control says reachable and the three other lines print 000.",
        },
        {
            "kind": "positive",
            "title": "Check 7: The workload's records and the audit record are in the SIEM",
            "hint": "Fix: confirm the forwarder from SIEM-1 is running (oc get pods -n openshift-logging) and that the client pod is running; records can take a minute to arrive.",
            "why": "AU-12. An application record and an audit record from the new project must both be searchable.",
            "code": (
                START_LINE
                + "NA=$("
                + LOKI_CURL
                + "--data-urlencode 'query={log_type=\"application\", kubernetes_namespace_name=\"cap-demo\"} |= \"cap-marker-client\"' | jq '.data.result | length')\n"
                "NB=$("
                + LOKI_CURL
                + AUDIT_QUERY + " | jq '.data.result | length')\n"
                "test \"${NA:-0}\" -ge 1 && echo \"application records: found\" || echo \"application records: missing\"\n"
                "test \"${NB:-0}\" -ge 1 && echo \"audit records: found\" || echo \"audit records: missing\""
            ),
            "expect": (
                "application records: found\n"
                "audit records: found"
            ),
            "checkpoint": "Both lines say found.",
        },
        {
            "kind": "negative",
            "title": "Check 8: An unsigned image is refused in the project",
            "hint": "Fix: add cap-demo to the namespaces list of policy require-signed-images (Step 5), then delete any unsigned-test pod and retry.",
            "why": "SI-7. A failed signature check must stop the pod from starting. The check looks for the policy name in the refusal, so a refusal from some other policy does not count.",
            "code": (
                "oc delete pod unsigned-test -n cap-demo --ignore-not-found > /dev/null\n"
                "OUT=$(oc run unsigned-test -n cap-demo --image=registry.access.redhat.com/ubi9/ubi-minimal --restart=Never -- sleep 60 2>&1)\n"
                "echo \"$OUT\" | grep -q 'was blocked due to the following policies' && echo \"$OUT\" | grep -q 'require-signed-images' && echo \"refused by require-signed-images\" || echo \"not refused by require-signed-images\"\n"
                "oc get pod -n cap-demo -o name | grep -c unsigned-test\n"
                "oc delete pod unsigned-test -n cap-demo --ignore-not-found > /dev/null"
            ),
            "expect": (
                "refused by require-signed-images\n"
                "0"
            ),
            "checkpoint": "The refusal names the policy require-signed-images and no unsigned pod exists. The check deletes the test pod at the end if it was created.",
        },
        {
            "kind": "positive",
            "title": "Check 9: The signed workload is admitted again after a restart",
            "hint": "Fix: the signed pod was refused. Check the registry-pull secret exists in cap-demo and that the image in cap-app.yaml is the digest reference from demo-app.",
            "why": "SI-7. The rule must refuse the unsigned image without stopping the signed one.",
            "code": (
                "oc delete pod -n cap-demo -l app=cap-app > /dev/null\n"
                "sleep 15\n"
                "oc wait --for=condition=Ready pod -l app=cap-app -n cap-demo --timeout=180s > /dev/null\n"
                "oc get pod -n cap-demo -l app=cap-app -o jsonpath='{.items[0].spec.containers[0].image}' | grep -c '@sha256:'"
            ),
            "expect": "1",
            "checkpoint": "A new pod is Ready and runs an image pinned by digest.",
        },
    ],
    "glossary": [
        ("Role and RoleBinding", "A Role lists allowed actions in one project. A RoleBinding gives that list to an identity."),
        ("Service account", "An identity for a program instead of a person."),
        ("Project (OpenShift)", "A named workspace in the cluster."),
        ("Pull request", "A request to merge a branch into main that someone else can review and approve."),
        ("Digest", "A fixed fingerprint of the exact content of an image."),
        ("Policy (Kyverno)", "A rule the cluster checks when a resource is created."),
        ("LogQL", "Loki's search language."),
    ],
    "next": "This is the last module. When all nine checks pass, you have shown the five controls work together on a new workload.",
}
