"""Recommended module sequence. IDs stay fixed; this list sets the order learners take them."""

ORDER = [
    "M00", "M02", "SIEM-1", "SIEM-2", "SIEM-3", "SIEM-4", "M12", "M08",
    "M05", "M06", "M11", "M07", "M04", "M03", "M09", "M10", "CAP",
]


def position(module_id: str) -> tuple[int, int]:
    """Return (1-based position, total) for a module id."""
    return ORDER.index(module_id) + 1, len(ORDER)
