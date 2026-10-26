"""SIEM-1: Collect audit logs. Pilot module for the data-driven format."""

FEDRAMP_HIGH = "fedramp-high-baseline.md"
NIST = "nist-sp-800-53r5-full.md"

MODULE = {
    "id": "SIEM-1",
    "slug": "Collect",
    "title": "Collect Audit Logs",
    "draft": "Commands follow Red Hat's published OpenShift Logging documentation but have not yet run in the lab. Field names can differ between Logging releases, so the forwarder is validated before it is applied.",
    "controls": ["AU-2", "AU-3", "AU-8", "AU-12"],
    "mentions": ["CM-3", "CM-5", "SC-8", "AU-5", "AU-6", "AU-9", "AU-11", "SI-4"],
    "unit_values_ok": ["30 seconds", "60 seconds"],
    "minutes": {"hands_on": 45, "verify": 20},
    "tools": ["OpenShift Container Platform", "Red Hat OpenShift Logging", "Loki and Grafana (free, open source)", "oc", "curl", "jq"],
    "diagrams": [
        {
            "id": "flow",
            "title": "Where the three kinds of log travel",
            "caption": "Every node produces three kinds of log. The collector reads all three, stamps each record with the node clock, and sends them to Loki. You search them in Grafana. Each step below adds one part, drawn with thick lines.",
            "per_step": True,
            "rankdir": "TB",
            "step_notes": {
                1: "Nothing is new yet. This is what the lab starts with: three kinds of log, a node clock, Loki and Grafana, and nothing connecting them.",
                2: "The collector gets its own limited identity, allowed to read the three kinds of log and nothing else.",
                3: "The ClusterLogForwarder starts the collector. It reads all three log types and sends them to Loki.",
                4: "You search Loki from Grafana to confirm each log type arrived.",
            },
            "zones": [
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "node", "label": "On every node", "parent": "cluster", "kind": "group"},
                {"id": "logging", "label": "Project openshift-logging", "parent": "cluster", "kind": "group"},
                {"id": "siem", "label": "Project siem", "parent": "cluster", "kind": "group"},
            ],
            "nodes": [
                {"id": "audit", "title": "Audit logs", "sub": "Who asked the API to do what", "zone": "node"},
                {"id": "infra", "title": "Infrastructure logs", "sub": "The cluster's own parts", "zone": "node"},
                {"id": "app", "title": "Application logs", "sub": "Your workloads", "zone": "node"},
                {"id": "clock", "title": "Node clock", "sub": "Sets every timestamp", "zone": "node", "kind": "warn"},
                {"id": "sa", "title": "Collector identity", "sub": "Limited permissions", "zone": "logging", "kind": "warn", "s": 2},
                {"id": "fwd", "title": "Collector", "sub": "ClusterLogForwarder", "zone": "logging", "kind": "ok", "s": 3},
                {"id": "loki", "title": "Loki", "sub": "Stores and indexes", "zone": "siem", "kind": "ok"},
                {"id": "graf", "title": "Grafana", "sub": "You search here", "zone": "siem"},
            ],
            "edges": [
                {"a": "audit", "b": "fwd", "n": 1, "label": "Read", "s": 3},
                {"a": "infra", "b": "fwd", "n": 1, "label": "Read", "s": 3},
                {"a": "app", "b": "fwd", "n": 1, "label": "Read", "s": 3},
                {"a": "clock", "b": "fwd", "label": "Time", "kind": "warn", "s": 3},
                {"a": "sa", "b": "fwd", "label": "Runs as", "flat": True, "s": 3},
                {"a": "fwd", "b": "loki", "n": 2, "label": "Send", "kind": "ok", "s": 3},
                {"a": "loki", "b": "graf", "n": 3, "label": "Query", "kind": "ok", "flat": True, "s": 4},
            ],
            "reading": [
                "Audit, infrastructure and application logs all flow into the collector (flow 1).",
                "The node clock sets the timestamp on each record before it is sent.",
                "The collector in the openshift-logging project sends everything to Loki in the siem project (flow 2).",
                "You search the stored logs from Grafana (flow 3).",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)"],
    "lab": {
        "start": "lab start siem-1",
        "env": ["LOKI_URL", "LOKI_CA_FILE", "LOKI_USER", "LOKI_PASSWORD"],
        "checks": [
            "A collector pod is running on every node.",
            "A test audit record reaches Loki and contains the six AU-3 elements.",
            "Node clocks are synchronized and stored timestamps show fractions of a second and a UTC marker.",
            "Removing the audit permission stops audit records, and restoring it brings them back.",
        ],
    },
    "requirement": (
        "An IL5 system must record security-relevant events, put enough detail in each record to "
        "reconstruct what happened, stamp each record with a trustworthy time, and make sure every "
        "required component is actually producing records. This module builds that foundation. "
        "Later modules store the records, search them for attacks, and respond."
    ),
    "mapping": [
        {
            "control": "AU-2 Event Logging",
            "plain": "Decide which events must be logged, say why, and review the list on a schedule.",
            "source": "NIST; FedRAMP",
            "covered": "Steps 3 and 4 send the three log types and confirm each one arrives.",
            "cite": [
                {"file": NIST, "quote": "Identify the types of events that the system is capable of logging in support of the audit"},
                {"file": FEDRAMP_HIGH, "quote": "AU-2 (c) [organization-defined subset of the auditable events defined in AU-2a to be audited continually for each identified event]."},
            ],
        },
        {
            "control": "AU-3 Content of Audit Records",
            "plain": "Each record says what happened, when, where, the source, the outcome, and who or what was involved.",
            "source": "NIST; FedRAMP",
            "covered": "Test 1 checks a real record against all six elements.",
            "cite": [
                {"file": NIST, "quote": "Identity of any individuals, subjects, or objects/entities associated with the event"},
                {"file": FEDRAMP_HIGH, "quote": "Identity of any individuals, subjects, or objects/entities associated with the event"},
            ],
        },
        {
            "control": "AU-8 Time Stamps",
            "plain": "Records use the system clock and a standard time reference (UTC, or a fixed offset).",
            "source": "NIST; FedRAMP",
            "covered": "Test 2 checks clock synchronization and the stored timestamp format.",
            "cite": [
                {"file": NIST, "quote": "Use internal system clocks to generate time stamps for audit records"},
                {"file": FEDRAMP_HIGH, "quote": "AU-8 (b) [one second granularity of time measurement]"},
            ],
        },
        {
            "control": "AU-12 Audit Record Generation",
            "plain": "The listed components produce audit records, and authorized staff choose which events.",
            "source": "NIST; FedRAMP",
            "covered": "Step 2 sets who may collect what. Test 3 proves the setting changes what arrives.",
            "cite": [
                {"file": NIST, "quote": "Provide audit record generation capability for the event types the system is capable of"},
                {"file": NIST, "quote": "Allow [Assignment: organization-defined personnel or roles] to select the event types that"},
                {"file": FEDRAMP_HIGH, "quote": "AU-12 (a) [all information system and network components where audit capability is deployed/available]"},
            ],
        },
    ],
    "intent": [
        {
            "control": "AU-2 Event Logging",
            "feared": "Something damaging happens and nobody can reconstruct who did what, because the events were never chosen for logging.",
            "scope": "Every component the system team operates. Logs a customer keeps in their own tenant are theirs to answer for.",
            "question": "If someone with privileged access did something damaging three weeks ago, is the record of it being written down today?",
            "evidence": "The list of events the system can log, the subset that is logged, the reason for each, and the date of the last review.",
            "sufficient": "Event types are identified, the logged subset has a reason, the people who use the logs agree with it, and it is reviewed at a set frequency. NIST leaves the review frequency to the organization, and FedRAMP assigns annually and whenever there is a change in the threat environment. This lab reviews at least annually, plus after a significant system change, a security incident, or a change in requirements.",
            "tieoff": "Each component owner knows which events they must produce, and someone tells them when the list changes.",
            "tool": "The log forwarder (Step 3) carries audit, infrastructure and application logs, and Step 4 proves each type is arriving.",
        },
        {
            "control": "AU-3 Content of Audit Records",
            "feared": "A log entry exists but cannot answer the question. It says something happened without saying who, where, or whether it worked.",
            "scope": "Records produced by the components the team operates.",
            "question": "Take one real log line. From that line alone, can you tell what happened, when, where, who did it, and whether it worked?",
            "evidence": "A sample record from each major component, checked against the six required elements.",
            "sufficient": "The record shows event type, time, location, source, outcome, and the identity involved. Identity details in this lab include username, full name, remote and server IP addresses, and host names.",
            "tieoff": "If a component's records fall short, someone owns the fix.",
            "tool": "OpenShift audit records already carry these fields. Test 1 shows you where each one sits.",
        },
        {
            "control": "AU-8 Time Stamps",
            "feared": "Records from different components cannot be put in order because their clocks disagree.",
            "scope": "Every component that produces audit records and the SIEM that stores them.",
            "question": "If two components logged the same event, would their timestamps agree closely enough to tell which came first?",
            "evidence": "Clock synchronization status for the nodes, and the stored timestamp format.",
            "sufficient": "Clocks synchronize to a time server using NTP (Network Time Protocol). FedRAMP assigns one second granularity for timestamps; the lab stores them to the millisecond or finer. Timestamps map to UTC, either stored in UTC or carrying an offset.",
            "tieoff": "Something detects a component whose clock has drifted. This module checks by hand. SIEM-3 adds the alert.",
            "tool": "chrony keeps node clocks in sync. Test 2 reads its status and checks a stored timestamp.",
        },
        {
            "control": "AU-12 Audit Record Generation",
            "feared": "Some components produce no audit records at all, and nobody knows which.",
            "scope": "Components the team can configure for logging.",
            "question": "Which components are not producing audit records right now, and is that a decision or an accident?",
            "evidence": "The components with logging on, the roles allowed to change it, and sample records.",
            "sufficient": "Logging is on for the defined components, only authorized staff can change which events are logged, and changes go through change management (CM-3).",
            "tieoff": "Something detects a newly added component that is not logging. Test 3 shows why this matters.",
            "tool": "One permission per log type (Step 2) lets you see, and later remove, each type on its own.",
        },
    ],
    "architect": (
        "Design the log path before building it. Decide which three log types must be collected, which "
        "identity the collector runs as and why it should hold no more than three read permissions, "
        "how the collector proves it is talking to the real SIEM, and how you will tell if records stop. "
        "Then build it and run the tests."
    ),
    "terms": [
        ("Audit record", "One saved entry describing a security-relevant event, such as a login or a settings change."),
        ("Collector", "A small program on each node that reads logs and sends them onward."),
        ("Log forwarder", "The configuration that tells collectors what to send and where."),
        ("SIEM", "Security Information and Event Management: a system that stores logs from many sources so analysts can search them and raise alerts."),
        ("Stream and label (Loki)", "A stream is a series of log lines that share the same labels. A label is a key=value tag such as log_type=audit."),
        ("UTC", "Coordinated Universal Time, the world reference time with no daylight-saving changes."),
        ("NTP", "Network Time Protocol: how computers set their clocks from a trusted time server."),
    ],
    "concepts": [
        {
            "heading": "2.1 Why logs are collected in one place",
            "paras": [
                "What is this? A cluster has many nodes (the servers it runs on) and many programs. Each writes logs in its own place. Collecting means copying those logs to one central, protected store.",
                "Why? After an incident, investigators need one timeline. Logs left on a node are lost when the node is rebuilt, and an attacker with access to a node can edit the logs on it.",
            ],
            "table": {
                "headers": ["Log type", "What it shows", "Question it answers"],
                "rows": [
                    ("Audit", "Who called the platform API, and node-level actions", "Who deleted this project, and when?"),
                    ("Infrastructure", "Platform and operating-system services", "Did a node restart or a service fail?"),
                    ("Application", "Programs running on the platform", "Did the web app reject this login?"),
                ],
            },
        },
        {
            "heading": "2.2 The collector and the log forwarder",
            "paras": [
                "OpenShift Logging installs a collector on every node. A resource called ClusterLogForwarder tells the collectors which log types to read (inputs), where to send them (outputs), and how to connect the two (pipelines).",
                "Because it is a file, the forwarder can be reviewed and kept in version control like any other configuration. That supports configuration change control.",
            ],
            "diagram": (
                "Nodes and pods                 Collector (on each node)          SIEM\n"
                "--------------                 ------------------------          ----\n"
                "audit, infrastructure,   -->   reads logs, adds labels   --TLS--> Loki --> Analyst (Grafana)\n"
                "application logs               ClusterLogForwarder decides\n"
                "                               which logs go where"
            ),
        },
        {
            "heading": "2.3 Loki and Grafana",
            "paras": [
                "Loki stores log lines and lets you search them. Grafana is the web screen analysts use to search and chart them. Both are free and open source.",
                "Loki indexes only the labels on each stream, not every word, so a search names a label first and then filters the text.",
            ],
            "table": {
                "headers": ["Concept", "What it means"],
                "rows": [
                    ("Log line", "One record stored as text. Here it is a JSON object with fields such as user, verb and time."),
                    ("LogQL", "Loki's search language. {log_type=\"audit\"} |= \"error\" means audit logs containing the word error."),
                    ("Grafana Explore", "The Grafana screen for running LogQL searches."),
                ],
            },
            "production": "In the real environment the SIEM sits in a protected enclave, Loki keeps its data in object storage instead of local disk, and logs arrive over an approved path. The lab uses one Loki instance so you practice the same steps.",
        },
    ],
    "steps": [
        {
            "title": "Check what you have",
            "why": "Confirm the cluster and the SIEM are both up before changing anything.",
            "blocks": [
                {
                    "code": (
                        "oc get nodes\n"
                        "oc get pods -n openshift-logging\n"
                        "curl -s --cacert \"$LOKI_CA_FILE\" -u \"$LOKI_USER:$LOKI_PASSWORD\" \"$LOKI_URL/ready\""
                    ),
                    "lines": [
                        ("oc get nodes", "Lists the servers in the cluster. oc is the OpenShift command-line tool."),
                        ("oc get pods -n openshift-logging", "Lists programs running in the logging project (a project is a named workspace)."),
                        ("curl ... /ready", "Asks Loki if it is ready. The four LOKI variables are set by lab start, so no secret is typed or saved."),
                    ],
                }
            ],
            "security": "Never paste passwords into commands or files. The lab keeps them in environment variables, out of your command history and out of git.",
            "action": "Run the three commands and count the nodes. That is how many collectors to expect.",
            "checkpoint": "Loki answers ready.",
        },
        {
            "title": "Give the collector a limited identity (AU-12)",
            "why": "A service account is an identity for a program instead of a person. The collector needs permission to read logs and nothing more, which is least privilege. The requirement leaves the roles that choose event types to the organization; this lab lets the ISSO, ISSE and Platform Administrators choose which event types are logged, through version-controlled configuration under change management, so keep these commands in git.",
            "blocks": [
                {
                    "code": (
                        "oc create sa collector -n openshift-logging\n"
                        "oc adm policy add-cluster-role-to-user collect-application-logs -z collector -n openshift-logging\n"
                        "oc adm policy add-cluster-role-to-user collect-infrastructure-logs -z collector -n openshift-logging\n"
                        "oc adm policy add-cluster-role-to-user collect-audit-logs -z collector -n openshift-logging\n"
                        "oc get clusterrolebinding | grep collect"
                    ),
                    "lines": [
                        ("oc create sa collector", "Creates the identity named collector."),
                        ("add-cluster-role-to-user ... collect-*-logs", "Grants one read permission per log type, so each can be seen and removed on its own."),
                        ("-z collector", "Says the target is the service account named collector."),
                        ("grep collect", "Shows only the bindings you just made."),
                    ],
                }
            ],
            "action": "Run the commands and read the list at the end.",
            "checkpoint": "You see three collect bindings.",
        },
        {
            "title": "Store the credentials and apply the log forwarder (AU-2, AU-12)",
            "why": "A secret is a protected object that holds sensitive values so they are not written into files. The forwarder refers to the secrets by name, so no password appears in the file you keep in git. The forwarder then connects the three log types to Loki over TLS (encryption for data in transit).",
            "blocks": [
                {
                    "code": (
                        "oc create secret generic loki-credentials -n openshift-logging \\\n"
                        "  --from-literal=username=\"$LOKI_USER\" \\\n"
                        "  --from-literal=password=\"$LOKI_PASSWORD\"\n"
                        "oc create secret generic loki-ca -n openshift-logging --from-file=ca.crt=\"$LOKI_CA_FILE\""
                    ),
                    "lines": [
                        ("loki-credentials", "Holds the user name and password for Loki."),
                        ("loki-ca", "Holds the certificate authority file, so the collector can check it is talking to the real Loki."),
                    ],
                },
                {
                    "lang": "yaml",
                    "code": (
                        "apiVersion: observability.openshift.io/v1\n"
                        "kind: ClusterLogForwarder\n"
                        "metadata:\n"
                        "  name: siem-forwarder\n"
                        "  namespace: openshift-logging\n"
                        "spec:\n"
                        "  serviceAccount:\n"
                        "    name: collector\n"
                        "  outputs:\n"
                        "    - name: siem-loki\n"
                        "      type: loki\n"
                        "      loki:\n"
                        "        url: \"${LOKI_URL}\"\n"
                        "        authentication:\n"
                        "          username:\n"
                        "            secretName: loki-credentials\n"
                        "            key: username\n"
                        "          password:\n"
                        "            secretName: loki-credentials\n"
                        "            key: password\n"
                        "      tls:\n"
                        "        ca:\n"
                        "          secretName: loki-ca\n"
                        "          key: ca.crt\n"
                        "  pipelines:\n"
                        "    - name: security-logs\n"
                        "      inputRefs:\n"
                        "        - audit\n"
                        "        - infrastructure\n"
                        "        - application\n"
                        "      outputRefs:\n"
                        "        - siem-loki"
                    ),
                    "lines": [
                        ("serviceAccount", "The limited identity from Step 2."),
                        ("outputs", "Where logs go: Loki over HTTPS with the certificate checked."),
                        ("authentication", "Points at the secret instead of holding the password."),
                        ("pipelines", "Connects the three log types (inputs) to the output."),
                    ],
                },
                {
                    "code": (
                        "oc explain clusterlogforwarders.observability.openshift.io.spec.outputs.loki\n"
                        "envsubst < siem-forwarder.yaml | oc apply --dry-run=server -f -\n"
                        "envsubst < siem-forwarder.yaml | oc apply -f -\n"
                        "oc get pods -n openshift-logging"
                    ),
                    "lines": [
                        ("oc explain ...", "Prints the fields your cluster's Logging release accepts. If a field name differs, use the one it shows."),
                        ("envsubst < siem-forwarder.yaml", "Replaces ${LOKI_URL} in the file with the real value from the lab env before passing it to oc."),
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc apply -f -", "Saves the forwarder. Collectors pick it up on every node. The dash reads from stdin."),
                    ],
                },
            ],
            "security": "The collector verifies Loki's certificate through the loki-ca secret. Skipping that check can be an assessment finding under SC-8, which protects information in transit.",
            "tip": "Keep siem-forwarder.yaml in git. Git shows who changed it and when, which supports change control (CM-3), and limiting who can push supports CM-5.",
            "action": "Save the YAML as siem-forwarder.yaml, run envsubst to check the substitution, validate with dry-run, apply, then count the collector pods.",
            "checkpoint": "One collector pod per node, all Running.",
        },
        {
            "title": "Confirm each log type arrives (AU-2)",
            "why": "The auditable events in this lab include logons, account changes, permission changes and use of the root account. Those events reach the SIEM only if their log type is collected. Ask Loki which log types it holds.",
            "blocks": [
                {
                    "code": (
                        "sleep 60\n"
                        "curl -s --cacert \"$LOKI_CA_FILE\" -u \"$LOKI_USER:$LOKI_PASSWORD\" \\\n"
                        "  \"$LOKI_URL/loki/api/v1/label/log_type/values\" | jq ."
                    ),
                    "lines": [
                        ("sleep 60", "Gives the collectors time to send their first records."),
                        ("label/log_type/values", "Asks Loki for every value of the log_type label it has stored."),
                        ("| jq .", "Prints the JSON answer in a readable layout."),
                    ],
                }
            ],
            "note": "Audit covers platform API actions and node activity. Application and infrastructure cover the rest of the events the lab lists. A missing type means a whole category of events is not reaching the SIEM.",
            "action": "Run the commands and list which of the three types appear.",
            "checkpoint": "The answer lists audit, infrastructure and application.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "One audit record answers the six AU-3 questions",
            "why": "Make something happen, then find it. Creating a project is an audited action.",
            "code": (
                "oc new-project lab-audit-test\n"
                "sleep 30\n"
                "curl -sG --cacert \"$LOKI_CA_FILE\" -u \"$LOKI_USER:$LOKI_PASSWORD\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/query_range\" \\\n"
                "  --data-urlencode 'query={log_type=\"audit\"} |= \"lab-audit-test\"' \\\n"
                "  --data-urlencode 'limit=1' | jq -r '.data.result[0].values[0][1]' | jq ."
            ),
            "expect": (
                "Example only. Your field names and values will differ.\n"
                "{\n"
                "  \"verb\": \"create\",\n"
                "  \"user\": { \"username\": \"admin\" },\n"
                "  \"sourceIPs\": [ \"10.0.4.17\" ],\n"
                "  \"requestURI\": \"/apis/project.openshift.io/v1/projectrequests\",\n"
                "  \"responseStatus\": { \"code\": 201 },\n"
                "  \"stageTimestamp\": \"2026-10-25T14:03:11.482913Z\"\n"
                "}"
            ),
            "checkpoint": "You can point to what happened, when, where, the source, the outcome and who, or you know which is missing.",
        },
        {
            "kind": "positive",
            "title": "Clocks are synchronized and timestamps show the millisecond and UTC",
            "why": "If a node clock is far off, every record from that node places events at the wrong moment. chrony is the time-sync service on the node.",
            "code": (
                "NODE=$(oc get nodes -o jsonpath='{.items[0].metadata.name}')\n"
                "oc debug node/$NODE -- chroot /host chronyc tracking\n"
                "date -u"
            ),
            "expect": (
                "Example only.\n"
                "Reference ID    : 0A000001 (ntp.lab.internal)\n"
                "Stratum         : 3\n"
                "System time     : 0.000012345 seconds fast of NTP time\n"
                "Leap status     : Normal"
            ),
            "checkpoint": "Leap status is Normal, the offset is tiny, and the timestamp from Test 1 shows fractions of a second and ends in Z.",
        },
        {
            "kind": "negative",
            "title": "Remove the audit permission and watch the records stop",
            "why": "A control you have only seen working is not proven. Remove one permission and see what changes. Nothing will warn you, which is the point: SIEM-3 builds the alert that does.",
            "code": (
                "oc adm policy remove-cluster-role-from-user collect-audit-logs -z collector -n openshift-logging\n"
                "oc new-project lab-audit-test-2\n"
                "sleep 60\n"
                "curl -sG --cacert \"$LOKI_CA_FILE\" -u \"$LOKI_USER:$LOKI_PASSWORD\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/query_range\" \\\n"
                "  --data-urlencode 'query={log_type=\"audit\"} |= \"lab-audit-test-2\"' \\\n"
                "  --data-urlencode 'limit=1' | jq '.data.result | length'\n"
                "oc adm policy add-cluster-role-to-user collect-audit-logs -z collector -n openshift-logging"
            ),
            "expect": "0",
            "checkpoint": "The count is 0 while the permission is removed. After you restore it, a new project's record arrives again.",
        },
    ],
    "glossary": [
        ("ClusterLogForwarder", "The OpenShift resource that connects log types to destinations."),
        ("Least privilege", "Giving a user or program only the access it needs."),
        ("TLS", "Transport Layer Security: encryption for data moving between systems."),
        ("Service account", "An identity for a program instead of a person."),
        ("Project (OpenShift)", "A named workspace in the cluster."),
        ("LogQL", "Loki's search language."),
    ],
    "next": "Next module: SIEM-2 Store and Protect Audit Logs: where the records live, how long they stay, and how to stop them being altered.",
}
