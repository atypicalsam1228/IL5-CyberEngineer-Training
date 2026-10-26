"""SIEM-2: Store and protect audit logs."""

NIST = "nist-sp-800-53r5-full.md"
FEDRAMP = "fedramp-high-baseline.md"
SRG_CSP = "u-cloud-service-provider-v1r6-srg.md"
SRG_MO = "u-cloud-computing-mission-owner-overview.md"

MODULE = {
    "id": "SIEM-2",
    "slug": "Store",
    "title": "Store and Protect Audit Logs",
    "draft": (
        "Commands follow Grafana Loki and AWS CLI documentation but have not yet run in the lab. "
        "The Loki settings (SSE-KMS, deletion_mode, retention_enabled) and the forwarder tuning field "
        "(deliveryMode) are checked with --help, oc explain or a config verify before they are used. "
        "The Loki configuration file in Step 3 must match the lab's starting schema, which lab start provides. "
        "UNRESOLVED: The Loki compactor runs background index compaction that deletes old TSDB index files. "
        "S3 Object Lock in Compliance mode blocks those deletes with AccessDenied until each object ages "
        "past its lock period. The lab uses a short lock period so errors are transient, but this must be "
        "tested live. grafana/loki issue 20181 is still an open feature request for separate chunk and index "
        "buckets, so Loki has no supported way yet to lock only the chunks; see the note in Step 3. "
        "The Grafana alert-rule, folder and data source endpoints in Step 4 still work but the Grafana docs mark them deprecated."
    ),
    "controls": ["AU-9", "AU-11", "AU-4", "AU-5"],
    "mentions": ["AC-2", "AU-2", "AU-6", "AU-8", "CM-3", "CM-5", "SC-8", "SI-4"],
    "unit_values_ok": ["60 seconds", "30 seconds", "5 minutes", "1 minute", "365 days", "180 days", "15 minutes"],
    "minutes": {"hands_on": 45, "verify": 25},
    "tools": ["Loki (free, open source)", "Amazon S3 with Object Lock and KMS encryption", "Grafana (free, open source)", "OpenShift Logging", "oc", "aws", "curl", "jq"],
    "diagrams": [
        {
            "id": "store",
            "title": "How audit logs are stored and protected",
            "caption": "Loki keeps the logs in an encrypted, locked storage bucket. Only the auditor can read, nobody can delete, and an alert warns before the volume fills. Each step below adds one part, drawn with thick lines.",
            "per_step": True,
            "rankdir": "LR",
            "step_notes": {
                1: "Nothing is new yet. The collector sends records to Loki, and the bucket already has Object Lock in Compliance mode and a Glacier archive rule. You only read those settings.",
                2: "The auditor identity gets the read-only role. The ordinary identity gets nothing, so Loki refuses its reads.",
                3: "Loki now writes to the bucket, each object is encrypted with your key, and the delete interface refuses every request.",
                4: "A Grafana alert rule watches the Loki volume and fires at 80 percent of capacity.",
                5: "The collector resends records until Loki accepts them.",
            },
            "zones": [
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "logging", "label": "Project openshift-logging", "parent": "cluster", "kind": "group"},
                {"id": "siem", "label": "Project siem", "parent": "cluster", "kind": "group"},
                {"id": "cloud", "label": "Your cloud account", "kind": "boundary"},
            ],
            "nodes": [
                {"id": "coll", "title": "Collector", "sub": "From SIEM-1", "zone": "logging"},
                {"id": "buf", "title": "Delivery retry", "sub": "Resends records after an outage", "zone": "logging", "kind": "ok", "s": 5},
                {"id": "loki", "title": "Loki", "sub": "Stores and serves logs", "zone": "siem", "kind": "ok"},
                {"id": "aud", "title": "Auditor identity", "sub": "Read-only role", "zone": "siem", "kind": "ok", "s": 2},
                {"id": "ord", "title": "Ordinary identity", "sub": "No role", "zone": "siem", "s": 2},
                {"id": "rule", "title": "Storage alert", "sub": "Fires at 80 percent", "zone": "siem", "kind": "warn", "s": 4},
                {"id": "bucket", "title": "Log bucket", "sub": "Object Lock, Compliance mode", "zone": "cloud", "kind": "ok"},
                {"id": "kms", "title": "Encryption key", "sub": "KMS", "zone": "cloud"},
                {"id": "glacier", "title": "Glacier archive", "sub": "After 365 days", "zone": "cloud"},
            ],
            "edges": [
                {"a": "coll", "b": "loki", "label": "Send"},
                {"a": "coll", "b": "buf", "label": "Retry", "kind": "ok", "flat": True, "s": 5},
                {"a": "aud", "b": "loki", "label": "Read allowed", "kind": "ok", "s": 2},
                {"a": "ord", "b": "loki", "label": "Read refused", "kind": "bad", "s": 2},
                {"a": "aud", "b": "loki", "label": "Delete refused", "kind": "bad", "s": 3},
                {"a": "rule", "b": "loki", "label": "Watch volume", "kind": "warn", "flat": True, "s": 4},
                {"a": "loki", "b": "bucket", "label": "Write", "kind": "ok", "s": 3},
                {"a": "kms", "b": "bucket", "label": "Encrypt", "kind": "ok", "s": 3},
                {"a": "bucket", "b": "glacier", "label": "Archive"},
            ],
            "reading": [
                "The collector sends records to Loki, and Loki writes them to the log bucket.",
                "The encryption key encrypts every object in the bucket, and Object Lock in Compliance mode stops objects being deleted.",
                "The auditor identity can read logs through Loki. The ordinary identity is refused.",
                "Loki refuses every delete request, even from the auditor.",
                "Old objects move to the Glacier archive, and a storage alert warns at 80 percent of volume capacity.",
                "If Loki is unreachable, the collector resends the records until Loki accepts them.",
            ],
        },
    ],
    "prereq": ["SIEM-1 Collect Audit Logs"],
    "lab_needs": [
        "Loki runs as deployment loki in namespace siem, reads its whole configuration from ConfigMap loki-config (key config.yaml) and starts with -config.expand-env=true. The pod has the environment variables LOG_BUCKET, KMS_KEY_ARN and AWS_REGION and an AWS identity allowed to use that bucket and key.",
        "The S3 bucket named by LOG_BUCKET was created with Object Lock enabled, versioning on, default encryption with KMS_KEY_ARN, a default Object Lock retention in Compliance mode with a short lab period, and a lifecycle rule that moves objects to Glacier after the archive period.",
        "The Loki endpoint in LOKI_URL accepts a Kubernetes bearer token, and allows a read only when the token's identity is bound to ClusterRole audit-log-reader (lab-provided). Everyone else receives HTTP 403.",
        "Grafana has a Loki data source named Loki and a Prometheus data source named Prometheus (cluster metrics). The learner's shell has GRAFANA_URL, GRAFANA_USER and GRAFANA_PASSWORD.",
        "lab start siem-2 provides siem-forwarder.yaml from SIEM-1 and the starting loki-config.",
    ],
    "lab": {
        "start": "lab start siem-2",
        "env": ["LOKI_URL", "LOKI_CA_FILE", "LOG_BUCKET", "KMS_KEY_ARN", "AWS_REGION", "GRAFANA_URL", "GRAFANA_USER", "GRAFANA_PASSWORD"],
        "checks": [
            "The log bucket is encrypted with the lab KMS key and Object Lock is on in Compliance mode.",
            "Loki's delete interface is disabled and the auditor role can read audit logs.",
            "An ordinary identity receives HTTP 403 on read and on delete.",
            "A locked object cannot be deleted, even by the cluster administrator's cloud identity.",
            "After a Loki outage, audit records created during the outage arrive once Loki returns.",
        ],
    },
    "requirement": (
        "An IL5 system must keep audit records for a defined period, protect them from being read, changed or "
        "deleted by people who should not, make sure there is room to hold them, and act when the logging "
        "process itself fails. This module moves the log store onto encrypted object storage, limits who can "
        "read and who can change it, shows the retention periods the lab sets, watches storage "
        "capacity, and proves that a Loki outage does not lose records."
    ),
    "mapping": [
        {
            "control": "AU-9 Protection of Audit Information",
            "plain": "Only the right people can read audit logs, nobody can change or delete them, and unauthorized attempts raise an alert.",
            "source": "NIST; FedRAMP",
            "covered": "Steps 2 and 3 set read-only access and disable deletion. Tests 1 to 3 prove the read, the refusal and the locked storage.",
            "cite": [
                {"file": NIST, "quote": "Protect audit information and audit logging tools from unauthorized access, modification"},
                {"file": FEDRAMP, "quote": "Alert [Assignment: organization-defined personnel or roles] upon detection of unauthorized access, modification, or deletion of audit information."},
                {"file": FEDRAMP, "quote": "Authorize access to management of audit logging functionality to only [Assignment: organization-defined subset of privileged users or roles]."},
                {"file": FEDRAMP, "quote": "Implement cryptographic mechanisms to protect the integrity of audit information and audit tools."},
            ],
        },
        {
            "control": "AU-11 Audit Record Retention",
            "plain": "Keep audit records for a set time so investigators can look back after an incident.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Step 1 reads the retention and archive settings. Step 3 turns off every way to delete early.",
            "cite": [
                {"file": NIST, "quote": "Retain audit records for [Assignment: organization-defined time period consistent with"},
                {"file": FEDRAMP, "quote": "The service provider retains audit records on-line for at least ninety days"},
                {"file": SRG_CSP, "quote": "for the period specified by AU-11"},
            ],
        },
        {
            "control": "AU-4 Audit Log Storage Capacity",
            "plain": "Reserve enough room for the logs. AU-5(1) adds a warning before the space runs out.",
            "source": "NIST; FedRAMP",
            "covered": "Step 4 creates a storage alert. The lab chooses 80 percent as the warning level.",
            "cite": [
                {"file": NIST, "quote": "Allocate audit log storage capacity to accommodate"},
                {"file": FEDRAMP, "quote": "Allocating sufficient audit log storage capacity reduces the likelihood of such capacity being exceeded"},
            ],
        },
        {
            "control": "AU-5 Response to Audit Logging Process Failures",
            "plain": "When logging breaks, tell named people within a set time and take the defined actions.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Step 5 turns on at-least-once delivery, the lab's local caching action. Test 4 stops Loki on purpose and shows no records are lost.",
            "cite": [
                {"file": NIST, "quote": "in the event of an audit logging process failure"},
                {"file": SRG_MO, "quote": "AU-5(1) DSPAV will be used, not FedRAMP."},
                {"file": FEDRAMP, "quote": "Alert [Assignment: organization-defined personnel or roles] within [Assignment: organization-defined time period] in the event of an audit logging process failure"},
            ],
        },
    ],
    "intent": [
        {
            "control": "AU-9 Protection of Audit Information",
            "feared": "An intruder or a careless administrator edits or deletes the log of what they did, and the evidence is gone.",
            "scope": "The log store, its storage bucket, its configuration, and the roles that can reach them.",
            "question": "Who can read the audit logs, who can change or delete them, and would anyone be told if they tried?",
            "evidence": "The role list for the log store, the storage encryption and lock settings, and a refused delete attempt.",
            "sufficient": "Read access is limited to named roles, unauthorized users cannot modify or delete records, integrity is protected with cryptography, and attempted tampering raises an alert. This lab goes further: nobody, including administrators, can delete the original records, and configuration changes need a second approver.",
            "tieoff": "Someone owns the alert for attempted tampering, and someone reviews the list of readers on a schedule.",
            "tool": "Loki on object storage with Object Lock, bearer-token read access limited to the audit role, and deletion switched off.",
        },
        {
            "control": "AU-11 Audit Record Retention",
            "feared": "An incident is found months later and the logs that would explain it were already thrown away.",
            "scope": "All audit records the team keeps, online and archived.",
            "question": "If an incident is discovered today, how far back can you read the logs, and where do older ones live?",
            "evidence": "The retention policy, the storage settings that carry it out, and a successful read of an older record.",
            "sufficient": "The retention period is written down, the settings match it, and nothing deletes records earlier. NIST leaves the period organization-defined, FedRAMP sets a minimum online period, and the lab sets online and archive stages. The lab sets no end date for the archive stage, so the end of retention is organization-defined and comes from the records retention policy.",
            "tieoff": "Someone owns the retention policy and the settings are reviewed when it changes.",
            "tool": "No automatic deletion in Loki, and an object-storage lifecycle rule that archives old objects.",
        },
        {
            "control": "AU-4 Audit Log Storage Capacity",
            "feared": "The log disk fills up quietly and new records are dropped just when they are needed.",
            "scope": "Every place audit records are stored or buffered: the object store, the Loki volume and the collector's local buffer.",
            "question": "How full is each place that holds audit logs, and who is told before it is full?",
            "evidence": "Current usage figures and the alert rule with its threshold and recipients.",
            "sufficient": "Capacity is sized for the retention requirement and an alert fires at 80 percent. Object storage grows on its own, so the volumes and buffers are the places that need watching.",
            "tieoff": "A named team receives the alert and acts on it.",
            "tool": "A Grafana alert on volume usage at 80 percent.",
        },
        {
            "control": "AU-5 Response to Audit Logging Process Failures",
            "feared": "The log store stops and records from that time are lost, with nobody told.",
            "scope": "The collector, the connection to Loki, and Loki itself.",
            "question": "If Loki stopped right now, would anyone know, and would the records written meanwhile still be kept?",
            "evidence": "The defined failure actions, the alert, and a test where the store was stopped and restored.",
            "sufficient": "Named people are alerted within the lab's alert time of 15 minutes, and the system keeps records while the store is away. The lab sets the alert delivery window and uses local caching as the defined action. FedRAMP's assigned additional action is to overwrite the oldest record; the lab chooses local caching so no records are lost. For the storage warning, the DoD mission owner overview says DoD-assigned values are used at IL5 instead of FedRAMP's; this module uses its own value.",
            "tieoff": "Alert recipients are current, and the failure test is repeated on a schedule.",
            "tool": "At-least-once delivery on the collector, which resends records Loki has not accepted, and the missing-logs alert built in SIEM-3.",
        },
    ],
    "architect": (
        "Design the store before changing it. Decide which identities may read, which may change settings, and "
        "which may do neither. Decide where each retention stage lives and what removes records at the end. "
        "Decide what each place that holds logs will do when it is full or unreachable. Then build and break it."
    ),
    "terms": [
        ("Object storage (S3)", "A cloud service that keeps files as objects in a bucket. It grows as needed."),
        ("Bucket", "A named container in object storage."),
        ("Object Lock", "An S3 feature that stops an object from being deleted or overwritten for a set period."),
        ("Compliance mode", "The Object Lock setting where nobody, including the account owner, can shorten or remove the lock."),
        ("SSE-KMS", "Server-side encryption using a key held in AWS Key Management Service."),
        ("Retention", "How long records are kept."),
        ("Bearer token", "A string that proves who is calling. The caller sends it in a request header."),
        ("HTTP status code", "A number a web service returns: 200 means success, 403 means refused."),
    ],
    "concepts": [
        {
            "heading": "2.1 Four jobs for the log store",
            "paras": [
                "What is this? Collecting logs (SIEM-1) is not enough. The place they land has four jobs: stay protected, keep records long enough, have room, and keep working when something fails.",
                "Why? An attacker's first move is often to erase their tracks. A full disk or a stopped service looks the same as an attacker who switched logging off.",
            ],
            "table": {
                "headers": ["Control", "Job", "Question to ask"],
                "rows": [
                    ("AU-9", "Protect", "Can anyone change or delete records?"),
                    ("AU-11", "Retain", "How far back can we read?"),
                    ("AU-4", "Have room", "How full is it, and who is told?"),
                    ("AU-5", "Survive failure", "What happens when logging breaks?"),
                ],
            },
        },
        {
            "heading": "2.2 Where Loki keeps data",
            "paras": [
                "Loki writes log chunks and its index to object storage. In this lab Loki keeps audit logs in AWS S3, and S3 Object Lock in Compliance mode is the cloud equivalent of write-once media (storage that cannot be rewritten).",
                "Data is encrypted in the bucket with a key you control in KMS (Key Management Service). The copy on the wire is already protected by TLS (encryption in transit) from SIEM-1.",
            ],
            "diagram": (
                "Collector --TLS--> Loki --writes--> S3 bucket (encrypted, Object Lock)\n"
                "                    ^                    |\n"
                "   auditor token ---+ read only           +--> lifecycle rule --> Glacier archive\n"
                "   ordinary token -----X (HTTP 403)"
            ),
        },
        {
            "heading": "2.3 Who can read and who can change",
            "paras": [
                "Reading and changing are separate powers. In this lab the auditor role can read logs and do nothing else. Changing where logs live or how long they stay is a configuration change, and this lab sends those through a reviewed merge request with a second approver.",
                "Loki also has a delete interface. Setting deletion_mode to disabled makes it refuse every delete request with HTTP 403, so even an administrator's credentials cannot use it.",
            ],
            "table": {
                "headers": ["Identity", "Read logs", "Delete logs", "Change Loki settings"],
                "rows": [
                    ("auditor", "Yes", "No", "No"),
                    ("ordinary user", "No", "No", "No"),
                    ("platform administrator", "Through the auditor role only", "No", "Yes, through reviewed change"),
                ],
            },
        },
    ],
    "steps": [
        {
            "title": "Read the current storage settings (AU-9, AU-11)",
            "why": "Before changing anything, record what protects the bucket today. These read-only commands show encryption, Object Lock and the lifecycle rule that archives old objects.",
            "blocks": [
                {
                    "code": (
                        "aws s3api get-bucket-encryption --bucket \"$LOG_BUCKET\"\n"
                        "aws s3api get-object-lock-configuration --bucket \"$LOG_BUCKET\"\n"
                        "aws s3api get-bucket-lifecycle-configuration --bucket \"$LOG_BUCKET\"\n"
                        "oc get configmap loki-config -n siem -o jsonpath='{.data.config\\.yaml}' | grep -n -E 'object_store|sse|retention|deletion'"
                    ),
                    "lines": [
                        ("get-bucket-encryption", "Shows the default encryption on the bucket and the key it uses."),
                        ("get-object-lock-configuration", "Shows whether Object Lock is on and its default mode (Compliance or Governance) and period."),
                        ("get-bucket-lifecycle-configuration", "Shows the rule that moves old objects to the Glacier archive. The lab puts that move at 365 days."),
                        ("grep ... loki-config", "Shows the lines of Loki's current configuration that concern storage, retention and deletion."),
                    ],
                }
            ],
            "note": "This lab uses an online stage of 180 days and an archive move at 365 days. The lab sets no end date for the archive stage; that end date is organization-defined and comes from the records retention policy.",
            "action": "Run the four commands. Write down the encryption algorithm, the Object Lock mode and the lifecycle transition.",
            "checkpoint": "Encryption is aws:kms, Object Lock mode is COMPLIANCE, and a lifecycle transition to GLACIER exists.",
        },
        {
            "title": "Create the auditor and ordinary identities (AU-9)",
            "why": "A service account is an identity for a program or a test user. You need one that is allowed to read logs and one that is not, so you can prove the difference. The auditor is bound to a read-only role. The ordinary identity gets nothing. This gives approved users read-only access to audit data.",
            "blocks": [
                {
                    "code": (
                        "oc create sa auditor -n siem\n"
                        "oc create sa ordinary-user -n siem\n"
                        "oc get clusterrole audit-log-reader\n"
                        "oc adm policy add-cluster-role-to-user audit-log-reader -z auditor -n siem\n"
                        "AUDITOR_TOKEN=$(oc create token auditor -n siem)\n"
                        "ORDINARY_TOKEN=$(oc create token ordinary-user -n siem)"
                    ),
                    "lines": [
                        ("oc create sa", "Creates the two identities."),
                        ("oc get clusterrole audit-log-reader", "Confirms the read-only role exists before you use it."),
                        ("add-cluster-role-to-user ... -z auditor", "Gives only the auditor the read-only role. The ordinary identity is left without it."),
                        ("oc create token", "Makes a short-lived bearer token for each identity and stores it in a shell variable, not a file. Do not print it."),
                    ],
                }
            ],
            "security": "Tokens are secrets. Keep them in shell variables only, never in files, tickets or the chat channel.",
            "action": "Run the commands. Then run oc auth can-i get pods -n siem --as=system:serviceaccount:siem:ordinary-user to see that the ordinary identity has no extra rights.",
            "checkpoint": "The role exists, the binding is created, and the ordinary identity gets the answer no.",
        },
        {
            "title": "Store Loki data in encrypted S3 and switch off deletion (AU-9, AU-11)",
            "why": "This configuration file replaces the one from the starting state. It writes chunks and the index to the bucket, encrypts each object with your KMS key, and sets deletion_mode to disabled so Loki's delete interface refuses every request. The retention period stays at zero, which means no age-based deletion, so nothing removes records before the organization-defined end of retention. The bucket name, key and region come from the Loki pod's environment, so no value is typed here. Changes to this file belong in version control with a second approver (CM-3 and CM-5).",
            "blocks": [
                {
                    "lang": "yaml",
                    "code": (
                        "auth_enabled: false\n"
                        "server:\n"
                        "  http_listen_port: 3100\n"
                        "common:\n"
                        "  path_prefix: /var/loki\n"
                        "  replication_factor: 1\n"
                        "  ring:\n"
                        "    kvstore:\n"
                        "      store: inmemory\n"
                        "schema_config:\n"
                        "  configs:\n"
                        "    - from: \"2024-04-01\"\n"
                        "      store: tsdb\n"
                        "      object_store: s3\n"
                        "      schema: v13\n"
                        "      index:\n"
                        "        prefix: index_\n"
                        "        period: 24h\n"
                        "storage_config:\n"
                        "  tsdb_shipper:\n"
                        "    active_index_directory: /var/loki/index\n"
                        "    cache_location: /var/loki/index_cache\n"
                        "  aws:\n"
                        "    bucketnames: ${LOG_BUCKET}\n"
                        "    region: ${AWS_REGION}\n"
                        "    sse:\n"
                        "      type: SSE-KMS\n"
                        "      kms_key_id: ${KMS_KEY_ARN}\n"
                        "compactor:\n"
                        "  working_directory: /var/loki/compactor\n"
                        "  retention_enabled: true\n"
                        "  delete_request_store: s3\n"
                        "limits_config:\n"
                        "  retention_period: 0s\n"
                        "  deletion_mode: disabled"
                    ),
                    "lines": [
                        ("object_store: s3", "Stores chunks and index in S3 instead of local disk."),
                        ("bucketnames, region", "Read from the pod's environment (LOG_BUCKET, AWS_REGION)."),
                        ("sse: type SSE-KMS", "Every object written is encrypted with your KMS key."),
                        ("retention_enabled: true, delete_request_store: s3", "Switches on the part of Loki that hosts the delete interface. Without it the interface does not exist at all and answers 404 instead of refusing. Loki requires the store setting when this is on."),
                        ("retention_period: 0s", "Zero means keep logs forever, so Loki never deletes by age. The archive rule and the retention policy decide the end."),
                        ("deletion_mode: disabled", "The delete interface answers HTTP 403 to everyone."),
                    ],
                },
                {
                    "code": (
                        "oc create configmap loki-config -n siem --from-file=config.yaml=loki-config.yaml --dry-run=client -o yaml | oc apply -f -\n"
                        "oc rollout restart deployment/loki -n siem\n"
                        "oc rollout status deployment/loki -n siem\n"
                        "sleep 60\n"
                        "oc logs deployment/loki -n siem | grep -i -E 'level=error' | head -5\n"
                        "curl -s --cacert \"$LOKI_CA_FILE\" -H \"Authorization: Bearer $AUDITOR_TOKEN\" \"$LOKI_URL/ready\""
                    ),
                    "lines": [
                        ("--from-file ... --dry-run=client -o yaml | oc apply", "Builds the configuration map from your file and applies it, replacing the old one."),
                        ("rollout restart / status", "Restarts Loki so it reads the new file and waits until it is ready."),
                        ("logs ... grep level=error", "Looks for startup errors such as a bad bucket or key. An empty result is good."),
                        ("curl ... /ready", "Asks Loki if it is ready, using the auditor token."),
                    ],
                },
            ],
            "security": "Skipping SSE-KMS would leave records readable by anyone with raw bucket access. SSE-KMS keeps each object encrypted with a key you control.",
            "tip": "Keep loki-config.yaml in git and change it only through a reviewed merge request. That gives a second approver over audit storage settings.",
            "note": (
                "Loki runs a background compactor that merges TSDB index files and deletes the old un-compacted ones. "
                "When the S3 bucket uses Object Lock in Compliance mode, those delete calls return AccessDenied until each "
                "object ages past its lock period. The lab sets a short lock period so the errors are transient and clear on their own. "
                "In Loki logs they appear as level=error storage component=compactor. "
                "Loki has no supported setting yet to lock only the chunks and leave the index unlocked: a request for separate "
                "chunk and index buckets is still open (grafana/loki issue 20181). Turning the compactor off stops the errors but "
                "lets the index fragment, which slows queries over time. Which trade-off a production system accepts is a "
                "decision for the system owner and needs a live test."
            ),
            "action": "Save the YAML as loki-config.yaml, apply it, restart Loki, and read the log check.",
            "checkpoint": "Rollout completes, no error lines appear, and ready answers ready.",
        },
        {
            "title": "Warn before storage fills (AU-4)",
            "why": "Object storage grows by itself, but the Loki volume and local buffers do not. This lab alerts at 80% of capacity. This creates a Grafana alert rule on volume usage. A rule has a query, a condition and a folder. A folder is a named group of rules. SIEM-3 connects alerts to Mattermost.",
            "blocks": [
                {
                    "code": (
                        "PROM_UID=$(curl -s -u \"$GRAFANA_USER:$GRAFANA_PASSWORD\" \"$GRAFANA_URL/api/datasources/name/Prometheus\" | jq -r .uid)\n"
                        "FOLDER_UID=$(curl -s -u \"$GRAFANA_USER:$GRAFANA_PASSWORD\" -H 'Content-Type: application/json' \\\n"
                        "  -d '{\"title\":\"siem-storage\"}' \"$GRAFANA_URL/api/folders\" | jq -r .uid)\n"
                        "echo \"$PROM_UID $FOLDER_UID\""
                    ),
                    "lines": [
                        ("api/datasources/name/Prometheus", "Looks up the id of the metrics data source by its name."),
                        ("api/folders", "Creates a folder for storage alerts and returns its id."),
                        ("echo", "Prints both ids so you can see neither is empty or null."),
                    ],
                },
                {
                    "lang": "json",
                    "code": (
                        "{\n"
                        "  \"title\": \"audit-storage-volume-high\",\n"
                        "  \"ruleGroup\": \"storage\",\n"
                        "  \"folderUID\": \"FOLDER_UID\",\n"
                        "  \"noDataState\": \"OK\",\n"
                        "  \"execErrState\": \"Error\",\n"
                        "  \"for\": \"1m\",\n"
                        "  \"condition\": \"B\",\n"
                        "  \"annotations\": {\"summary\": \"A Loki volume is at or above 80% of capacity\"},\n"
                        "  \"labels\": {\"control\": \"AU-4\"},\n"
                        "  \"data\": [\n"
                        "    {\n"
                        "      \"refId\": \"A\",\n"
                        "      \"datasourceUid\": \"PROM_UID\",\n"
                        "      \"relativeTimeRange\": {\"from\": 600, \"to\": 0},\n"
                        "      \"model\": {\"refId\": \"A\", \"expr\": \"max(kubelet_volume_stats_used_bytes{namespace=\\\"siem\\\"} / kubelet_volume_stats_capacity_bytes{namespace=\\\"siem\\\"}) * 100\"}\n"
                        "    },\n"
                        "    {\n"
                        "      \"refId\": \"B\",\n"
                        "      \"datasourceUid\": \"-100\",\n"
                        "      \"relativeTimeRange\": {\"from\": 0, \"to\": 0},\n"
                        "      \"model\": {\n"
                        "        \"refId\": \"B\",\n"
                        "        \"type\": \"classic_conditions\",\n"
                        "        \"datasource\": {\"type\": \"__expr__\", \"uid\": \"-100\"},\n"
                        "        \"conditions\": [{\"type\": \"query\", \"query\": {\"params\": [\"A\"]}, \"reducer\": {\"type\": \"last\", \"params\": []}, \"evaluator\": {\"type\": \"gt\", \"params\": [80]}, \"operator\": {\"type\": \"and\"}}]\n"
                        "      }\n"
                        "    }\n"
                        "  ]\n"
                        "}"
                    ),
                    "lines": [
                        ("expr", "Percent used of every volume in the siem namespace; the highest one is tested."),
                        ("evaluator gt 80", "The rule fires when usage is above 80."),
                        ("noDataState OK", "If the metric is missing the rule stays quiet. Check the rule's health in Step 4's last command."),
                        ("labels control AU-4", "A label SIEM-3 routing and your review can filter on."),
                    ],
                },
                {
                    "code": (
                        "sed -e \"s/FOLDER_UID/$FOLDER_UID/\" -e \"s/PROM_UID/$PROM_UID/\" storage-rule.json > storage-rule-final.json\n"
                        "curl -s -u \"$GRAFANA_USER:$GRAFANA_PASSWORD\" -H 'Content-Type: application/json' -H 'X-Disable-Provenance: true' \\\n"
                        "  -d @storage-rule-final.json \"$GRAFANA_URL/api/v1/provisioning/alert-rules\" | jq '{title, condition, uid}'\n"
                        "sleep 60\n"
                        "curl -s -u \"$GRAFANA_USER:$GRAFANA_PASSWORD\" \"$GRAFANA_URL/api/prometheus/grafana/api/v1/rules\" | jq '.data.groups[].rules[] | select(.name==\"audit-storage-volume-high\") | {name, state, health}'"
                    ),
                    "lines": [
                        ("sed", "Fills the two ids into the rule file and writes a new copy."),
                        ("alert-rules POST", "Creates the rule. X-Disable-Provenance keeps it editable in the Grafana screen."),
                        ("api/prometheus/grafana/api/v1/rules", "Lists rules with their current state and health."),
                    ],
                },
            ],
            "note": "If health shows error, the metric name or data source is not available in your cluster. Check the data source with the Grafana Explore screen and use the volume metric it lists.",
            "action": "Save the JSON as storage-rule.json, then run the commands.",
            "checkpoint": "The rule is created and its health is ok. State inactive means usage is below the threshold.",
        },
        {
            "title": "Keep records when the connection to Loki fails (AU-5)",
            "why": "This lab uses local caching as the defined action when the connection to the central store is lost. At-least-once delivery makes the collector resend any record it has read but not yet delivered, including after the collector restarts, until Loki accepts it. Red Hat's documentation does not say where those records wait, so Test 4 proves the result rather than the mechanism. Check the field name with oc explain first, because Logging releases differ.",
            "blocks": [
                {
                    "code": (
                        "oc explain clusterlogforwarders.observability.openshift.io.spec.outputs.loki.tuning\n"
                        "oc patch clusterlogforwarders.observability.openshift.io siem-forwarder -n openshift-logging --type json \\\n"
                        "  -p '[{\"op\":\"add\",\"path\":\"/spec/outputs/0/loki/tuning\",\"value\":{\"deliveryMode\":\"AtLeastOnce\"}}]' --dry-run=server\n"
                        "oc patch clusterlogforwarders.observability.openshift.io siem-forwarder -n openshift-logging --type json \\\n"
                        "  -p '[{\"op\":\"add\",\"path\":\"/spec/outputs/0/loki/tuning\",\"value\":{\"deliveryMode\":\"AtLeastOnce\"}}]'\n"
                        "sleep 60\n"
                        "oc get pods -n openshift-logging"
                    ),
                    "lines": [
                        ("oc explain ...tuning", "Prints the delivery options your Logging release accepts."),
                        ("--dry-run=server", "Asks the cluster to check the change without saving it."),
                        ("deliveryMode AtLeastOnce", "Resends records that were read but not yet delivered, instead of dropping them. Some records may arrive twice."),
                        ("oc get pods", "Collectors restart to pick up the change. Wait until all are Running."),
                    ],
                }
            ],
            "tip": "The alert that tells people the store has failed is the missing-logs rule you build in SIEM-3. The lab sets 15 minutes for alert delivery.",
            "action": "Run the commands and wait for the collector pods to be Running.",
            "checkpoint": "The patch is accepted and every collector pod is Running.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "The auditor role can read retained audit logs",
            "why": "Protection that blocks the auditor too is not useful. Prove the right role can read.",
            "code": (
                "curl -sG --cacert \"$LOKI_CA_FILE\" -H \"Authorization: Bearer $AUDITOR_TOKEN\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/query_range\" \\\n"
                "  --data-urlencode 'query={log_type=\"audit\"}' \\\n"
                "  --data-urlencode 'limit=1' | jq '.data.result | length'"
            ),
            "expect": "1",
            "checkpoint": "The count is 1 or more. Zero means no audit records are stored or the auditor lacks the role.",
        },
        {
            "kind": "negative",
            "title": "An ordinary user cannot read or delete audit logs",
            "why": "Use the identity with no role. A secure store refuses it. The delete request is also tried with the auditor, which should fail too because nobody may delete.",
            "code": (
                "echo read-by-ordinary:\n"
                "curl -s -o /dev/null -w '%{http_code}\\n' -G --cacert \"$LOKI_CA_FILE\" -H \"Authorization: Bearer $ORDINARY_TOKEN\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/query_range\" --data-urlencode 'query={log_type=\"audit\"}'\n"
                "echo delete-by-ordinary:\n"
                "curl -s -o /dev/null -w '%{http_code}\\n' -X POST --cacert \"$LOKI_CA_FILE\" -H \"Authorization: Bearer $ORDINARY_TOKEN\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/delete?query=%7Blog_type%3D%22audit%22%7D&start=1700000000\"\n"
                "echo delete-by-auditor:\n"
                "curl -s -o /dev/null -w '%{http_code}\\n' -X POST --cacert \"$LOKI_CA_FILE\" -H \"Authorization: Bearer $AUDITOR_TOKEN\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/delete?query=%7Blog_type%3D%22audit%22%7D&start=1700000000\"\n"
                "oc auth can-i update configmap/loki-config -n siem --as=system:serviceaccount:siem:ordinary-user"
            ),
            "expect": (
                "read-by-ordinary:\n"
                "403\n"
                "delete-by-ordinary:\n"
                "403\n"
                "delete-by-auditor:\n"
                "403\n"
                "no"
            ),
            "checkpoint": "All three web calls return 403 and the permission check says no. A 200 or 204 on any delete is a failed control.",
        },
        {
            "kind": "negative",
            "title": "A locked object cannot be deleted even with administrator cloud rights",
            "why": "Object Lock in Compliance mode is the cloud equivalent of write-once media. Write a small test object of your own, then try to delete that exact version and watch the bucket refuse. Your test object stays in the bucket until its lock period ends; it holds no log data.",
            "code": (
                "KEY=lab-lock-test/$(date +%s).txt\n"
                "VID=$(echo lock test | aws s3api put-object --bucket \"$LOG_BUCKET\" --key \"$KEY\" --body - --server-side-encryption aws:kms --ssekms-key-id \"$KMS_KEY_ARN\" --query VersionId --output text)\n"
                "aws s3api delete-object --bucket \"$LOG_BUCKET\" --key \"$KEY\" --version-id \"$VID\""
            ),
            "expect": (
                "Example only.\n"
                "An error occurred (AccessDenied) when calling the DeleteObject operation: Access Denied because object protected by object lock."
            ),
            "checkpoint": "The delete fails with AccessDenied. If it succeeds, the bucket default lock is not in Compliance mode.",
        },
        {
            "kind": "negative",
            "title": "Stop Loki and show no records are lost",
            "why": "Break the log store on purpose. The collector should buffer records and deliver them when Loki returns. The marker project is created while Loki is down.",
            "code": (
                "oc scale deployment/loki -n siem --replicas=0\n"
                "oc new-project lab-outage-test\n"
                "sleep 60\n"
                "oc scale deployment/loki -n siem --replicas=1\n"
                "oc rollout status deployment/loki -n siem\n"
                "sleep 60\n"
                "curl -sG --cacert \"$LOKI_CA_FILE\" -H \"Authorization: Bearer $AUDITOR_TOKEN\" \\\n"
                "  \"$LOKI_URL/loki/api/v1/query_range\" \\\n"
                "  --data-urlencode 'query={log_type=\"audit\"} |= \"lab-outage-test\"' \\\n"
                "  --data-urlencode 'limit=1' | jq '.data.result | length'"
            ),
            "expect": "1",
            "checkpoint": "The count is 1 or more, so the record written during the outage arrived afterwards. A 0 means the delivery setting in Step 5 is not active.",
        },
    ],
    "glossary": [
        ("Object Lock", "An S3 feature that stops objects being deleted or overwritten for a set time."),
        ("KMS", "Key Management Service: AWS service that holds encryption keys."),
        ("Lifecycle rule", "A bucket rule that moves or expires objects by age."),
        ("Bearer token", "A string sent with a request to prove who is calling."),
        ("Alert rule (Grafana)", "A saved query and condition that raises an alert when the condition is true."),
        ("Write-once media", "Storage that cannot be rewritten after data is placed on it."),
    ],
    "next": "Next module: SIEM-3 Detect and Alert: rules that watch the logs, alerts that arrive in Mattermost, and a routine for reviewing them.",
}
