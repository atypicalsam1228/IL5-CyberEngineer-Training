"""Immutable data types shared across the lab CLI."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyTest:
    """One verify test from a module definition."""

    kind: str
    title: str
    code: str
    expect: str
    hint: str = ""


@dataclass(frozen=True)
class ModuleSpec:
    """Per-module metadata derived from generators/content."""

    id: str
    title: str
    position: int
    total: int
    prereq: tuple[str, ...]
    env: tuple[str, ...]
    needs: tuple[str, ...]
    minutes: int
    tests: tuple[VerifyTest, ...]
    scored: bool = False

    @property
    def state_name(self) -> str:
        """Directory name under states/ (lower-case module id)."""
        return self.id.lower()
