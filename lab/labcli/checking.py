"""Compare verify-test output with the expected text from the module."""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

from labcli.models import VerifyTest

EXAMPLE_PREFIX = "example only"
EMPTY_MARKER = "(empty output)"
PLACEHOLDER_PATTERN = re.compile(r"xxxx|example|<|\.\.\.", re.IGNORECASE)


@dataclass(frozen=True)
class Expectation:
    """mode 'exact' compares whole output; 'loose' checks that line labels appear."""

    mode: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class TestResult:
    __test__ = False  # not a pytest class

    title: str
    kind: str
    passed: bool
    mode: str
    expected: str
    actual: str
    detail: str
    exit_code: int
    hint: str = ""


def _norm(text: str) -> str:
    return "\n".join(" ".join(line.split()) for line in text.strip().splitlines() if line.strip())


def _label(line: str) -> str:
    """Stable part of an example line: text before a tab or the first colon."""
    head = line.split("\t", 1)[0]
    if ":" in head:
        head = head.split(":", 1)[0]
    return " ".join(head.split())


def _is_usable_label(label: str) -> bool:
    if not label or label.startswith("("):
        return False
    return PLACEHOLDER_PATTERN.search(label) is None


def parse_expect(expect: str) -> Expectation:
    lines = expect.strip().splitlines()
    if lines and lines[0].strip().lower().startswith(EXAMPLE_PREFIX):
        labels = tuple(l for l in (_label(x) for x in lines[1:]) if _is_usable_label(l))
        return Expectation("loose", labels)
    return Expectation("exact", tuple(lines))


def _exact_detail(expected: str, actual: str) -> str:
    diff = difflib.unified_diff(
        _norm(expected).splitlines(), _norm(actual).splitlines(), "expected", "actual", lineterm="", n=0
    )
    return "\n".join(diff)


def evaluate(test: VerifyTest, actual_output: str, exit_code: int) -> TestResult:
    expectation = parse_expect(test.expect)
    if expectation.mode == "exact":
        expected_text = "" if test.expect.strip() == EMPTY_MARKER else test.expect
        passed = _norm(expected_text) == _norm(actual_output)
        detail = "" if passed else _exact_detail(expected_text, actual_output)
    else:
        flat = " ".join(actual_output.split())
        missing = [l for l in expectation.lines if l not in flat]
        passed = not missing
        detail = "" if passed else "missing from output: " + "; ".join(missing)
    return TestResult(test.title, test.kind, passed, expectation.mode, test.expect, actual_output, detail, exit_code, test.hint)


def redact(text: str, secrets: tuple[str, ...]) -> str:
    out = text
    for secret in secrets:
        if secret:
            out = out.replace(secret, "***")
    return out


def format_result(index: int, result: TestResult) -> str:
    label = "PASS" if result.passed else "FAIL"
    head = f"{label}  Test {index} ({result.kind}): {result.title}"
    if result.passed:
        return head
    parts = [head, f"  match mode: {result.mode}"]
    if result.detail:
        parts.append("  difference:")
        parts.extend("    " + line for line in result.detail.splitlines())
    parts.append("  expected:")
    parts.extend("    " + line for line in result.expected.strip().splitlines())
    parts.append(f"  actual (exit code {result.exit_code}):")
    actual = result.actual.strip().splitlines() or ["(empty output)"]
    parts.extend("    " + line for line in actual)
    if result.hint:
        parts.append("  " + result.hint)
    return "\n".join(parts)
