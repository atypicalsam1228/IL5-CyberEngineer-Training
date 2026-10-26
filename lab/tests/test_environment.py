from __future__ import annotations

from pathlib import Path

import pytest

from labcli.environment import EngineNotFoundError, LabEnv, detect_engine


def make_env(tmp_path: Path, in_shell: bool = False) -> LabEnv:
    return LabEnv(
        engine="podman",
        image="img:1",
        workspace=tmp_path / "ws",
        states_dir=tmp_path / "states",
        terraform_dir=tmp_path / "tf",
        in_shell=in_shell,
        passthrough=("LOKI_URL", "LOKI_PASSWORD"),
    )


def test_detect_prefers_podman() -> None:
    assert detect_engine(lambda n: f"/bin/{n}") == "podman"


def test_detect_docker_fallback() -> None:
    assert detect_engine(lambda n: "/bin/docker" if n == "docker" else None) == "docker"


def test_detect_override() -> None:
    assert detect_engine(lambda n: None, override="docker") == "docker"


def test_detect_none() -> None:
    with pytest.raises(EngineNotFoundError):
        detect_engine(lambda n: None)


def test_shell_argv_passes_names_not_values(tmp_path: Path) -> None:
    argv = make_env(tmp_path).shell_argv()
    assert argv[:3] == ("podman", "run", "--rm")
    assert "-it" in argv
    assert "LOKI_PASSWORD" in argv
    assert not any("=" in a and "PASSWORD" in a for a in argv)
    assert "img:1" in argv and argv[-1] == "bash"
    assert any(a.endswith(":/workspace") for a in argv)


def test_env_file_only_if_present(tmp_path: Path) -> None:
    env = make_env(tmp_path)
    assert "--env-file" not in env.shell_argv()
    env.env_file.parent.mkdir(parents=True)
    env.env_file.write_text("A=b\n", encoding="utf-8")
    assert "--env-file" in env.shell_argv()


def test_wrap_in_container_vs_in_shell(tmp_path: Path) -> None:
    outer = make_env(tmp_path).wrap(("oc", "get", "pods"))
    assert outer[0] == "podman" and outer[-3:] == ("oc", "get", "pods")
    assert "-it" not in outer
    assert make_env(tmp_path, in_shell=True).wrap(("oc", "get", "pods")) == ("oc", "get", "pods")


def test_wrap_mounts_states_readonly(tmp_path: Path) -> None:
    argv = make_env(tmp_path).wrap(("true",), states=True)
    assert any(a.endswith(":/lab/states:ro") for a in argv)


def test_wrap_mounts_terraform(tmp_path: Path) -> None:
    argv = make_env(tmp_path).wrap(("true",), terraform=True)
    assert any(a.endswith(":/lab/terraform") for a in argv)


def test_shell_argv_inside_shell_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        make_env(tmp_path, in_shell=True).shell_argv()
