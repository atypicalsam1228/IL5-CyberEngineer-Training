# M11 start state: Malware and Runtime Detection

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: Creates an empty config map falco-custom-rules in security-tools (kept if it exists); 20-demo-app.sh (demo-app with a working sh); 30-siem-forwarder.sh (SIEM-1 end state if missing).
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running); SIEM-1 (log forwarder sending application logs to Loki)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
