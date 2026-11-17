"""Command-line interface for the gradebook."""

import argparse
import logging
import sys

from gradebook import service, storage
from gradebook.log_config import setup_logging
from gradebook.validation import parse_grade, parse_student_id, parse_text

logger = logging.getLogger("gradebook.cli")


def cmd_add_student(data, args):
    """Handle the add-student command."""
    name = parse_text(args.name, "Name")
    student_id = service.add_student(data, name)
    return f"Added student {student_id}: {name}", True


def cmd_add_course(data, args):
    """Handle the add-course command."""
    code = parse_text(args.code, "Course code").upper()
    title = parse_text(args.title, "Title")
    service.add_course(data, code, title)
    return f"Added course {code}: {title}", True


def cmd_enroll(data, args):
    """Handle the enroll command."""
    student_id = parse_student_id(args.student_id)
    code = parse_text(args.course, "Course code").upper()
    service.enroll(data, student_id, code)
    return f"Enrolled student {student_id} in {code}", True


def cmd_add_grade(data, args):
    """Handle the add-grade command."""
    student_id = parse_student_id(args.student_id)
    code = parse_text(args.course, "Course code").upper()
    grade = parse_grade(args.grade)
    service.add_grade(data, student_id, code, grade)
    return f"Added grade {grade} for student {student_id} in {code}", True


def cmd_list(data, args):
    """Handle the list command."""
    if args.what == "students":
        items = [str(s) for s in service.list_students(data, args.sort)]
    elif args.what == "courses":
        items = [str(c) for c in service.list_courses(data, args.sort)]
    else:
        items = [
            format_enrollment(row)
            for row in service.list_enrollments(data, args.sort)
        ]
    if not items:
        return f"No {args.what} found.", False
    return "\n".join(items), False


def format_enrollment(row):
    """Format one enrollment row for display."""
    grades = ", ".join(str(g) for g in row["grades"]) or "none"
    average = "n/a" if row["average"] is None else f"{row['average']:.2f}"
    return (
        f"{row['student_name']} ({row['student_id']}) - "
        f"{row['course_code']}: grades [{grades}], average {average}"
    )


def cmd_avg(data, args):
    """Handle the avg command."""
    student_id = parse_student_id(args.student_id)
    code = parse_text(args.course, "Course code").upper()
    average = service.compute_average(data, student_id, code)
    return f"Average for student {student_id} in {code}: {average:.2f}", False


def cmd_gpa(data, args):
    """Handle the gpa command."""
    student_id = parse_student_id(args.student_id)
    gpa = service.compute_gpa(data, student_id)
    return f"GPA for student {student_id}: {gpa:.2f}", False


HANDLERS = {
    "add-student": cmd_add_student,
    "add-course": cmd_add_course,
    "enroll": cmd_enroll,
    "add-grade": cmd_add_grade,
    "list": cmd_list,
    "avg": cmd_avg,
    "gpa": cmd_gpa,
}


def build_parser():
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="main.py", description="Gradebook command-line tool"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-student", help="add a student")
    p.add_argument("--name", required=True)

    p = sub.add_parser("add-course", help="add a course")
    p.add_argument("--code", required=True)
    p.add_argument("--title", required=True)

    p = sub.add_parser("enroll", help="enroll a student in a course")
    p.add_argument("--student-id", required=True)
    p.add_argument("--course", required=True)

    p = sub.add_parser("add-grade", help="add a grade")
    p.add_argument("--student-id", required=True)
    p.add_argument("--course", required=True)
    p.add_argument("--grade", required=True)

    p = sub.add_parser("list", help="list students, courses or enrollments")
    p.add_argument("what", choices=["students", "courses", "enrollments"])
    p.add_argument("--sort", choices=["name", "code"])

    p = sub.add_parser("avg", help="average of a student in a course")
    p.add_argument("--student-id", required=True)
    p.add_argument("--course", required=True)

    p = sub.add_parser("gpa", help="GPA of a student")
    p.add_argument("--student-id", required=True)

    return parser


def main(argv=None):
    """Run the CLI and return a process exit code."""
    setup_logging()
    args = build_parser().parse_args(argv)
    try:
        data = storage.load_data()
        message, changed = HANDLERS[args.command](data, args)
        if changed:
            storage.save_data(data)
    except (ValueError, OSError) as exc:
        logger.error("Command %s failed: %s", args.command, exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    logger.info("Command %s succeeded", args.command)
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
