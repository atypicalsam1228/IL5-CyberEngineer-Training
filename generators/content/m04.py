"""M04: FIPS Cryptography and Keys (SC-13, SC-12, SC-28)."""

NIST = "nist-sp-800-53r5-full.md"
OVERVIEW = "u-cloud-computing-mission-owner-overview.md"
CSP_SRG = "u-cloud-service-provider-v1r6-srg.md"

EXPLAIN_COND = (
    "'{range .items[0].status.conditions[?(@.type==\"Encrypted\")]}{.reason}{\"\\n\"}{.message}{\"\\n\"}'"
)

MODULE = {
    "id": "M04",
    "slug": "Crypto",
    "title": "FIPS Cryptography and Keys",
    "draft": (
        "Commands follow Red Hat's published OpenShift Container Platform documentation (etcd encryption, TLS security "
        "profiles, FIPS) and the AWS CLI reference, but have not yet run in the lab. The node FIPS check reads the "
        "kernel flag in /proc, and the openssl messages on a FIPS node differ between releases, so the expected output "
        "is labeled as an example. The etcd pod lookup and the openssl cipher names are checked by the "
        "dry-run and by the first run of Test 1 and Test 4. Not confirmable without a live cluster: the AWS CLI "
        "version in the tools container (Test 5 needs AWS CLI v2 for base64 handling; confirm with aws --version), "
        "and whether the lab network can reach the router on port 443 for Test 4 (confirm with the first openssl "
        "command). Red Hat's documentation (the 4.21 guide and the matching OKD 4.22 guide) also describes an external "
        "KMS v2 option for etcd that is marked Technology Preview, is not recommended for production and needs the "
        "TechPreviewNoUpgrade feature set; this module does not use it."
    ),
    "controls": ["SC-13", "SC-12", "SC-28"],
    "mentions": ["SC-8", "SC-7", "CM-3"],
    "unit_values_ok": ["20 minutes"],
    "minutes": {"hands_on": 45, "verify": 20},
    "tools": [
        "OpenShift Container Platform (built with FIPS mode on)",
        "AWS Key Management Service (KMS)",
        "oc",
        "aws",
        "openssl",
        "jq",
    ],
    "diagrams": [
        {
            "id": "crypto",
            "title": "Encryption at rest under one customer-managed key",
            "caption": "The cluster nodes already run in FIPS mode. The steps set the TLS profile, start encrypting the cluster database, and put the disks and the backup bucket under a key you control. New parts are drawn with thick lines.",
            "per_step": True,
            "rankdir": "LR",
            "step_notes": {
                1: "You only read the state: the nodes are in FIPS mode and the cluster database holds secrets in plain form.",
                2: "The TLS profile is set on the API server and the router, and the cluster database starts encrypting its secrets.",
                3: "Rotation is turned on for the customer-managed key.",
                4: "Disk volumes and the backup bucket are encrypted by default with the same key.",
                5: "All three components report that the secrets are encrypted.",
            },
            "zones": [
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "aws", "label": "Your AWS account", "kind": "boundary"},
            ],
            "nodes": [
                {"id": "nodes", "title": "Cluster nodes", "sub": "FIPS mode on", "zone": "cluster", "kind": "ok"},
                {"id": "api", "title": "API server", "sub": "Handles requests", "zone": "cluster"},
                {"id": "router", "title": "Router", "sub": "Traffic into the cluster", "zone": "cluster"},
                {"id": "etcd", "title": "Cluster database", "sub": "Stored in etcd", "zone": "cluster"},
                {"id": "tls", "title": "TLS profile", "sub": "Intermediate", "zone": "cluster", "kind": "ok", "s": 2},
                {"id": "key", "title": "Customer-managed key", "sub": "AWS KMS", "zone": "aws"},
                {"id": "rot", "title": "Key rotation", "sub": "Turned on", "zone": "aws", "kind": "ok", "s": 3},
                {"id": "vol", "title": "Disk volumes", "sub": "EBS", "zone": "aws"},
                {"id": "bkt", "title": "Backup bucket", "sub": "S3", "zone": "aws"},
            ],
            "edges": [
                {"a": "nodes", "b": "api", "label": "Run"},
                {"a": "nodes", "b": "router", "label": "Run"},
                {"a": "api", "b": "etcd", "label": "Stores secrets in plain form", "kind": "bad", "s": 1, "until": 2},
                {"a": "api", "b": "etcd", "label": "Starts encrypting", "kind": "warn", "s": 2, "until": 5},
                {"a": "api", "b": "etcd", "label": "Encrypts with AES-GCM", "kind": "ok", "s": 5},
                {"a": "tls", "b": "api", "label": "Applies to", "s": 2},
                {"a": "tls", "b": "router", "label": "Applies to", "s": 2},
                {"a": "rot", "b": "key", "label": "Rotates", "s": 3},
                {"a": "vol", "b": "key", "label": "Encrypted with", "kind": "ok", "s": 4},
                {"a": "bkt", "b": "key", "label": "Encrypted with", "kind": "ok", "s": 4},
            ],
            "reading": [
                "The cluster nodes run in FIPS mode and host the API server and the router.",
                "A TLS profile is applied to the API server and the router.",
                "The API server encrypts secrets in etcd with AES-GCM once the rollout is complete.",
                "Disk volumes and the backup bucket are encrypted with the customer-managed key, and the key rotates.",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)"],
    "lab_needs": [
        "The lab AWS identity can call kms:DescribeKey, EnableKeyRotation, DisableKeyRotation, GetKeyRotationStatus, CreateKey (only with the tag ManagedBy=lab-exercise), TagResource, and Encrypt, Decrypt, DisableKey and ScheduleKeyDeletion (only on keys carrying that tag), the EC2 describe-volumes and default-encryption calls, and S3 get and put bucket encryption. DisableKeyRotation is used by lab start to turn rotation off before the module begins.",
        "KMS_KEY_ARN is a symmetric customer-managed key. The roles used by the cluster storage drivers and by the backup tool are allowed to use it.",
        "lab start m04 leaves etcd encryption off, the TLS profiles unset, and key rotation off.",
        "openssl in the tools container supports the s_client command with the -cipher option, and the AWS CLI in the tools container is version 2 (Test 5 passes base64 values).",
        "The lab network can reach the cluster router on port 443 (Test 4).",
    ],
    "lab": {
        "start": "lab start m04",
        "env": ["AWS_REGION", "KMS_KEY_ARN", "BACKUP_BUCKET"],
        "checks": [
            "A secret read directly from etcd starts with the AES-GCM encryption marker.",
            "Key rotation is on, cluster volumes use encryption, and the backup bucket's default encryption uses the customer-managed key.",
            "MD5 is refused on a FIPS node while SHA-256 works.",
            "The router refuses a weak cipher and negotiates TLS 1.2 or higher with an approved cipher.",
            "A disabled key cannot decrypt data.",
        ],
    },
    "requirement": (
        "An IL5 system must use cryptography that has been validated against the federal standard, must keep data "
        "encrypted where it is stored, and must control the keys that do the encrypting. This module checks that the "
        "platform runs in FIPS mode, sets the TLS profile on the platform, turns on encryption of the cluster "
        "database, and puts the storage encryption keys under a customer-managed key with rotation. Each step is "
        "followed by a check that the setting works and a check that a weaker setting fails."
    ),
    "mapping": [
        {
            "control": "SC-13 Cryptographic Protection",
            "plain": "Use the kinds of cryptography the organization has approved for each use, implemented by validated modules.",
            "source": "NIST; DoD SRG",
            "covered": "Step 1 reads the FIPS state of the nodes and the TLS profiles. Step 2 sets the TLS profile. Tests 3 and 4 show a weak algorithm and a weak cipher refused.",
            "cite": [
                {"file": NIST, "quote": "Implement the following types of cryptography required for each specified cryptographic use"},
                {"file": OVERVIEW, "quote": "Use FIPS 140-2 or FIPS 140-3 validated cryptography modules (minimally Impact Level 1)"},
                {"file": OVERVIEW, "quote": "operated in FIPS mode in accordance with federal government policy/standards for the protection of all CUI."},
            ],
        },
        {
            "control": "SC-12 Cryptographic Key Establishment and Management",
            "plain": "Keys are generated, stored, used, rotated and destroyed under rules, and the system owner controls them.",
            "source": "NIST; DoD SRG",
            "covered": "Step 3 turns on rotation for the customer-managed key. Test 5 disables a key and shows data can no longer be decrypted.",
            "cite": [
                {"file": NIST, "quote": "Establish and manage cryptographic keys when cryptography is employed within the system in accordance with the following key management requirements"},
                {"file": OVERVIEW, "quote": "CSP Mission Owner maintains control of the keys, from creation through storage and use to destruction."},
                {"file": CSP_SRG, "quote": "FIPS 140-2 or FIPS 140-3 Level 3 accreditation."},
            ],
        },
        {
            "control": "SC-28 Protection of Information at Rest",
            "plain": "Stored information is encrypted, and the keys for it are protected.",
            "source": "NIST; DoD SRG",
            "covered": "Steps 2, 4 and 5 turn on etcd, volume and bucket encryption. Tests 1 and 2 read the evidence.",
            "cite": [
                {"file": NIST, "quote": "of the following information at rest"},
                {"file": OVERVIEW, "quote": "Implement FIPS 140-2/3 compliant, data-at-rest encryption on all DOD files housed in CSP IaaS storage service offerings."},
            ],
        },
    ],
    "intent": [
        {
            "control": "SC-13 Cryptographic Protection",
            "feared": "Data is encrypted with something that looks strong but was never validated, so the protection cannot be shown to an assessor.",
            "scope": "Every place the system uses cryptography: node operating systems, platform TLS, storage, and signing.",
            "question": "For each use of cryptography, can you name the module that does it and show it is validated and running in FIPS mode?",
            "evidence": "The FIPS state of the nodes, the TLS profile of each platform endpoint, and a failed attempt to use a non-approved algorithm.",
            "sufficient": "The DoD Cloud Computing SRG accepts FIPS 140-2 or FIPS 140-3 validated modules operated in FIPS mode. This lab uses FIPS 140-3 or the current version for hardware, software and firmware components, and TLS for all network session traffic. Red Hat describes its modules as FIPS validated or Modules In Process, so record each module's status. The approved version and level for each use are organization-defined, so find them in the SSP.",
            "tieoff": "Someone tracks the validation status of the modules and re-checks when a platform release changes.",
            "tool": "OpenShift built in FIPS mode (Step 1) and the platform TLS profile (Step 2).",
        },
        {
            "control": "SC-12 Cryptographic Key Establishment and Management",
            "feared": "Whoever holds the keys can read everything, or a lost or leaked key cannot be dealt with.",
            "scope": "Keys for data at rest: the AWS KMS key used for volumes and buckets, and the etcd encryption keys.",
            "question": "Who can use each key, who can change it, and what happens to the data if the key is disabled?",
            "evidence": "The key description, the rotation status, the key policy, and a test that a disabled key stops decryption.",
            "sufficient": "Keys are generated in FIPS validated hardware, access is limited by IAM policy and key policy, and destruction is by scheduled deletion with a mandatory waiting period. The DoD SRG requires hardware security modules used in cloud-based key management to have FIPS 140-2 or 140-3 Level 3 accreditation. The rotation interval is organization-defined, so read it from the SSP or ask the ISSO before you rely on the AWS default.",
            "tieoff": "Someone owns the key policy and reviews who is on it.",
            "tool": "Step 3 turns on rotation for the key, and Test 5 shows what disabling a key does.",
        },
        {
            "control": "SC-28 Protection of Information at Rest",
            "feared": "Someone gets a copy of a disk, a snapshot, a bucket or the cluster database and reads it in plain text.",
            "scope": "The cluster database (etcd), the volumes the cluster uses, and the backup bucket.",
            "question": "If you were handed a raw copy of each place data is stored, what would you see?",
            "evidence": "The raw value of a secret in etcd, the key used by each volume, and the bucket's default encryption setting.",
            "sufficient": "Each store is encrypted, the keys for storage are managed in AWS KMS, and the controls are documented in the SSP. The DoD SRG says to implement FIPS 140-2 or 140-3 compliant data-at-rest encryption for files in IaaS storage services.",
            "tieoff": "Something detects a new volume or bucket that is not encrypted. Default encryption (Step 4) prevents most of them.",
            "tool": "etcd encryption (Step 2), default volume encryption and bucket encryption with the customer-managed key (Step 4).",
        },
    ],
    "architect": (
        "Decide before you build. For each store (etcd, volumes, buckets) decide which key protects it and who may use "
        "that key. For each network endpoint decide the lowest TLS version and the allowed ciphers. Find the "
        "organization-defined values first: the approved FIPS version and level, and the key rotation interval."
    ),
    "terms": [
        ("FIPS 140", "The federal standard for cryptographic modules. A module is validated when an accredited lab has tested it against the standard. Versions 140-2 and 140-3 both appear in the sources."),
        ("FIPS mode", "A setting that makes the operating system use only the validated modules and approved algorithms."),
        ("TLS security profile", "A named setting (Old, Intermediate or Modern) that fixes the lowest TLS version and the allowed ciphers for a platform endpoint."),
        ("Cipher", "The algorithm that encrypts the data. A TLS connection picks one from the list both sides allow."),
        ("etcd", "The database where the cluster keeps its configuration and its secrets."),
        ("Customer-managed key", "An AWS KMS key that you create and control, as opposed to a key AWS creates and manages for you."),
        ("Key rotation", "Replacing the key material in a key on a schedule, so old key material is used less and less."),
        ("Cryptographic erase", "Making data unreadable by destroying or disabling the key that encrypts it."),
        ("Data at rest", "Information that is stored, not moving across a network."),
    ],
    "concepts": [
        {
            "heading": "2.1 Validated cryptography and FIPS mode",
            "paras": [
                "What is this? FIPS 140 is the federal standard for the software and hardware that do encryption. A validated module has been tested by a lab. FIPS mode is the setting that makes a system use only those modules. Both matter: the DoD Cloud Computing SRG says to use validated modules and to operate them in FIPS mode.",
                "Why? Without FIPS mode a system can silently fall back to an algorithm that is not approved. The OpenShift cluster in this lab is installed with FIPS mode on, and FIPS mode can only be chosen at install time, so you check it rather than set it. Read Red Hat's wording carefully: it says OpenShift uses FIPS validated or Modules In Process modules from the operating system, and that TLS FIPS support is not yet complete. Record the validation status of each module in your evidence instead of assuming every module is validated.",
            ],
            "table": {
                "headers": ["Parameter", "Value", "Where it is set"],
                "rows": [
                    ("Cryptography standard", "FIPS 140-3 or the current version", "The lab (SC-13)"),
                    ("Accepted validated modules", "FIPS 140-2 or FIPS 140-3, operated in FIPS mode", "DoD Cloud Computing SRG"),
                    ("Key management hardware (HSM)", "FIPS 140-2 or FIPS 140-3 Level 3", "DoD Cloud Service Provider SRG (cloud-based key management)"),
                    ("Validated modules apply at", "All Impact Levels (the SRG says minimally Impact Level 1)", "DoD Cloud Computing SRG (data at rest)"),
                    ("Network session traffic", "TLS", "The lab (SC-13)"),
                    ("Key rotation interval", "Organization-defined", "Your SSP"),
                    ("Encryption algorithm for the cluster database", "Organization-defined", "Your SSP"),
                ],
            },
        },
        {
            "heading": "2.2 TLS security profiles",
            "paras": [
                "TLS (Transport Layer Security) is the encryption used on web connections. OpenShift lets you choose a TLS security profile for the API server, the ingress router (which handles traffic into the cluster) and the kubelet (the agent on each node). The profile fixes the lowest TLS version and the list of ciphers.",
                "Intermediate requires TLS 1.2 or higher and offers only modern ciphers. Old also allows older versions and older ciphers. Modern is stricter than Intermediate. This lab uses TLS on all network sessions, and the requirement does not name a profile. Which profile your organization requires is organization-defined, so find it in the SSP. Intermediate is the platform default, so setting it explicitly records the choice and does not change behavior.",
            ],
            "table": {
                "headers": ["Profile", "Meaning"],
                "rows": [
                    ("Old", "Accepts older TLS versions and ciphers for old clients"),
                    ("Intermediate", "TLS 1.2 or higher and modern ciphers (the control plane default)"),
                    ("Modern", "The strictest built-in profile: TLS 1.3 only. Red Hat marks it currently unsupported on some endpoints, so Intermediate is the profile this lab uses"),
                    ("Custom", "You list the version and ciphers yourself"),
                ],
            },
        },
        {
            "heading": "2.3 Encryption at rest: three stores",
            "paras": [
                "etcd is the cluster database. It holds every secret in the cluster. OpenShift does not encrypt it until you turn encryption on. Volumes hold program data, and AWS can encrypt them with a KMS key. Buckets hold backups and logs, and S3 can encrypt each object with a KMS key by default.",
            ],
            "diagram": (
                "Secret in etcd  --> encrypted by the API server (AES-GCM) --> key stored in the cluster\n"
                "Volume (EBS)    --> encrypted by AWS with the customer-managed key\n"
                "Object (S3)     --> encrypted by AWS with the customer-managed key"
            ),
        },
        {
            "heading": "2.4 Who controls the key",
            "paras": [
                "The DoD Cloud Computing SRG says the mission owner keeps control of the keys from creation through storage and use to destruction. A customer-managed key in AWS KMS gives you the controls for that: a key policy that names who can use it, rotation, and disable or scheduled deletion.",
                "Disabling or destroying a key makes everything encrypted under it unreadable. That is cryptographic erase, and the SRG describes it as a way to destroy data or clean up a data spill without the cloud provider's help. Test 5 shows it on a throwaway key.",
                "Two cautions from the SRG. It says one key should not be used to encrypt all or large chunks of Mission Owner data, so the single lab key in this module is a teaching simplification and your SSP decides how many keys you need. It also describes the options for key control as a hardware security module, a dedicated HSM service, or a cloud KMS service evaluated by NSA, so confirm with the ISSO that the KMS in use meets that.",
            ],
        },
    ],
    "steps": [
        {
            "title": "Read the platform's cryptographic state (SC-13)",
            "why": "Before changing anything, read what is set now. FIPS mode is a kernel setting on each node. A value of 1 means the kernel is running in FIPS mode. An empty TLS profile means the platform default is in use.",
            "blocks": [
                {
                    "code": (
                        "NODE=$(oc get nodes -o jsonpath='{.items[0].metadata.name}')\n"
                        "oc debug node/$NODE -- chroot /host cat /proc/sys/crypto/fips_enabled\n"
                        "oc get configmap cluster-config-v1 -n kube-system -o jsonpath='{.data.install-config}' | grep -i fips\n"
                        "oc get apiserver cluster -o jsonpath='{.spec.tlsSecurityProfile}{\"\\n\"}'\n"
                        "oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.tlsSecurityProfile}{\"\\n\"}'\n"
                        "oc get apiserver cluster -o jsonpath='{.spec.encryption}{\"\\n\"}'"
                    ),
                    "lines": [
                        ("NODE=$(...)", "Saves the name of the first node in a variable."),
                        ("oc debug node/$NODE -- chroot /host cat ...", "Opens a short-lived shell on the node and reads the kernel's FIPS flag. The result 1 means FIPS mode is on."),
                        ("oc get configmap cluster-config-v1 ... grep", "Reads the install settings the cluster was built with. Look for fips: true."),
                        ("oc get apiserver ... tlsSecurityProfile", "Shows the API server's TLS profile. Empty means the default, which is Intermediate."),
                        ("oc get ingresscontroller ...", "Shows the router's TLS profile. Empty means it follows the API server."),
                        ("... .spec.encryption", "Shows the etcd encryption setting. Empty means etcd is not encrypted."),
                    ],
                }
            ],
            "note": "oc debug prints a few extra lines about starting the node shell. The one-character answer 1 is the line that matters. Red Hat states that FIPS cannot be turned on after a cluster is deployed, and that TLS FIPS support is not complete in this release. If the node prints 0, the cluster has to be rebuilt; no setting in this module fixes it.",
            "action": "Run the block and write down the six answers.",
            "checkpoint": "The node prints 1, the install settings show fips: true, and the TLS profiles and the encryption setting are empty.",
        },
        {
            "title": "Set the TLS profile and turn on etcd encryption (SC-13, SC-28)",
            "why": "An empty setting relies on a default that can change with a release. Setting the profile makes the choice explicit and visible to an assessor. The same change to the API server object also turns on etcd encryption with AES-GCM. Neither NIST nor the SRG names an algorithm for the cluster database, so use the one in your SSP. Red Hat documents two types, aesgcm and aescbc, and this lab uses aesgcm. The platform rolls the change out, which takes a while. OpenShift rotates the etcd encryption keys on its own schedule, which is separate from the AWS KMS key in Step 3.",
            "blocks": [
                {
                    "code": (
                        "oc patch apiserver cluster --type=merge --dry-run=server -p '{\"spec\":{\"encryption\":{\"type\":\"aesgcm\"},\"tlsSecurityProfile\":{\"type\":\"Intermediate\",\"intermediate\":{}}}}'\n"
                        "oc patch apiserver cluster --type=merge -p '{\"spec\":{\"encryption\":{\"type\":\"aesgcm\"},\"tlsSecurityProfile\":{\"type\":\"Intermediate\",\"intermediate\":{}}}}'\n"
                        "oc patch ingresscontroller default -n openshift-ingress-operator --type=merge -p '{\"spec\":{\"tlsSecurityProfile\":{\"type\":\"Intermediate\",\"intermediate\":{}}}}'"
                    ),
                    "lines": [
                        ("--dry-run=server", "Checks the change without saving it."),
                        ("oc patch apiserver cluster", "Changes the API server object: encryption type aesgcm and the Intermediate TLS profile."),
                        ("--type=merge -p '{...}'", "Merges the JSON into the object and leaves other settings alone."),
                        ("oc patch ingresscontroller default", "Sets the same profile on the router that handles traffic into the cluster."),
                    ],
                }
            ],
            "security": "Do not take an etcd backup until Step 5 reports that encryption is complete. A backup taken part way through can be only partly encrypted.",
            "tip": "Keep the three patches in git, so changes to cryptographic settings show who changed them and when (CM-3).",
            "action": "Run the three commands. The API server restarts its pods, and on a single-node cluster oc can fail for several minutes. Retry the command if it does.",
            "checkpoint": "Both patch commands print patched.",
        },
        {
            "title": "Turn on rotation for the customer-managed key (SC-12)",
            "why": "The lab gives you a customer-managed key in AWS KMS (KMS_KEY_ARN). Check it is one you control and that it is a key AWS can rotate, then turn rotation on. The rotation interval is organization-defined, so this lab uses the setting AWS applies when you do not choose.",
            "blocks": [
                {
                    "code": (
                        "aws kms describe-key --key-id \"$KMS_KEY_ARN\" --region \"$AWS_REGION\" --query 'KeyMetadata.{Manager:KeyManager,State:KeyState,Spec:KeySpec,Origin:Origin}' --output json\n"
                        "aws kms enable-key-rotation --key-id \"$KMS_KEY_ARN\" --region \"$AWS_REGION\"\n"
                        "aws kms get-key-rotation-status --key-id \"$KMS_KEY_ARN\" --region \"$AWS_REGION\""
                    ),
                    "lines": [
                        ("describe-key ... --query", "Shows who manages the key (CUSTOMER means you), its state, its type and where the key material came from."),
                        ("enable-key-rotation", "Turns on automatic rotation for the key."),
                        ("get-key-rotation-status", "Confirms rotation is on."),
                    ],
                }
            ],
            "note": "Rotation replaces the key material inside the same key. Data encrypted earlier stays readable, and nothing needs re-encrypting.",
            "action": "Run the three commands.",
            "checkpoint": "Manager is CUSTOMER, State is Enabled, and KeyRotationEnabled is true.",
        },
        {
            "title": "Encrypt volumes and the backup bucket with the key (SC-28, SC-12)",
            "why": "Default encryption makes the safe choice automatic. Setting it means a new volume or object is encrypted under your key even if nobody asks for encryption. These are the two storage services this lab covers.",
            "blocks": [
                {
                    "code": (
                        "aws ec2 enable-ebs-encryption-by-default --region \"$AWS_REGION\"\n"
                        "aws ec2 modify-ebs-default-kms-key-id --kms-key-id \"$KMS_KEY_ARN\" --region \"$AWS_REGION\"\n"
                        "aws ec2 get-ebs-default-kms-key-id --region \"$AWS_REGION\"\n"
                        "aws s3api put-bucket-encryption --bucket \"$BACKUP_BUCKET\" --region \"$AWS_REGION\" --server-side-encryption-configuration \"$(jq -n --arg k \"$KMS_KEY_ARN\" '{Rules:[{ApplyServerSideEncryptionByDefault:{SSEAlgorithm:\"aws:kms\",KMSMasterKeyID:$k},BucketKeyEnabled:true}]}')\"\n"
                        "aws s3api get-bucket-encryption --bucket \"$BACKUP_BUCKET\" --region \"$AWS_REGION\""
                    ),
                    "lines": [
                        ("enable-ebs-encryption-by-default", "New volumes in this region are encrypted automatically."),
                        ("modify-ebs-default-kms-key-id", "Says which key encrypts them: your customer-managed key."),
                        ("get-ebs-default-kms-key-id", "Reads the setting back."),
                        ("put-bucket-encryption ... jq -n", "Builds the setting with jq so the key address is filled in without typing it. Every new object in the bucket is encrypted with your key."),
                        ("get-bucket-encryption", "Reads the bucket setting back."),
                    ],
                }
            ],
            "note": "These settings apply to new volumes and new objects. Volumes that already exist keep the encryption they were created with. Test 2 lists them. One key for both stores is a lab simplification; the SRG says one key should not encrypt large chunks of data (see 2.4).",
            "action": "Run the block and read the last two answers.",
            "checkpoint": "The default key is your key address, and the bucket's rule shows aws:kms with the same key address.",
        },
        {
            "title": "Wait for etcd encryption to finish (SC-28)",
            "why": "Turning on etcd encryption starts a background job that rewrites every secret in encrypted form. Red Hat documents that it can take 20 minutes or longer. Three components report their own progress, and all three must say the work is complete.",
            "blocks": [
                {
                    "code": (
                        f"oc get openshiftapiserver -o=jsonpath={EXPLAIN_COND}\n"
                        f"oc get kubeapiserver -o=jsonpath={EXPLAIN_COND}\n"
                        f"oc get authentication.operator.openshift.io -o=jsonpath={EXPLAIN_COND}"
                    ),
                    "lines": [
                        ("oc get openshiftapiserver ...", "Reads the Encrypted status of the OpenShift API server."),
                        ("oc get kubeapiserver ...", "Reads the same status for the Kubernetes API server."),
                        ("oc get authentication.operator.openshift.io ...", "Reads it for the OAuth servers that handle logins."),
                        ("jsonpath range ... Encrypted", "Prints the reason and the message from the condition named Encrypted."),
                    ],
                }
            ],
            "note": "EncryptionInProgress means keep waiting. Run the block again every few minutes while you do the checks in Test 2 and Test 3.",
            "action": "Run the block until all three print EncryptionCompleted.",
            "checkpoint": "All three components print EncryptionCompleted.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "A secret is stored encrypted in etcd",
            "why": "Do not trust the status message alone. Read the stored value from etcd itself. An encrypted value starts with a marker that names the algorithm.",
            "code": (
                "ETCD_POD=$(oc get pods -n openshift-etcd -l app=etcd -o name | head -1)\n"
                "oc exec -n openshift-etcd $ETCD_POD -- etcdctl get /kubernetes.io/secrets/openshift-config/pull-secret --print-value-only | head -c 18\n"
                "echo"
            ),
            "expect": "Example only.\nk8s:enc:aesgcm:v1:",
            "checkpoint": "The value starts with k8s:enc:aesgcm. Before encryption was on, it started with k8s and unreadable characters instead.",
        },
        {
            "kind": "positive",
            "title": "The key rotates and storage uses it",
            "why": "Show the three pieces of evidence an assessor asks for: rotation on, volumes encrypted, bucket encrypted with your key.",
            "code": (
                "aws kms get-key-rotation-status --key-id \"$KMS_KEY_ARN\" --region \"$AWS_REGION\"\n"
                "aws ec2 describe-volumes --region \"$AWS_REGION\" --filters \"Name=tag-key,Values=kubernetes.io/cluster/*\" --query 'Volumes[].{Volume:VolumeId,Encrypted:Encrypted,Key:KmsKeyId}' --output table\n"
                "aws s3api get-bucket-encryption --bucket \"$BACKUP_BUCKET\" --region \"$AWS_REGION\" | jq '.ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault'"
            ),
            "expect": (
                "Example only. Your identifiers will differ.\n"
                "{ \"KeyRotationEnabled\": true, ... other fields such as the next rotation date }\n"
                "| Volume | Encrypted | Key |\n"
                "| vol-0abc | True | arn:aws:kms:region:account:key/example |\n"
                "{ \"SSEAlgorithm\": \"aws:kms\", \"KMSMasterKeyID\": \"arn:aws:kms:region:account:key/example\" }"
            ),
            "checkpoint": "Rotation is true, every cluster volume shows Encrypted True, and the bucket shows aws:kms. A volume that shows a different key was created before default encryption was set, so note it for the owner.",
        },
        {
            "kind": "negative",
            "title": "A non-approved algorithm is refused on the FIPS node",
            "why": "FIPS mode works if it removes the algorithms that are not approved. SHA-256 is approved. MD5 is not.",
            "code": (
                "NODE=$(oc get nodes -o jsonpath='{.items[0].metadata.name}')\n"
                "oc debug node/$NODE -- chroot /host sh -c 'echo test | openssl sha256'\n"
                "oc debug node/$NODE -- chroot /host sh -c 'echo test | openssl md5'"
            ),
            "expect": (
                "Example only. Wording varies by release.\n"
                "SHA2-256(stdin)= f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2\n"
                "Error setting digest\n"
                "(error text that includes the word unsupported)"
            ),
            "checkpoint": "SHA-256 prints a hash. MD5 prints an error and no hash.",
        },
        {
            "kind": "negative",
            "title": "The router refuses a weak cipher",
            "why": "Ask the router to use an older cipher that the Intermediate profile does not allow. First show what it does negotiate.",
            "code": (
                "oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.tlsSecurityProfile.type}{\"\\n\"}'\n"
                "HOST=$(oc get route console -n openshift-console -o jsonpath='{.spec.host}')\n"
                "openssl s_client -connect \"$HOST:443\" -servername \"$HOST\" </dev/null 2>&1 | grep -E \"Protocol|Cipher\"\n"
                "openssl s_client -connect \"$HOST:443\" -servername \"$HOST\" -tls1_2 -cipher AES128-SHA </dev/null 2>&1 | grep -i \"cipher is\"\n"
                "openssl s_client -connect \"$HOST:443\" -servername \"$HOST\" -tls1_2 -cipher ECDHE-RSA-AES128-GCM-SHA256 </dev/null 2>&1 | grep -i \"cipher is\""
            ),
            "expect": (
                "Example only.\n"
                "Intermediate\n"
                "Protocol  : TLSv1.3\n"
                "Cipher    : TLS_AES_256_GCM_SHA384\n"
                "New, (NONE), Cipher is (NONE)\n"
                "New, TLSv1.2, Cipher is ECDHE-RSA-AES128-GCM-SHA256"
            ),
            "checkpoint": "The profile reads Intermediate. The first openssl command negotiates TLS 1.2 or higher with an approved cipher. The weak cipher shows (NONE) or prints nothing, meaning no connection was made. The last command, with an Intermediate cipher, connects: that shows the weak cipher was refused by the router and not by a missing feature in your openssl. The default profile refuses the weak cipher too; setting the profile explicitly is what makes the choice visible.",
        },
        {
            "kind": "negative",
            "title": "A disabled key cannot decrypt (cryptographic erase)",
            "why": "Create a throwaway key tagged ManagedBy=lab-exercise (the lab identity may only disable or delete keys that carry this tag), encrypt a word, then disable the key and try to decrypt. Then schedule the key for deletion so it does not stay in your account. Never run this against your real key.",
            "code": (
                "KEY_ID=$(aws kms create-key --description \"lab throwaway key\" --tags TagKey=ManagedBy,TagValue=lab-exercise --region \"$AWS_REGION\" --query KeyMetadata.KeyId --output text)\n"
                "CT=$(aws kms encrypt --key-id \"$KEY_ID\" --plaintext aGVsbG8= --region \"$AWS_REGION\" --query CiphertextBlob --output text)\n"
                "aws kms decrypt --ciphertext-blob \"$CT\" --region \"$AWS_REGION\" --query Plaintext --output text\n"
                "aws kms disable-key --key-id \"$KEY_ID\" --region \"$AWS_REGION\"\n"
                "aws kms decrypt --ciphertext-blob \"$CT\" --region \"$AWS_REGION\" --query Plaintext --output text\n"
                "aws kms schedule-key-deletion --key-id \"$KEY_ID\" --pending-window-in-days 7 --region \"$AWS_REGION\""
            ),
            "expect": (
                "Example only.\n"
                "aGVsbG8=\n"
                "An error occurred (DisabledException) when calling the Decrypt operation: ... is disabled."
            ),
            "checkpoint": "The first decrypt prints the encoded word. After the key is disabled, decrypt fails with DisabledException. The last command schedules deletion using the shortest waiting period AWS accepts.",
        },
    ],
    "glossary": [
        ("AES-GCM", "An approved encryption algorithm that also detects tampering."),
        ("HSM", "Hardware Security Module: tamper-resistant hardware that generates and protects keys."),
        ("KMS", "AWS Key Management Service: the AWS service that creates and controls encryption keys."),
        ("EBS", "Elastic Block Store: the AWS service that provides disk volumes."),
        ("S3", "Simple Storage Service: the AWS object storage service. Its containers are called buckets."),
        ("Router (ingress)", "The part of OpenShift that receives web traffic into the cluster."),
        ("Kubelet", "The agent on each node that runs the pods."),
        ("Key policy", "The rule document on a KMS key that says who may use and manage it."),
    ],
    "next": "Next module: M03 Boundary and Default-Deny: which components may talk to which, and whether traffic is protected only at the boundary or also between internal components.",
}
