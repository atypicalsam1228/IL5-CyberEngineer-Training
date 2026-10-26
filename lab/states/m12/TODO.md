# TODO: start state for M12 (Backup and Recovery)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: OADP operator in openshift-adp and secret cloud-credentials (key cloud) from a LabId-tagged IAM user limited to BACKUP_BUCKET and KMS_KEY_ARN.
- [live] 1: Operator default channel, and that the credentials work with the bucket and key (the BackupStorageLocation shows Available only after M12 step 2).
+ [done] 2: Checks the backup bucket exists and encrypts by default with KMS_KEY_ARN (bucket created by terraform/storage.tf).
+ [done] 3: demo-app mounts writable claim demo-data at /data; image has sh and cat.
- [live] 3: Storage class supports file-level backup through the OADP node agent; /data writable under the restricted SCC (fsGroup).
+ [done] 4: Nothing to build: lab start m12 does not extend Velero retention (this is a statement in the module); step 3 of the module uses the schedule and the learner must take a new backup after 30 days.
- [live] 5: velero client version matches the OADP Velero server; lab shell aws identity can read the backup bucket.

Open items from review (live test or decision):
- Velero default retention expires lab backups unless --ttl is set (review M12).
