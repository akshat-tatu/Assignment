"""Input parsing helpers that raise ValueError on invalid input."""

from .models import validate_grade


def parse_grade(raw):
    """Convert text to a validated grade between 0 and 100."""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid grade '{raw}': enter a number from 0 to 100"
        ) from None
    value = validate_grade(value)
    return int(value) if value.is_integer() else value


def parse_student_id(raw):
    """Convert text to a positive integer student id."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid student id '{raw}': must be a whole number"
        ) from None
    if value < 1:
        raise ValueError("Student id must be a positive whole number")
    return value


def parse_text(raw, field):
    """Return stripped text or raise ValueError if it is empty."""
    text = (raw or "").strip()
    if not text:
        raise ValueError(f"{field} must not be empty")
    return text
