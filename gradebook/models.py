"""Core data models for the gradebook."""

from numbers import Real


def _require_text(value, field):
    """Return a stripped non-empty string or raise ValueError."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _require_id(value, field):
    """Return a positive integer id or raise ValueError."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return value


def normalize_code(value):
    """Return a course code in canonical upper-case form."""
    return _require_text(value, "course code").upper()


def validate_grade(value):
    """Return the grade if it is a number from 0 to 100."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("grade must be a number")
    if not 0 <= value <= 100:
        raise ValueError("grade must be between 0 and 100")
    return value


class Student:
    """A student identified by a numeric id."""

    def __init__(self, id, name):
        self.id = _require_id(id, "student id")
        self.name = _require_text(name, "name")

    def __str__(self):
        return f"[{self.id}] {self.name}"

    def to_dict(self):
        """Return a JSON-serialisable representation."""
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, raw):
        """Build a Student from a dictionary."""
        return cls(raw.get("id"), raw.get("name"))


class Course:
    """A course identified by a code."""

    def __init__(self, code, title):
        self.code = normalize_code(code)
        self.title = _require_text(title, "title")

    def __str__(self):
        return f"{self.code}: {self.title}"

    def to_dict(self):
        """Return a JSON-serialisable representation."""
        return {"code": self.code, "title": self.title}

    @classmethod
    def from_dict(cls, raw):
        """Build a Course from a dictionary."""
        return cls(raw.get("code"), raw.get("title"))


class Enrollment:
    """A student's enrollment in a course, with its grades."""

    def __init__(self, student_id, course_code, grades=None):
        self.student_id = _require_id(student_id, "student id")
        self.course_code = normalize_code(course_code)
        if grades is None:
            grades = []
        if not isinstance(grades, list):
            raise ValueError("grades must be a list")
        self.grades = [validate_grade(grade) for grade in grades]

    def __str__(self):
        grades = ", ".join(str(grade) for grade in self.grades) or "none"
        return (
            f"Student {self.student_id} in {self.course_code}: "
            f"grades [{grades}]"
        )

    def add_grade(self, grade):
        """Validate and append a grade."""
        self.grades.append(validate_grade(grade))

    def to_dict(self):
        """Return a JSON-serialisable representation."""
        return {
            "student_id": self.student_id,
            "course_code": self.course_code,
            "grades": list(self.grades),
        }

    @classmethod
    def from_dict(cls, raw):
        """Build an Enrollment from a dictionary."""
        return cls(
            raw.get("student_id"), raw.get("course_code"), raw.get("grades")
        )
