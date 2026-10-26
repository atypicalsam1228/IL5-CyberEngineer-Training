"""Load module metadata from generators/ (read-only imports by file path)."""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from labcli.models import ModuleSpec, VerifyTest


class UnknownModuleError(KeyError):
    """Raised when a module id is not in the recommended order."""


def normalize_id(raw: str) -> str:
    return raw.strip().upper()


@dataclass(frozen=True)
class Catalog:
    modules: tuple[ModuleSpec, ...]

    def get(self, raw_id: str) -> ModuleSpec:
        wanted = normalize_id(raw_id)
        for module in self.modules:
            if module.id == wanted:
                return module
        known = ", ".join(m.id for m in self.modules)
        raise UnknownModuleError(f"Unknown module '{raw_id}'. Known modules: {known}")


def _load_file(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _content_path(generators: Path, module_id: str) -> Path:
    return generators / "content" / (module_id.lower().replace("-", "_") + ".py")


def _build_tests(raw: list[dict[str, Any]]) -> tuple[VerifyTest, ...]:
    return tuple(
        VerifyTest(kind=t["kind"], title=t["title"], code=t["code"], expect=t["expect"], hint=t.get("hint", ""))
        for t in raw
    )


def _build_spec(data: dict[str, Any], position: int, total: int) -> ModuleSpec:
    minutes = data.get("minutes", {})
    lab = data.get("lab", {})
    return ModuleSpec(
        id=data["id"],
        title=data["title"],
        position=position,
        total=total,
        prereq=tuple(data.get("prereq") or ()),
        env=tuple(lab.get("env") or ()),
        needs=tuple(data.get("lab_needs") or ()),
        minutes=int(minutes.get("hands_on", 0)) + int(minutes.get("verify", 0)),
        tests=_build_tests(data.get("verify") or []),
        scored=bool(data.get("scored", False)),
    )


def load_catalog(generators: Path) -> Catalog:
    """Read ORDER and each MODULE dict. Never writes to generators/."""
    order_path = generators / "order.py"
    if not order_path.is_file():
        raise ValueError(f"order.py not found in {generators}")
    order: list[str] = list(_load_file(order_path, "lab_order").ORDER)
    specs: list[ModuleSpec] = []
    for index, module_id in enumerate(order, start=1):
        path = _content_path(generators, module_id)
        if not path.is_file():
            raise ValueError(f"Content file for {module_id} not found: {path}")
        data = _load_file(path, f"lab_content_{index}").MODULE
        if data["id"] != module_id:
            raise ValueError(f"Id mismatch in {path}: {data['id']} != {module_id}")
        specs.append(_build_spec(data, index, len(order)))
    return Catalog(modules=tuple(specs))
