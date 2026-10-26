"""Per-module commands: modules, start, reset, check."""
from __future__ import annotations

import json
from argparse import Namespace
from datetime import datetime, timezone

from labcli.catalog import UnknownModuleError
from labcli.checking import evaluate, format_result, redact
from labcli.context import EXIT_FAIL, EXIT_OK, EXIT_USAGE, Ctx, engine_or_none
from labcli.models import ModuleSpec
from labcli.states import Step, plan_state

MODULES_FILE = "modules.json"
KYVERNO_ANCHOR = "M07"
KYVERNO_NOTE = (
    "NOTE: Kyverno enforce policies from M07 stay active in the demo namespace until you\n"
    "run 'lab reset m07'. Pods you create in demo must comply with them."
)
TODO_PREVIEW_LINES = 12


def cmd_modules(ctx: Ctx, args: Namespace) -> int:
    catalog = ctx.catalog()
    ctx.say(f"{'#':>2}  {'ID':<7} {'Min':>3}  Title")
    for m in catalog.modules:
        ctx.say(f"{m.position:>2}  {m.id:<7} {m.minutes:>3}  {m.title}")
    return EXIT_OK


def _lookup(ctx: Ctx, raw: str) -> ModuleSpec | None:
    try:
        return ctx.catalog().get(raw)
    except UnknownModuleError as err:
        ctx.say(f"ERROR: {err.args[0]}")
        return None


def _record(ctx: Ctx, module: ModuleSpec, action: str) -> None:
    path = ctx.workspace / ".lab" / MODULES_FILE
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        current = {}
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated = {**current, module.id: {"action": action, "at": stamp}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(updated, indent=2), encoding="utf-8")


def _kyverno_note_applies(ctx: Ctx, module: ModuleSpec) -> bool:
    anchors = [m for m in ctx.catalog().modules if m.id == KYVERNO_ANCHOR]
    return bool(anchors) and module.position >= anchors[0].position


def _print_todo(ctx: Ctx, todo: str) -> None:
    ctx.say("INCOMPLETE: this start state is only partly built. Still needed (see states/<module>/TODO.md):")
    items = [l for l in todo.strip().splitlines() if l.startswith("- ")]
    for line in items[:TODO_PREVIEW_LINES]:
        ctx.say("  " + line[:200])


def _apply_steps(ctx: Ctx, module: ModuleSpec, steps: tuple[Step, ...]) -> bool:
    env = engine_or_none(ctx)
    if env is None:
        return False
    for step in steps:
        ctx.say(f"  applying {step.name}")
        try:
            result = ctx.deps.runner.run(env.wrap(step.argv, states=True))
        except OSError as err:
            ctx.say(f"ERROR: cannot run {step.name}: {err}")
            return False
        if result.returncode != 0:
            ctx.say(f"ERROR: {step.name} failed (exit {result.returncode}):")
            ctx.say(redact(result.output, ctx.secrets()).strip())
            return False
    return True


def _run_state(ctx: Ctx, args: Namespace, reset: bool) -> int:
    module = _lookup(ctx, args.module)
    if module is None:
        return EXIT_USAGE
    action = "reset" if reset else "start"
    plan = plan_state(ctx.lab_states_dir() / module.state_name, module.state_name, reset)
    if plan.missing:
        ctx.say(f"No start state for {module.id} yet (states/{module.state_name}/ not found).")
        return EXIT_FAIL
    ctx.say(f"{action} {module.id}: {module.title}")
    if module.prereq:
        ctx.say("Prerequisites: " + "; ".join(module.prereq))
    if not plan.steps:
        _print_todo(ctx, plan.todo)
        return EXIT_FAIL
    if args.dry_run:
        for step in plan.steps:
            ctx.say(f"  would apply {step.name}: " + " ".join(step.argv))
    elif not _apply_steps(ctx, module, plan.steps):
        return EXIT_FAIL
    else:
        _record(ctx, module, action)
    if plan.todo:
        _print_todo(ctx, plan.todo)
    if _kyverno_note_applies(ctx, module):
        ctx.say(KYVERNO_NOTE)
    return EXIT_OK


def cmd_start(ctx: Ctx, args: Namespace) -> int:
    return _run_state(ctx, args, reset=False)


def cmd_reset(ctx: Ctx, args: Namespace) -> int:
    return _run_state(ctx, args, reset=True)


def _select_tests(module: ModuleSpec, only: int | None) -> list[tuple[int, object]] | None:
    numbered = list(enumerate(module.tests, start=1))
    if only is None:
        return numbered
    chosen = [pair for pair in numbered if pair[0] == only]
    return chosen or None


def cmd_check(ctx: Ctx, args: Namespace) -> int:
    module = _lookup(ctx, args.module)
    if module is None:
        return EXIT_USAGE
    selected = _select_tests(module, args.test)
    if selected is None:
        ctx.say(f"ERROR: {module.id} has {len(module.tests)} tests; no test {args.test}.")
        return EXIT_USAGE
    ctx.say(f"check {module.id}: {module.title}")
    if args.dry_run:
        for number, test in selected:
            ctx.say(f"  would run test {number} ({test.kind}) inside the lab shell:")
            ctx.say("\n".join("    " + line for line in test.code.splitlines()))
        return EXIT_OK
    env = engine_or_none(ctx)
    if env is None:
        return EXIT_USAGE
    return _run_tests(ctx, env, selected, module.scored, module)


def _run_one(ctx: Ctx, env, test):
    secrets = ctx.secrets()
    try:
        result = ctx.deps.runner.run(env.wrap(("bash", "-c", test.code)))
    except OSError as err:
        return evaluate(test, f"could not run: {err}", 127)
    return evaluate(test, redact(result.output, secrets), result.returncode)


def _run_tests(ctx: Ctx, env, selected, scored: bool = False, module=None) -> int:
    failed = 0
    for number, test in selected:
        outcome = _run_one(ctx, env, test)
        ctx.say(format_result(number, outcome))
        failed += 0 if outcome.passed else 1
    total = len(selected)
    ctx.say(f"{total - failed} of {total} tests passed." + ("" if not failed else f" {failed} FAILED."))
    if scored and total == len(module.tests):
        ctx.say(f"Score: {total - failed} of {total}." + (" Capstone complete." if not failed else ""))
    return EXIT_FAIL if failed else EXIT_OK
