"""Argument parsing and dispatch for the lab command."""
from __future__ import annotations

import argparse
import shutil
import sys
from collections.abc import Callable, Sequence
from os import environ as os_environ

from labcli.commands_image import cmd_build_image
from labcli.commands_lab import cmd_down, cmd_shell, cmd_status, cmd_up
from labcli.commands_module import cmd_check, cmd_modules, cmd_reset, cmd_start
from labcli.context import EXIT_USAGE, Ctx, Deps
from labcli.executor import SubprocessRunner

__all__ = ["Deps", "main", "build_parser", "default_deps"]

Handler = Callable[[Ctx, argparse.Namespace], int]


def _add_dry_run(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--dry-run", action="store_true", help="print what would run; change nothing")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lab", description="IL5 hands-on lab helper")
    cmds = parser.add_subparsers(dest="command")
    _add_dry_run(cmds.add_parser("shell", help="open the lab tools container"))
    for name, text in (("up", "build your lab in AWS (costs money)"), ("down", "destroy your lab (stops the cost)")):
        sub = cmds.add_parser(name, help=text)
        _add_dry_run(sub)
        sub.add_argument("--yes", action="store_true", help="skip the confirmation question")
    for name, text in (("start", "load a module's starting state"), ("reset", "return a module to its starting state")):
        sub = cmds.add_parser(name, help=text)
        sub.add_argument("module")
        _add_dry_run(sub)
    check = cmds.add_parser("check", help="run a module's tests")
    check.add_argument("module")
    check.add_argument("--test", type=int, default=None, help="run only this test number")
    _add_dry_run(check)
    _add_dry_run(cmds.add_parser("build-image", help="build the tools container image locally"))
    cmds.add_parser("status", help="show lab status")
    cmds.add_parser("modules", help="list modules in recommended order")
    return parser


HANDLERS: dict[str, Handler] = {
    "shell": cmd_shell, "up": cmd_up, "down": cmd_down, "status": cmd_status,
    "build-image": cmd_build_image, "modules": cmd_modules, "start": cmd_start, "reset": cmd_reset, "check": cmd_check,
}


def default_deps() -> Deps:
    return Deps(
        runner=SubprocessRunner(),
        out=sys.stdout,
        ask=input,
        which=shutil.which,
        environ=dict(os_environ),
    )


def main(argv: Sequence[str] | None = None, deps: Deps | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    ctx = Ctx(deps or default_deps())
    if args.command is None:
        ctx.say(parser.format_help())
        return EXIT_USAGE
    try:
        return HANDLERS[args.command](ctx, args)
    except ValueError as err:
        ctx.say(f"ERROR: {err}")
        return EXIT_USAGE
