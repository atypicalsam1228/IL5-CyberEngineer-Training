# il5-lab-tools image

The tools container that `lab shell` and `lab check` run in. Image name:
`il5-lab-tools:latest` (override with `LAB_IMAGE`). Built locally; nothing is pushed anywhere.

## Build

From the `lab` folder, any of:

- `python lab.py build-image` (add `--dry-run` to see the command)
- Mac or Linux: `./image/build.sh`
- Windows PowerShell: `.\image\build.ps1`

It needs podman or docker, internet access, and a BuildKit-capable builder (Docker Desktop and
podman 4+ qualify). The build verifies every download against a pinned sha256
(`checksums.sha256`) and the AWS CLI against the vendor GPG signature, and stops on any mismatch.

## Contents

See `versions.txt` for each tool, its version, download URL, how it is verified, and arm64 status.
Base: Red Hat UBI 9 minimal. Runs as user `lab` (uid 1001, gid 0), HOME `/home/lab`,
workdir `/workspace`, no entrypoint (the CLI passes `bash` or a command). No credentials are in the
image: AWS and lab variables are passed in by name at run time.

## CPU types

The build targets the CPU of the machine that builds it: Apple M-series builds arm64, Intel, AMD and
most Windows PCs build amd64. Every tool has a Linux arm64 build, so there is no gap. Do not
mix: an image built on one CPU type is not meant to be copied to the other.

## Known limits

- `ubi-minimal:9.8` is a floating tag. For a release, resolve it to a digest and replace the tag.
- Podman rootless on Linux maps uid 1001 to a sub-uid, so writes to the mounted workspace can fail.
  Fix: run with `--userns=keep-id:uid=1001,gid=0` or make the workspace folder world-writable.
  Docker Desktop (Mac, Windows) is not affected.
- `velero` client is 1.18.x to match the OADP 1.6 server minor; confirm the server patch version in
  your cluster with `velero version -n openshift-adp` and rebuild if the minor differs.
- The AWS CLI signing key expires 2027-07-01; refresh `aws-cli-public-key.asc` from the AWS install
  guide when it is replaced.
- Bump a tool: edit its ARG in the Dockerfile and its rows in `checksums.sha256`, then `versions.txt`.
