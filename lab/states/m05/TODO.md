# TODO: start state for M05 (Identity and Multi-Factor Sign-In)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

- [lab-build] 1: Keycloak at KEYCLOAK_URL with a certificate signed by the cluster ingress CA.
+ [done] 1: Checks it answers and an admin token is issued.
- [lab-build] 2: Passthrough route and https-client-auth=request on Keycloak.
- [lab-build] 3: The card-issuing CA in secret card-ca and its certificate in the Keycloak trust store (needs openssl, outside the allowed tools for state scripts).
+ [done] 3: Checks secret card-ca has tls.crt and tls.key.
- [live] 4: Admin token lifetime long enough for one step.
+ [done] 5: Checks the OAuth resource has no other identity providers.
- [live] 6: python3 and openssl present in the tools image.

Open items from review (live test or decision):
- Optional: blocked-password list file on Keycloak for the passwordBlacklist policy (review M05).
