"""Business logic operating on a gradebook data dictionary."""

from statistics import mean

from .models import Course, Enrollment, Student, normalize_code


def _find_student(data, student_id):
    for student in data["students"]:
        if student["id"] == student_id:
            return student
    raise ValueError(f"Unknown student id: {student_id}")


def _find_course(data, course_code):
    for course in data["courses"]:
        if course["code"] == course_code:
            return course
    raise ValueError(f"Unknown course code: {course_code}")


def _find_enrollment(data, student_id, course_code):
    for entry in data["enrollments"]:
        if (
            entry["student_id"] == student_id
            and entry["course_code"] == course_code
        ):
            return entry
    return None


def _require_enrollment(data, student_id, course_code):
    _find_student(data, student_id)
    _find_course(data, course_code)
    entry = _find_enrollment(data, student_id, course_code)
    if entry is None:
        raise ValueError(
            f"Student {student_id} is not enrolled in {course_code}"
        )
    return entry


def add_student(data, name):
    """Add a student and return the new id."""
    new_id = max((s["id"] for s in data["students"]), default=0) + 1
    student = Student(new_id, name)
    data["students"].append(student.to_dict())
    return student.id


def add_course(data, code, title):
    """Add a course; the code must be unique."""
    course = Course(code, title)
    if any(c["code"] == course.code for c in data["courses"]):
        raise ValueError(f"Course {course.code} already exists")
    data["courses"].append(course.to_dict())


def enroll(data, student_id, course_code):
    """Enroll an existing student in an existing course."""
    course_code = normalize_code(course_code)
    _find_student(data, student_id)
    _find_course(data, course_code)
    if _find_enrollment(data, student_id, course_code) is not None:
        raise ValueError(
            f"Student {student_id} is already enrolled in {course_code}"
        )
    data["enrollments"].append(Enrollment(student_id, course_code).to_dict())


def add_grade(data, student_id, course_code, grade):
    """Record a grade for an enrolled student."""
    entry = _require_enrollment(data, student_id, normalize_code(course_code))
    enrollment = Enrollment.from_dict(entry)
    enrollment.add_grade(grade)
    entry["grades"] = enrollment.grades


def list_students(data, sort_by=None):
    """Return students sorted by name or, by default, by id."""
    students = [Student.from_dict(raw) for raw in data["students"]]
    if sort_by == "name":
        return sorted(students, key=lambda s: s.name.lower())
    return sorted(students, key=lambda s: s.id)


def list_courses(data, sort_by=None):
    """Return courses sorted by title or, by default, by code."""
    courses = [Course.from_dict(raw) for raw in data["courses"]]
    if sort_by == "name":
        return sorted(courses, key=lambda c: c.title.lower())
    return sorted(courses, key=lambda c: c.code)


def list_enrollments(data, sort_by=None):
    """Return enrollment rows sorted by student name or course code."""
    names = {s["id"]: s["name"] for s in data["students"]}
    rows = [
        {
            "student_id": e["student_id"],
            "student_name": names.get(e["student_id"], "Unknown"),
            "course_code": e["course_code"],
            "grades": list(e["grades"]),
            "average": mean(e["grades"]) if e["grades"] else None,
        }
        for e in data["enrollments"]
    ]
    if sort_by == "name":
        return sorted(
            rows, key=lambda r: (r["student_name"].lower(), r["course_code"])
        )
    return sorted(rows, key=lambda r: (r["course_code"], r["student_id"]))


def compute_average(data, student_id, course_code):
    """Return the mean grade of a student in a course."""
    entry = _require_enrollment(data, student_id, normalize_code(course_code))
    if not entry["grades"]:
        raise ValueError(
            f"No grades recorded for student {student_id} "
            f"in {entry['course_code']}"
        )
    return mean(entry["grades"])


def compute_gpa(data, student_id):
    """Return the mean of a student's course averages."""
    _find_student(data, student_id)
    averages = [
        mean(e["grades"])
        for e in data["enrollments"]
        if e["student_id"] == student_id and e["grades"]
    ]
    if not averages:
        raise ValueError(f"No grades recorded for student {student_id}")
    return mean(averages)
