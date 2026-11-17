import unittest

from gradebook import service, storage


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.data = storage.empty_data()
        self.student_id = service.add_student(self.data, "Alice")
        service.add_course(self.data, "CS101", "Intro to CS")
        service.enroll(self.data, self.student_id, "CS101")

    def test_add_student_returns_incrementing_ids(self):
        second = service.add_student(self.data, "Bob")
        self.assertEqual(self.student_id, 1)
        self.assertEqual(second, 2)
        self.assertEqual(len(self.data["students"]), 2)

    def test_add_student_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            service.add_student(self.data, "   ")
        self.assertEqual(len(self.data["students"]), 1)

    def test_add_grade_happy_path(self):
        service.add_grade(self.data, self.student_id, "CS101", 90)
        self.assertEqual(self.data["enrollments"][0]["grades"], [90])

    def test_add_grade_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            service.add_grade(self.data, self.student_id, "CS101", 101)
        self.assertEqual(self.data["enrollments"][0]["grades"], [])

    def test_add_grade_requires_enrollment(self):
        service.add_course(self.data, "MA201", "Linear Algebra")
        with self.assertRaises(ValueError):
            service.add_grade(self.data, self.student_id, "MA201", 80)

    def test_compute_average_happy_path(self):
        service.add_grade(self.data, self.student_id, "CS101", 80)
        service.add_grade(self.data, self.student_id, "CS101", 100)
        average = service.compute_average(self.data, self.student_id, "CS101")
        self.assertEqual(average, 90)

    def test_compute_average_without_grades_fails(self):
        with self.assertRaises(ValueError):
            service.compute_average(self.data, self.student_id, "CS101")

    def test_compute_gpa_is_mean_of_course_averages(self):
        service.add_course(self.data, "MA201", "Linear Algebra")
        service.enroll(self.data, self.student_id, "MA201")
        service.add_grade(self.data, self.student_id, "CS101", 90)
        service.add_grade(self.data, self.student_id, "MA201", 70)
        self.assertEqual(service.compute_gpa(self.data, self.student_id), 80)


if __name__ == "__main__":
    unittest.main()
