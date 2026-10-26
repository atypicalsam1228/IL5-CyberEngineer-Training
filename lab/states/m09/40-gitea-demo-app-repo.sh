#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Seeds the Gitea repository demo-app (under GITEA_USER): a small Python app,
# a Dockerfile and a tests folder, on branch main and on branch critical-finding. Files are written only when
# they differ, so a second run changes nothing.
#   main:             Dockerfile base is the ubi9/python-311 image used elsewhere in the course.
#   critical-finding: Dockerfile base is docker.io/library/nginx:1.16, the old image M08 also uses.
# Confirm with trivy on a live cluster that main has no HIGH or CRITICAL and critical-finding has at least one.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env GITEA_URL GITEA_USER GITEA_TOKEN

APP_PY='import json


def handle(path):
    """Return (status, body) for a request path."""
    if path == "/healthz":
        return 200, json.dumps({"status": "ok"})
    if path == "/":
        return 200, json.dumps({"app": "demo-app"})
    return 404, json.dumps({"error": "not found"})


def serve(port=8080):  # pragma: no cover
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, body = handle(self.path)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":  # pragma: no cover
    serve()'

TEST_PY='import unittest

import app


class HandleTests(unittest.TestCase):
    def test_root(self):
        self.assertEqual(app.handle("/")[0], 200)

    def test_health(self):
        status, body = app.handle("/healthz")
        self.assertEqual(status, 200)
        self.assertIn("ok", body)

    def test_unknown_path(self):
        self.assertEqual(app.handle("/missing")[0], 404)


if __name__ == "__main__":
    unittest.main()'

dockerfile() { # base image
  printf 'FROM %s\nWORKDIR /app\nCOPY app.py .\nEXPOSE 8080\nCMD ["python3", "app.py"]' "$1"
}

gitea_ensure_repo demo-app
gitea_put_file demo-app main app.py "Add demo application" "$APP_PY"
gitea_put_file demo-app main tests/test_app.py "Add unit tests" "$TEST_PY"
gitea_put_file demo-app main Dockerfile "Add Dockerfile" "$(dockerfile registry.access.redhat.com/ubi9/python-311)"
gitea_ensure_branch demo-app critical-finding main
gitea_put_file demo-app critical-finding Dockerfile "Use an old base image with known flaws" "$(dockerfile docker.io/library/nginx:1.16)"
