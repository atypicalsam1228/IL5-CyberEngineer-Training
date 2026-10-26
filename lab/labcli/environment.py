"""Tools-container environment: engine detection and command wrapping."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ENGINES = ("podman", "docker")
DEFAULT_IMAGE = "il5-lab-tools:latest"
CONTAINER_WORKSPACE = "/workspace"
CONTAINER_STATES = "/lab/states"
CONTAINER_TERRAFORM = "/lab/terraform"
KUBECONFIG_IN_CONTAINER = "/workspace/.lab/kubeconfig"

CONTRACT_VARS = (
    "LAB_ID AWS_REGION CLUSTER_NAME CLUSTER_API LOKI_URL LOKI_CA_FILE LOKI_USER LOKI_PASSWORD "
    "GRAFANA_URL GRAFANA_USER GRAFANA_PASSWORD MM_URL MM_WEBHOOK_URL KEYCLOAK_URL "
    "KEYCLOAK_ADMIN_USER KEYCLOAK_ADMIN_PASSWORD GITEA_URL GITEA_USER GITEA_TOKEN ARGOCD_URL "
    "REGISTRY_HOST BACKUP_BUCKET LOG_BUCKET ARTIFACTS_BUCKET BASTION_ID KMS_KEY_ARN VPC_ID"
).split()

AWS_VARS = (
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "AWS_PROFILE", "AWS_DEFAULT_REGION",
)

SECRET_MARKERS = ("PASSWORD", "TOKEN", "SECRET", "ACCESS_KEY")


class EngineNotFoundError(RuntimeError):
    """Neither podman nor docker is installed."""


def detect_engine(which: Callable[[str], str | None], override: str | None = None) -> str:
    if override:
        return override
    for name in ENGINES:
        if which(name):
            return name
    raise EngineNotFoundError("Install podman or docker, then try again.")


def is_secret_name(name: str) -> bool:
    return any(marker in name for marker in SECRET_MARKERS)


@dataclass(frozen=True)
class LabEnv:
    engine: str
    image: str
    workspace: Path
    states_dir: Path
    terraform_dir: Path
    in_shell: bool
    passthrough: tuple[str, ...] = tuple(CONTRACT_VARS) + AWS_VARS

    @property
    def state_dir(self) -> Path:
        return self.workspace / ".lab"

    @property
    def env_file(self) -> Path:
        return self.state_dir / "lab.env"

    def _base(self, interactive: bool, mounts: tuple[str, ...]) -> list[str]:
        argv = [self.engine, "run", "--rm"]
        argv += ["-it"] if interactive else ["-i"]
        argv += ["-v", f"{self.workspace}:{CONTAINER_WORKSPACE}", "-w", CONTAINER_WORKSPACE]
        for mount in mounts:
            argv += ["-v", mount]
        argv += ["-e", "LAB_IN_SHELL=1", "-e", f"KUBECONFIG={KUBECONFIG_IN_CONTAINER}"]
        if self.env_file.is_file():
            argv += ["--env-file", str(self.env_file)]
        for name in self.passthrough:
            argv += ["-e", name]  # name only: the value is inherited, never put on the command line
        return argv

    def shell_argv(self) -> tuple[str, ...]:
        if self.in_shell:
            raise ValueError("Already inside the lab shell.")
        mounts = (f"{self.states_dir}:{CONTAINER_STATES}:ro",)
        return tuple(self._base(True, mounts)) + (self.image, "bash")

    def wrap(self, argv: tuple[str, ...], states: bool = False, terraform: bool = False) -> tuple[str, ...]:
        """Return argv that runs inside the tools container (unchanged if already inside)."""
        if self.in_shell:
            return argv
        mounts: list[str] = []
        if states:
            mounts.append(f"{self.states_dir}:{CONTAINER_STATES}:ro")
        if terraform:
            mounts.append(f"{self.terraform_dir}:{CONTAINER_TERRAFORM}")
        return tuple(self._base(False, tuple(mounts))) + (self.image,) + argv
