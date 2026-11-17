"""Create sample data and save it to data/gradebook.json."""

from gradebook import service, storage
from gradebook.log_config import setup_logging


def build_sample_data():
    """Return a gradebook populated with sample records."""
    data = storage.empty_data()
    alice = service.add_student(data, "Alice Johnson")
    bob = service.add_student(data, "Bob Smith")
    carla = service.add_student(data, "Carla Gomez")

    service.add_course(data, "CS101", "Intro to CS")
    service.add_course(data, "MA201", "Linear Algebra")

    for student_id, code in [
        (alice, "CS101"),
        (alice, "MA201"),
        (bob, "CS101"),
        (carla, "MA201"),
    ]:
        service.enroll(data, student_id, code)

    for student_id, code, grade in [
        (alice, "CS101", 95),
        (alice, "CS101", 88),
        (alice, "MA201", 91),
        (bob, "CS101", 72),
        (bob, "CS101", 80),
        (carla, "MA201", 85.5),
    ]:
        service.add_grade(data, student_id, code, grade)
    return data


def main():
    """Build the sample data and write it to disk."""
    setup_logging()
    storage.save_data(build_sample_data())
    print(f"Sample data saved to {storage.DEFAULT_PATH}")


if __name__ == "__main__":
    main()
