#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Seeds the Gitea repository demo-config (under GITEA_USER) on branch main with
# deployment.yaml (Deployment demo-app, replicas: 1, the image demo-app runs right now) and service.yaml,
# and gives user lab-reviewer write access. GITEA_TOKEN must belong to an administrator.
# Branch protection on main is what M10 step 3 builds, so it is not set here.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env GITEA_URL GITEA_USER GITEA_TOKEN

image=$(oc get deployment demo-app -n demo -o jsonpath='{.spec.template.spec.containers[0].image}')
[ -n "$image" ] || die "deployment demo-app has no image to put in git"
has_data_volume=$(oc get deployment demo-app -n demo -o json | jq 'any(.spec.template.spec.volumes[]?; .name == "demo-data")')

deployment="apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: demo
  labels:
    app: demo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      serviceAccountName: demo-app
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: demo-app
          image: ${image}
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: [\"ALL\"]"
live_command=$(oc get deployment demo-app -n demo -o json | jq -c '.spec.template.spec.containers[0].command // empty')
if [ -n "$live_command" ]; then
  deployment="${deployment}
          command: ${live_command}"
fi
if [ "$has_data_volume" = true ]; then
  deployment="${deployment}
          volumeMounts:
            - name: demo-data
              mountPath: /data
      volumes:
        - name: demo-data
          persistentVolumeClaim:
            claimName: demo-data"
fi

service='apiVersion: v1
kind: Service
metadata:
  name: demo-app
  namespace: demo
spec:
  selector:
    app: demo-app
  ports:
    - name: http
      port: 8080
      targetPort: 8080'

gitea_ensure_repo demo-config
gitea_put_file demo-config main deployment.yaml "Add demo-app deployment" "$deployment"
gitea_put_file demo-config main service.yaml "Add demo-app service" "$service"

gitea_call GET /users/lab-reviewer
if [ "$GITEA_CODE" != 200 ]; then
  password=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32)
  gitea_call POST /admin/users "$(jq -n --arg p "$password" '{username: "lab-reviewer", email: "lab-reviewer@lab.invalid", password: $p, must_change_password: false}')"
  [ "$GITEA_CODE" = 201 ] || die "could not create Gitea user lab-reviewer (HTTP $GITEA_CODE); GITEA_TOKEN must be an administrator token"
fi
gitea_call PUT "/repos/$GITEA_USER/demo-config/collaborators/lab-reviewer" '{"permission":"write"}'
[ "$GITEA_CODE" = 204 ] || die "could not give lab-reviewer write access to demo-config (HTTP $GITEA_CODE)"
