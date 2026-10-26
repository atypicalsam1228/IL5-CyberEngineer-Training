from __future__ import annotations

from pathlib import Path

import pytest

from labcli.catalog import UnknownModuleError, load_catalog, normalize_id

REAL_GEN = Path(__file__).resolve().parents[2] / "generators"


def test_loads_in_order(gen_dir: Path) -> None:
    catalog = load_catalog(gen_dir)
    assert [m.id for m in catalog.modules] == ["M00", "SIEM-1"]
    assert catalog.modules[1].position == 2


def test_module_fields(gen_dir: Path) -> None:
    mod = load_catalog(gen_dir).get("siem-1")
    assert mod.title == "Title SIEM-1"
    assert mod.env == ("LOKI_URL", "LOKI_PASSWORD")
    assert mod.needs == ("need one",)
    assert mod.state_name == "siem-1"
    assert len(mod.tests) == 2
    assert mod.tests[0].kind == "positive"
    assert mod.minutes == 55


def test_unknown_module(gen_dir: Path) -> None:
    with pytest.raises(UnknownModuleError):
        load_catalog(gen_dir).get("nope")


def test_normalize_id() -> None:
    assert normalize_id(" siem-1 ") == "SIEM-1"
    assert normalize_id("m00") == "M00"


def test_missing_content_file(gen_dir: Path) -> None:
    (gen_dir / "content" / "m00.py").unlink()
    with pytest.raises(ValueError, match="M00"):
        load_catalog(gen_dir)


def test_missing_generators_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="order.py"):
        load_catalog(tmp_path / "absent")


def test_id_mismatch(gen_dir: Path) -> None:
    path = gen_dir / "content" / "m00.py"
    path.write_text(path.read_text(encoding="utf-8").replace('"id": "M00"', '"id": "X"'), encoding="utf-8")
    with pytest.raises(ValueError, match="mismatch"):
        load_catalog(gen_dir)


@pytest.mark.skipif(not REAL_GEN.exists(), reason="real generators not present")
def test_real_catalog() -> None:
    catalog = load_catalog(REAL_GEN)
    assert len(catalog.modules) >= 17
    assert catalog.modules[0].id == "M00"
    assert all(m.tests for m in catalog.modules)


@pytest.mark.skipif(not REAL_GEN.exists(), reason="real generators not present")
def test_capstone_is_last_scored_with_hints() -> None:
    cap = load_catalog(REAL_GEN).modules[-1]
    assert cap.id == "CAP" and cap.scored
    assert len(cap.tests) == 9
    assert all(t.hint.startswith("Fix:") for t in cap.tests)
    assert {t.kind for t in cap.tests} == {"positive", "negative"}


def test_real_cap_state_exists() -> None:
    state = Path(__file__).resolve().parents[1] / "states" / "cap"
    assert (state / "TODO.md").is_file() and (state / "10-gitea-repo.sh").is_file()
    assert (state / "reset.d" / "10-clean-cap.sh").is_file()
