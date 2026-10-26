"""Commands that act on the whole lab: shell, up, down, status."""
from __future__ import annotations

import json
import os
from argparse import Namespace

from labcli.credentials import read_env_file, with_generated, write_private
from labcli.context import EXIT_FAIL, EXIT_OK, EXIT_USAGE, Ctx, engine_or_none
from labcli.environment import CONTRACT_VARS, LabEnv, detect_engine, EngineNotFoundError
from labcli.terraform import (
    COST_WARNING,
    DESTROY_WARNING,
    DOWN_FAILED,
    apply_argv,
    destroy_argv,
    init_argv,
    output_argv,
    outputs_to_env,
)

CONFIRM_UP = "yes"
CONFIRM_DOWN = "destroy"
MODULES_FILE = "modules.json"


def cmd_shell(ctx: Ctx, args: Namespace) -> int:
    if ctx.in_shell:
        ctx.say("You are already inside the lab shell.")
        return EXIT_USAGE
    env = engine_or_none(ctx)
    if env is None:
        return EXIT_USAGE
    argv = env.shell_argv()
    if args.dry_run:
        ctx.show(argv)
        return EXIT_OK
    env.workspace.mkdir(parents=True, exist_ok=True)
    return ctx.deps.runner.run_interactive(argv)


def _terraform_ready(ctx: Ctx, env: LabEnv) -> bool:
    if any(env.terraform_dir.glob("*.tf")):
        return True
    ctx.say(f"TODO: no Terraform files in {env.terraform_dir}. The lab build is not provided yet.")
    return False


def _lifecycle_env(ctx: Ctx) -> LabEnv | None:
    if ctx.in_shell:
        ctx.say("Run this from your own computer, not inside the lab shell.")
        return None
    return engine_or_none(ctx)


def _confirmed(ctx: Ctx, assume_yes: bool, word: str) -> bool:
    if assume_yes:
        return True
    answer = ctx.deps.ask(f"Type '{word}' to continue: ").strip().lower()
    return answer == word


def _write_env_file(ctx: Ctx, env: LabEnv, values: dict[str, str]) -> None:
    text = "".join(f"{k}={v}\n" for k, v in sorted(values.items()))
    write_private(env.env_file, text)
    try:
        os.chmod(env.env_file, 0o600)
    except OSError:
        ctx.say("Note: could not restrict permissions on the lab variables file.")
    ctx.say("Saved lab variables: " + (", ".join(sorted(values)) or "none"))


def _export_outputs(ctx: Ctx, env: LabEnv) -> None:
    result = ctx.deps.runner.run(env.wrap(output_argv(), terraform=True))
    values = outputs_to_env(result.output) if result.returncode == 0 else {}
    if values:
        # Keep credentials from an earlier `lab up`; create random ones for the rest.
        _write_env_file(ctx, env, with_generated({**read_env_file(env.env_file), **values}))
    else:
        ctx.say("No lab variables found in Terraform outputs. 'lab shell' will lack them.")


def cmd_up(ctx: Ctx, args: Namespace) -> int:
    env = _lifecycle_env(ctx)
    if env is None:
        return EXIT_USAGE
    if not _terraform_ready(ctx, env):
        return EXIT_FAIL
    ctx.say(COST_WARNING)
    steps = (init_argv(), apply_argv())
    if args.dry_run:
        for step in steps:
            ctx.show(env.wrap(step, terraform=True))
        ctx.show(env.wrap(output_argv(), terraform=True))
        return EXIT_OK
    if not _confirmed(ctx, args.yes, CONFIRM_UP):
        ctx.say("Cancelled. Nothing was built.")
        return EXIT_FAIL
    env.state_dir.mkdir(parents=True, exist_ok=True)
    for step in steps:
        if ctx.deps.runner.run_interactive(env.wrap(step, terraform=True)) != 0:
            ctx.say("Build failed. Some resources may exist and cost money. Run 'lab down' to clean up.")
            return EXIT_FAIL
    _export_outputs(ctx, env)
    ctx.say("Lab is up. Remember: run 'lab down' when you finish.")
    return EXIT_OK


def cmd_down(ctx: Ctx, args: Namespace) -> int:
    env = _lifecycle_env(ctx)
    if env is None:
        return EXIT_USAGE
    ctx.say(DESTROY_WARNING)
    argv = env.wrap(destroy_argv(), terraform=True)
    if args.dry_run:
        ctx.show(argv)
        return EXIT_OK
    if not _confirmed(ctx, args.yes, CONFIRM_DOWN):
        ctx.say("Cancelled. Your lab is STILL RUNNING and still costs money.")
        return EXIT_FAIL
    if ctx.deps.runner.run_interactive(argv) != 0:
        ctx.say(DOWN_FAILED)
        return EXIT_FAIL
    for leftover in (env.env_file, env.state_dir / MODULES_FILE):
        leftover.unlink(missing_ok=True)
    ctx.say("Lab destroyed. Verify in the AWS console that nothing tagged with your lab id remains.")
    return EXIT_OK


def _engine_label(ctx: Ctx) -> str:
    if ctx.in_shell:
        return "inside lab shell"
    try:
        return detect_engine(ctx.deps.which, ctx.deps.environ.get("LAB_ENGINE"))
    except EngineNotFoundError:
        return "none found (install podman or docker)"


def _module_records(ctx: Ctx) -> dict[str, dict[str, str]]:
    path = ctx.workspace / ".lab" / MODULES_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def cmd_status(ctx: Ctx, args: Namespace) -> int:
    ctx.say(f"Container engine: {_engine_label(ctx)}")
    ctx.say(f"Workspace: {ctx.workspace}")
    state = ctx.workspace / ".lab" / "terraform.tfstate"
    ctx.say("Lab built: " + ("yes (Terraform state present)" if state.is_file() else "no"))
    ctx.say("Lab variables (values are never shown):")
    for name in CONTRACT_VARS:
        ctx.say(f"  {name}: " + ("set" if ctx.deps.environ.get(name) else "not set"))
    records = _module_records(ctx)
    ctx.say("Modules applied: " + (", ".join(f"{k} ({v.get('action', '?')})" for k, v in records.items()) or "none"))
    return EXIT_OK
