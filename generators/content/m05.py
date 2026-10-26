"""M05: Identity and multi-factor sign-in (Keycloak, OpenShift OIDC, one-time codes, certificates)."""

FEDRAMP = "fedramp-high-baseline.md"
NIST = "nist-sp-800-53r5-full.md"
SRG = "u-cloud-service-provider-v1r6-srg.md"

MODULE = {
    "id": "M05",
    "slug": "Identity",
    "title": "Identity and Multi-Factor Sign-In",
    "draft": (
        "Commands follow the Keycloak Admin REST API, Red Hat OpenShift OAuth and Keycloak X.509 documentation but have not yet run in the lab. "
        "Keycloak field names and flow names change between releases, so each setting is read back after it is applied. "
        "Three items are the least certain and are checked first when the lab is built: importing a one-time-password seed with a new user, "
        "the certificate sign-in flow, and the exact error text Keycloak returns for a locked account. "
        "The seed import uses the secretEncoding field that Keycloak reads for one-time-password credentials; confirm with the credential list in Step 2. "
        "The X.509 setting names (x509-cert-auth.*) are documented by display name in the Keycloak server administration guide and their stored keys were read from the Keycloak source (they are not listed on a docs page); they are read back with the flow executions call if Step 4 fails. "
        "The lab does not pin a Keycloak version; documentation was checked against Keycloak 26.8.1, and error wording and HTTP status codes differ between releases, so tests print the error code and description only."
    ),
    "controls": ["IA-2", "IA-5", "AC-2", "AC-7", "AC-11"],
    "mentions": ["AC-6", "AC-17", "AU-14"],
    "unit_values_ok": ["60 seconds", "200 seconds", "15 minutes", "15 minute", "15 characters", "24 hours"],
    "minutes": {"hands_on": 45, "verify": 20},
    "tools": ["OpenShift Container Platform", "Keycloak (free, open source)", "oc", "curl", "jq", "openssl", "python3"],
    "diagrams": [
        {
            "id": "flow",
            "title": "How a sign-in reaches one identity provider",
            "caption": "Keycloak keeps the accounts and the rules. OpenShift hands its sign-in to Keycloak, and a certificate can stand in for a smart card. Each step below adds one part, drawn with thick lines.",
            "per_step": True,
            "rankdir": "TB",
            "step_notes": {
                1: "You create the il5 realm with the lockout, password, idle and event settings.",
                2: "You add two accounts, each with a password and a registered one-time-code seed.",
                3: "OpenShift hands its sign-in to Keycloak, and the OpenShift token idle limit is set to 15 minutes.",
                4: "A lab card authority issues a certificate for analyst1, and Keycloak maps the name in the certificate to the account with the same name.",
            },
            "zones": [
                {"id": "shell", "label": "Your lab shell", "kind": "boundary"},
                {"id": "cluster", "label": "Your cluster", "kind": "boundary"},
                {"id": "kc", "label": "Namespace keycloak", "parent": "cluster", "kind": "group"},
                {"id": "os", "label": "OpenShift sign-in", "parent": "cluster", "kind": "group"},
            ],
            "nodes": [
                {"id": "cert", "title": "Certificate and key", "sub": "For analyst1, stands in for a card", "zone": "shell", "kind": "warn", "s": 4},
                {"id": "admin", "title": "Admin commands", "sub": "Web calls with an admin token", "zone": "shell"},
                {"id": "realm", "title": "Realm il5", "sub": "Lock after 3, idle 15 minutes", "zone": "kc", "kind": "ok", "s": 1},
                {"id": "users", "title": "Accounts", "sub": "Password and one-time code", "zone": "kc", "kind": "ok", "s": 2},
                {"id": "ca", "title": "Lab card authority", "sub": "Signs certificates", "zone": "kc", "kind": "warn"},
                {"id": "cflow", "title": "Certificate sign-in", "sub": "Client lab-cac", "zone": "kc", "kind": "ok", "s": 4},
                {"id": "oauth", "title": "OAuth server", "sub": "Token idle limit 15 minutes", "zone": "os", "kind": "ok", "s": 3},
            ],
            "edges": [
                {"a": "admin", "b": "realm", "n": 1, "label": "Creates", "s": 1},
                {"a": "admin", "b": "users", "n": 2, "label": "Adds", "s": 2},
                {"a": "oauth", "b": "realm", "n": 3, "label": "Hands sign-in to", "kind": "ok", "s": 3, "beside": True, "pad": 1},
                {"a": "ca", "b": "cert", "n": 4, "label": "Issues", "kind": "warn", "s": 4},
                {"a": "cert", "b": "cflow", "label": "Presented to", "s": 4},
                {"a": "cflow", "b": "users", "label": "Maps name to", "kind": "ok", "s": 4},
            ],
            "reading": [
                "You create the il5 realm in Keycloak with the lockout, password, idle and event settings (flow 1).",
                "You add accounts that need a password and a one-time code (flow 2).",
                "The OpenShift OAuth server hands sign-in to the realm (flow 3).",
                "The lab card authority issues a certificate, which is presented to the certificate sign-in and mapped to the account with the same name (flow 4).",
            ],
        },
    ],
    "prereq": ["Module 0 (terminal and git basics)", "Module 2 (lab running)"],
    "lab_needs": [
        "Keycloak answers at KEYCLOAK_URL over HTTPS. Its certificate is signed by the cluster ingress certificate authority (the config map default-ingress-cert in the namespace openshift-config-managed).",
        "Keycloak is published through a passthrough route and started with client certificate requests turned on (the option https-client-auth set to request), so it can see a certificate that a client presents.",
        "A lab card-issuing certificate authority (certificate and key) in the secret card-ca in the namespace keycloak, and its certificate in the Keycloak trust store.",
        "The master realm admin token lasts long enough for one step (or the lab accepts a fresh token request at the start of each step).",
        "The cluster OAuth resource has no other identity providers, because Step 3 replaces the list.",
        "python3 and openssl in the lab shell.",
    ],
    "lab": {
        "start": "lab start m05",
        "env": ["KEYCLOAK_URL", "KEYCLOAK_ADMIN_USER", "KEYCLOAK_ADMIN_PASSWORD"],
        "checks": [
            "The il5 realm exists with brute-force protection on, a lockout threshold of three, and an idle session limit.",
            "A user with a password and a one-time code receives a token, and the same user with a password alone does not.",
            "A client certificate issued by the lab card authority signs in as the matching user, and no certificate does not.",
            "Three wrong passwords lock an account and the correct password is then refused until an administrator unlocks it.",
            "A session left idle past the shortened limit is refused, and the normal limit is restored.",
            "OpenShift sign-in is handed to Keycloak and the OAuth resource carries the token inactivity limit.",
        ],
    },
    "requirement": (
        "An IL5 system must know who is signing in, ask for more than a password, stop password guessing, close accounts that are no longer needed, "
        "and end sessions that sit idle. This module builds that around one identity provider (a service that keeps the user accounts and decides who may sign in) "
        "that OpenShift trusts. You will set the rules, sign in with a one-time code and with a certificate that stands in for a smart card, "
        "lock an account on purpose, and watch an idle session expire. Module M06 then decides what each signed-in person may do."
    ),
    "mapping": [
        {
            "control": "IA-2 Identification and Authentication (Organizational Users)",
            "plain": "Every person is identified uniquely and proves who they are with more than one factor.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Step 2 adds the one-time code, Step 4 adds certificate sign-in, and Tests 2 to 5 prove both.",
            "cite": [
                {"file": NIST, "quote": "Uniquely identify and authenticate organizational users"},
                {"file": SRG, "quote": "CSPs will enforce the use of a physical token referred to as the"},
                {"file": FEDRAMP, "quote": "Implement multi-factor authentication for access to non-privileged accounts."},
                {"file": FEDRAMP, "quote": "IA-2 (12) Guidance: Include Common Access Card (CAC), i.e., the DoD technical implementation of PIV/FIPS 201/HSPD-12."},
            ],
        },
        {
            "control": "IA-5 Authenticator Management",
            "plain": "Passwords, one-time-code seeds and certificates are strong enough, protected, and revocable.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Step 1 sets the password rule. Step 4 issues a certificate from a lab card authority.",
            "cite": [
                {"file": NIST, "quote": "Ensuring that authenticators have sufficient strength of mechanism for their intended use"},
                {"file": SRG, "quote": "DSPAV must be used."},
                {"file": FEDRAMP, "quote": "Long passwords or passphrases are preferable over shorter passwords."},
                {"file": FEDRAMP, "quote": "IA-5 Requirement: Authenticators must be compliant with NIST SP 800-63-3 Digital Identity Guidelines IAL, AAL, FAL level 3."},
            ],
        },
        {
            "control": "AC-2 Account Management",
            "plain": "Accounts are created, enabled, modified, disabled and removed by named managers, and the actions are logged.",
            "source": "NIST; FedRAMP",
            "covered": "Step 2 creates accounts. Test 8 disables one, removes one, and reads the recorded events.",
            "cite": [
                {"file": NIST, "quote": "Create, enable, modify, disable, and remove accounts in accordance with"},
                {"file": FEDRAMP, "quote": "AC-2 (h) (1) [twenty-four (24) hours]"},
            ],
        },
        {
            "control": "AC-7 Unsuccessful Logon Attempts",
            "plain": "A set number of wrong passwords locks the account, and the lock has a defined release.",
            "source": "NIST; FedRAMP; DoD SRG",
            "covered": "Step 1 sets the lockout. Test 6 locks an account on purpose and unlocks it as an administrator.",
            "cite": [
                {"file": NIST, "quote": "lock the account or node until released by an administrator"},
                {"file": SRG, "quote": "For privileged users, DOD required an account lock after three"},
                {"file": SRG, "quote": "levels must be configured to require an administrator unlock"},
                {"file": SRG, "quote": "allow 10 attempts with the account automatically unlocked"},
                {"file": SRG, "quote": "after 30 minutes. If rate limiting is not used, normal DSPAV"},
                {"file": FEDRAMP, "quote": "AC-7 Requirement: In alignment with NIST SP 800-63B"},
            ],
        },
        {
            "control": "AC-11 Device Lock",
            "plain": "An idle session stops working and the person must sign in again to continue.",
            "source": "NIST; FedRAMP",
            "covered": "Step 1 sets the identity provider idle limit and Step 3 sets the OpenShift token limit. Test 7 shows a session expire.",
            "cite": [
                {"file": NIST, "quote": "initiating a device lock after [Assignment: organization-defined time period] of inactivity"},
                {"file": FEDRAMP, "quote": "AC-11 (a) [fifteen (15) minutes]; requiring the user to initiate a device lock before leaving the system unattended"},
                {"file": NIST, "quote": "Retain the device lock until the user reestablishes access using established identification and"},
            ],
        },
    ],
    "intent": [
        {
            "control": "IA-2 Identification and Authentication (Organizational Users)",
            "feared": "Someone signs in as another person, or gets in with only a stolen password, and the record cannot say who it really was.",
            "scope": "Every person who signs in to the cluster or the tools behind it. Programs that sign in on their own are a separate question.",
            "question": "For the last administrator sign-in, can you show that the person was identified uniquely and proved who they were with more than one factor?",
            "evidence": "Unique accounts, the sign-in methods that are switched on, and a test showing a password alone is refused.",
            "sufficient": "Each user has a unique identity and signs in with multiple factors. The DoD cloud SRG expects a physical token (the Common Access Card) for IL4 and IL5 users. This lab uses a certificate (standing in for the card) or a one-time password as the factors, and Keycloak as the identity service.",
            "tieoff": "Any exception to the card requirement is approved and recorded by a named owner.",
            "tool": "Keycloak asks for a password plus a one-time code (Step 2) and accepts an X.509 certificate that stands in for the card (Step 4). OpenShift hands its sign-in to Keycloak (Step 3).",
        },
        {
            "control": "IA-5 Authenticator Management",
            "feared": "Passwords are weak, certificates and their keys are loose, or a lost authenticator keeps working.",
            "scope": "Passwords, one-time-code seeds, certificates and their private keys.",
            "question": "What stops a short or guessable password from being set, and what happens to a certificate when its owner leaves?",
            "evidence": "The password rule, how certificates are issued and trusted, and how a lost one is revoked.",
            "sufficient": "The lab password rule has four parts: at least 15 characters, checked against common and compromised lists, stored with a salted key derivation function, and sent only over encrypted channels. The DoD Cloud Service Provider SRG says the DoD Specific Assignment Values (DSPAV) must be used for the IA-5(1) password parameters at IL4, IL5 and IL6. Step 1 enforces the length and the encrypted channel; the list check needs a blocked-password file on the Keycloak server, which this lab does not provide, so confirm how production meets it. How often authenticators are changed is organization-defined and the lab sets no routine password expiry; ask the ISSO where the value is recorded.",
            "tieoff": "Lost, stolen or compromised credentials are revoked, the revocation is documented, and someone owns that process.",
            "tool": "The realm password rule (Step 1) and a certificate issued by a lab card authority (Step 4). The production note after Step 4 covers revocation.",
        },
        {
            "control": "AC-2 Account Management",
            "feared": "Accounts pile up with no owner, former staff keep access, and nobody can show when an account was made or closed.",
            "scope": "User accounts held in the identity provider.",
            "question": "Who created this account, who approved it, and when was it disabled after the person left?",
            "evidence": "The account list with enabled state, the create, disable and remove events, and a disabled account failing to sign in.",
            "sufficient": "Only account managers create, enable, modify, disable and remove accounts, each action has documented approval and is logged, and account managers are notified within 24 hours when an account is no longer required (the FedRAMP assigned value). FedRAMP also assigns 24 hours to disable user accounts that are expired, no longer associated with a user, or in violation of policy. When an account is removed is organization-defined.",
            "tieoff": "Accounts are reviewed on a set schedule (FedRAMP High assigns monthly for privileged and every six months for non-privileged accounts), and managers are told when an account is no longer needed.",
            "tool": "The administrator interface creates, disables and removes accounts (Step 2 and Test 8), and Keycloak admin events record each action.",
        },
        {
            "control": "AC-7 Unsuccessful Logon Attempts",
            "feared": "An attacker guesses passwords without limit until one works.",
            "scope": "Every sign-in path that accepts a password.",
            "question": "After the allowed number of wrong guesses, exactly what happens, and who can undo it?",
            "evidence": "The lockout settings and a test where wrong passwords lock an account.",
            "sufficient": "The DoD cloud SRG sets IL5 values. Privileged users lock after three unsuccessful attempts and an administrator must unlock them. Non-privileged users, if rate limiting is used, may have 10 attempts with automatic unlock after 30 minutes. The lab sets Keycloak to lock after three consecutive failures regardless of time interval.",
            "tieoff": "Lockouts reach the SIEM, so a burst of locked accounts (which can also be a denial of service) is noticed.",
            "tool": "Realm brute-force protection (Step 1) and a deliberate lockout with an administrator unlock (Test 6).",
        },
        {
            "control": "AC-11 Device Lock",
            "feared": "A person walks away from a signed-in session and someone else uses it.",
            "scope": "Web and command-line sessions to the cluster and the tools behind the identity provider.",
            "question": "If I leave my desk, how long until my session stops working, and what must I do to get back in?",
            "evidence": "The idle limits and a test showing an idle session refused.",
            "sufficient": "FedRAMP assigns 15 minutes of inactivity for the device lock, and unlocking needs re-authentication. This module enforces the same limit in the identity provider and in OpenShift.",
            "tieoff": "A session the workstation did not lock still ends at the identity layer.",
            "tool": "The realm idle limit (Step 1), the OpenShift token inactivity limit (Step 3) and a shortened-limit test (Test 7).",
        },
    ],
    "architect": (
        "Design before building. Decide which people need which sign-in method, how many wrong passwords lock an account and who unlocks it, "
        "how long a session may sit idle, how a certificate maps to exactly one account, and how OpenShift will trust Keycloak without sharing a password. "
        "Then build it and run the tests."
    ),
    "terms": [
        ("Identity provider", "A service that keeps user accounts and decides who may sign in. Other systems trust its answer."),
        ("Realm (Keycloak)", "A separate space inside Keycloak with its own users, rules and clients."),
        ("Client (Keycloak)", "A program registered with Keycloak that may ask it to sign users in. OpenShift is one."),
        ("OIDC", "OpenID Connect: a standard way for one system to hand sign-in to another and receive a signed proof of who the user is."),
        ("MFA", "Multi-factor authentication: proving identity with two or more different kinds of proof, such as something you know and something you have."),
        ("TOTP", "Time-based one-time password: a code from an authenticator app that changes on a short fixed cycle."),
        ("X.509 certificate", "A signed file that links a name to a public key. The matching private key proves the holder owns it."),
        ("Certificate authority", "The organization (here a lab service) whose signature makes a certificate trusted."),
        ("CAC and PIV", "Common Access Card and Personal Identity Verification card: government smart cards that hold a certificate and a private key behind a PIN."),
        ("Brute force", "Guessing passwords again and again until one works."),
        ("Access token", "A short-lived signed pass that proves a sign-in succeeded."),
        ("Admin REST API", "The web address style Keycloak offers so an administrator can change settings with commands instead of clicks."),
    ],
    "concepts": [
        {
            "heading": "2.1 One identity provider, many systems",
            "paras": [
                "What is this? Instead of every system keeping its own passwords, systems send the user to one identity provider. The provider checks the user, then returns a signed proof (an access token). The systems trust the signature.",
                "Why? One place to require more than a password, one place to lock guessing attacks, one place to close an account when a person leaves. OpenShift, Argo CD and other tools can all use it.",
            ],
            "diagram": (
                "Person        OpenShift sign-in         Keycloak (identity provider)\n"
                "------        -----------------         ----------------------------\n"
                "opens console -> sends user to Keycloak -> checks password + one-time code\n"
                "                                           or X.509 certificate\n"
                "              <- receives signed token  <- applies lockout and idle rules\n"
                "gets in as the user named in the token"
            ),
            "table": {
                "headers": ["Keycloak word", "What it is here"],
                "rows": [
                    ("Realm il5", "The space that holds this module's users and rules."),
                    ("Client openshift", "The registration that lets OpenShift ask Keycloak to sign users in."),
                    ("Client lab-cli", "A lab-only client that lets the tests sign in from the command line, because a command line cannot click through a web page."),
                    ("Client lab-cac", "A lab-only client wired to certificate sign-in."),
                ],
            },
        },
        {
            "heading": "2.2 Two ways to prove who you are",
            "paras": [
                "Password plus one-time code. The password is something you know. The code comes from an authenticator that holds a secret seed, so it is something you have. Keycloak can refuse a code it has already seen.",
                "Certificate. A real smart card holds a private key that never leaves the card and asks for a PIN before it will sign anything. This lab treats it as the primary multi-factor method. The lab has no card reader, so it issues a certificate and key from a lab certificate authority and keeps the key in a file you protect. The sign-in logic you test is the same: Keycloak checks the certificate chain, then maps the name in the certificate to one account.",
            ],
            "table": {
                "headers": ["Method", "Something you have", "Something you know", "In the lab"],
                "rows": [
                    ("Password and code", "The authenticator seed", "The password", "Step 2, Tests 2 and 3"),
                    ("Certificate", "The private key (a card in production)", "The card PIN (production only)", "Step 4, Tests 4 and 5"),
                ],
            },
        },
        {
            "heading": "2.3 Lockout and idle limits",
            "paras": [
                "Lockout answers guessing. The DoD cloud SRG gives two IL5 patterns: privileged users lock after three wrong attempts and only an administrator can unlock; non-privileged users, if rate limiting is used, may have more attempts with an automatic unlock. The lab sets Keycloak to three consecutive failures. This module uses three for every account, which is stricter than the non-privileged option and satisfies the privileged one.",
                "Idle limits answer unattended sessions. The lab uses 15 minutes, the FedRAMP value for the device lock. Keycloak has its own idle limit for sign-in sessions, and OpenShift has a token inactivity limit. A workstation policy can enforce the same limit, so this module shows it at the identity layer as a second line.",
            ],
            "table": {
                "headers": ["Setting", "Where", "Value source"],
                "rows": [
                    ("Failures before lock", "Keycloak realm", "SRG privileged rule and lab choice"),
                    ("How the lock is released", "Keycloak realm", "SRG: administrator unlock"),
                    ("Idle limit", "Keycloak realm and OpenShift OAuth", "FedRAMP AC-11 value"),
                    ("Time before failures stop counting", "Keycloak realm", "Not used. Permanent lockout has no failure reset time, which fits the lab choice of three consecutive failures regardless of time interval."),
                ],
            },
            "production": "In the real environment people sign in with the physical card and PIN through the enterprise identity service, and Keycloak sits behind it. Certificates are checked for revocation with the DoD revocation services (the SRG requires OCSP or CRL checking of DoD certificates), the card authority is the DoD PKI, and lockout for card users is also enforced by the enterprise directory. The lab uses a stand-in authority so you practice the same settings.",
        },
    ],
    "steps": [
        {
            "title": "Create the realm and its rules (AC-7, AC-11, IA-5)",
            "why": "A realm is a separate space in Keycloak with its own users and rules. One file sets the lockout, the password rule, the idle limit and event recording. Keycloak is reached through its Admin REST API (web commands an administrator uses instead of clicking). You first ask for an admin token, a temporary pass that proves you are the administrator.",
            "blocks": [
                {
                    "code": r"""oc get configmap default-ingress-cert -n openshift-config-managed -o jsonpath='{.data.ca-bundle\.crt}' > ingress-ca.crt
KC_TOKEN_URL="$KEYCLOAK_URL/realms/master/protocol/openid-connect/token"
KC_API="$KEYCLOAK_URL/admin/realms"
TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
test -n "$TOKEN" && echo "admin token received"
""".rstrip("\n"),
                    "lines": [
                        ("oc get configmap default-ingress-cert", "Copies the cluster's certificate authority into ingress-ca.crt, so curl can check that Keycloak's certificate is genuine."),
                        ("KC_TOKEN_URL and KC_API", "Two shortcuts for Keycloak addresses, so later commands stay short."),
                        ("TOKEN=$(curl ...)", "Asks Keycloak's master realm for an admin token. The user name and password come from lab variables, so nothing secret is typed."),
                        ("test -n ... && echo", "Prints a message only if a token came back."),
                    ],
                },
                {
                    "lang": "json",
                    "code": r"""{
  "realm": "il5",
  "enabled": true,
  "sslRequired": "all",
  "registrationAllowed": false,
  "bruteForceProtected": true,
  "permanentLockout": true,
  "failureFactor": 3,
  "ssoSessionIdleTimeout": 900,
  "passwordPolicy": "length(15) and notUsername",
  "eventsEnabled": true,
  "adminEventsEnabled": true,
  "adminEventsDetailsEnabled": true
}""",
                    "lines": [
                        ("sslRequired: all", "Refuses any sign-in that is not encrypted."),
                        ("bruteForceProtected", "Turns on guessing protection. Keycloak leaves it off by default."),
                        ("permanentLockout", "A locked account stays locked until an administrator releases it. This matches the SRG rule for privileged users."),
                        ("failureFactor", "How many failures lock the account. Three is the value this lab uses."),
                        ("ssoSessionIdleTimeout", "The idle limit in seconds. It is the 15-minute session lock value written as seconds."),
                        ("passwordPolicy", "Requires a password of at least 15 characters (the length this lab uses) that is not the user name."),
                        ("eventsEnabled and adminEventsEnabled", "Record sign-in events and administrator actions so Tests 6 and 8 can read them."),
                    ],
                },
                {
                    "code": r"""curl -s --cacert ingress-ca.crt -o /dev/null -w "%{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @il5-realm.json "$KC_API"
curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5" | jq '{bruteForceProtected, permanentLockout, failureFactor, ssoSessionIdleTimeout, passwordPolicy}'""",
                    "lines": [
                        ("-X POST ... -d @il5-realm.json", "Sends the file to Keycloak to create the realm. A result of 201 means created."),
                        ("-w \"%{http_code}\\n\"", "Prints the web status code, so you see success or failure."),
                        ("curl ... \"$KC_API/il5\" | jq", "Reads the realm back and shows only the settings this module cares about."),
                    ],
                },
            ],
            "note": "In permanent lockout mode Keycloak does not use a failure reset time: failures never age out, which matches the lab choice of three consecutive failures regardless of time interval. (The Keycloak setting maxDeltaTimeSeconds only applies to temporary lockout.)",
            "security": "Never paste passwords into commands or files. The lab keeps the admin credentials in environment variables, out of your command history and out of git.",
            "action": "Save the JSON as il5-realm.json. Run the first block, then the third. Read the printed settings.",
            "checkpoint": "The create call prints 201 and the read-back shows protection on, lockout permanent, a failure factor of three, and the password rule.",
        },
        {
            "title": "Create users and require a second factor (IA-2, IA-5, AC-2)",
            "why": "An account manager creates each account, and the account must prove a second factor. The lab accounts are created with a password and a registered authenticator seed, so the tests can produce the one-time code from the command line. The helper below makes a random seed, which is a throwaway lab value that lives only in your shell. After the two accounts exist, you switch on the rule that every future account must enrol an authenticator at first sign-in.",
            "blocks": [
                {
                    "lang": "python",
                    "code": r"""import base64
import hashlib
import hmac
import os
import struct
import sys
import time

STATE_FILE = ".totp-last-step"
PERIOD = 30


def code_for(secret: bytes, step: int) -> str:
    digest = hmac.new(secret, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 15
    number = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{number % 1000000:06d}"


def last_step() -> int:
    try:
        with open(STATE_FILE, encoding="ascii") as handle:
            return int(handle.read())
    except (OSError, ValueError):
        return -1


def next_fresh_step() -> int:
    step = int(time.time()) // PERIOD
    while step <= last_step():
        time.sleep(1)
        step = int(time.time()) // PERIOD
    with open(STATE_FILE, "w", encoding="ascii") as handle:
        handle.write(str(step))
    return step


if len(sys.argv) == 1:
    print(base64.b32encode(os.urandom(20)).decode("ascii"))
else:
    print(code_for(base64.b32decode(sys.argv[1]), next_fresh_step()))""",
                    "lines": [
                        ("No argument", "Prints a new random seed (a secret string an authenticator app would store)."),
                        ("With the seed as the argument", "Prints the current six-digit code, the same way an authenticator app does."),
                        ("code_for", "Standard time-based one-time password math: sign the current time slot with the seed and cut out six digits."),
                        ("next_fresh_step", "Waits for a new time slot if this helper already gave out the current one, because Keycloak can refuse a code it has already seen."),
                    ],
                },
                {
                    "lang": "json",
                    "code": r"""{
  "username": "template",
  "enabled": true,
  "emailVerified": true,
  "email": "template@lab.invalid",
  "firstName": "Lab",
  "lastName": "User",
  "credentials": [
    {"type": "password", "temporary": false},
    {"type": "otp", "userLabel": "lab authenticator",
     "credentialData": "{\"subType\":\"totp\",\"digits\":6,\"counter\":0,\"period\":30,\"algorithm\":\"HmacSHA1\",\"secretEncoding\":\"BASE32\"}"}
  ]
}""",
                    "lines": [
                        ("username, email, names", "Filled in per account by the command below."),
                        ("credentials: password", "Placeholder. The command below puts the generated password here."),
                        ("credentials: otp", "A registered one-time-code authenticator. The command below puts the seed here. The settings say a six-digit time-based code using the standard algorithm."),
                    ],
                },
                {
                    "code": r"""OTP_SEED=$(python3 totp.py)
USER_PW=$(openssl rand -base64 24)
LAB_TOKEN_URL="$KEYCLOAK_URL/realms/il5/protocol/openid-connect/token"
TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
for name in analyst1 locktest1; do
  jq --arg pw "$USER_PW" --arg seed "$OTP_SEED" --arg name "$name" '.username = $name | .email = ($name + "@lab.invalid") | .credentials[0].value = $pw | .credentials[1].secretData = ({value: $seed} | tojson)' user-template.json | curl -s --cacert ingress-ca.crt -o /dev/null -w "$name: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @- "$KC_API/il5/users"
done
curl -s --cacert ingress-ca.crt -o /dev/null -w "client lab-cli: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"clientId":"lab-cli","publicClient":true,"directAccessGrantsEnabled":true,"standardFlowEnabled":false}' "$KC_API/il5/clients"
curl -s --cacert ingress-ca.crt -o /dev/null -w "enrol rule: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"alias":"CONFIGURE_TOTP","name":"Configure OTP","providerId":"CONFIGURE_TOTP","enabled":true,"defaultAction":true,"priority":10}' "$KC_API/il5/authentication/required-actions/CONFIGURE_TOTP"
""".rstrip("\n"),
                    "lines": [
                        ("OTP_SEED and USER_PW", "A random authenticator seed and a random password of more than 15 characters. They exist only in this shell session."),
                        ("for name in analyst1 locktest1", "Repeats the create call for two accounts: one for the sign-in tests and one to lock on purpose."),
                        ("jq ... user-template.json", "Fills the template with each account's name, the password and the seed, without writing a secret to disk."),
                        ("-X POST ... /users", "Creates the account. A result of 201 means created."),
                        ("client lab-cli", "Registers the lab-only client that lets the tests sign in from the command line (direct access grants are the Keycloak name for typing a user name and password into a command)."),
                        ("CONFIGURE_TOTP ... defaultAction", "From now on every new account must enrol an authenticator the first time it signs in."),
                    ],
                },
                {
                    "code": r"""TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
USER_ID=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/users?username=analyst1&exact=true" | jq -r '.[0].id')
curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/users/$USER_ID/credentials" | jq 'map(.type)'""",
                    "lines": [
                        ("USER_ID=$(curl ... users?username=analyst1)", "Looks up the account's internal identifier. Later steps reuse it."),
                        ("users/$USER_ID/credentials | jq 'map(.type)'", "Lists the kinds of credential stored for the account, without showing any secret."),
                    ],
                },
            ],
            "security": "The password and seed are random, live only in shell variables, and are never printed. If the credential list does not show an otp entry, stop: the seed import did not work on this Keycloak release, and the account has no second factor.",
            "tip": "Keep user-template.json and totp.py in git. Account creation is then a reviewed, repeatable change instead of a series of clicks.",
            "action": "Save totp.py and user-template.json. Run the first command with the helper, then the other blocks in order.",
            "checkpoint": "Both accounts and the client print 201 and the enrol rule prints 204. The credential list shows password and otp.",
        },
        {
            "title": "Hand OpenShift sign-in to Keycloak (IA-2, AC-11)",
            "why": "OpenShift has a built-in sign-in service called the OAuth server. You register OpenShift as a client in Keycloak, give OpenShift the client secret (a password the two systems share) and the certificate authority it must trust, and point the OAuth resource at the realm. The same resource also sets the OpenShift token inactivity limit, so an idle OpenShift session stops working.",
            "blocks": [
                {
                    "code": r"""APPS_DOMAIN=$(oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}')
TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
jq -n --arg uri "https://oauth-openshift.$APPS_DOMAIN/oauth2callback/keycloak" '{clientId: "openshift", protocol: "openid-connect", publicClient: false, standardFlowEnabled: true, directAccessGrantsEnabled: false, redirectUris: [$uri]}' | curl -s --cacert ingress-ca.crt -o /dev/null -w "client openshift: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @- "$KC_API/il5/clients"
CLIENT_UUID=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/clients?clientId=openshift" | jq -r '.[0].id')
CLIENT_SECRET=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/clients/$CLIENT_UUID/client-secret" | jq -r .value)
oc create secret generic keycloak-client-secret -n openshift-config --from-literal=clientSecret="$CLIENT_SECRET"
oc create configmap keycloak-ca -n openshift-config --from-file=ca.crt=ingress-ca.crt""",
                    "lines": [
                        ("APPS_DOMAIN", "The cluster's application address suffix. OpenShift's sign-in service lives under it."),
                        ("jq -n ... redirectUris", "Builds the client definition. The redirect address is the only place Keycloak will send the user back to, and it must match OpenShift's callback address."),
                        ("publicClient: false", "Makes this a confidential client: it must present a secret, which is stronger than a public client."),
                        ("client-secret", "Reads the secret Keycloak generated, straight into a variable."),
                        ("oc create secret ... -n openshift-config", "Stores the secret where the OAuth server reads it. The key name must be clientSecret."),
                        ("oc create configmap keycloak-ca", "Stores the certificate authority the OAuth server uses to check Keycloak's certificate."),
                    ],
                },
                {
                    "lang": "yaml",
                    "code": r"""apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  identityProviders:
    - name: keycloak
      mappingMethod: claim
      type: OpenID
      openID:
        clientID: openshift
        clientSecret:
          name: keycloak-client-secret
        ca:
          name: keycloak-ca
        issuer: ISSUER_URL
        claims:
          preferredUsername:
            - preferred_username
          name:
            - name
          email:
            - email
  tokenConfig:
    accessTokenInactivityTimeout: 15m""",
                    "lines": [
                        ("identityProviders: name keycloak", "The name shown on the OpenShift sign-in page. It is also part of the callback address."),
                        ("type: OpenID", "Says this provider speaks OIDC."),
                        ("clientID and clientSecret", "Who OpenShift is to Keycloak. The secret is referred to by name, so it is not written in this file."),
                        ("ca", "The certificate authority from the config map above."),
                        ("issuer: ISSUER_URL", "The realm address. The next command swaps in the real address."),
                        ("claims", "Which fields of Keycloak's signed answer become the OpenShift user name, display name and email."),
                        ("accessTokenInactivityTimeout: 15m", "An OpenShift session unused for 15 minutes stops working. This is the AC-11 value."),
                    ],
                },
                {
                    "code": r"""oc explain oauth.spec.identityProviders.openID
sed "s|ISSUER_URL|$KEYCLOAK_URL/realms/il5|" oauth-keycloak.yaml | oc apply --dry-run=server -f -
sed "s|ISSUER_URL|$KEYCLOAK_URL/realms/il5|" oauth-keycloak.yaml | oc apply -f -
sleep 60
oc get clusteroperator authentication kube-apiserver""",
                    "lines": [
                        ("oc explain ...", "Prints the fields your cluster accepts. If a field name differs, use the one it shows."),
                        ("sed \"s|ISSUER_URL|...|\"", "Replaces the placeholder with the real realm address, without editing the file."),
                        ("--dry-run=server", "Asks the cluster to check the file without saving it."),
                        ("oc apply -f -", "Saves the OAuth resource. The sign-in service restarts to pick it up."),
                        ("oc get clusteroperator authentication kube-apiserver", "Shows whether the restart finished. Changing the token inactivity limit also rolls out a new Kubernetes API server revision, which takes several minutes. Wait until PROGRESSING shows False for both."),
                    ],
                },
            ],
            "security": "This step replaces the whole identity provider list. The lab starts with none. On a cluster that already has providers, read them first with oc get oauth cluster -o yaml and add to the list instead.",
            "action": "Save the YAML as oauth-keycloak.yaml. Run the three blocks. If PROGRESSING still shows True for either line, wait and run the last command again.",
            "checkpoint": "The dry run succeeds, the apply succeeds, and the authentication and kube-apiserver operators settle to AVAILABLE True and PROGRESSING False.",
        },
        {
            "title": "Add certificate sign-in that stands in for a smart card (IA-2, IA-5)",
            "why": "A smart card carries a certificate. To emulate it, you act as the card issuer: take the lab card authority, issue a certificate for analyst1, and tell Keycloak to accept certificates from that authority and to map the name inside the certificate to the account with the same name. The test client lab-cac uses a flow (an ordered list of checks Keycloak runs at sign-in) that contains only the certificate check.",
            "blocks": [
                {
                    "code": r"""oc get secret card-ca -n keycloak -o jsonpath='{.data.tls\.crt}' | base64 -d > card-ca.crt
oc get secret card-ca -n keycloak -o jsonpath='{.data.tls\.key}' | base64 -d > card-ca.key
chmod 600 card-ca.key
openssl req -new -newkey rsa:3072 -nodes -keyout analyst1.key -out analyst1.csr -subj "/CN=analyst1"
printf 'keyUsage = digitalSignature\nextendedKeyUsage = clientAuth\n' > client-ext.cnf
openssl x509 -req -in analyst1.csr -CA card-ca.crt -CAkey card-ca.key -CAcreateserial -days 30 -extfile client-ext.cnf -out analyst1.crt
chmod 600 analyst1.key
openssl x509 -in analyst1.crt -noout -subject -issuer""",
                    "lines": [
                        ("oc get secret card-ca", "Copies the lab card authority's certificate and key out of the cluster."),
                        ("openssl req -new ... -subj \"/CN=analyst1\"", "Creates a new private key and a signing request that names the holder analyst1. On a real card the key is made inside the card and never leaves it."),
                        ("client-ext.cnf", "Marks the certificate as usable for signing in as a client, not for other purposes."),
                        ("openssl x509 -req ... -CA", "The authority signs the request. The -days value is how long the certificate stays valid; it is a short lab value."),
                        ("chmod 600", "Lets only you read the key files. This stands in for the card PIN."),
                        ("openssl x509 -noout -subject -issuer", "Prints who the certificate names and who signed it."),
                    ],
                },
                {
                    "code": r"""TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
curl -s --cacert ingress-ca.crt -o /dev/null -w "flow: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"alias":"cac-direct-grant","providerId":"basic-flow","topLevel":true,"builtIn":false,"description":"Lab smart card emulation"}' "$KC_API/il5/authentication/flows"
curl -s --cacert ingress-ca.crt -o /dev/null -w "step: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"provider":"direct-grant-auth-x509-username"}' "$KC_API/il5/authentication/flows/cac-direct-grant/executions/execution"
curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/authentication/flows/cac-direct-grant/executions" | jq '.[] | select(.providerId == "direct-grant-auth-x509-username") | .requirement = "REQUIRED"' | curl -s --cacert ingress-ca.crt -o /dev/null -w "required: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @- "$KC_API/il5/authentication/flows/cac-direct-grant/executions"
EXEC_ID=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/authentication/flows/cac-direct-grant/executions" | jq -r '.[0].id')
CA_DN=$(openssl x509 -in card-ca.crt -noout -subject -nameopt RFC2253 | sed 's/^subject= *//')
jq -n --arg dn "$CA_DN" '{alias: "cac-x509", config: {"x509-cert-auth.mapping-source-selection": "Match SubjectDN using regular expression", "x509-cert-auth.regular-expression": "CN=(.*?)(?:,|$)", "x509-cert-auth.mapper-selection": "Username or Email", "x509-cert-auth.casubjectdn": $dn, "x509-cert-auth.crl-checking-enabled": "false", "x509-cert-auth.ocsp-checking-enabled": "false", "x509-cert-auth.confirmation-page-disallowed": "true"}}' | curl -s --cacert ingress-ca.crt -o /dev/null -w "mapping: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @- "$KC_API/il5/authentication/executions/$EXEC_ID/config"
FLOW_ID=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/authentication/flows" | jq -r '.[] | .alias + " " + .id' | grep cac-direct-grant | awk '{print $2}')
jq -n --arg flow "$FLOW_ID" '{clientId: "lab-cac", publicClient: true, directAccessGrantsEnabled: true, standardFlowEnabled: false, authenticationFlowBindingOverrides: {direct_grant: $flow}}' | curl -s --cacert ingress-ca.crt -o /dev/null -w "client lab-cac: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @- "$KC_API/il5/clients"
""".rstrip("\n"),
                    "lines": [
                        ("authentication/flows (first call)", "Creates an empty flow named cac-direct-grant."),
                        ("direct-grant-auth-x509-username", "Adds Keycloak's certificate check as the only step in the flow."),
                        ("requirement = \"REQUIRED\"", "Makes the step mandatory. Keycloak adds new steps in a switched-off state."),
                        ("mapping-source-selection and regular-expression", "Reads the CN (common name) field from the certificate subject and uses it as the identity."),
                        ("mapper-selection: Username or Email", "Matches that identity to the account with the same user name."),
                        ("CA_DN and casubjectdn", "Reads the subject name of the lab card authority from its certificate and gives it to Keycloak as the trusted issuer. Keycloak documents this setting as required; leaving it empty is a deprecated configuration."),
                        ("crl-checking-enabled and ocsp-checking-enabled", "Revocation checks, set to false (off) in the lab. See the production note."),
                        ("authenticationFlowBindingOverrides", "Gives only the lab-cac client this certificate flow. Other clients keep password and one-time code."),
                    ],
                },
            ],
            "security": "The key analyst1.key stands in for the card. Anyone who can read the file can sign in as analyst1, which is why a real card holds the key and asks for a PIN. Keep the file readable only by you, and never copy it into git.",
            "note": "Keycloak trusts the certificate only if it chains to a certificate authority in the Keycloak trust store, which the lab already holds for the card authority. The web server checks that chain before Keycloak sees the certificate.",
            "action": "Run the two blocks. Read the printed subject and issuer, and check that the five calls print 201 or 204.",
            "checkpoint": "The certificate subject shows CN=analyst1 and the issuer is the lab card authority. The calls print 201 or 204.",
        },
    ],
    "verify": [
        {
            "kind": "positive",
            "title": "OpenShift hands sign-in to Keycloak",
            "why": "OpenShift's sign-in address should now send people to the il5 realm. This asks for the OpenShift token request page (the address OpenShift documents for its browser sign-in) and follows the redirects, then looks for the provider name or the realm path.",
            "code": r"""OAUTH_URL="https://oauth-openshift.$APPS_DOMAIN/oauth/token/request"
curl -s -L --cacert ingress-ca.crt "$OAUTH_URL" | grep -o -E 'keycloak|realms/il5' | sort -u
oc whoami --show-console""",
            "expect": (
                "Example only. You see keycloak, realms/il5, or both.\n"
                "keycloak\n"
                "realms/il5\n"
                "https://console-openshift-console.apps.example.invalid"
            ),
            "checkpoint": "The output names keycloak or realms/il5. In a browser, the console address shows a keycloak button that leads to the Keycloak sign-in page.",
        },
        {
            "kind": "positive",
            "title": "A valid user with a password and a one-time code signs in",
            "why": "This is the success case: the right password and a fresh code from the helper.",
            "code": r"""curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=analyst1 --data-urlencode password="$USER_PW" -d totp="$(python3 totp.py "$OTP_SEED")" -d scope=openid "$LAB_TOKEN_URL" | jq '{token_type, scope, signed_in: (.access_token != null)}'""",
            "expect": (
                "Example only.\n"
                "{\n"
                "  \"token_type\": \"Bearer\",\n"
                "  \"scope\": \"openid profile email\",\n"
                "  \"signed_in\": true\n"
                "}"
            ),
            "checkpoint": "signed_in is true.",
        },
        {
            "kind": "negative",
            "title": "A password alone is refused",
            "why": "Take away the second factor and the same account must fail. If this succeeds, MFA is not enforced.",
            "code": r"""curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=analyst1 --data-urlencode password="$USER_PW" -d scope=openid "$LAB_TOKEN_URL" | jq '{error, error_description}'""",
            "expect": (
                "Example only. The wording can differ by release.\n"
                "{\n"
                "  \"error\": \"invalid_grant\",\n"
                "  \"error_description\": \"Invalid user credentials\"\n"
                "}"
            ),
            "checkpoint": "An error comes back and there is no token.",
        },
        {
            "kind": "positive",
            "title": "A certificate from the lab card authority signs in as the matching user",
            "why": "Present the certificate and key. No password and no code are sent. The second command opens the token and prints the user name Keycloak mapped the certificate to.",
            "code": r"""curl -s --cacert ingress-ca.crt --cert analyst1.crt --key analyst1.key -d client_id=lab-cac -d grant_type=password -d scope=openid "$LAB_TOKEN_URL" | jq -r '.access_token' | python3 -c "import base64,json,sys;p=sys.stdin.read().strip().split('.')[1];print(json.loads(base64.urlsafe_b64decode(p+'='*(-len(p)%4)))['preferred_username'])"
""".rstrip(),
            "expect": (
                "Example only.\n"
                "analyst1"
            ),
            "checkpoint": "The name printed is analyst1, the CN in the certificate.",
        },
        {
            "kind": "negative",
            "title": "No certificate, no sign-in",
            "why": "The same client with no certificate must fail, because the certificate check is the only step in its flow.",
            "code": r"""curl -s --cacert ingress-ca.crt -d client_id=lab-cac -d grant_type=password -d scope=openid "$LAB_TOKEN_URL" | jq '{error, error_description}'""",
            "expect": (
                "Example only. The wording can differ by release.\n"
                "{\n"
                "  \"error\": \"invalid_request\",\n"
                "  \"error_description\": \"X509 client certificate is missing.\"\n"
                "}"
            ),
            "checkpoint": "An error comes back and there is no token.",
        },
        {
            "kind": "negative",
            "title": "Wrong passwords lock the account",
            "why": "Three wrong passwords in a row must lock the account, and then even the correct password and a valid code must fail until an administrator releases it. Keycloak deliberately gives the same plain error for a locked account as for a wrong password, so an attacker cannot tell the account is locked; the status call that follows shows the lock. Two seconds between attempts keeps Keycloak from treating them as a separate quick-login lock.",
            "code": r"""TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
LOCK_ID=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/users?username=locktest1&exact=true" | jq -r '.[0].id')
for i in 1 2 3; do
  echo "wrong password, attempt $i: $(curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=locktest1 -d password=not-the-password -d totp=000000 "$LAB_TOKEN_URL" | jq -r .error)"
  sleep 2
done
curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=locktest1 --data-urlencode password="$USER_PW" -d totp="$(python3 totp.py "$OTP_SEED")" "$LAB_TOKEN_URL" | jq '{error, error_description}'
TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/attack-detection/brute-force/users/$LOCK_ID" | jq '{numFailures, disabled}'
curl -s --cacert ingress-ca.crt -o /dev/null -w "unlock: %{http_code}\n" -X DELETE -H "Authorization: Bearer $TOKEN" "$KC_API/il5/attack-detection/brute-force/users/$LOCK_ID"
curl -s --cacert ingress-ca.crt -o /dev/null -w "enable: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"enabled":true}' "$KC_API/il5/users/$LOCK_ID"
curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=locktest1 --data-urlencode password="$USER_PW" -d totp="$(python3 totp.py "$OTP_SEED")" "$LAB_TOKEN_URL" | jq '{signed_in: (.access_token != null)}'""",
            "expect": (
                "Example only. Error wording can differ by release.\n"
                "wrong password, attempt 1: invalid_grant\n"
                "wrong password, attempt 2: invalid_grant\n"
                "wrong password, attempt 3: invalid_grant\n"
                "{\n"
                "  \"error\": \"invalid_grant\",\n"
                "  \"error_description\": \"Invalid user credentials\"\n"
                "}\n"
                "{\n"
                "  \"numFailures\": 3,\n"
                "  \"disabled\": true\n"
                "}\n"
                "unlock: 204\n"
                "enable: 204\n"
                "{\n"
                "  \"signed_in\": true\n"
                "}"
            ),
            "checkpoint": "After three failures the correct password is refused and the status shows disabled true. After the administrator unlock, the account signs in again.",
        },
        {
            "kind": "negative",
            "title": "An idle session times out",
            "why": "Waiting 15 minutes is too long for a lab, so this shortens the idle limit to 60 seconds, signs in, waits 200 seconds without using the session, and tries to continue it. Keycloak allows a short tolerance beyond the idle limit when it checks a session, so the wait is much longer than the limit. The refresh token is the proof that lets a session continue without typing credentials again. The last command restores the normal limit.",
            "code": r"""TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
curl -s --cacert ingress-ca.crt -o /dev/null -w "shorten idle limit: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"ssoSessionIdleTimeout":60}' "$KC_API/il5"
RT=$(curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=analyst1 --data-urlencode password="$USER_PW" -d totp="$(python3 totp.py "$OTP_SEED")" "$LAB_TOKEN_URL" | jq -r .refresh_token)
sleep 200
curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=refresh_token -d refresh_token="$RT" "$LAB_TOKEN_URL" | jq '{error, error_description}'
TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
curl -s --cacert ingress-ca.crt -o /dev/null -w "restore idle limit: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"ssoSessionIdleTimeout":900}' "$KC_API/il5"
""".rstrip(),
            "expect": (
                "Example only. Error wording can differ by release.\n"
                "shorten idle limit: 204\n"
                "{\n"
                "  \"error\": \"invalid_grant\",\n"
                "  \"error_description\": \"Session not active\"\n"
                "}\n"
                "restore idle limit: 204"
            ),
            "checkpoint": "The continue attempt is refused after the idle wait, and the restore call prints 204.",
        },
        {
            "kind": "negative",
            "title": "Disable an account, remove an account, read the recorded events",
            "why": "A disabled account must fail to sign in even with the right password and code. A removed account must be gone. Keycloak's admin events are the record of who changed what.",
            "code": r"""TOKEN=$(curl -s --cacert ingress-ca.crt -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KC_TOKEN_URL" | jq -r .access_token)
curl -s --cacert ingress-ca.crt -o /dev/null -w "disable analyst1: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"enabled":false}' "$KC_API/il5/users/$USER_ID"
curl -s --cacert ingress-ca.crt -d client_id=lab-cli -d grant_type=password -d username=analyst1 --data-urlencode password="$USER_PW" -d totp="$(python3 totp.py "$OTP_SEED")" "$LAB_TOKEN_URL" | jq '{error, error_description}'
curl -s --cacert ingress-ca.crt -o /dev/null -w "enable analyst1: %{http_code}\n" -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"enabled":true}' "$KC_API/il5/users/$USER_ID"
curl -s --cacert ingress-ca.crt -o /dev/null -w "create temp1: %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"username":"temp1","enabled":true}' "$KC_API/il5/users"
TEMP_ID=$(curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/users?username=temp1&exact=true" | jq -r '.[0].id')
curl -s --cacert ingress-ca.crt -o /dev/null -w "remove temp1: %{http_code}\n" -X DELETE -H "Authorization: Bearer $TOKEN" "$KC_API/il5/users/$TEMP_ID"
curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/users?username=temp1&exact=true" | jq 'length'
curl -s --cacert ingress-ca.crt -H "Authorization: Bearer $TOKEN" "$KC_API/il5/admin-events?resourceTypes=USER&max=8" | jq -r '.[] | "\(.operationType) \(.resourcePath)"'""",
            "expect": (
                "Example only. User identifiers will differ.\n"
                "disable analyst1: 204\n"
                "{\n"
                "  \"error\": \"invalid_grant\",\n"
                "  \"error_description\": \"Account disabled\"\n"
                "}\n"
                "enable analyst1: 204\n"
                "create temp1: 201\n"
                "remove temp1: 204\n"
                "0\n"
                "DELETE users/6f1c0b0e-0000-0000-0000-000000000000\n"
                "CREATE users/6f1c0b0e-0000-0000-0000-000000000000\n"
                "UPDATE users/3a7d2c10-0000-0000-0000-000000000000\n"
                "UPDATE users/3a7d2c10-0000-0000-0000-000000000000\n"
                "UPDATE users/5b2e9d44-0000-0000-0000-000000000000\n"
                "(older create events follow)"
            ),
            "checkpoint": "The disabled account is refused, the removed account is gone (count 0), and the events list shows CREATE, UPDATE and DELETE actions, newest first.",
        },
    ],
    "glossary": [
        ("Realm (Keycloak)", "A separate space inside Keycloak with its own users, rules and clients."),
        ("OIDC", "OpenID Connect: a standard for letting one system sign users in for another."),
        ("MFA", "Multi-factor authentication: two or more different kinds of proof."),
        ("TOTP", "A one-time code that changes on a short fixed cycle."),
        ("X.509 certificate", "A signed file that links a name to a public key."),
        ("Certificate authority", "The party whose signature makes a certificate trusted."),
        ("Access token", "A short-lived signed proof that a sign-in succeeded."),
        ("Refresh token", "A proof that lets a session continue without typing credentials again, until the session expires."),
        ("Flow (Keycloak)", "An ordered list of checks Keycloak runs when someone signs in."),
        ("Confidential client", "A client that must present a secret to Keycloak, which is stronger than a public client."),
    ],
    "next": "Next module: M06 Privileged Access and Session Audit: who may do administrative work, how administrators reach the system, and how their sessions are recorded.",
}
