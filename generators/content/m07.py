"""M07: Hardening and policy as code (CM-6, CM-7, CM-2)."""

FEDRAMP = "fedramp-high-baseline.md"
NIST = "nist-sp-800-53r5-full.md"
SRG = "u-cloud-service-provider-v1r6-srg.md"

MODULE = {
    "id": "M07",
    "slug": "Harden",
    "title": "Hardening and Policy as Code",
    "draft": (
        "Commands follow Red Hat's published Compliance Operator documentation and the Kyverno policy library but have not yet run in the lab. "
        "Profile names are read from the cluster with oc get before they are used. Kyverno field names differ between releases, so the policies are "
        "checked with oc explain and a server-side dry run before they are applied. Which rules fail on a fresh cluster, and which of those have a "
        "fix that needs no node restart, depends on the cluster, so Step 3 and Test 4 find them with a query instead of naming one. "
        "Red Hat's Compliance Operator documentation states that ocp4-stig, ocp4-stig-node and rhcos4-stig always point to the latest STIG version and that a node profile must be used with its platform profile; the live profile list on your cluster is still the authority (oc get profiles.compliance -o wide). "
        "The lab pins Kyverno 1.19.2 (Helm chart kyverno/kyverno 3.9.2). In that release ClusterPolicy (kyverno.io/v1) is deprecated in favor of the newer CEL-based policy types (ValidatingPolicy and others in policies.kyverno.io), and the Kyverno project says it will remove ClusterPolicy in 1.20, but 1.19 still fully supports it. "
        "This module therefore keeps ClusterPolicy, because the lab pins 1.19.2, and the rule-level validate.failureAction field is the documented spelling there; the cluster may print a deprecation warning when you apply the policies, which is expected. Do not move the lab to Kyverno 1.20 or later without rewriting the policies. Confirm the fields with oc explain and oc get crd clusterpolicies.kyverno.io. "
        "OpenShift's built-in security context admission may add a non-root setting to the bad-root pod, which would let it through (Red Hat documents that the restricted SCCs assign a user ID from the namespace range, but does not say whether runAsNonRoot is added); confirm with oc apply --dry-run=server -o yaml on bad-pods.yaml before relying on Test 3."
    ),
    "controls": ["CM-6", "CM-7", "CM-2"],
    "mentions": ["CM-3", "CM-7(1)", "CM-7(5)", "CM-2(1)", "CM-2(3)", "CM-11", "CA-5", "RA-5", "SI-2"],
    "unit_values_ok": ["2 minutes", "5 minutes", "10 minutes"],
    "minutes": {"hands_on": 45, "verify": 25},
    "tools": [
        "OpenShift Container Platform",
        "OpenShift Compliance Operator",
        "Kyverno (free, open source)",
        "oc",
        "jq",
        "git",
    ],
    "diagrams": [
        {
            "id": "harden",
            "title": "Scan the cluster, then refuse bad pods",
            "caption": "The Compliance Operator checks the cluster against the STIG and reports pass or fail. Kyverno checks every new pod in the demo namespace and refuses the ones that ask for too much. Your baseline files are saved in git. New parts are drawn with thick lines.",
            "per_step": True,
            "rankdir": "TB",
            "step_notes": {
                1: "Both tools are already installed. You only read the profile names and check that the pods are running.",
                2: "A scan binding picks the two STIG profiles and starts a scan that reports and changes nothing.",
                3: "Failing rules are read from the results, and some come with a fix that needs no node restart.",
                4: "Kyverno now checks each pod request against three policies and refuses the ones that break a rule.",
                5: "The scan binding and the policy files are saved in git, which keeps every version.",
            },
            "zones": [
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "comp", "label": "Namespace openshift-compliance", "parent": "cluster", "kind": "group"},
                {"id": "kyv", "label": "Namespace kyverno", "parent": "cluster", "kind": "group"},
                {"id": "demo", "label": "Namespace demo", "parent": "cluster", "kind": "group"},
                {"id": "work", "label": "Your workstation", "kind": "boundary", "s": 5, "labelloc": "b"},
            ],
            "nodes": [
                {"id": "op", "title": "Compliance Operator", "sub": "Scans and reports", "zone": "comp"},
                {"id": "prof", "title": "STIG profiles", "sub": "Platform and node", "zone": "comp"},
                {"id": "bind", "title": "Scan binding", "sub": "Named stig-scan", "zone": "comp", "s": 2},
                {"id": "res", "title": "Check results", "sub": "Pass, fail, manual", "zone": "comp", "kind": "warn", "s": 2},
                {"id": "fix", "title": "Settings-only fixes", "sub": "No node restart", "zone": "comp", "s": 3},
                {"id": "kv", "title": "Kyverno", "sub": "Admission controller", "zone": "kyv"},
                {"id": "pol", "title": "Three policies", "sub": "Enforce, demo only", "zone": "kyv", "s": 4},
                {"id": "req", "title": "Pod requests", "sub": "Create requests", "zone": "demo", "s": 4},
                {"id": "okp", "title": "Compliant pod", "sub": "Runs", "zone": "demo", "kind": "ok", "s": 4},
                {"id": "badp", "title": "Refused pods", "sub": "Privileged, latest tag, root", "zone": "demo", "kind": "bad", "s": 4},
                {"id": "git", "title": "Git baseline", "sub": "Scan and policy files", "zone": "work", "kind": "ok", "s": 5},
            ],
            "edges": [
                {"a": "op", "b": "prof", "label": "Ships"},
                {"a": "bind", "b": "prof", "label": "Selects", "s": 2},
                {"a": "bind", "b": "op", "label": "Starts a scan", "s": 2},
                {"a": "op", "b": "res", "label": "Writes", "s": 2},
                {"a": "res", "b": "fix", "label": "Offers", "s": 3},
                {"a": "kv", "b": "pol", "label": "Reads", "s": 4},
                {"a": "req", "b": "kv", "label": "Checked first", "s": 4},
                {"a": "kv", "b": "okp", "label": "Allows", "kind": "ok", "s": 4},
                {"a": "kv", "b": "badp", "label": "Refuses", "kind": "bad", "s": 4},
                {"a": "bind", "b": "git", "label": "Saved in", "s": 5},
                {"a": "pol", "b": "git", "label": "Saved in", "s": 5},
            ],
            "reading": [
                "The Compliance Operator uses a scan binding to run the STIG profiles and writes the check results.",
                "Some failing rules come with a settings-only fix that needs no node restart.",
                "Kyverno reads three policies and checks each pod request in the demo namespace.",
                "A compliant pod is allowed. Privileged, latest-tag and root pods are refused.",
                "The scan binding and the policy files are saved in git as the baseline.",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)"],
    "lab_needs": [
        "Compliance Operator installed in the openshift-compliance namespace with the default ProfileBundles valid.",
        "The demo-app deployment in the demo namespace uses a fixed version tag (not latest) and sets runAsNonRoot: true in its pod spec, so its pods pass the three policies when they restart.",
        "Kyverno 1.19.2 (Helm chart kyverno/kyverno 3.9.2) running in the kyverno namespace. Do not install 1.20 or later, which removes the ClusterPolicy type this module uses.",
    ],
    "lab": {
        "start": "lab start m07",
        "env": [],
        "checks": [
            "The STIG scan suite finished and reports PASS and FAIL results.",
            "The three Kyverno policies exist and are set to enforce in the demo namespace.",
            "A policy-compliant pod runs in the demo namespace.",
            "A privileged pod, a latest-tag pod and a root pod are each denied.",
            "A failing hardening rule is fixed and passes on the next scan.",
        ],
    },
    "requirement": (
        "An IL5 system must be set up in the most restrictive way that still lets it do its job, and it must stay that way. "
        "This module does two things. First, it scans the cluster against the DISA STIG (a security checklist published by the "
        "Defense Information Systems Agency) and fixes a failing setting. Second, it writes rules as code (policy as code: rules "
        "kept in files that the cluster itself enforces) so that workloads asking for more power than they need are refused at the door."
    ),
    "mapping": [
        {
            "control": "CM-6 Configuration Settings",
            "plain": "Pick a secure checklist, apply it, record any exception, and watch for changes.",
            "source": "NIST; FedRAMP",
            "covered": "Steps 2 and 3 scan against the DISA STIG profiles. Test 4 fixes a failing rule.",
            "cite": [
                {"file": NIST, "quote": "Establish and document configuration settings for components employed within the system that reflect the most restrictive mode consistent with operational requirements"},
                {"file": NIST, "quote": "Identify, document, and approve any deviations from established configuration settings"},
                {"file": FEDRAMP, "quote": "The service provider shall use the DoD STIGs to establish configuration settings"},
            ],
        },
        {
            "control": "CM-7 Least Functionality",
            "plain": "Allow only the capabilities the mission needs and block the rest.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Step 4 writes three Kyverno policies. Tests 2 and 3 show an allowed pod and refused pods.",
            "cite": [
                {"file": NIST, "quote": "Prohibit or restrict the use of the following functions, ports, protocols, software, and/or services"},
                {"file": FEDRAMP, "quote": "CM-7 (1) (a) [at least annually]"},
                
                {"file": SRG, "quote": "CM-7(5) DSPAV must be used"},
            ],
        },
        {
            "control": "CM-2 Baseline Configuration",
            "plain": "Keep a current, version-controlled baseline and review it on a schedule.",
            "source": "NIST; FedRAMP",
            "covered": "Step 5 records the pinned checklist and commits the policies to git.",
            "cite": [
                {"file": NIST, "quote": "Develop, document, and maintain under configuration control, a current baseline"},
                {"file": FEDRAMP, "quote": "CM-2 (b) (1) [at least annually and when a significant change occurs]"},
                {"file": NIST, "quote": "of previous versions of baseline configurations of the system to support rollback."},
            ],
        },
    ],
    "intent": [
        {
            "control": "CM-6 Configuration Settings",
            "feared": "A system component runs with a default or weak setting nobody chose, and an attacker uses it.",
            "scope": "Every component the system team operates, including the cluster and the nodes it runs on. Settings the cloud provider controls belong to the provider.",
            "question": "For this component, which checklist defines the right setting, and does the live setting match it today?",
            "evidence": "The chosen checklist, the scan result for each setting, and the recorded reason for every setting that deviates.",
            "sufficient": "The checklist is named, applied, and checked automatically. Every deviation is approved and written down. FedRAMP requires the DoD STIGs to establish configuration settings, with CIS Level 2 and then custom baselines only where no STIG exists. The lab uses the DISA STIGs and sends each deviation to a Plan of Action and Milestones (POA&M: the tracked list of known weaknesses and the dates they will be fixed).",
            "tieoff": "Someone owns each failing rule until it is fixed or formally accepted. Changes to a setting go through change control (CM-3).",
            "tool": "The Compliance Operator scans against the STIG profiles (Steps 2 and 3) and can apply many fixes itself. Test 4 shows a failing rule becoming a passing one.",
        },
        {
            "control": "CM-7 Least Functionality",
            "feared": "A workload runs with more power than it needs, such as full control of the node, and a flaw in it becomes a takeover of the platform.",
            "scope": "Every workload and service the team lets run on the platform.",
            "question": "What is the least this workload needs, and what stops it from asking for more?",
            "evidence": "The policies that refuse extra capability, and a refused request that proves they work.",
            "sufficient": "Only essential capabilities are allowed, the rest are blocked by something automatic rather than by good intentions, and the list is reviewed on a schedule. FedRAMP sets that review (CM-7(1)) to at least annually. The DoD SRG says DSPAV (DoD-specific assignment values) must be used for CM-7(5), so this module does not invent an allow list.",
            "tieoff": "Someone tells the policy owner when a team needs an exception, and the exception is recorded.",
            "tool": "Kyverno policies (Step 4) refuse privileged containers, containers that can run as root, and the mutable latest image tag.",
        },
        {
            "control": "CM-2 Baseline Configuration",
            "feared": "Nobody can say what the approved configuration is, so nobody can tell a legitimate change from an attack.",
            "scope": "The system as a whole, kept in files that can be compared over time.",
            "question": "Where is the approved configuration written, and how would we know it changed?",
            "evidence": "The pinned checklist content, the policy files, and the version history that shows each change.",
            "sufficient": "The baseline is under configuration control, reviewed on a set frequency and when circumstances change, and earlier versions are kept so a change can be undone. FedRAMP sets the review to at least annually and when a significant change occurs. The lab reviews semi-annually or upon significant changes, and keeps all previous versions in version control (CM-2(3)).",
            "tieoff": "Someone owns each review and records it.",
            "tool": "Step 5 reads the pinned checklist version from the cluster and commits the policy files to git, which keeps every version.",
        },
    ],
    "architect": (
        "Decide which checklist applies, which scans you will run and which you will leave out and why, which workload "
        "requests the platform must refuse, and where the approved policy files live so changes are reviewed. "
        "Then build it and run the tests."
    ),
    "terms": [
        ("STIG", "Security Technical Implementation Guide: a checklist of secure settings published by the Defense Information Systems Agency."),
        ("Compliance Operator", "An OpenShift add-on (an operator is a program that manages another program for you) that scans the cluster against a checklist and reports each rule as pass or fail."),
        ("Profile and rule", "A profile is a named checklist. A rule is one item on it, such as one setting that must have one value."),
        ("Remediation", "A prepared fix for a failing rule that the operator can apply for you."),
        ("Policy as code", "Security rules kept in files that the cluster itself enforces, so they can be reviewed and versioned like software."),
        ("Admission controller", "A gate in the cluster that checks every create or change request before it is saved and can refuse it."),
        ("Kyverno", "A free, open source admission controller that reads policies written in YAML."),
        ("Privileged container", "A container with nearly the same power as the node it runs on."),
        ("Image tag", "The label after the colon in an image name, such as :1.2. The tag latest is a label that moves, so it does not say which version runs."),
    ],
    "concepts": [
        {
            "heading": "7.1 Two ways to enforce least functionality",
            "paras": [
                "What is this? A setting can be wrong in two ways. The platform itself can be set up loosely (a hardening problem), or a workload can ask for more power than it needs (a policy problem). This module checks the first with the Compliance Operator and blocks the second with Kyverno.",
                "Why? A scan finds problems after the fact. A policy refuses the problem before it exists. An IL5 system needs both, because the scan proves the baseline is in place and the policy keeps it there.",
            ],
            "table": {
                "headers": ["Tool", "When it acts", "Question it answers"],
                "rows": [
                    ("Compliance Operator scan", "On a schedule or on demand, after things are running", "Does the cluster match the STIG today?"),
                    ("Kyverno policy", "At the moment someone creates a workload", "Should this request be allowed at all?"),
                ],
            },
        },
        {
            "heading": "7.2 The STIG profiles the operator ships",
            "paras": [
                "The Compliance Operator ships ready-made profiles built from the DISA STIG for Red Hat OpenShift. A platform profile checks cluster settings such as the API server. A node profile checks each node. Red Hat documents that a node profile must be used with its matching platform profile. The names without a version suffix always point to the newest STIG release the operator carries.",
                "You do not type these names from memory. Step 1 lists them from your own cluster, which is the source of truth for your release.",
            ],
            "table": {
                "headers": ["Profile name", "Checks"],
                "rows": [
                    ("ocp4-stig", "Platform: cluster settings (latest STIG release)"),
                    ("ocp4-stig-node", "Node: OpenShift settings on each host (latest STIG release)"),
                    ("rhcos4-stig", "Node: operating system settings of each host (latest STIG release)"),
                    ("names ending in a version such as -v2r3", "An older, pinned STIG release, kept for teams that must stay on it"),
                ],
            },
        },
        {
            "heading": "7.3 How Kyverno decides",
            "paras": [
                "When anyone creates a pod, the cluster's admission controller (the gate described in the terms table) asks Kyverno before saving it. Kyverno compares the pod to each policy. In Enforce mode a pod that breaks a policy is refused with a message. In Audit mode it is allowed and only reported. This module uses Enforce, scoped to the demo namespace (a named workspace in the cluster), so the rest of the lab keeps working.",
            ],
            "diagram": (
                "kubectl/oc create pod  -->  cluster API  -->  Kyverno policies  -->  saved and scheduled\n"
                "                                                |\n"
                "                                                +--> refused with a message (Enforce)"
            ),
            "production": "In the real environment policies are applied by the GitOps pipeline from a reviewed repository, never by hand, and a policy exception is a recorded change. The lab applies them by hand so you see each step.",
        },
    ],
    "steps": [
        {
            "title": "Check what you have and read the real profile names",
            "why": "Confirm the Compliance Operator and Kyverno are ready, then list the STIG profiles your cluster actually ships. Profile names change between releases, so read them instead of trusting a document.",
            "blocks": [
                {
                    "code": (
                        "oc get csv -n openshift-compliance\n"
                        "oc get profilebundle -n openshift-compliance\n"
                        "oc get profiles.compliance -n openshift-compliance | grep stig\n"
                        "oc get pods -n kyverno"
                    ),
                    "lines": [
                        ("oc get csv", "Lists installed operators (a csv is the record of one installed operator)."),
                        ("oc get profilebundle", "Shows the checklist content the operator loaded. Each bundle should say VALID."),
                        ("oc get profiles.compliance ... | grep stig", "Lists every checklist whose name contains stig."),
                        ("oc get pods -n kyverno", "Lists the Kyverno programs. They should be Running."),
                    ],
                }
            ],
            "action": "Run the commands. Write down the platform and node STIG profile names without a version suffix.",
            "checkpoint": "ProfileBundles are VALID, Kyverno pods are Running, and you can see ocp4-stig and ocp4-stig-node in the list (or the equivalent names your release shows).",
        },
        {
            "title": "Scan the cluster against the STIG (CM-6)",
            "why": "A ScanSettingBinding connects profiles to scan settings and starts the scan. The default scan setting reports problems and does not change anything, which is what you want for a first look. Only the platform and OpenShift node profiles are used here. The operating-system profile is left out because many of its fixes restart the node, and one of them turns off remote login.",
            "blocks": [
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: compliance.openshift.io/v1alpha1\n"
                        "kind: ScanSettingBinding\n"
                        "metadata:\n"
                        "  name: stig-scan\n"
                        "  namespace: openshift-compliance\n"
                        "profiles:\n"
                        "  - name: ocp4-stig\n"
                        "    kind: Profile\n"
                        "    apiGroup: compliance.openshift.io/v1alpha1\n"
                        "  - name: ocp4-stig-node\n"
                        "    kind: Profile\n"
                        "    apiGroup: compliance.openshift.io/v1alpha1\n"
                        "settingsRef:\n"
                        "  name: default\n"
                        "  kind: ScanSetting\n"
                        "  apiGroup: compliance.openshift.io/v1alpha1"
                    ),
                    "lines": [
                        ("kind: ScanSettingBinding", "The object that starts a scan."),
                        ("profiles", "The two checklists to run. Use the names you found in Step 1."),
                        ("settingsRef: default", "Uses the built-in setting that scans and reports without changing anything."),
                    ],
                },
                {
                    "code": (
                        "oc apply -f stig-scan.yaml --dry-run=server\n"
                        "oc apply -f stig-scan.yaml\n"
                        "oc get compliancescan -n openshift-compliance\n"
                        "oc wait compliancesuite/stig-scan -n openshift-compliance --for=jsonpath='{.status.phase}'=DONE --timeout=30m\n"
                        "oc get compliancesuite stig-scan -n openshift-compliance"
                    ),
                    "lines": [
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc apply -f", "Saves the binding. The operator creates a suite and one scan per profile."),
                        ("oc get compliancescan", "Shows each scan moving through its phases."),
                        ("oc wait ... DONE", "Waits until the suite finishes. A node scan can take several minutes."),
                        ("oc get compliancesuite", "Shows the final phase and result."),
                    ],
                },
            ],
            "security": "Red Hat warns that applying every automatic fix in a profile such as rhcos4-stig turns off the sshd service (the remote login service) on the nodes. This is why you review fixes before applying them. If an organization must keep a rule from being applied, the operator supports a tailored profile (a copy of a profile with named rules switched off) and the reason belongs in the POA&M.",
            "action": "Save the YAML as stig-scan.yaml, validate it, apply it, then wait for the suite to finish.",
            "checkpoint": "The suite phase is DONE and its result is NON-COMPLIANT. That is the normal first result, not a failure of the tool.",
        },
        {
            "title": "Read the results and find fixes you can apply safely (CM-6)",
            "why": "Each rule becomes a result object with a status and a severity. For some failing rules the operator also prepares a remediation. A remediation that changes a node needs a restart, so look for the ones that change only cluster settings.",
            "blocks": [
                {
                    "code": (
                        "oc get compliancecheckresults -n openshift-compliance -l compliance.openshift.io/suite=stig-scan -o json | jq -r '.items[].status' | sort | uniq -c\n"
                        "oc get compliancecheckresults -n openshift-compliance -l 'compliance.openshift.io/suite=stig-scan,compliance.openshift.io/check-status=FAIL' --no-headers | head -20\n"
                        "oc get complianceremediations -n openshift-compliance -o json | jq -r '.items[] | select(.spec.current.object.kind != \"MachineConfig\") | .metadata.name'"
                    ),
                    "lines": [
                        ("jq -r '.items[].status' | sort | uniq -c", "Counts how many rules passed, failed or need a manual look."),
                        ("check-status=FAIL", "Lists only the failing rules."),
                        ("head -20", "Shows the first twenty lines so the list stays readable."),
                        ("select(... != MachineConfig)", "Keeps the remediations that change cluster settings only, with no node restart."),
                    ],
                }
            ],
            "note": "A status of MANUAL means the tool cannot decide and a person must check. Those rules still count toward the baseline. Red Hat documents that many platform findings cannot be fixed automatically (for example, the allowed registries list depends on the organization), so few rules have a ready settings-only fix. Some cluster-setting fixes make the API server restart its pods, so expect the cluster to be briefly unreachable after you apply one.",
            "action": "Run the three commands. Copy one name from the last list for Test 4.",
            "checkpoint": "You see counts for each status and at least one safe remediation name. If the last list is empty, tell your instructor: the lab needs a rule with a settings-only fix.",
        },
        {
            "title": "Enforce least functionality with Kyverno (CM-7)",
            "why": "Write three policies. Together they block a container with node-level power, a container that may run as the root user (the all-powerful account), and the moving latest image tag. Each policy is scoped to the demo namespace and set to Enforce.",
            "blocks": [
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: kyverno.io/v1\n"
                        "kind: ClusterPolicy\n"
                        "metadata:\n"
                        "  name: disallow-privileged-containers\n"
                        "spec:\n"
                        "  background: true\n"
                        "  rules:\n"
                        "    - name: privileged-containers\n"
                        "      match:\n"
                        "        any:\n"
                        "          - resources:\n"
                        "              kinds:\n"
                        "                - Pod\n"
                        "              namespaces:\n"
                        "                - demo\n"
                        "      validate:\n"
                        "        failureAction: Enforce\n"
                        "        message: \"Privileged containers are not allowed.\"\n"
                        "        pattern:\n"
                        "          spec:\n"
                        "            =(ephemeralContainers):\n"
                        "              - =(securityContext):\n"
                        "                  =(privileged): \"false\"\n"
                        "            =(initContainers):\n"
                        "              - =(securityContext):\n"
                        "                  =(privileged): \"false\"\n"
                        "            containers:\n"
                        "              - =(securityContext):\n"
                        "                  =(privileged): \"false\"\n"
                        "---\n"
                        "apiVersion: kyverno.io/v1\n"
                        "kind: ClusterPolicy\n"
                        "metadata:\n"
                        "  name: require-run-as-nonroot\n"
                        "spec:\n"
                        "  background: true\n"
                        "  rules:\n"
                        "    - name: run-as-non-root\n"
                        "      match:\n"
                        "        any:\n"
                        "          - resources:\n"
                        "              kinds:\n"
                        "                - Pod\n"
                        "              namespaces:\n"
                        "                - demo\n"
                        "      validate:\n"
                        "        failureAction: Enforce\n"
                        "        message: \"Containers must be set to run as a non-root user.\"\n"
                        "        anyPattern:\n"
                        "          - spec:\n"
                        "              securityContext:\n"
                        "                runAsNonRoot: \"true\"\n"
                        "              =(ephemeralContainers):\n"
                        "                - =(securityContext):\n"
                        "                    =(runAsNonRoot): \"true\"\n"
                        "              =(initContainers):\n"
                        "                - =(securityContext):\n"
                        "                    =(runAsNonRoot): \"true\"\n"
                        "              containers:\n"
                        "                - =(securityContext):\n"
                        "                    =(runAsNonRoot): \"true\"\n"
                        "          - spec:\n"
                        "              =(ephemeralContainers):\n"
                        "                - securityContext:\n"
                        "                    runAsNonRoot: \"true\"\n"
                        "              =(initContainers):\n"
                        "                - securityContext:\n"
                        "                    runAsNonRoot: \"true\"\n"
                        "              containers:\n"
                        "                - securityContext:\n"
                        "                    runAsNonRoot: \"true\"\n"
                        "---\n"
                        "apiVersion: kyverno.io/v1\n"
                        "kind: ClusterPolicy\n"
                        "metadata:\n"
                        "  name: disallow-latest-tag\n"
                        "spec:\n"
                        "  background: true\n"
                        "  rules:\n"
                        "    - name: require-image-tag\n"
                        "      match:\n"
                        "        any:\n"
                        "          - resources:\n"
                        "              kinds:\n"
                        "                - Pod\n"
                        "              namespaces:\n"
                        "                - demo\n"
                        "      validate:\n"
                        "        failureAction: Enforce\n"
                        "        message: \"An image tag is required.\"\n"
                        "        foreach:\n"
                        "          - list: \"request.object.spec.containers\"\n"
                        "            pattern:\n"
                        "              image: \"*:*\"\n"
                        "          - list: \"request.object.spec.initContainers\"\n"
                        "            pattern:\n"
                        "              image: \"*:*\"\n"
                        "          - list: \"request.object.spec.ephemeralContainers\"\n"
                        "            pattern:\n"
                        "              image: \"*:*\"\n"
                        "    - name: block-latest-tag\n"
                        "      match:\n"
                        "        any:\n"
                        "          - resources:\n"
                        "              kinds:\n"
                        "                - Pod\n"
                        "              namespaces:\n"
                        "                - demo\n"
                        "      validate:\n"
                        "        failureAction: Enforce\n"
                        "        message: \"The latest tag is not allowed. Use a fixed version.\"\n"
                        "        foreach:\n"
                        "          - list: \"request.object.spec.containers\"\n"
                        "            pattern:\n"
                        "              image: \"!*:latest\"\n"
                        "          - list: \"request.object.spec.initContainers\"\n"
                        "            pattern:\n"
                        "              image: \"!*:latest\"\n"
                        "          - list: \"request.object.spec.ephemeralContainers\"\n"
                        "            pattern:\n"
                        "              image: \"!*:latest\""
                    ),
                    "lines": [
                        ("kind: ClusterPolicy", "A Kyverno policy that applies across the cluster."),
                        ("namespaces: demo", "Limits each rule to the demo namespace so the rest of the lab is untouched."),
                        ("failureAction: Enforce", "Refuse the request. Audit would only report it."),
                        ("=(securityContext): =(privileged): false", "If a security setting is present, privileged must be false. The =( ) marks an optional field."),
                        ("anyPattern", "Passes if either listed shape matches: the pod is set non-root as a whole, or every container is."),
                        ("foreach ... list", "Checks every container, init container and ephemeral container (a temporary debugging container) in the pod, not only the main ones."),
                        ("image: !*:latest", "Refuses any image whose name ends in :latest. The other rule refuses an image with no tag."),
                    ],
                },
                {
                    "code": (
                        "oc explain clusterpolicy.spec.rules.validate.failureAction\n"
                        "oc apply -f least-functionality.yaml --dry-run=server\n"
                        "oc apply -f least-functionality.yaml\n"
                        "oc get clusterpolicy"
                    ),
                    "lines": [
                        ("oc explain ...", "Prints the field your Kyverno release accepts. Older releases set the action at the top of the policy instead. Use what it shows."),
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc get clusterpolicy", "Lists the policies and whether each is ready."),
                    ],
                },
            ],
            "tip": "The organization-defined list of what is a mission-essential capability is set by the system owner. These three rules are the common starting set, not the whole list. A team that needs an exception asks for it, and the exception is recorded.",
            "action": "Save the YAML as least-functionality.yaml, validate it, apply it, and list the policies.",
            "checkpoint": "Three policies exist and each shows READY true.",
        },
        {
            "title": "Record the baseline (CM-2)",
            "why": "A baseline is only useful if you can say exactly what it is and see how it changed. The operator keeps the checklist content as a container image, and this lab pins it by digest (a fingerprint that identifies one exact version). The policy files go into git, which keeps every version.",
            "blocks": [
                {
                    "code": (
                        "oc get profile.compliance ocp4-stig -n openshift-compliance\n"
                        "oc get profilebundle ocp4 -n openshift-compliance -o jsonpath='{.spec.contentImage}{\"\\n\"}'\n"
                        "mkdir -p baseline\n"
                        "cp stig-scan.yaml least-functionality.yaml baseline/\n"
                        "cd baseline\n"
                        "git init\n"
                        "git add .\n"
                        "git -c user.name=learner -c user.email=learner@lab.internal commit -m \"Record hardening baseline\"\n"
                        "git log --oneline"
                    ),
                    "lines": [
                        ("oc get profile.compliance ocp4-stig", "Shows the checklist and its version."),
                        ("jsonpath='{.spec.contentImage}'", "Prints the image the checklist content comes from."),
                        ("git init, git add, git commit", "Starts a repository and saves the first version of both files."),
                        ("git log --oneline", "Shows the version history."),
                    ],
                }
            ],
            "note": "If the image shown ends in a tag instead of a digest, record that. Pinning the content by digest is an operations decision, and the lab does not change it.",
            "action": "Run the commands.",
            "checkpoint": "git log shows one commit, and you have the checklist version and content image on screen.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "The scan reports results",
            "why": "Count what the scan found. A scan that returns nothing proves nothing.",
            "code": (
                "oc get compliancecheckresults -n openshift-compliance -l compliance.openshift.io/suite=stig-scan -o json | jq -r '.items[].status' | sort | uniq -c\n"
                "oc get compliancesuite stig-scan -n openshift-compliance -o jsonpath='{.status.result}{\"\\n\"}'"
            ),
            "expect": (
                "Example only. Your counts will differ.\n"
                "     41 FAIL\n"
                "     12 MANUAL\n"
                "     58 PASS\n"
                "NON-COMPLIANT"
            ),
            "checkpoint": "There are both PASS and FAIL results, and the suite result is NON-COMPLIANT or COMPLIANT.",
        },
        {
            "kind": "positive",
            "title": "A policy-compliant pod runs",
            "why": "The policies must not block good workloads. This pod sets itself to non-root, drops extra capabilities, and uses the fixed tag from the demo-app deployment.",
            "lang": "bash",
            "code": (
                "DEMO_IMAGE=$(oc get deployment demo-app -n demo -o jsonpath='{.spec.template.spec.containers[0].image}')\n"
                "echo \"$DEMO_IMAGE\"\n"
                "cat policy-ok.yaml\n"
                "sed \"s|DEMO_IMAGE|$DEMO_IMAGE|\" policy-ok.yaml | oc apply -f -\n"
                "oc wait pod/policy-ok -n demo --for=condition=Ready --timeout=120s\n"
                "oc get pod policy-ok -n demo"
            ),
            "expect": (
                "Example only. First save this file as policy-ok.yaml:\n"
                "apiVersion: v1\n"
                "kind: Pod\n"
                "metadata:\n"
                "  name: policy-ok\n"
                "  namespace: demo\n"
                "spec:\n"
                "  securityContext:\n"
                "    runAsNonRoot: true\n"
                "    seccompProfile:\n"
                "      type: RuntimeDefault\n"
                "  containers:\n"
                "    - name: app\n"
                "      image: DEMO_IMAGE\n"
                "      securityContext:\n"
                "        allowPrivilegeEscalation: false\n"
                "        capabilities:\n"
                "          drop:\n"
                "            - ALL\n"
                "\n"
                "Then the run ends with:\n"
                "NAME        READY   STATUS    RESTARTS   AGE\n"
                "policy-ok   1/1     Running   0          15s"
            ),
            "checkpoint": "The pod is created and reaches Running. Nothing was refused.",
        },
        {
            "kind": "negative",
            "title": "Non-compliant pods are denied",
            "why": "Ask for what the policies forbid: a privileged container, the latest tag, and no non-root setting. Save the file below as bad-pods.yaml first. As cluster-admin you are allowed to ask for a privileged pod, so only the Kyverno policy stands in the way. That is the point.",
            "code": (
                "cat bad-pods.yaml\n"
                "sed \"s|DEMO_IMAGE|$DEMO_IMAGE|\" bad-pods.yaml | oc apply -f -\n"
                "oc get pods -n demo | grep bad-"
            ),
            "expect": (
                "Example only. Save this as bad-pods.yaml first (three pods in one file):\n"
                "apiVersion: v1\n"
                "kind: Pod\n"
                "metadata: { name: bad-privileged, namespace: demo }\n"
                "spec:\n"
                "  securityContext: { runAsNonRoot: true }\n"
                "  containers:\n"
                "    - { name: app, image: DEMO_IMAGE, securityContext: { privileged: true } }\n"
                "---\n"
                "apiVersion: v1\n"
                "kind: Pod\n"
                "metadata: { name: bad-latest, namespace: demo }\n"
                "spec:\n"
                "  securityContext: { runAsNonRoot: true }\n"
                "  containers:\n"
                "    - { name: app, image: \"registry.access.redhat.com/ubi9/ubi-minimal:latest\" }\n"
                "---\n"
                "apiVersion: v1\n"
                "kind: Pod\n"
                "metadata: { name: bad-root, namespace: demo }\n"
                "spec:\n"
                "  containers:\n"
                "    - { name: app, image: DEMO_IMAGE }\n"
                "\n"
                "Then the run prints one denial per pod and the last command prints nothing:\n"
                "Error from server: admission webhook \"validate.kyverno.svc-fail\" denied the request:\n"
                "resource Pod/demo/bad-privileged was blocked due to the following policies\n"
                "disallow-privileged-containers:\n"
                "  privileged-containers: 'validation error: Privileged containers are not allowed.'\n"
                "(similar messages for bad-latest and bad-root)"
            ),
            "checkpoint": "Each of the three pods is refused with the message from its policy, and no bad- pod exists afterwards.",
        },
        {
            "kind": "negative",
            "title": "A failing hardening rule stays failed until it is fixed",
            "why": "A scan result that never changes teaches nothing. Take the safe remediation name you copied in Step 3, show that its rule fails, apply the fix, scan again, and show that it passes. If the rule was already fixed by an earlier run, pick another name from the Step 3 list.",
            "code": (
                "FILTER='.items[] | select(.spec.current.object.kind != \"MachineConfig\") | .metadata.name'\n"
                "RULE=$(oc get complianceremediations -n openshift-compliance -o json | jq -r \"$FILTER\" | head -1)\n"
                "echo \"$RULE\"\n"
                "oc get compliancecheckresult \"$RULE\" -n openshift-compliance -o jsonpath='{.status}{\"\\n\"}'\n"
                "oc patch complianceremediation \"$RULE\" -n openshift-compliance --type merge -p '{\"spec\":{\"apply\":true}}'\n"
                "oc annotate compliancescans/ocp4-stig -n openshift-compliance compliance.openshift.io/rescan=\n"
                "oc wait compliancesuite/stig-scan -n openshift-compliance --for=jsonpath='{.status.phase}'=DONE --timeout=30m\n"
                "oc get compliancecheckresult \"$RULE\" -n openshift-compliance -o jsonpath='{.status}{\"\\n\"}'"
            ),
            "expect": (
                "Example only. The rule name will differ.\n"
                "ocp4-stig-example-rule\n"
                "FAIL\n"
                "complianceremediation.compliance.openshift.io/ocp4-stig-example-rule patched\n"
                "compliancescan.compliance.openshift.io/ocp4-stig annotated\n"
                "compliancesuite.compliance.openshift.io/stig-scan condition met\n"
                "PASS"
            ),
            "checkpoint": "The same rule reads FAIL before the fix and PASS after the rescan. If the wait finishes before the rescan starts, wait 2 minutes and run the last command again.",
        },
    ],
    "glossary": [
        ("STIG", "Security Technical Implementation Guide: a checklist of secure settings."),
        ("Compliance Operator", "The OpenShift add-on that scans against checklists."),
        ("ScanSettingBinding", "The object that connects profiles to scan settings and starts a scan."),
        ("Remediation", "A prepared fix for a failing rule."),
        ("Policy as code", "Security rules kept in files the cluster enforces."),
        ("Admission controller", "A gate that checks every create or change request."),
        ("Kyverno", "A free admission controller driven by YAML policies."),
        ("Namespace", "A named workspace in the cluster."),
        ("POA&M", "Plan of Action and Milestones: the tracked list of known weaknesses and the dates they will be fixed."),
        ("Digest", "A fingerprint that identifies one exact version of an image."),
    ],
    "next": "Next module: M04 FIPS Cryptography and Keys: whether the encryption itself is approved, and who holds the keys.",
}
