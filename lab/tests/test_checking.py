from __future__ import annotations

from labcli.checking import evaluate, format_result, parse_expect, redact
from labcli.models import VerifyTest


def make(expect: str) -> VerifyTest:
    return VerifyTest(kind="positive", title="t", code="x", expect=expect)


def test_exact_match_ignores_whitespace() -> None:
    result = evaluate(make("0"), "0\n", 0)
    assert result.passed and result.mode == "exact"


def test_exact_mismatch_has_diff() -> None:
    result = evaluate(make("0"), "1\n", 0)
    assert not result.passed
    assert "-0" in result.detail and "+1" in result.detail


def test_empty_output_expectation() -> None:
    assert evaluate(make("(empty output)"), "", 0).passed
    assert not evaluate(make("(empty output)"), "oops", 0).passed


def test_loose_labels_found() -> None:
    expect = "Example only. names differ\nLeap status     : Normal\nStratum : 3"
    assert parse_expect(expect).mode == "loose"
    result = evaluate(make(expect), "Stratum         : 2\nLeap status : Normal\n", 0)
    assert result.passed


def test_loose_missing_label() -> None:
    result = evaluate(make("Example only.\nalpha: 1\nbeta: 2"), "alpha: 9", 0)
    assert not result.passed
    assert "beta" in result.detail


def test_loose_skips_placeholders() -> None:
    expect = "Example only.\nCVE-2019-XXXX\tlib\n(the second query prints nothing)\nreal: 1"
    assert parse_expect(expect).lines == ("real",)


def test_loose_with_only_placeholders_passes_on_any_output() -> None:
    assert evaluate(make("Example only.\n(nothing)"), "", 0).passed


def test_redact_secrets() -> None:
    assert redact("pw=hunter2 end", ("hunter2",)) == "pw=*** end"
    assert redact("abc", ("",)) == "abc"


def test_format_result_pass_and_fail() -> None:
    ok = evaluate(make("0"), "0", 0)
    bad = evaluate(make("0"), "1", 1)
    assert format_result(1, ok).startswith("PASS")
    text = format_result(2, bad)
    assert text.startswith("FAIL") and "expected" in text and "actual" in text


def test_loose_label_before_tab() -> None:
    assert parse_expect("Example only.\nfailed-login-burst\tfiring").lines == ("failed-login-burst",)


def test_hint_printed_on_failure_only() -> None:
    test = VerifyTest(kind="positive", title="t", code="x", expect="0", hint="Fix: do the thing.")
    assert "Fix: do the thing." in format_result(1, evaluate(test, "1", 0))
    assert "Fix:" not in format_result(1, evaluate(test, "0", 0))
