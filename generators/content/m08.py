"""M08: Vulnerability management (RA-5, SI-2, CA-5)."""

NIST = "nist-sp-800-53r5-full.md"
FEDRAMP = "fedramp-high-baseline.md"
SRG = "u-cloud-service-provider-v1r6-srg.md"

MODULE = {
    "id": "M08",
    "slug": "Vulnerabilities",
    "title": "Vulnerability Management",
    "draft": (
        "Commands follow the Trivy and Trivy Operator documentation but have not yet run in the lab. Report field names "
        "(for example report.summary.criticalCount) can differ between Trivy Operator releases, so Step 4 prints the summary "
        "before any filtering. The vulnerable and clean example images are public images chosen to show the two outcomes. "
        "Their findings change as the vulnerability database changes, so counts will differ from the examples. "
        "Registry listings on 2026-10-26 show both example tags exist (Docker Hub nginx 1.16 and the Chainguard static latest tag); not yet confirmed in the lab: that the lab shell can pull them (confirm with trivy image on each tag), "
        "that the lab shell has GNU date for date -d in Step 5 (confirm with date -d tomorrow +%F), and that the operator has "
        "its cluster RBAC assessment scanner enabled (confirm with oc get clusterrbacassessmentreports). The lab "
        "starts the fix clock on the day the scan found the flaw."
    ),
    "controls": ["RA-5", "SI-2", "CA-5"],
    "mentions": ["CM-6", "SI-4"],
    "unit_values_ok": ["2 minutes", "5 minutes", "15 days"],
    "minutes": {"hands_on": 45, "verify": 25},
    "tools": [
        "OpenShift Container Platform",
        "Trivy and Trivy Operator (free, open source)",
        "oc",
        "jq",
    ],
    "diagrams": [
        {
            "id": "flow",
            "title": "From a scan finding to a tracked deadline",
            "caption": "You scan an old image by hand, then run it in the cluster so the operator scans it too. You read the operator's report and record one serious finding as a plan-of-action item with a due date. Each step below adds one part, drawn with thick lines.",
            "per_step": True,
            "rankdir": "TB",
            "step_notes": {
                1: "Nothing is new yet. You confirm the scanner in your lab shell and the Trivy Operator in the cluster.",
                2: "The Trivy command scans the old image and saves the findings to a file.",
                3: "The old image runs in the vuln-lab project, and the operator scans it and writes a vulnerability report.",
                4: "You read the report by severity and note which findings have no fix.",
                5: "One serious finding becomes a plan-of-action item in security-tools, with a due date set by its severity.",
            },
            "zones": [
                {"id": "shell", "label": "Your lab shell", "kind": "boundary"},
                {"id": "registry", "label": "Image registry", "kind": "boundary"},
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "tools", "label": "Project security-tools", "parent": "cluster", "kind": "group"},
                {"id": "vuln", "label": "Project vuln-lab", "parent": "cluster", "kind": "group"},
            ],
            "nodes": [
                {"id": "trivy", "title": "Trivy command", "sub": "Scans one image", "zone": "shell"},
                {"id": "file", "title": "Findings file", "sub": "File vuln-image.json", "zone": "shell", "s": 2},
                {"id": "oc", "title": "Cluster and JSON tools", "sub": "You read results here", "zone": "shell"},
                {"id": "img", "title": "Old web server image", "sub": "Known to have flaws", "zone": "registry", "kind": "bad"},
                {"id": "op", "title": "Trivy Operator", "sub": "Scans running workloads", "zone": "tools", "kind": "ok"},
                {"id": "poam", "title": "Plan-of-action item", "sub": "ConfigMap with a due date", "zone": "tools", "kind": "warn", "s": 5},
                {"id": "dep", "title": "Workload vuln-demo", "sub": "Runs the old image", "zone": "vuln", "kind": "bad", "s": 3},
                {"id": "rep", "title": "Vulnerability report", "sub": "Counts per severity", "zone": "vuln", "s": 3},
            ],
            "edges": [
                {"a": "trivy", "b": "img", "n": 1, "label": "Scans", "s": 2},
                {"a": "trivy", "b": "file", "label": "Saves", "flat": True, "s": 2},
                {"a": "img", "b": "dep", "n": 2, "label": "Runs as", "s": 3},
                {"a": "op", "b": "dep", "n": 3, "label": "Scans", "s": 3},
                {"a": "dep", "b": "rep", "label": "Gets", "flat": True, "s": 3},
                {"a": "oc", "b": "rep", "n": 4, "label": "Reads", "s": 4},
                {"a": "oc", "b": "poam", "n": 5, "label": "Creates", "kind": "warn", "s": 5},
            ],
            "reading": [
                "The Trivy command scans the old image and saves the findings to a file (flow 1).",
                "The old image runs as the vuln-demo workload in the vuln-lab project (flow 2).",
                "The Trivy Operator in security-tools scans the workload and writes a vulnerability report (flow 3).",
                "You read the report by severity with oc and jq (flow 4).",
                "You record one serious finding as a plan-of-action item in security-tools, with a due date from its severity (flow 5).",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)"],
    "lab_needs": [
        "Trivy Operator running in security-tools and set to scan the vuln-lab namespace; it must be able to fetch the vulnerability database or use a mirror the lab provides.",
        "The lab shell can pull docker.io/library/nginx:1.16 and cgr.dev/chainguard/static:latest, or the lab mirrors them and the module is updated with the mirror names.",
    ],
    "lab": {
        "start": "lab start m08",
        "env": [],
        "checks": [
            "The Trivy command-line scan of the old image reports findings and fails the gate.",
            "Trivy Operator lists a vulnerability report for the old image in the cluster.",
            "A plan-of-action item exists in security-tools with a due date, and none is overdue.",
            "The clean image scans with zero HIGH or CRITICAL findings and passes the gate.",
            "The plan-of-action item can be marked closed.",
        ],
    },
    "requirement": (
        "An IL5 system must look for known security flaws on a regular basis, rank what it finds, fix each flaw inside a "
        "set time, and keep a written plan for any flaw it cannot fix in time. This module uses Trivy to find flaws in "
        "container images and in the cluster, reads the findings by severity, compares them with the fix deadlines, and "
        "records an unfixed flaw as a plan-of-action item inside the cluster."
    ),
    "mapping": [
        {
            "control": "RA-5 Vulnerability Monitoring and Scanning",
            "plain": "Scan on a schedule, analyze the results, and fix findings within set response times.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Steps 2 to 4 scan and read findings. Tests 1 and 2 prove a known flaw is found.",
            "cite": [
                {"file": NIST, "quote": "Analyze vulnerability scan reports and results from vulnerability monitoring"},
                {"file": NIST, "quote": "in accordance with an organizational assessment of risk"},
                {"file": NIST, "quote": "Remediate legitimate vulnerabilities [Assignment: organization-defined response times]"},
                {"file": SRG, "quote": "CSPs must mitigate High and Critical risk findings within 30 days and Moderate findings within 90 days."},
                {"file": FEDRAMP, "quote": "low risk vulnerabilities mitigated within one hundred and eighty (180) days from date of discovery"},
            ],
        },
        {
            "control": "SI-2 Flaw Remediation",
            "plain": "Identify and report flaws, test the fix, install it within a set time, and use change control.",
            "source": "NIST",
            "covered": "Step 5 sets a due date from the severity. Test 4 shows what a remediated image looks like (it scans clean). Testing a fix before install and change control are part of the requirement and are not exercised in this lab. NIST leaves the install time to the organization; the lab sets it by severity.",
            "cite": [
                {"file": NIST, "quote": "Test software and firmware updates related to flaw remediation for effectiveness and potential side effects before installation"},
                {"file": NIST, "quote": "Install security-relevant software and firmware updates within"},
                {"file": NIST, "quote": "Incorporate flaw remediation into the organizational configuration management process."},
            ],
        },
        {
            "control": "CA-5 Plan of Action and Milestones",
            "plain": "Keep a tracked plan for each known weakness, with the cause, the steps and the dates, and keep it current.",
            "source": "NIST; DoD SRG",
            "covered": "Step 5 creates a plan-of-action item. Test 3 lists it and checks for overdue items.",
            "cite": [
                {"file": NIST, "quote": "Develop a plan of action and milestones for the system to document the planned remediation actions"},
                {"file": NIST, "quote": "Update existing plan of action and milestones [Assignment: organization-defined frequency]"},
                {"file": SRG, "quote": "DRs must be tracked in the POA&M to ensure risk awareness and facilitate resolution tracking."},
            ],
        },
    ],
    "intent": [
        {
            "control": "RA-5 Vulnerability Monitoring and Scanning",
            "feared": "A known flaw sits in a running component for months because nobody looked, or somebody looked and nobody read the result.",
            "scope": "The system and the applications it hosts, including every container image that runs on the platform.",
            "question": "If a serious flaw was published this morning, would we find out which running images contain it, and how soon?",
            "evidence": "Scan reports with dates, the list of what was scanned, and the findings sorted by severity.",
            "sufficient": "Scans run on a defined schedule and when new flaws are published, the results are analyzed and not just stored, and findings are fixed within set response times. NIST leaves the scan frequency to the organization and FedRAMP High sets it to monthly. This lab scans on demand with Trivy and lets the operator rescan on a schedule it keeps.",
            "tieoff": "Someone reads each report and assigns every serious finding to an owner.",
            "tool": "Trivy finds the flaws (Step 2). Trivy Operator keeps a report for every running workload (Step 3) and Step 4 reads them by severity.",
        },
        {
            "control": "SI-2 Flaw Remediation",
            "feared": "A fix exists but is never installed, or is installed untested and breaks the system.",
            "scope": "Software and firmware in everything the team operates. Images the team builds are theirs to rebuild.",
            "question": "For each finding, is there a fix, who is applying it, and by what date?",
            "evidence": "The finding, its severity, the date found, the fix version, the deadline, and the date it was closed.",
            "sufficient": "Updates are tested before installation, installed within the set time for their severity, and go through change management. NIST leaves the install time to the organization, and FedRAMP High sets it to within 30 days of the release of the updates. This lab sets the times by severity and leaves Low and Informational to the system owner or their designee.",
            "tieoff": "Someone checks whether deadlines are being met and tells the owner when one is close.",
            "tool": "Step 5 turns a severity into a due date from the severity table. Test 4 shows what a remediated image looks like: no serious findings.",
        },
        {
            "control": "CA-5 Plan of Action and Milestones",
            "feared": "A flaw that cannot be fixed in time simply disappears from view, and the people who accept the risk never see it.",
            "scope": "Every known weakness in the system that is not yet fixed.",
            "question": "For each flaw we have not fixed, where is the plan, who owns it, and when is it due?",
            "evidence": "One tracked item per open weakness, with cause, steps, dates and status, reviewed on a schedule.",
            "sufficient": "Each open weakness has an entry showing the vulnerability, its root cause and its milestones, and entries are updated until they are closed or a risk acceptance is approved. NIST leaves the update frequency to the organization and FedRAMP High sets it to at least monthly; this lab reviews entries quarterly, which is less often than FedRAMP High allows. The DoD SRG says deviation requests must be tracked in the plan.",
            "tieoff": "Someone reviews the open items on the review schedule and closes the ones that are done.",
            "tool": "A labeled ConfigMap (a small stored record in the cluster) holds each item (Step 5), and one query lists the open and overdue ones (Test 3). The lab keeps the record in the cluster so you practice the fields. The official record is kept in the organization's system of record.",
        },
    ],
    "architect": (
        "Decide what gets scanned (images before they run, images while they run, the cluster settings), how often, who reads "
        "the result, which severities have which deadlines, and how an item that misses its deadline becomes a tracked plan. "
        "Then build it and run the tests."
    ),
    "terms": [
        ("Vulnerability", "A flaw in software that an attacker could use."),
        ("CVE", "Common Vulnerabilities and Exposures: a public ID, such as CVE-2024-0001, for one known flaw."),
        ("Severity", "How serious a flaw is: CRITICAL, HIGH, MEDIUM or LOW."),
        ("Container image", "The packaged files a container starts from: a program and the pieces it needs."),
        ("Trivy", "A free, open source scanner that compares what is inside an image or cluster with a database of known flaws."),
        ("Trivy Operator", "A program that runs Trivy inside the cluster for you and saves each result as a report object."),
        ("Fixed version", "The first version of a package in which a flaw is repaired. Empty means no fix is published yet."),
        ("POA&M", "Plan of Action and Milestones: the tracked record of a known weakness, its cause, its steps and its dates."),
        ("ConfigMap", "A small named record stored in the cluster. Labels on it let you search for groups of records."),
    ],
    "concepts": [
        {
            "heading": "8.1 What a scan finds",
            "paras": [
                "What is this? Software is built from many smaller packages, and researchers publish flaws found in them. A scanner lists what is inside an image, looks each package up in a database of those published flaws, and reports the matches.",
                "Why? You cannot fix what you cannot see, and the list changes every day. An image that was clean last month can have a serious finding today without a single byte changing, because new flaws are published about old packages.",
            ],
            "table": {
                "headers": ["Field", "What it tells you", "What you do with it"],
                "rows": [
                    ("CVE ID", "Which flaw", "Look up details, search for it in other images"),
                    ("Package and installed version", "Where the flaw lives", "Find the owner of that package"),
                    ("Severity", "How serious it is", "Choose the deadline"),
                    ("Fixed version", "The first repaired version, or empty", "Rebuild with it, or start a plan-of-action item if empty"),
                ],
            },
        },
        {
            "heading": "8.2 Trivy two ways",
            "paras": [
                "The trivy command scans one image on demand, which is useful for a quick check and for a pass or fail gate (a check that stops a release when the scan finds something serious). Trivy Operator scans everything that runs in the cluster and keeps one report object for each workload, which is useful for reading the whole cluster at once. They use the same database, so they agree.",
            ],
            "diagram": (
                "Image  --trivy image-->  findings in your terminal  (gate: exit code 1 if serious findings)\n"
                "\n"
                "Workload starts  -->  Trivy Operator scans it  -->  VulnerabilityReport object  -->  you read it with oc\n"
                "Cluster objects  -->  Trivy Operator audits them -->  ConfigAuditReport, RBAC reports"
            ),
        },
        {
            "heading": "8.3 Fix deadlines come from the sources",
            "paras": [
                "NIST leaves the response time to the organization (RA-5 and SI-2), and the DoD SRG assigns its own for cloud providers: High and Critical within 30 days and Moderate within 90 days. FedRAMP High assigns 30 days for high-risk, 90 days for moderate-risk and 180 days for low-risk vulnerabilities, counted from the date of discovery, and says a date in the CISA Known Exploited Vulnerabilities catalog replaces that value. Trivy calls the middle level MEDIUM where others say Medium or Moderate. The lab chooses the values shown in the lab column, and Step 5 uses them.",
            ],
            "table": {
                "headers": ["Severity", "This lab (RA-5 and SI-2)", "DoD SRG (cloud providers)"],
                "rows": [
                    ("Critical", "15 days", "30 days (High and Critical together)"),
                    ("High", "30 days", "30 days (High and Critical together)"),
                    ("Medium or Moderate", "90 days", "90 days"),
                    ("Low", "Set by the system owner or their designee", "Aligned with FedRAMP guidance (180 days in FedRAMP High)"),
                ],
            },
        },
        {
            "heading": "8.4 What goes in a plan-of-action item",
            "paras": [
                "When a flaw cannot be fixed by its deadline, for example because no fixed version exists yet, it becomes a plan-of-action item. Each entry in this lab names the vulnerability, its root cause, its milestones and a completion date. In this lab each item is a ConfigMap with a poam label, so one query lists them all.",
            ],
            "production": "In the real environment the official POA&M lives in the organization's system of record, with approvals and reviews on a schedule. The cluster record in this lab teaches the fields and the habit of checking for overdue items.",
        },
    ],
    "steps": [
        {
            "title": "Check what you have",
            "why": "Confirm the scanner program and the Trivy Operator are present before scanning anything.",
            "blocks": [
                {
                    "code": (
                        "trivy --version\n"
                        "oc get pods -n security-tools | grep trivy\n"
                        "oc get crd | grep aquasecurity"
                    ),
                    "lines": [
                        ("trivy --version", "Prints the version of the scanner in your lab shell."),
                        ("oc get pods -n security-tools | grep trivy", "Shows the Trivy Operator program running in the cluster."),
                        ("oc get crd | grep aquasecurity", "Lists the report types the operator added (a crd is a new kind of object added to the cluster)."),
                    ],
                }
            ],
            "action": "Run the commands.",
            "checkpoint": "You see a Trivy version, a Running operator pod, and report types such as vulnerabilityreports.",
        },
        {
            "title": "Scan a known-vulnerable image (RA-5)",
            "why": "Start with an old image that is known to contain flaws. The first scan downloads the vulnerability database, so it can take a few minutes. The results go to a file so you can read them several ways.",
            "blocks": [
                {
                    "code": (
                        "VULN_IMAGE=docker.io/library/nginx:1.16\n"
                        "trivy image --scanners vuln --severity HIGH,CRITICAL --quiet --format json --output vuln-image.json \"$VULN_IMAGE\"\n"
                        "jq '[.Results[]?.Vulnerabilities[]?] | length' vuln-image.json\n"
                        "jq -r '[.Results[]?.Vulnerabilities[]? | .Severity] | group_by(.) | map([.[0], length]) | .[] | @tsv' vuln-image.json\n"
                        "jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity==\"CRITICAL\") | [.VulnerabilityID, .PkgName, .InstalledVersion, .FixedVersion] | @tsv' vuln-image.json | head -10"
                    ),
                    "lines": [
                        ("VULN_IMAGE=...", "Stores the image name in a variable so later commands reuse it."),
                        ("trivy image --scanners vuln", "Scans the image for known flaws only."),
                        ("--severity HIGH,CRITICAL", "Keeps only the two most serious levels."),
                        ("--format json --output vuln-image.json", "Saves the result as a JSON file."),
                        ("jq ... | length", "Counts the findings."),
                        ("group_by(.) ... @tsv", "Counts findings per severity."),
                        ("select(.Severity==CRITICAL)", "Lists the critical ones: ID, package, installed version, fixed version. An empty last column means no fix is published."),
                    ],
                }
            ],
            "action": "Run the commands and note how many findings there are and how many have an empty fixed version.",
            "checkpoint": "The count is greater than zero and the severity list shows HIGH and CRITICAL rows.",
        },
        {
            "title": "Run the image in the cluster and let the operator scan it (RA-5)",
            "why": "A scan you run by hand only covers what you remember to scan. Trivy Operator scans every workload as it starts. Start the old image in its own project (a named workspace in the cluster) and wait for the report. The command sleep keeps the container alive without starting the web server.",
            "blocks": [
                {
                    "code": (
                        "oc new-project vuln-lab\n"
                        "oc create deployment vuln-demo --image=\"$VULN_IMAGE\" -n vuln-lab -- sleep 3600\n"
                        "oc rollout status deployment/vuln-demo -n vuln-lab --timeout=300s\n"
                        "sleep 120\n"
                        "oc get vulnerabilityreports -n vuln-lab -o wide"
                    ),
                    "lines": [
                        ("oc new-project vuln-lab", "Creates the workspace."),
                        ("oc create deployment ... -- sleep 3600", "Starts the old image and keeps it running for an hour."),
                        ("oc rollout status", "Waits until the pod is up."),
                        ("sleep 120", "Gives the operator time to scan."),
                        ("oc get vulnerabilityreports ... -o wide", "Lists the report with a count per severity. If the list is empty, wait 2 minutes and run it again."),
                    ],
                }
            ],
            "action": "Run the commands.",
            "checkpoint": "One report appears for the vuln-demo workload with counts in the CRITICAL and HIGH columns.",
        },
        {
            "title": "Read the findings by severity and look at the cluster itself (RA-5)",
            "why": "Analyzing the results means reading them: which severities, which packages, which have a fix. The operator also audits the cluster's own configuration and access rules, and saves those results the same way.",
            "blocks": [
                {
                    "code": (
                        "REPORT=$(oc get vulnerabilityreports -n vuln-lab -o jsonpath='{.items[0].metadata.name}')\n"
                        "oc get vulnerabilityreport \"$REPORT\" -n vuln-lab -o json | jq '.report.summary'\n"
                        "oc get vulnerabilityreport \"$REPORT\" -n vuln-lab -o json | jq -r '.report.vulnerabilities[] | select(.severity==\"CRITICAL\") | [.vulnerabilityID, .resource, .installedVersion, .fixedVersion] | @tsv' | head -10\n"
                        "oc get configauditreports -n vuln-lab -o wide\n"
                        "oc get clusterrbacassessmentreports -o wide | head -10"
                    ),
                    "lines": [
                        ("REPORT=$(...)", "Stores the name of the report you just found."),
                        ("jq '.report.summary'", "Prints the counts per severity. Check the field names here before filtering."),
                        ("select(.severity==CRITICAL)", "Lists the critical findings with their fix versions."),
                        ("oc get configauditreports", "Lists settings problems found in the workload's configuration."),
                        ("oc get clusterrbacassessmentreports", "Lists problems in who is allowed to do what across the cluster."),
                    ],
                }
            ],
            "note": "A finding with an empty fixed version cannot be repaired by updating yet. Those are the ones that become plan-of-action items in the next step.",
            "action": "Run the commands. Choose the findings with the highest severity and note which have no fix.",
            "checkpoint": "You can say how many CRITICAL and HIGH findings the image has and how many have no fix.",
        },
        {
            "title": "Set the deadline and track it as a plan-of-action item (SI-2, CA-5)",
            "why": "Pick one HIGH or CRITICAL finding, preferring one with no fix. Its severity sets the deadline from this lab's table: 15 days for Critical and 30 days for High. Then record it as a ConfigMap labeled poam=open with these fields: the vulnerability, its root cause, the milestone, and the dates. No document is written.",
            "blocks": [
                {
                    "code": (
                        "PICK='[.report.vulnerabilities[] | select(.severity==\"HIGH\" or .severity==\"CRITICAL\")] | sort_by((.fixedVersion // \"\") != \"\") | .[0] | [.vulnerabilityID, .severity, .resource, .installedVersion] | @tsv'\n"
                        "ITEM=$(oc get vulnerabilityreport \"$REPORT\" -n vuln-lab -o json | jq -r \"$PICK\")\n"
                        "CVE=$(echo \"$ITEM\" | cut -f1)\n"
                        "SEV=$(echo \"$ITEM\" | cut -f2)\n"
                        "PKG=$(echo \"$ITEM\" | cut -f3)\n"
                        "VER=$(echo \"$ITEM\" | cut -f4)\n"
                        "test \"$SEV\" = CRITICAL && WINDOW=15 || WINDOW=30\n"
                        "TODAY=$(date -u +%F)\n"
                        "DUE=$(date -u -d \"+${WINDOW} days\" +%F)\n"
                        "echo \"$CVE $SEV $PKG $VER due $DUE\""
                    ),
                    "lines": [
                        ("PICK=... sort_by(.fixedVersion != ...)", "Picks one serious finding, putting the ones with no fix first."),
                        ("cut -f1 ... cut -f4", "Splits the line into ID, severity, package and version."),
                        ("test ... && WINDOW=15 || WINDOW=30", "Uses the lab window: 15 for Critical, 30 for High."),
                        ("date -u -d ... +%F", "Works out today and the due date as year-month-day, in UTC."),
                    ],
                },
                {
                    "code": (
                        "NAME=\"poam-$(echo \"$CVE\" | tr 'A-Z' 'a-z')\"\n"
                        "oc create configmap \"$NAME\" -n security-tools \\\n"
                        "  --from-literal=finding=\"$CVE\" \\\n"
                        "  --from-literal=severity=\"$SEV\" \\\n"
                        "  --from-literal=component=\"$PKG\" \\\n"
                        "  --from-literal=installed-version=\"$VER\" \\\n"
                        "  --from-literal=root-cause=\"Vulnerable package in the base image\" \\\n"
                        "  --from-literal=milestone=\"Rebuild on a patched base image and redeploy\" \\\n"
                        "  --from-literal=identified=\"$TODAY\" \\\n"
                        "  --from-literal=due=\"$DUE\" \\\n"
                        "  --from-literal=status=open\n"
                        "oc label configmap \"$NAME\" -n security-tools poam=open\n"
                        "oc get configmap \"$NAME\" -n security-tools -o jsonpath='{.data}{\"\\n\"}'"
                    ),
                    "lines": [
                        ("NAME=poam-...", "Builds a record name from the CVE ID, in lower case because names must be."),
                        ("oc create configmap --from-literal=...", "Stores one field per line: finding, severity, component, root cause, milestone, dates."),
                        ("oc label ... poam=open", "Adds the label that lets one query find every open item."),
                        ("oc get configmap -o jsonpath", "Prints the stored fields so you can check them."),
                    ],
                },
            ],
            "tip": "This lab reviews plan-of-action items quarterly, and individual items are updated until closure or an approved risk acceptance. Any change to an item (new milestone, new date) is an edit to this record, so keep the history by editing, not by deleting and recreating.",
            "action": "Run both blocks, then read the printed fields.",
            "checkpoint": "The ConfigMap exists in security-tools with a poam=open label, a due date, and all nine fields.",
        },
    ],
    "verify": [
        {
            "kind": "negative",
            "title": "The scan finds the known-vulnerable image and fails the gate",
            "why": "A gate that never fails proves nothing. Run the scan with an exit code (a number a command returns: zero means success, anything else means failure) so a pipeline could stop on it.",
            "code": (
                "trivy image --scanners vuln --severity CRITICAL --quiet --exit-code 1 --format json --output gate.json \"$VULN_IMAGE\"\n"
                "echo \"exit code: $?\"\n"
                "jq '[.Results[]?.Vulnerabilities[]?] | length' gate.json\n"
                "jq -r '.Results[]?.Vulnerabilities[]? | [.VulnerabilityID, .PkgName, .Severity] | @tsv' gate.json | head -5"
            ),
            "expect": (
                "Example only. Your IDs and counts will differ.\n"
                "exit code: 1\n"
                "27\n"
                "CVE-2019-XXXX\tlibexample\tCRITICAL\n"
                "CVE-2020-XXXX\tlibsample\tCRITICAL"
            ),
            "checkpoint": "The exit code is 1, the count is greater than zero, and the first findings are listed with their severity.",
        },
        {
            "kind": "positive",
            "title": "The operator lists the same finding in the cluster",
            "why": "The cluster should know about the flaw without you scanning by hand. Read the operator's report for the running workload.",
            "code": (
                "oc get vulnerabilityreports -n vuln-lab -o wide\n"
                "oc get vulnerabilityreport \"$REPORT\" -n vuln-lab -o json | jq '.report.summary.criticalCount + .report.summary.highCount'"
            ),
            "expect": (
                "Example only.\n"
                "NAME                              REPOSITORY      TAG    SCANNER   AGE   CRITICAL   HIGH   MEDIUM   LOW   UNKNOWN\n"
                "replicaset-vuln-demo-6d9f7c8b-nginx   library/nginx   1.16   Trivy     6m    27         92     120      80    0\n"
                "119"
            ),
            "checkpoint": "A report exists for the old image and the combined CRITICAL and HIGH number is greater than zero.",
        },
        {
            "kind": "positive",
            "title": "The plan-of-action item is listed and nothing is overdue",
            "why": "Tracking only works if you can ask two questions quickly: what is open, and what has passed its date.",
            "code": (
                "oc get configmap -n security-tools -l poam=open -o json | jq -r '.items[] | [.metadata.name, .data.severity, .data.due] | @tsv'\n"
                "TODAY=$(date -u +%F)\n"
                "oc get configmap -n security-tools -l poam=open -o json | jq -r --arg today \"$TODAY\" '.items[] | select(.data.due < $today) | .metadata.name'"
            ),
            "expect": (
                "Example only.\n"
                "poam-cve-2019-xxxx\tHIGH\t2026-11-25\n"
                "(the second query prints nothing)"
            ),
            "checkpoint": "Your item appears in the first list, and the second list is empty because the due date has not passed.",
        },
        {
            "kind": "positive",
            "title": "A minimal, patched image scans clean and passes the gate",
            "why": "The other side of the test: an image with no serious findings must pass. This image stands in for a rebuilt, patched version of your workload. This minimal image contains almost no packages, so there is almost nothing to be flawed. If the gate failed here too, it would be noise rather than a control.",
            "code": (
                "CLEAN_IMAGE=cgr.dev/chainguard/static:latest\n"
                "trivy image --scanners vuln --severity HIGH,CRITICAL --quiet --exit-code 1 --format json --output clean.json \"$CLEAN_IMAGE\"\n"
                "echo \"exit code: $?\"\n"
                "jq '[.Results[]?.Vulnerabilities[]?] | length' clean.json"
            ),
            "expect": (
                "Example only. A new flaw published tomorrow can change this result, which is why the scan repeats.\n"
                "exit code: 0\n"
                "0"
            ),
            "checkpoint": "The exit code is 0 and the count is 0. If either differs, read the findings: that is the control working.",
        },
        {
            "kind": "positive",
            "title": "Close the item once the fix is in",
            "why": "An item that never closes becomes noise. When the fix is in and the new image scans clean, mark the item closed and record the date.",
            "code": (
                "oc label configmap \"$NAME\" -n security-tools poam=closed --overwrite\n"
                "oc annotate configmap \"$NAME\" -n security-tools closed-on=\"$TODAY\" --overwrite\n"
                "oc get configmap -n security-tools -l poam=open --no-headers | wc -l"
            ),
            "expect": (
                "Example only.\n"
                "configmap/poam-cve-2019-xxxx labeled\n"
                "configmap/poam-cve-2019-xxxx annotated\n"
                "0"
            ),
            "checkpoint": "The open list no longer shows the item, and the item still exists with a closed label and a closing date.",
        },
    ],
    "glossary": [
        ("Vulnerability", "A flaw in software that an attacker could use."),
        ("CVE", "Common Vulnerabilities and Exposures: a public ID for one known flaw."),
        ("Severity", "How serious a flaw is."),
        ("Exit code", "A number a command returns when it ends: zero means success."),
        ("Gate", "A check that stops a release when it fails."),
        ("Trivy Operator", "The program that scans workloads inside the cluster."),
        ("POA&M", "Plan of Action and Milestones: the tracked record of a known weakness."),
        ("ConfigMap", "A small named record stored in the cluster."),
        ("Label", "A key=value tag on an object that lets you search for groups of objects."),
        ("Project (OpenShift)", "A named workspace in the cluster."),
    ],
    "next": "Next module: M05 Identity and Multi-Factor Sign-In: who may sign in, how they prove who they are, and what happens after failed attempts.",
}
