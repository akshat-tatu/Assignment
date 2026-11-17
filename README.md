# Gradebook CLI

A small command-line gradebook built with Python. It manages students, courses, enrollments and grades, and stores everything in a JSON file.

## Project structure

```
gradebook/
├── main.py                 # argparse CLI
├── gradebook/
│   ├── __init__.py
│   ├── models.py           # Student, Course, Enrollment
│   ├── storage.py          # load_data / save_data (JSON)
│   ├── service.py          # business logic
│   ├── validation.py       # parse_grade, parse_student_id, parse_text
│   └── log_config.py       # logging setup
├── scripts/seed.py         # sample data generator
├── tests/test_service.py   # unittest suite
├── data/gradebook.json     # sample data
└── logs/app.log            # created on first run
```

## Setup

Requires Python 3.9+. No third-party packages are needed.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

## Seed sample data

Run from the project root:

```bash
python -m scripts.seed
```

Expected output:

```
Sample data saved to /path/to/gradebook/data/gradebook.json
```

This creates 3 students, 2 courses, 4 enrollments and several grades.

## Usage

```bash
python main.py list students
```
```
[1] Sunil Chedi
[2] Bhole Singh
[3] Harry Sharma
```

```bash
python main.py list courses --sort name
```
```
CS111: Intro to CS
MTH111: Linear Algebra
```

```bash
python main.py list enrollments --sort name
```
```
Sunil Chedi (1) - CS111: grades [95, 88], average 91.50
Sunil Chedi (1) - MTH111: grades [91], average 91.00
Bhole Singh (2) - CS111: grades [72, 80], average 76.00
Harry Sharma (3) - MTH111: grades [85.5], average 85.50
```

```bash
python main.py avg --student-id 1 --course CS101
```
```
Average for student 1 in CS101: 91.50
```

```bash
python main.py gpa --student-id 1
```
```
GPA for student 1: 91.25
```

```bash
python main.py add-student --name "Dev Patel"
python main.py add-course --code CS150 --title "Data Structures"
python main.py enroll --student-id 4 --course CS150
python main.py add-grade --student-id 4 --course CS150 --grade 97.5
```
```
Added student 4: Dev Patel
Added course CS150: Data Structures
Enrolled student 4 in CS150
Added grade 97.5 for student 4 in CS150
```

### Commands

| Command | Arguments |
|---|---|
| `add-student` | `--name` |
| `add-course` | `--code`, `--title` |
| `enroll` | `--student-id`, `--course` |
| `add-grade` | `--student-id`, `--course`, `--grade` |
| `list` | `students` / `courses` / `enrollments`, optional `--sort name` or `--sort code` |
| `avg` | `--student-id`, `--course` |
| `gpa` | `--student-id` |

### Error handling

Errors are printed to stderr with exit code 1:

```bash
python main.py add-grade --student-id 1 --course CS101 --grade 150
```
```
Error: grade must be between 0 and 100
```

```bash
python main.py add-grade --student-id 3 --course CS101 --grade 90
```
```
Error: Student 3 is not enrolled in CS101
```

```bash
python main.py enroll --student-id 99 --course CS101
```
```
Error: Unknown student id: 99
```

## Running the tests

```bash
python -m unittest discover -s tests -v
```

## Logging

INFO and ERROR messages (loading, saving, failed commands) are written to `logs/app.log`.

## Design decisions & limitations

- **Service functions take the data dictionary as their first argument** (for example `add_student(data, name)`) instead of using global state. This keeps them pure with respect to I/O and easy to test; the CLI loads the data, calls a function, and saves.
- **Data is stored as plain dictionaries** in JSON. The model classes are used for validation and display, and convert to and from dictionaries.
- **Course codes are normalised to upper case**, so `cs101` and `CS101` are the same course.
- **GPA is the simple mean of per-course averages**, not weighted by credits, and courses without grades are ignored.
- **`--sort name`** sorts students by name, courses by title and enrollments by student name; **`--sort code`** sorts courses and enrollments by course code. Students are listed by id when sorting by code.
- **Limitations:** the whole file is rewritten on every change, there is no file locking, so concurrent runs can overwrite each other. There are no commands to delete or edit records, and student ids are never reused.
