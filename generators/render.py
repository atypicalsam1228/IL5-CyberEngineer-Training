"""Render a module content file (content/<id>.py defining MODULE) to .docx and .md.

Usage: python render.py SIEM-1 [MOD-ID ...]   (or: python render.py --all)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from il5_doc_builder import DocBuilder
from module_diagrams import render_diagrams, render_step_diagram
from order import position
from tool_links import tool_rows

HERE = Path(__file__).resolve().parent
CONTENT_DIR = HERE / "content"
OUT_DIR = HERE.parent / "modules"

INTENT_LABELS = (
    ("feared", "What the control author feared"),
    ("scope", "Is it in scope for the system"),
    ("question", "The operational question"),
    ("evidence", "What evidence proves it"),
    ("sufficient", "How much is enough"),
    ("tieoff", "Who is told when it fails"),
    ("tool", "How the tool in this module satisfies it"),
)


def load_module(module_id: str) -> dict:
    path = CONTENT_DIR / f"{module_id.lower().replace('-', '_')}.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULE


def _header(b: DocBuilder, m: dict) -> None:
    mins = m["minutes"]
    suffix = f" ({', '.join(m['controls'])})" if m["controls"] else ""
    b.title(f"{m['id']}: {m['title']}{suffix}")
    if m.get("draft"):
        b.note(f"DRAFT. {m['draft']}")
    b.table(
        ["Item", "Detail"],
        [
            ["Sequence", "Module {} of {} in the recommended order".format(*position(m["id"]))],
            ["Timed work", f"About {mins['hands_on'] + mins['verify']} minutes ({mins['hands_on']} hands-on, {mins['verify']} verify)"],
            ["Modes", "Ready Lab (prebuilt) or Architect (you design and build it)"],
            ["Standalone start", f"`{m['lab']['start']}`"],
            ["Combined start", "Continue from the end state of the previous module"],
            ["End state", f"`lab check {m['id'].lower()}` passes"],
            ["Tools", ", ".join(m["tools"])],
            ["Prerequisites", ", ".join(m["prereq"])],
        ] + ([["Extra lab needs", "; ".join(m["lab_needs"])]] if m.get("lab_needs") else []),
    )


def _intent(b: DocBuilder, m: dict) -> None:
    b.h1("1. Why This Matters")
    b.para(m["requirement"])
    if not m["mapping"]:
        return
    b.h2("Control mapping")
    b.table(
        ["Control", "What it requires, in plain words", "Source of the value", "Where this module covers it"],
        [[r["control"], r["plain"], r["source"], r["covered"]] for r in m["mapping"]],
    )
    b.h2("What each control is for")
    b.para("Read these answers first. They explain what each control is trying to prevent and how this module's tool meets it.")
    for item in m["intent"]:
        b.h3(item["control"])
        b.table(["Question", "Answer"], [[label, item[key]] for key, label in INTENT_LABELS])
    if m.get("architect"):
        b.h2("Architect mode brief")
        b.para(m["architect"])


def _terms_and_concepts(b: DocBuilder, m: dict) -> None:
    b.h2("Terms in this module")
    b.para("Each term is also explained the first time it appears. This table is a quick lookup.")
    b.table(["Term", "Plain meaning"], [list(t) for t in m["terms"]])
    b.h1("2. The Tools")
    b.h2("Tools used in this module")
    b.para("Each tool name links to its official overview. The last column says how the tool is used in the lab.")
    b.tool_table(tool_rows(m))
    render_diagrams(b, m)
    for c in m["concepts"]:
        b.h2(c["heading"])
        for p in c["paras"]:
            b.para(p)
        if c.get("table"):
            b.table(c["table"]["headers"], [list(r) for r in c["table"]["rows"]])
        if c.get("diagram"):
            b.code(c["diagram"], "text")
        if c.get("production"):
            b.production(c["production"])


def _code(b: DocBuilder, block: dict) -> None:
    b.code(block["code"], block.get("lang", "bash"))
    if block.get("lines"):
        b.table(["Part", "What it does"], [list(r) for r in block["lines"]])


def _steps(b: DocBuilder, m: dict) -> None:
    b.h1("3. Implement")
    b.para(f"Ready Lab learners start with `{m['lab']['start']}`. Architect learners design each step first using the brief above.")
    for n, s in enumerate(m["steps"], start=1):
        b.h2(f"Step {n}. {s['title']}")
        b.para(s["why"])
        render_step_diagram(b, m, n)
        for block in s["blocks"]:
            _code(b, block)
        if s.get("note"):
            b.note(s["note"])
        if s.get("security"):
            b.security(s["security"])
        if s.get("tip"):
            b.tip(s["tip"])
        b.action(s["action"])
        b.checkpoint(s["checkpoint"])


def _verify(b: DocBuilder, m: dict) -> None:
    b.h1("4. Verify It Works")
    for n, v in enumerate(m["verify"], start=1):
        b.h2(f"Test {n} ({v['kind']}). {v['title']}")
        b.para(v["why"])
        b.code(v["code"], v.get("lang", "bash"))
        b.output(v["expect"])
        b.checkpoint(v["checkpoint"])
    b.para("Run `lab check " + m["id"].lower() + "` to run these tests automatically. It checks:")
    for item in m["lab"]["checks"]:
        b.bullet(item)


def _closing(b: DocBuilder, m: dict) -> None:
    b.h1("5. Glossary and Next Steps")
    b.table(["Term", "Meaning"], [list(g) for g in m["glossary"]])
    if m.get("production"):
        b.production(m["production"])
    b.tip(m["next"])


def render(m: dict) -> tuple[Path, Path]:
    b = DocBuilder()
    _header(b, m)
    _intent(b, m)
    _terms_and_concepts(b, m)
    _steps(b, m)
    _verify(b, m)
    _closing(b, m)
    return b.save(OUT_DIR, f"{m['id']}-{m['slug']}")


def main(argv: list[str]) -> int:
    ids = [p.stem.replace("_", "-").upper() for p in sorted(CONTENT_DIR.glob("*.py"))] if argv == ["--all"] else argv
    for module_id in ids:
        docx_path, md_path = render(load_module(module_id))
        print(f"{module_id}: {docx_path.name}, {md_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
