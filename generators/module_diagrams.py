"""Learner diagrams inside a module: Graphviz rendering and checks.

A module may define `diagrams`, a list of at most MAX_DIAGRAMS dicts:
  id       short slug, unique in the module
  title    what the picture shows (the claim); starts with a capital letter
  caption  one or two plain sentences telling the learner what to look for
  reading  list of plain sentences that say the same thing in words (alt text and the .md text)
  rankdir  "LR" (default) or "TB"
  zones    list of boundaries: {"id", "label", "parent"?, "kind"?, "s"?}; kind is "boundary" (dashed, default)
           or "group" (solid, light)
  nodes    list of boxes: {"id", "title", "sub"?, "zone"?, "kind"?, "s"?}
  edges    list of arrows: {"a", "b", "label"?, "n"?, "kind"?, "s"?, "pad"?, "minlen"?, "beside"?}; beside puts the label next to the arrow, pad adds blank space before the label,
           minlen lengthens the arrow; n is the flow number shown as a badge
  flat     True on an edge keeps both ends on the same row or column
  kind     neutral (default), ok, bad, warn
  per_step True to draw one picture per module step; "step_notes": {1: "...", ...} adds one sentence under it.

Every node must sit inside a zone, so nothing is accidentally drawn outside the boundary. Every title, sub and
label starts with a capital letter. `s=N` on a zone, node or edge means "added in step N": for step k the renderer
draws parts with s<=k, outlines the ones with s==k in blue, and keeps later parts invisible so nothing moves.
"""

from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

import sources

MAX_DIAGRAMS = 3
MAX_NODES = 12
MAX_WIDTH_IN = 6.3
MAX_HEIGHT_IN = 5.2
DPI = 200
FONT = "Segoe UI,Arial,sans-serif"
STEP_ACCENT = "#1565C0"
IMG_DIR = Path(__file__).resolve().parent.parent / "modules" / "img"
REQUIRED_KEYS = ("id", "title", "caption", "reading", "nodes", "edges", "zones")
DOT_CANDIDATES = (
    "dot",
    "C:/Program Files/Graphviz/bin/dot.exe",
    "/usr/bin/dot",
    "/opt/homebrew/bin/dot",
)
# kind -> (fill, line, header text)
KINDS = {
    "neutral": ("#F4F6F8", "#455A64", "#263238"),
    "ok": ("#E8F5E9", "#2E7D32", "#1B5E20"),
    "bad": ("#FFEBEE", "#C62828", "#8E1B1B"),
    "warn": ("#FFF8E1", "#B26A00", "#7A4A00"),
}
ZONE_STYLE = {
    "boundary": ('"dashed,rounded"', "#455A64", "#FFFFFF"),
    "group": ('"rounded,filled"', "#B0BEC5", "#F8FAFB"),
}


def find_dot() -> str | None:
    for candidate in DOT_CANDIDATES:
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    return None


def _run_dot(source: str, fmt: str, out: Path | None = None) -> subprocess.CompletedProcess:
    dot = find_dot()
    if dot is None:
        raise FileNotFoundError("Graphviz dot not found")
    args = [dot, f"-T{fmt}"]
    if fmt == "png":
        args += [f"-Gdpi={DPI}"]
    if out is not None:
        args += ["-o", str(out)]
    return subprocess.run(args, input=source.encode("ascii"), capture_output=True, check=False)


def _q(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _node_label(node: dict, text_color: str) -> str:
    title = html.escape(node["title"])
    rows = f'<TR><TD ALIGN="CENTER"><FONT POINT-SIZE="15" COLOR="{text_color}"><B>{title}</B></FONT></TD></TR>'
    if node.get("sub"):
        sub = html.escape(node["sub"])
        rows += f'<TR><TD ALIGN="CENTER"><FONT POINT-SIZE="12" COLOR="#546E7A">{sub}</FONT></TD></TR>'
    return f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">{rows}</TABLE>>'


def _visible(part: dict, k: int | None) -> bool:
    if k is None:
        return "until" not in part
    return part.get("s", 0) <= k and k < part.get("until", 10**6)


def _is_new(part: dict, k: int | None) -> bool:
    return k is not None and part.get("s", 0) == k and k > 0


def _node_line(node: dict, k: int | None) -> str:
    fill, line, text = KINDS[node.get("kind", "neutral")]
    if not _visible(node, k):
        return f'  {node["id"]} [label={_node_label(node, text)}, style=invis];'
    pen = 1.6
    if _is_new(node, k):
        line, pen = STEP_ACCENT, 4.0
    return (
        f'  {node["id"]} [label={_node_label(node, text)}, fillcolor="{fill}", color="{line}", penwidth={pen}];'
    )


def _edge_label(text: str, color: str, pad: int = 0, trailing: bool = False) -> str:
    """HTML label on a white box, so an arrow or a boundary line never runs through the words."""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe + "&#160;" * pad if trailing else "&#160;" * pad + safe
    return (
        f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">'
        f'<TR><TD BGCOLOR="white"><FONT COLOR="{color}">{safe}</FONT></TD></TR></TABLE>>'
    )


def _edge_line(edge: dict, k: int | None) -> str:
    kind = edge.get("kind", "neutral")
    _, line, text = KINDS[kind]
    if not _visible(edge, k):
        flat = ", constraint=false" if edge.get("flat") else ""
        lab = f", label={_edge_label(edge['label'], text, edge.get('pad', 0))}" if edge.get("label") else ""
        return f'  {edge["a"]} -> {edge["b"]} [style=invis{lab}{flat}];'
    label = edge.get("label", "")
    if edge.get("n"):
        label = f'{edge["n"]}  {label}'.strip()
    pen = 4.0 if _is_new(edge, k) else 2.0
    color = line
    style = "dashed" if kind == "bad" else "solid"
    flat = ", constraint=false" if edge.get("flat") else ""
    flat += f", minlen={edge['minlen']}" if edge.get("minlen") else ""
    attr = "xlabel" if edge.get("beside") else "label"
    lab = f", {attr}={_edge_label(label, text, edge.get('pad', 0), bool(edge.get('beside')))}" if label else ""
    return f'  {edge["a"]} -> {edge["b"]} [color="{color}", fontcolor="{text}", penwidth={pen}, style={style}{lab}{flat}];'


def _zone_block(zone: dict, zones: list[dict], nodes: list[dict], k: int | None, indent: int = 1) -> list[str]:
    pad = "  " * indent
    style, line, fill = ZONE_STYLE[zone.get("kind", "boundary")]
    if not _visible(zone, k):
        out = [f'{pad}subgraph cluster_{zone["id"]} {{ style=invis; label="";']
    else:
        out = [
            f'{pad}subgraph cluster_{zone["id"]} {{',
            f'{pad}  label={_q(zone["label"])}; labeljust={zone.get('labeljust', 'l')}; labelloc={zone.get('labelloc', 't')}; fontsize=13; fontcolor="#37474F";',
            f'{pad}  style={style}; color="{line}"; fillcolor="{fill}"; penwidth=1.6; margin=18;',
        ]
    for child in (z for z in zones if z.get("parent") == zone["id"]):
        out += _zone_block(child, zones, nodes, k, indent + 1)
    for node in (n for n in nodes if n.get("zone") == zone["id"]):
        out.append("  " * (indent + 1) + _node_line(node, k).strip())
    out.append(f"{pad}}}")
    return out


def full_source(diagram: dict, k: int | None = None) -> str:
    """DOT source for the finished picture (k=None) or for module step k."""
    zones, nodes = diagram["zones"], diagram["nodes"]
    lines = [
        "digraph G {",
        f'  graph [rankdir={diagram.get("rankdir", "LR")}, bgcolor="white", pad=0.3, nodesep=0.6, ranksep=1.0, '
        f'fontname="{FONT}", forcelabels=true, splines=true];',
        f'  node [shape=box, style="rounded,filled", fontname="{FONT}", margin="0.25,0.14", width=1.6, height=0.7];',
        f'  edge [fontname="{FONT}", fontsize=13, arrowsize=1.0];',
    ]
    for top in (z for z in zones if not z.get("parent")):
        lines += _zone_block(top, zones, nodes, k)
    lines += [_edge_line(e, k) for e in diagram["edges"]]
    lines.append("}")
    return "\n".join(lines) + "\n"


def _step_diagram(m: dict) -> dict | None:
    return next((d for d in (m.get("diagrams") or []) if d.get("per_step")), None)


def _width_for(png: Path) -> float:
    """Fit the image into the page, keeping its shape."""
    from PIL import Image

    with Image.open(png) as im:
        w, h = im.size
    return min(MAX_WIDTH_IN, MAX_HEIGHT_IN * w / h)


def _draw(diagram: dict, k: int | None, png: Path, label: str) -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    result = _run_dot(full_source(diagram, k), "png", png)
    if result.returncode != 0:
        raise RuntimeError(f"{label}: {result.stderr.decode(errors='replace')[:200]}")


def render_step_diagram(b, m: dict, n: int) -> None:
    """Add the picture for module step n (what this step is about to build) if the module has one."""
    diagram = _step_diagram(m)
    if diagram is None:
        return
    png = IMG_DIR / f"{m['id']}-step-{n}.png"
    _draw(diagram, n, png, f"{m['id']} step {n} diagram")
    b.para("What this step adds (thick lines and outlines are new):")
    b.image(png, f"{diagram['title']}, after step {n}", "", width_in=_width_for(png))
    note = (diagram.get("step_notes") or {}).get(n)
    if note:
        b.bullet(note)


def render_diagrams(b, m: dict) -> None:
    """Add every finished-picture diagram of module `m` to the document builder `b`."""
    diagrams = m.get("diagrams") or []
    if not diagrams:
        return
    b.h2("How it fits together")
    for index, diagram in enumerate(diagrams, start=1):
        b.h3(diagram["title"])
        b.para(diagram["caption"])
        png = IMG_DIR / f"{m['id']}-diagram-{index}.png"
        _draw(diagram, None, png, f"{m['id']} diagram {diagram['id']}")
        b.image(png, diagram["title"], "", width_in=_width_for(png))
        for line in diagram["reading"]:
            b.bullet(line)


def _capital(text: str) -> bool:
    return bool(text) and (text[0].isupper() or text[0].isdigit())


def _texts(d: dict) -> list[tuple[str, str]]:
    out = [("title", d["title"])]
    out += [("zone label", z["label"]) for z in d["zones"]]
    for n in d["nodes"]:
        out.append(("node title", n["title"]))
        if n.get("sub"):
            out.append(("node sub", n["sub"]))
    out += [("edge label", e["label"]) for e in d["edges"] if e.get("label")]
    return out


def _check_structure(d: dict, steps: int, err) -> None:
    did = d["id"]
    zone_ids = {z["id"] for z in d["zones"]}
    node_ids = {n["id"] for n in d["nodes"]}
    if len(node_ids) != len(d["nodes"]):
        err(f"diagram {did}: duplicate node id")
    for n in d["nodes"]:
        if n.get("zone") not in zone_ids:
            err(f"diagram {did}: node {n['id']} is not inside a zone (it would be drawn outside the boundary)")
        if n.get("kind", "neutral") not in KINDS:
            err(f"diagram {did}: node {n['id']} has unknown kind")
    for z in d["zones"]:
        if z.get("parent") and z["parent"] not in zone_ids:
            err(f"diagram {did}: zone {z['id']} has unknown parent")
    for e in d["edges"]:
        if e["a"] not in node_ids or e["b"] not in node_ids:
            err(f"diagram {did}: edge {e['a']}->{e['b']} names an unknown node")
    for kind, text in _texts(d):
        if not _capital(text):
            err(f"diagram {did}: {kind} '{text}' must start with a capital letter")
    if d.get("per_step"):
        notes = d.get("step_notes") or {}
        for part in [*d["zones"], *d["nodes"], *d["edges"]]:
            if part.get("s", 0) > steps:
                err(f"diagram {did}: s={part['s']} but the module has {steps} steps")
        missing = [n for n in range(1, steps + 1) if n not in notes]
        if missing:
            err(f"diagram {did}: step_notes missing for steps {missing}")
        for text in notes.values():
            if not _capital(text) or not text.rstrip().endswith("."):
                err(f"diagram {did}: step note '{text}' must be a capitalized sentence ending in a period")


def check_diagrams(m: dict, err, warn) -> None:
    """Report problems with module `m`'s diagrams through the err and warn callbacks."""
    diagrams = m.get("diagrams") or []
    if len(diagrams) > MAX_DIAGRAMS:
        err(f"diagrams: {len(diagrams)} given, at most {MAX_DIAGRAMS}")
    seen: set[str] = set()
    banned = [x.lower() for x in sources.banned_names() if x.strip()]
    for d in diagrams:
        missing = [k for k in REQUIRED_KEYS if k not in d]
        if missing:
            err(f"diagram {d.get('id', '?')}: missing {missing}")
            continue
        if d["id"] in seen:
            err(f"diagram {d['id']}: duplicate id")
        seen.add(d["id"])
        text = " ".join([d["title"], d["caption"], *d["reading"], *(t for _, t in _texts(d))])
        if not text.isascii():
            err(f"diagram {d['id']}: non-ASCII text")
            continue
        hit = [x for x in banned if x in text.lower()]
        if hit:
            err(f"diagram {d['id']}: banned words {hit}")
        if not d["reading"]:
            err(f"diagram {d['id']}: 'reading' is empty")
        if len(d["nodes"]) > MAX_NODES:
            err(f"diagram {d['id']}: {len(d['nodes'])} nodes, at most {MAX_NODES}")
        _check_structure(d, len(m.get("steps", [])), err)
        _check_render(d, err, warn)


def _check_render(d: dict, err, warn) -> None:
    if find_dot() is None:
        warn(f"diagram {d['id']}: Graphviz not installed, drawing not checked")
        return
    result = _run_dot(full_source(d), "plain")
    if result.returncode != 0:
        err(f"diagram {d['id']}: Graphviz error: {result.stderr.decode(errors='replace')[:160]}")
    elif result.stderr.strip():
        warn(f"diagram {d['id']}: Graphviz warning: {result.stderr.decode(errors='replace')[:120]}")
