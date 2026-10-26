# M04 start state: FIPS Cryptography and Keys

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: Turns etcd encryption off, unsets the API server and router TLS profiles, and turns key rotation off.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Note: Kyverno enforce policies from M07 persist in the demo namespace unless you run `lab reset m07`.

Scripts here have not been run on a live cluster.
