#!/usr/bin/env bash
# Create the cap-config repository and protect main. Idempotent.
# Needs GITEA_URL, GITEA_USER and GITEA_TOKEN (an administrator token), and the Gitea user lab-reviewer.
set -u
API="$GITEA_URL/api/v1"
AUTH="Authorization: token $GITEA_TOKEN"
REPO="$API/repos/$GITEA_USER/cap-config"
REVIEWER="lab-reviewer"

code=$(curl -s -o /dev/null -w '%{http_code}' -H "$AUTH" "$REPO")
if [ "$code" != "200" ]; then
  curl -sf -X POST -H "$AUTH" -H "Content-Type: application/json" "$API/user/repos" \
    -d '{"name":"cap-config","auto_init":true,"default_branch":"main","private":true}' > /dev/null || { echo "could not create cap-config"; exit 1; }
fi

# The approvals allow-list keeps only users who already have access to the repository,
# so the reviewer must be a collaborator BEFORE the protection rule is saved.
curl -sf -X PUT -H "$AUTH" -H "Content-Type: application/json" "$REPO/collaborators/$REVIEWER" \
  -d '{"permission":"write"}' > /dev/null || { echo "could not give $REVIEWER write access to cap-config (does the user exist?)"; exit 1; }

curl -s -o /dev/null -X DELETE -H "$AUTH" "$REPO/branch_protections/main"
curl -sf -X POST -H "$AUTH" -H "Content-Type: application/json" "$REPO/branch_protections" \
  -d '{"rule_name":"main","enable_push":false,"required_approvals":1,"enable_approvals_whitelist":true,"approvals_whitelist_username":["'"$REVIEWER"'"],"block_on_rejected_reviews":true,"dismiss_stale_approvals":true}' > /dev/null || { echo "could not protect main"; exit 1; }

# Read the rule back so a silently dropped allow-list entry is caught here, not during the check.
rule=$(curl -sf -H "$AUTH" "$REPO/branch_protections/main") || { echo "could not read the protection rule back"; exit 1; }
echo "$rule" | jq -e --arg r "$REVIEWER" '.enable_push == false and .required_approvals == 1 and ((.approvals_whitelist_username // []) | index($r) != null)' > /dev/null \
  || { echo "protection rule on main is not as expected (push enabled, wrong approval count, or $REVIEWER missing from the allow-list)"; exit 1; }
echo "cap-config ready"
