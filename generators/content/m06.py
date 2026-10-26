"""M06: Privileged access (OpenShift RBAC, Session Manager jump host, session records in the SIEM)."""

NIST = "nist-sp-800-53r5-full.md"
FEDRAMP = "fedramp-high-baseline.md"

JUMP_TF = r"""terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {}

variable "vpc_id" {
  type = string
}

variable "kms_key_arn" {
  type = string
}

variable "lab_id" {
  type = string
}

data "aws_vpc" "lab" {
  id = var.vpc_id
}

data "aws_subnets" "lab" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_security_group" "jump" {
  name        = "jump-${var.lab_id}"
  description = "Jump host with no inbound rules"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_egress_rule" "ssm_https" {
  security_group_id = aws_security_group.jump.id
  description       = "HTTPS to the Systems Manager endpoints inside the VPC"
  cidr_ipv4         = data.aws_vpc.lab.cidr_block
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_cloudwatch_log_group" "sessions" {
  name       = "/il5/ssm-sessions/${var.lab_id}"
  kms_key_id = var.kms_key_arn
}

resource "aws_iam_role" "jump" {
  name = "jump-${var.lab_id}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.jump.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "session_logs" {
  name = "session-logs"
  role = aws_iam_role.jump.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:DescribeLogGroups"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogStreams"]
        Resource = "${aws_cloudwatch_log_group.sessions.arn}:*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "jump" {
  name = "jump-${var.lab_id}"
  role = aws_iam_role.jump.name
}

locals {
  session_inputs = {
    s3BucketName                = ""
    s3KeyPrefix                 = ""
    s3EncryptionEnabled         = true
    cloudWatchLogGroupName      = aws_cloudwatch_log_group.sessions.name
    cloudWatchEncryptionEnabled = true
    cloudWatchStreamingEnabled  = true
    kmsKeyId                    = ""
    runAsEnabled                = false
    runAsDefaultUser            = ""
    idleSessionTimeout          = "15"
    maxSessionDuration          = ""
  }
}

resource "aws_ssm_document" "session_preferences" {
  name            = "SSM-SessionManagerRunShell"
  document_type   = "Session"
  document_format = "JSON"
  content = jsonencode({
    schemaVersion = "1.0"
    description   = "Session Manager preferences for the jump host"
    sessionType   = "Standard_Stream"
    inputs = merge(local.session_inputs, {
      shellProfile = { windows = "", linux = "" }
    })
  })
}

resource "aws_ssm_document" "logged_command" {
  name            = "il5-logged-command-${var.lab_id}"
  document_type   = "Session"
  document_format = "JSON"
  content = jsonencode({
    schemaVersion = "1.0"
    description   = "Logged session that runs one command and ends"
    sessionType   = "Standard_Stream"
    inputs = merge(local.session_inputs, {
      shellProfile = { windows = "", linux = "id; echo m06-session-marker; exit" }
    })
  })
}

resource "aws_instance" "jump" {
  ami                         = data.aws_ssm_parameter.al2023.value
  instance_type               = "t3.micro"
  subnet_id                   = sort(data.aws_subnets.lab.ids)[0]
  vpc_security_group_ids      = [aws_security_group.jump.id]
  iam_instance_profile        = aws_iam_instance_profile.jump.name
  associate_public_ip_address = false

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "jump-${var.lab_id}"
  }
}

output "instance_id" {
  value = aws_instance.jump.id
}

output "security_group_id" {
  value = aws_security_group.jump.id
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.sessions.name
}

output "session_document_name" {
  value = aws_ssm_document.logged_command.name
}
""".rstrip()

MODULE = {
    "id": "M06",
    "slug": "Privileged",
    "title": "Privileged Access and Session Audit",
    "draft": (
        "Commands follow Red Hat's OpenShift RBAC documentation, the HashiCorp AWS provider, and the AWS Systems Manager Session Manager documentation but have not yet run in the lab. "
        "Role bindings are validated with a server dry run before they are applied. Two items are the least certain and are checked first when the lab is built: "
        "whether a named Standard_Stream preferences document whose shell profile ends in exit closes the session cleanly and still writes records to the log group "
        "(check with aws logs describe-log-streams --log-group-name \"$LOG_GROUP\" after the first session), "
        "and the exact audit field names for an impersonated request (check by printing one Loki audit record and listing its keys with jq). "
        "AWS documents the account-wide preferences for sessions started without a document name, so the tests use a named Standard_Stream document instead of AWS-StartInteractiveCommand (AWS also states that streaming session data is not supported for interactive commands). "
        "The jump host uses the newest Amazon Linux 2023 image from the public parameter; AWS notes the default AL2023 kernel is not always the FIPS-validated one, so a FIPS requirement on the jump host is a decision for the lab owner."
    ),
    "controls": ["AC-6", "AC-17", "AU-14"],
    "mentions": ["IA-2", "AC-2", "AC-11", "AU-6", "SC-7"],
    "unit_values_ok": ["30 seconds", "90 seconds", "15 minutes", "15 minute"],
    "minutes": {"hands_on": 45, "verify": 20},
    "tools": ["OpenShift Container Platform", "AWS Systems Manager Session Manager", "Terraform", "Loki and Grafana (free, open source)", "oc", "aws", "curl", "jq"],
    "diagrams": [
        {
            "id": "access",
            "title": "Three roles inside, one door to the jump host",
            "caption": "Roles decide what each person may do in the cluster. The jump host has no way in except Session Manager, and everything done there is recorded and copied to Loki. Each step below adds parts, drawn with thick lines.",
            "per_step": True,
            "rankdir": "LR",
            "step_notes": {
                1: "Three people get three roles: an administrator limited to namespaces, a developer limited to the demo namespace, and a read-only auditor.",
                2: "The permission check proves each role. The administrator may create namespaces, the developer is refused, and the auditor can only read.",
                3: "The jump host has no inbound rule, no public address and no key pair. It connects out to Systems Manager and writes session records to a log group.",
                4: "You start a session through Systems Manager, and a script copies the session records into Loki, next to the audit records.",
            },
            "zones": [
                {"id": "people", "label": "People", "kind": "group"},
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "siem", "label": "Loki, the log store", "parent": "cluster", "kind": "group"},
                {"id": "api", "label": "Cluster control plane", "parent": "cluster", "kind": "group"},
                {"id": "aws", "label": "Your AWS account", "kind": "boundary"},
                {"id": "vpc", "label": "Lab network (VPC)", "parent": "aws", "kind": "group"},
                {"id": "svc", "label": "AWS services", "parent": "aws", "kind": "group"},
            ],
            "nodes": [
                {"id": "admin", "title": "Administrator", "sub": "User admin1, role il5-platform-admin", "zone": "people", "s": 1},
                {"id": "dev", "title": "Developer", "sub": "User dev1, role edit in demo only", "zone": "people", "s": 1},
                {"id": "audit", "title": "Auditor", "sub": "User audit1, role cluster-reader", "zone": "people", "s": 1},
                {"id": "you", "title": "You", "sub": "Start the session", "zone": "people", "s": 4},
                {"id": "kapi", "title": "Kubernetes API", "sub": "Checks every request", "zone": "api"},
                {"id": "loki", "title": "Loki", "sub": "Audit and session records", "zone": "siem", "kind": "ok"},
                {"id": "jump", "title": "Jump host", "sub": "No inbound rule, no public address, no key pair", "zone": "vpc", "kind": "ok", "s": 3},
                {"id": "ssm", "title": "Systems Manager", "sub": "Session Manager", "zone": "svc", "s": 3},
                {"id": "logs", "title": "Log group", "sub": "Session records", "zone": "svc", "s": 3},
            ],
            "edges": [
                {"a": "admin", "b": "kapi", "label": "Create namespace: allowed", "kind": "ok", "s": 2},
                {"a": "dev", "b": "kapi", "label": "Create namespace: refused", "kind": "bad", "s": 2},
                {"a": "audit", "b": "kapi", "label": "Read only", "kind": "ok", "s": 2},
                {"a": "kapi", "b": "loki", "label": "Audit record"},
                {"a": "jump", "b": "ssm", "label": "Connects out", "kind": "ok", "s": 3},
                {"a": "jump", "b": "logs", "label": "Writes", "n": 2, "s": 3},
                {"a": "you", "b": "ssm", "label": "Start session", "n": 1, "kind": "ok", "s": 4, "minlen": 2},
                {"a": "logs", "b": "loki", "label": "Copy with script", "n": 3, "kind": "ok", "s": 4},
            ],
            "reading": [
                "The administrator may create namespaces, the developer is refused, and the auditor can only read.",
                "The Kubernetes API sends an audit record of each request to Loki.",
                "The jump host connects out to Systems Manager, so nothing connects in.",
                "A session started through Systems Manager is written to a log group (flow 2), then copied into Loki (flow 3).",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)", "SIEM-1 (audit logs reaching Loki)"],
    "lab_needs": [
        "The Session Manager plugin installed in the lab shell (the aws command needs it to open sessions).",
        "A subnet in VPC_ID that can reach the Systems Manager service privately (VPC endpoints for ssm, ssmmessages and ec2messages inside the VPC).",
        "AWS credentials in the lab shell that may create EC2, IAM, CloudWatch Logs and Systems Manager resources, and read the public AMI parameter.",
        "A KMS key policy that lets CloudWatch Logs use KMS_KEY_ARN.",
        "No Session Manager preferences document exists yet in the account and Region (Terraform creates SSM-SessionManagerRunShell).",
        "Terraform can download the AWS provider from the internet.",
        "Audit logs already reach Loki (SIEM-1 done), and the Loki address accepts log pushes.",
    ],
    "lab": {
        "start": "lab start m06",
        "env": ["LOKI_URL", "LOKI_CA_FILE", "LOKI_USER", "LOKI_PASSWORD", "VPC_ID", "KMS_KEY_ARN", "LAB_ID"],
        "checks": [
            "Three roles exist (administrator, developer, auditor) and oc auth can-i shows the expected yes and no for each.",
            "An administrator action succeeds and its audit record reaches Loki with the administrator named.",
            "A developer is refused the same action and the refusal is recorded.",
            "The jump host is online in Session Manager, has no public address, no key pair and no inbound rule.",
            "A session on the jump host is recorded and the record is searchable in Loki.",
        ],
    },
    "requirement": (
        "An IL5 system must give each person only the access their duties need, allow remote administration only through approved and controlled paths, "
        "and be able to record what happens in a privileged session. This module builds three separate OpenShift roles (administrator, developer, auditor), "
        "a jump host (a locked-down server that administrators go through to reach other systems) that has no open SSH port, "
        "and a path that sends session records to the SIEM. M05 decided who can sign in. This module decides what they may do once in, and how that is recorded."
    ),
    "mapping": [
        {
            "control": "AC-6 Least Privilege",
            "plain": "Each person and process gets only the access needed for assigned tasks, and administrative work is separated from everyday work.",
            "source": "NIST; FedRAMP",
            "covered": "Steps 1 and 2 create three roles and prove them with oc auth can-i. Test 3 shows a developer refused.",
            "cite": [
                {"file": NIST, "quote": "Employ the principle of least privilege, allowing only authorized accesses for users"},
                {"file": NIST, "quote": "Prevent non-privileged users from executing privileged functions."},
                {"file": NIST, "quote": "Log the execution of privileged functions."},
                {"file": FEDRAMP, "quote": "AC-6 (7) (a)-1  [at a minimum, annually]"},
            ],
        },
        {
            "control": "AC-17 Remote Access",
            "plain": "Each type of remote access is defined, authorized, and limited to approved methods.",
            "source": "NIST",
            "covered": "Step 3 builds a jump host with no inbound rule and Session Manager as the only way in. Test 4 proves SSH is not available.",
            "cite": [
                {"file": NIST, "quote": "Establish and document usage restrictions, configuration/connection requirements, and implementation guidance"},
                {"file": NIST, "quote": "Authorize each type of remote access to the system prior to allowing such connections."},
                {"file": NIST, "quote": "Route remote accesses through authorized and managed network access control points."},
            ],
        },
        {
            "control": "AU-14 Session Audit",
            "plain": "Defined roles can record, view, hear or log the content of a user session, and the session auditing is developed and used in consultation with legal counsel.",
            "source": "NIST",
            "covered": "Step 3 turns on session logging. Step 4 sends the records to Loki. Test 2 finds a marker typed in a session.",
            "cite": [
                {"file": NIST, "quote": "the content of a user session under"},
                {"file": NIST, "quote": "in consultation with legal counsel"},
                {"file": NIST, "quote": "Develop, integrate, and use session auditing activities in consultation with legal counsel"},
            ],
        },
    ],
    "intent": [
        {
            "control": "AC-6 Least Privilege",
            "feared": "One stolen or misused account can change anything, because everyone has more access than their job needs.",
            "scope": "Every person and every program with access to the cluster.",
            "question": "Pick any account. Can you list exactly what it may do, and is each item needed for that person's duties?",
            "evidence": "The roles and who holds them, a permission check for each role, and a refused attempt by a role that lacks the permission.",
            "sufficient": "Developers can change resources only in the namespaces assigned to their team. Administrative functions are kept apart from everyday accounts. FedRAMP sets the privilege review at a minimum of annually, and this lab reviews them quarterly.",
            "tieoff": "Someone owns the quarterly review and removes access that is no longer needed.",
            "tool": "Three OpenShift roles (Step 1), checked with oc auth can-i (Step 2) and refused in Test 3.",
        },
        {
            "control": "AC-17 Remote Access",
            "feared": "Administrators reach servers over paths nobody manages, such as an SSH port open to the internet.",
            "scope": "Every way a person can reach a server or the cluster from outside the system boundary.",
            "question": "List every door into the administration network. Is each one approved, and does each one require sign-in and leave a record?",
            "evidence": "The approved access methods, the security group rules, and a test that the unapproved path does not exist.",
            "sufficient": "Remote access uses only approved methods. The lab also ends idle remote sessions after 15 minutes of inactivity.",
            "tieoff": "A change that opens a new path (for example a new inbound rule) goes through change control and is noticed.",
            "tool": "A jump host with no inbound rule, no public address and no key pair, reached only through Session Manager (Step 3).",
        },
        {
            "control": "AU-14 Session Audit",
            "feared": "A privileged session does something damaging and nobody can see what was typed or shown.",
            "scope": "Privileged sessions on the jump host. Everyday user sessions are a policy decision for the organization.",
            "question": "If an administrator's session ended an hour ago, can an authorized reviewer see what happened in it?",
            "evidence": "The session logging setting, a recorded session, and the same record found in the SIEM.",
            "sufficient": "The capability exists for the defined roles, session records go to the SIEM, and the use of session recording is planned with legal counsel and the privacy office.",
            "tieoff": "The security operations team reviews session records and alerts on unusual activity, such as sessions from unexpected places.",
            "tool": "Session Manager logging to a log group (Step 3) and a push of those records to Loki (Step 4).",
        },
    ],
    "architect": (
        "Design before building. Decide which duties each role needs and how narrow the administrator role can be, which single path reaches the jump host, "
        "what the jump host must never have (a public address, an inbound port, a key pair), where session records go, and who may read them. Then build it and run the tests."
    ),
    "terms": [
        ("Least privilege", "Giving a person or program only the access it needs."),
        ("RBAC", "Role-based access control: permissions are attached to roles, and people are given roles."),
        ("ClusterRole", "An OpenShift object that lists permissions, such as which actions are allowed on which kinds of resources."),
        ("Role binding", "An OpenShift object that gives a role to a person or group, either in one namespace or across the whole cluster."),
        ("Impersonation", "Running a command as another user (the --as flag) to test what that user may do. Only highly privileged accounts may do this."),
        ("Jump host", "A locked-down server that administrators go through to reach other systems, so there is one controlled door."),
        ("Session Manager", "An AWS Systems Manager feature that opens a shell on a server through the AWS service, so the server needs no inbound port."),
        ("Security group", "An AWS firewall attached to a server. It lists which network traffic is allowed in and out."),
        ("Session record", "A saved copy of what appeared in a user session."),
        ("Terraform", "A tool that builds cloud resources from text files, so the build can be reviewed and repeated."),
    ],
    "concepts": [
        {
            "heading": "2.1 Roles instead of favors",
            "paras": [
                "What is this? OpenShift decides every request by asking: does any role bound to this user allow this action on this resource? A role lists allowed actions. A role binding hands the role to a person. No role, no access.",
                "Why? Giving people named roles with narrow lists means a stolen account can only do what that role could do, and a reviewer can read the list. The cluster-admin role can do everything, so it is not handed out for daily work.",
            ],
            "table": {
                "headers": ["Role in this module", "Who", "Where", "May do"],
                "rows": [
                    ("Administrator (il5-platform-admin)", "admin1", "Whole cluster", "Create, list and delete namespaces. Nothing else."),
                    ("Developer (edit)", "dev1", "Namespace demo only", "Create and change workloads in demo."),
                    ("Auditor (cluster-reader)", "audit1", "Whole cluster, read only", "Read most resources. Cannot read secrets or change anything."),
                ],
            },
        },
        {
            "heading": "2.2 One door in: the jump host and Session Manager",
            "paras": [
                "SSH (a remote login protocol) normally needs an open network port, a public address and a key file that can be copied. Session Manager reverses this. The jump host's agent makes an outbound connection to the AWS Systems Manager service. When an authorized person starts a session, AWS relays it over that connection. The server needs no inbound rule at all.",
                "Access then depends on AWS permissions (who may start a session), and AWS records who started it and when. The server's security group has no inbound rule, so there is nothing to scan from the internet.",
            ],
            "diagram": (
                "Administrator                 AWS Systems Manager               Jump host (private)\n"
                "-------------                 -------------------               -------------------\n"
                "aws ssm start-session  -->    checks AWS permissions    <--     agent connects OUT\n"
                "                              relays the session  --------->    runs the shell\n"
                "                                       |\n"
                "                                       +--> session record --> log group --> Loki\n"
                "No inbound port, no public address, no key pair on the jump host."
            ),
        },
        {
            "heading": "2.3 Recording what happens",
            "paras": [
                "Session Manager can stream everything shown in a session to a log group. A short script then copies those records into Loki, next to the OpenShift audit records, so the SIEM holds both what was done in the cluster and what was done in the shell.",
                "The records are the content of the session, so they can contain sensitive data. NIST requires session auditing to be developed in consultation with legal counsel, so plan session recording with legal counsel and the privacy office. Read the production note before turning it on for real users.",
            ],
            "table": {
                "headers": ["Record", "Where it starts", "Where it ends up"],
                "rows": [
                    ("OpenShift API audit record", "The cluster API", "Loki, log_type audit (SIEM-1)"),
                    ("Session record", "Session Manager on the jump host", "Log group, then Loki, log_type session (Step 4)"),
                    ("Who started the session", "AWS Systems Manager", "Session history (Step 4)"),
                ],
            },
            "production": "In the real environment session records go to the enterprise SIEM over an approved path, are kept under the retention rules for audit data, and are readable only by the security operations team. The script in Step 4 is a lab stand-in for that path. Whether and when sessions are recorded for each role is decided with legal counsel and the privacy office before it is switched on.",
        },
    ],
    "steps": [
        {
            "title": "Create three roles and bind them to people (AC-6)",
            "why": "Three roles keep duties apart. The administrator role is custom and narrow on purpose: it can manage namespaces and nothing else, so it is far smaller than cluster-admin. The developer role is the built-in edit role, bound in one namespace only. The auditor role is the built-in cluster-reader role, which reads but cannot change. The names admin1, dev1 and audit1 are example user names. M05 created different accounts, but a binding works even before a person has signed in, and the tests below ask the cluster about these names with impersonation, so no sign-in is needed.",
            "blocks": [
                {
                    "lang": "yaml",
                    "code": r"""apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: il5-platform-admin
rules:
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch", "create", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: il5-platform-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: il5-platform-admin
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: admin1
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: il5-developer
  namespace: demo
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: edit
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: dev1
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: il5-auditor
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-reader
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: audit1""",
                    "lines": [
                        ("ClusterRole il5-platform-admin", "The custom administrator role. The rules list allows get, list, watch, create and delete on namespaces only."),
                        ("ClusterRoleBinding il5-platform-admin", "Gives that role to admin1 across the whole cluster."),
                        ("RoleBinding il5-developer (namespace demo)", "Gives the built-in edit role to dev1 inside demo only. A role binding in a namespace stops at that namespace."),
                        ("ClusterRoleBinding il5-auditor", "Gives the built-in cluster-reader role to audit1, read only."),
                        ("kind: User, name", "The person, as the name that appears in OpenShift after Keycloak sign-in."),
                    ],
                },
                {
                    "code": r"""oc apply -f rbac.yaml --dry-run=server
oc apply -f rbac.yaml
oc get clusterrolebinding il5-platform-admin il5-auditor
oc get rolebinding il5-developer -n demo""",
                    "lines": [
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc apply -f rbac.yaml", "Saves the roles and bindings."),
                        ("oc get clusterrolebinding ...", "Shows the two cluster-wide bindings you made."),
                        ("oc get rolebinding ... -n demo", "Shows the developer binding in the demo namespace."),
                    ],
                },
            ],
            "tip": "Keep rbac.yaml in git. Git shows who changed a role and when, and the quarterly privilege review becomes a read of one file.",
            "action": "Save the YAML as rbac.yaml and run the second block.",
            "checkpoint": "The dry run lists each object as created (dry run), the apply creates them, and the get commands show the three bindings.",
        },
        {
            "title": "Prove each role with oc auth can-i (AC-6)",
            "why": "oc auth can-i asks the cluster whether a user may do an action, and answers yes or no without doing it. The --as flag asks the question as another user (impersonation, which your cluster-admin account is allowed to do). A role you have never tested is a role you are only hoping works.",
            "blocks": [
                {
                    "code": r"""for u in admin1 dev1 audit1; do
  echo "== $u"
  echo "create namespaces: $(oc auth can-i create namespaces --as=$u)"
  echo "create deployments in demo: $(oc auth can-i create deployments -n demo --as=$u)"
  echo "read secrets in openshift-config: $(oc auth can-i get secrets -n openshift-config --as=$u)"
  echo "list pods in all namespaces: $(oc auth can-i list pods --all-namespaces --as=$u)"
done""",
                    "lines": [
                        ("for u in admin1 dev1 audit1; do ... done", "Repeats the four questions for each of the three users."),
                        ("oc auth can-i create namespaces --as=$u", "Asks whether the user may create namespaces. This is the administrator duty."),
                        ("create deployments -n demo", "Asks whether the user may create workloads in demo. This is the developer duty."),
                        ("get secrets -n openshift-config", "Asks whether the user may read cluster secrets. Nobody in this table should."),
                        ("list pods --all-namespaces", "Asks whether the user may read across the cluster. This is the auditor duty."),
                    ],
                },
            ],
            "note": "Expected answers. admin1: yes, no, no, no. dev1: no, yes, no, no. audit1: no, no, no, yes. Any other answer means a binding is wrong, so fix it before going on.",
            "action": "Run the loop and compare each answer with the note.",
            "checkpoint": "All twelve answers match the expected table.",
        },
        {
            "title": "Build a jump host that has no way in except Session Manager (AC-17, AU-14)",
            "why": "Terraform builds the jump host from one file, so the design can be reviewed before it exists. The security group has no inbound rule at all, and the server has no public address and no key pair. The only door is Session Manager, which relies on the server's role (an identity attached to the server) and on the AWS permissions of the person who starts the session. The same file creates a log group and Session Manager preferences that stream sessions to it. The account-wide preferences cover ordinary shell sessions. A second, named preferences document covers the one-command session used in the tests, because AWS applies the account-wide document only to sessions started without a document name. The idle limit uses a 15-minute value. Session Manager ends the idle session instead of locking a screen.",
            "blocks": [
                {
                    "lang": "terraform",
                    "code": JUMP_TF,
                    "lines": [
                        ("aws_security_group jump and aws_vpc_security_group_egress_rule", "The server's firewall. The separate egress rule (the form the Terraform AWS provider documents as current practice) allows traffic out to the Systems Manager service inside the VPC. There is no ingress rule, so nothing can connect in."),
                        ("aws_cloudwatch_log_group sessions", "Where session records are stored, encrypted with the lab key."),
                        ("aws_iam_role jump and the two policies", "The server's identity. One managed policy lets the agent talk to Systems Manager. One small policy lets it write to the log group and nothing else."),
                        ("aws_ssm_document session_preferences", "The account-wide Session Manager settings. Ordinary shell sessions stream to the log group, and idleSessionTimeout is the 15-minute value written in minutes."),
                        ("aws_ssm_document logged_command", "A named preferences document with the same logging. Its shell profile runs id, prints a marker word and exits, so a session needs no typing."),
                        ("aws_instance jump", "The server. associate_public_ip_address is false and there is no key_name, so there is no public address and no key pair. http_tokens required turns on the safer version of the instance metadata service."),
                        ("output", "Prints the identifiers and the session document name that later steps need."),
                    ],
                },
                {
                    "code": r"""terraform init
terraform validate
terraform plan -var "vpc_id=$VPC_ID" -var "kms_key_arn=$KMS_KEY_ARN" -var "lab_id=$LAB_ID" -out jump.plan
terraform apply jump.plan
JUMP_ID=$(terraform output -raw instance_id)
SG_ID=$(terraform output -raw security_group_id)
LOG_GROUP=$(terraform output -raw log_group_name)
LOGGED_DOC=$(terraform output -raw session_document_name)
sleep 90
aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$JUMP_ID" --query 'InstanceInformationList[0].PingStatus' --output text""",
                    "lines": [
                        ("terraform init", "Downloads the AWS provider (the part of Terraform that talks to AWS)."),
                        ("terraform validate", "Checks the file for mistakes before anything is built."),
                        ("terraform plan -var ... -out jump.plan", "Shows what will be built and saves that exact plan. The three values come from lab variables."),
                        ("terraform apply jump.plan", "Builds exactly what the saved plan shows."),
                        ("terraform output -raw", "Reads the identifiers into variables."),
                        ("sleep 90", "Gives the server time to start and register with Systems Manager."),
                        ("aws ssm describe-instance-information", "Asks Systems Manager whether it can see the server. Online means the agent has connected."),
                    ],
                },
            ],
            "security": "Read the plan before you apply it. You should see no ingress rule in the security group and no public address on the instance. If either appears, stop and fix the file.",
            "action": "Save the Terraform as main.tf. Run the second block. If the last line does not print Online, wait and run it again.",
            "checkpoint": "The plan shows the resources, the apply succeeds, and the last command prints Online.",
        },
        {
            "title": "Open a session and send its record to the SIEM (AU-14)",
            "why": "A session record that sits only in a log group does not help the security team. This step opens a short session on the jump host (the logged-command document runs id and a marker word, then the session ends), reads the session history, and copies the log group's records into Loki with the label log_type=session. The copy command is a lab stand-in for the production path. Loki then holds the session records beside the audit records from SIEM-1.",
            "blocks": [
                {
                    "code": r"""aws ssm start-session --target "$JUMP_ID" --document-name "$LOGGED_DOC"
aws ssm describe-sessions --state History --filters key=Target,value="$JUMP_ID" --query 'Sessions[].[SessionId,Owner,Status]' --output table
aws ssm describe-sessions --state Active --output json""",
                    "lines": [
                        ("aws ssm start-session", "Opens a session through the AWS service. No SSH, no key, no open port."),
                        ("--document-name \"$LOGGED_DOC\"", "Uses the named preferences document, so the session is logged and runs its shell profile (id, a marker word, exit) without typing."),
                        ("describe-sessions --state History", "Lists past sessions with the person (Owner) who started each. This is the who and when."),
                        ("describe-sessions --state Active", "Lists sessions open right now. This is the live view of Session Manager connections. It is empty when no session is open."),
                    ],
                },
                {
                    "code": r"""sleep 30
aws logs filter-log-events --log-group-name "$LOG_GROUP" --output json | jq '{streams: [{stream: {log_type: "session", source: "ssm"}, values: [.events[] | [((.timestamp | tostring) + "000000"), .message]]}]}' | curl -s --cacert "$LOKI_CA_FILE" -u "$LOKI_USER:$LOKI_PASSWORD" -H "Content-Type: application/json" -X POST --data-binary @- -w "loki push: %{http_code}\n" "$LOKI_URL/loki/api/v1/push"
curl -sG --cacert "$LOKI_CA_FILE" -u "$LOKI_USER:$LOKI_PASSWORD" "$LOKI_URL/loki/api/v1/query_range" --data-urlencode 'query={log_type="session"}' --data-urlencode 'limit=5' | jq -r '.data.result[].values[][1]'""",
                    "lines": [
                        ("sleep 30", "Gives the session log time to reach the log group."),
                        ("aws logs filter-log-events", "Reads the session records from the log group."),
                        ("jq '{streams: ...}'", "Reshapes them into the format Loki accepts. Each record gets its time in nanoseconds (the millisecond time with six zeros added, which is what Loki expects) and the label log_type=session."),
                        ("curl ... /loki/api/v1/push", "Sends the records to Loki. A result of 204 means accepted."),
                        ("curl -sG ... query_range", "Asks Loki for the five newest session records, to prove they arrived."),
                    ],
                },
            ],
            "security": "Session records show everything that appeared on screen, which can include sensitive data. Limit who can read the session label in Loki to the security team, and plan session recording with legal counsel and the privacy office before using it for real users.",
            "note": "If the session stays open after the marker prints, type exit. If the log group stays empty, run an ordinary shell once (aws ssm start-session --target with no document name) and type exit. The account-wide logging setting applies to that kind of session.",
            "action": "Run both blocks. Read the session table and the Loki output.",
            "checkpoint": "The session table lists your session, the push prints 204, and the Loki query returns text that includes uid.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "An administrator action is allowed and recorded",
            "why": "admin1 creates a namespace. The cluster allows it, and the audit record names who asked (you, the impersonator) and who was impersonated (admin1). The last command removes the test namespace as admin1, which the same role allows.",
            "code": r"""oc create namespace m06-admin-test --as=admin1
sleep 30
curl -sG --cacert "$LOKI_CA_FILE" -u "$LOKI_USER:$LOKI_PASSWORD" "$LOKI_URL/loki/api/v1/query_range" --data-urlencode 'query={log_type="audit"} |= "impersonatedUser" |= "admin1" |= "/api/v1/namespaces"' --data-urlencode 'limit=5' | jq -r '.data.result[].values[][1]' | jq -c 'select(.verb == "create") | {verb, requestURI, user: .user.username, impersonated: .impersonatedUser.username, code: .responseStatus.code}'
oc delete namespace m06-admin-test --as=admin1""",
            "expect": (
                "Example only. Your field values will differ.\n"
                "namespace/m06-admin-test created\n"
                "{\"verb\":\"create\",\"requestURI\":\"/api/v1/namespaces\",\"user\":\"kube:admin\",\"impersonated\":\"admin1\",\"code\":201}\n"
                "namespace \"m06-admin-test\" deleted"
            ),
            "checkpoint": "The namespace is created, and a record shows verb create, impersonated admin1, and code 201.",
        },
        {
            "kind": "positive",
            "title": "A session on the jump host is recorded and found in the SIEM",
            "why": "The session runs a command that prints a marker no one else would produce. The search starts at the time recorded just before the session, so an earlier push cannot satisfy it. If the marker is found in Loki, the path from the jump host to the SIEM works end to end.",
            "code": r"""START_NS="$(date +%s)000000000"
aws ssm start-session --target "$JUMP_ID" --document-name "$LOGGED_DOC"
sleep 30
aws logs filter-log-events --log-group-name "$LOG_GROUP" --output json | jq '{streams: [{stream: {log_type: "session", source: "ssm"}, values: [.events[] | [((.timestamp | tostring) + "000000"), .message]]}]}' | curl -s --cacert "$LOKI_CA_FILE" -u "$LOKI_USER:$LOKI_PASSWORD" -H "Content-Type: application/json" -X POST --data-binary @- -w "loki push: %{http_code}\n" "$LOKI_URL/loki/api/v1/push"
sleep 5
curl -sG --cacert "$LOKI_CA_FILE" -u "$LOKI_USER:$LOKI_PASSWORD" "$LOKI_URL/loki/api/v1/query_range" --data-urlencode 'query={log_type="session"} |= "m06-session-marker"' --data-urlencode "start=$START_NS" --data-urlencode 'limit=1' | jq '.data.result | length'""",
            "expect": (
                "Example only.\n"
                "Starting session with SessionId: lab-user-0a1b2c3d4e5f6a7b8\n"
                "m06-session-marker\n"
                "Exiting session with sessionId: lab-user-0a1b2c3d4e5f6a7b8.\n"
                "loki push: 204\n"
                "1"
            ),
            "checkpoint": "The last number is 1 or more, meaning Loki holds a record that contains the marker.",
        },
        {
            "kind": "negative",
            "title": "A developer cannot do an administrator action",
            "why": "dev1 tries the same namespace creation. The cluster must refuse it, nothing must be created, and the refusal itself must be in the audit record, because a denied attempt is worth seeing.",
            "code": r"""oc create namespace m06-dev-test --as=dev1
oc get namespace m06-dev-test
sleep 30
curl -sG --cacert "$LOKI_CA_FILE" -u "$LOKI_USER:$LOKI_PASSWORD" "$LOKI_URL/loki/api/v1/query_range" --data-urlencode 'query={log_type="audit"} |= "impersonatedUser" |= "dev1" |= "/api/v1/namespaces"' --data-urlencode 'limit=5' | jq -r '.data.result[].values[][1]' | jq -c 'select(.verb == "create") | {verb, impersonated: .impersonatedUser.username, code: .responseStatus.code}'""",
            "expect": (
                "Example only. Your cluster's wording may differ.\n"
                "Error from server (Forbidden): namespaces is forbidden: User \"dev1\" cannot create resource \"namespaces\" in API group \"\" at the cluster scope\n"
                "Error from server (NotFound): namespaces \"m06-dev-test\" not found\n"
                "{\"verb\":\"create\",\"impersonated\":\"dev1\",\"code\":403}"
            ),
            "checkpoint": "The create is Forbidden, the namespace does not exist, and the audit record shows code 403.",
        },
        {
            "kind": "negative",
            "title": "SSH from the internet is not possible",
            "why": "Check the three things SSH would need: an inbound rule, a public address, and a key pair. All three must be absent. The port probe at the end is a last demonstration. It proves little by itself, because the lab shell sits outside the VPC, so the first two commands are the real proof.",
            "code": r"""aws ec2 describe-security-groups --group-ids "$SG_ID" --query 'SecurityGroups[0].IpPermissions' --output json
aws ec2 describe-instances --instance-ids "$JUMP_ID" --query 'Reservations[0].Instances[0].[PublicIpAddress,KeyName]' --output json
JUMP_IP=$(aws ec2 describe-instances --instance-ids "$JUMP_ID" --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
timeout 5 bash -c "echo > /dev/tcp/$JUMP_IP/22" && echo "port 22 reachable" || echo "port 22 not reachable"
""".rstrip("\n"),
            "expect": (
                "[]\n"
                "[\n"
                "    null,\n"
                "    null\n"
                "]\n"
                "port 22 not reachable"
            ),
            "checkpoint": "The inbound rule list is empty, the public address and key name are both null, and port 22 is not reachable.",
        },
    ],
    "glossary": [
        ("Least privilege", "Giving a person or program only the access it needs."),
        ("RBAC", "Role-based access control."),
        ("ClusterRole", "An OpenShift object that lists allowed actions."),
        ("Role binding", "An OpenShift object that gives a role to a person or group."),
        ("Impersonation", "Running a command as another user to test what that user may do."),
        ("Jump host", "A locked-down server that administrators pass through."),
        ("Session Manager", "An AWS feature that opens a shell on a server without an inbound port."),
        ("Security group", "An AWS firewall attached to a server."),
        ("Session record", "A saved copy of what appeared in a session."),
        ("Terraform", "A tool that builds cloud resources from text files."),
        ("SSH", "Secure Shell: a remote login protocol that normally needs an open network port."),
        ("Instance profile", "The way an AWS server is given an IAM role."),
    ],
    "next": "Next module: M11 Malware and Runtime Detection: scan files for malware and watch running containers for suspicious behavior, with alerts reaching the logs you now collect.",
}
