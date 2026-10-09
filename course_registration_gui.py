"""
College Course Registration System - GUI Version
==================================================
Same OOP design as the terminal version (Student, Course, RegistrationSystem),
with a Tkinter graphical interface layered on top instead of a text menu.

Classes
-------
Student             -> manages student data and the student's registered courses
Course              -> manages course data and the course's enrolled students
RegistrationSystem  -> manages all operations (add, register, drop, report)
RegistrationApp     -> the Tkinter GUI that drives RegistrationSystem

Rules enforced
--------------
* A student cannot exceed 24 credits.
* A course cannot exceed its seat capacity.
* A student cannot register for the same course twice.
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


class RegistrationError(Exception):
    """Raised when a registration rule is violated or input is invalid."""


# ----------------------------------------------------------------------------
# Course
# ----------------------------------------------------------------------------
class Course:
    """Stores course data and tracks which students are enrolled."""

    def __init__(self, code, title, credits, capacity):
        if credits <= 0:
            raise RegistrationError("Credits must be a positive number.")
        if capacity <= 0:
            raise RegistrationError("Capacity must be a positive number.")
        self._code = code.strip().upper()
        self._title = title.strip()
        self._credits = credits
        self._capacity = capacity
        self._enrolled_students = []  # list of Student objects

    @property
    def code(self):
        return self._code

    @property
    def title(self):
        return self._title

    @property
    def credits(self):
        return self._credits

    @property
    def capacity(self):
        return self._capacity

    @property
    def enrolled_count(self):
        return len(self._enrolled_students)

    @property
    def seats_available(self):
        return self._capacity - len(self._enrolled_students)

    def has_seat(self):
        return self.seats_available > 0

    def has_student(self, student):
        return student in self._enrolled_students

    def add_student(self, student):
        if not self.has_seat():
            raise RegistrationError(f"{self._code} is full. No seats available.")
        if self.has_student(student):
            raise RegistrationError(f"Student is already enrolled in {self._code}.")
        self._enrolled_students.append(student)

    def remove_student(self, student):
        if student not in self._enrolled_students:
            raise RegistrationError(f"Student is not enrolled in {self._code}.")
        self._enrolled_students.remove(student)


# ----------------------------------------------------------------------------
# Student
# ----------------------------------------------------------------------------
class Student:
    """Stores student data and the list of courses the student is registered in."""

    MAX_CREDITS = 24

    def __init__(self, student_id, name, email):
        if not student_id.strip():
            raise RegistrationError("Student ID cannot be empty.")
        if not name.strip():
            raise RegistrationError("Student name cannot be empty.")
        if "@" not in email or "." not in email:
            raise RegistrationError("Please enter a valid email address.")
        self._student_id = student_id.strip().upper()
        self._name = name.strip()
        self._email = email.strip()
        self._courses = []  # list of Course objects

    @property
    def student_id(self):
        return self._student_id

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def courses(self):
        return list(self._courses)

    @property
    def total_credits(self):
        return sum(course.credits for course in self._courses)

    def is_registered_for(self, course):
        return course in self._courses

    def can_take(self, course):
        if self.total_credits + course.credits > self.MAX_CREDITS:
            raise RegistrationError(
                f"Credit limit exceeded. Current: {self.total_credits}, "
                f"Course: {course.credits}, Max allowed: {self.MAX_CREDITS}."
            )

    def add_course(self, course):
        self._courses.append(course)

    def remove_course(self, course):
        self._courses.remove(course)


# ----------------------------------------------------------------------------
# RegistrationSystem
# ----------------------------------------------------------------------------
class RegistrationSystem:
    """Manages all students, courses, and registration operations."""

    def __init__(self):
        self._students = {}  # student_id -> Student
        self._courses = {}   # course_code -> Course

    def _get_student(self, student_id):
        sid = student_id.strip().upper()
        if sid not in self._students:
            raise RegistrationError(f"No student found with ID '{sid}'.")
        return self._students[sid]

    def _get_course(self, code):
        c = code.strip().upper()
        if c not in self._courses:
            raise RegistrationError(f"No course found with code '{c}'.")
        return self._courses[c]

    @property
    def students(self):
        return list(self._students.values())

    @property
    def courses(self):
        return list(self._courses.values())

    def add_student(self, student_id, name, email):
        student = Student(student_id, name, email)
        if student.student_id in self._students:
            raise RegistrationError(f"Student ID '{student.student_id}' already exists.")
        self._students[student.student_id] = student
        return student

    def add_course(self, code, title, credits, capacity):
        course = Course(code, title, credits, capacity)
        if course.code in self._courses:
            raise RegistrationError(f"Course code '{course.code}' already exists.")
        self._courses[course.code] = course
        return course

    def register_course(self, student_id, course_code):
        student = self._get_student(student_id)
        course = self._get_course(course_code)

        if student.is_registered_for(course):
            raise RegistrationError(f"{student.name} is already registered for {course.code}.")
        if not course.has_seat():
            raise RegistrationError(f"{course.code} is full. No seats available.")
        student.can_take(course)

        course.add_student(student)
        student.add_course(course)
        return student, course

    def drop_course(self, student_id, course_code):
        student = self._get_student(student_id)
        course = self._get_course(course_code)

        if not student.is_registered_for(course):
            raise RegistrationError(f"{student.name} is not registered for {course.code}.")
        course.remove_student(student)
        student.remove_course(course)
        return student, course

    def load_sample_data(self):
        self.add_student("S101", "Aarav Sharma", "aarav@college.edu")
        self.add_student("S102", "Diya Reddy", "diya@college.edu")
        self.add_student("S103", "Rohan Mehta", "rohan@college.edu")

        self.add_course("CS101", "Introduction to Programming", 4, 3)
        self.add_course("CS201", "Data Structures", 4, 2)
        self.add_course("CS301", "Database Systems", 3, 30)
        self.add_course("MA101", "Calculus I", 4, 40)
        self.add_course("PH101", "Physics I", 4, 35)
        self.add_course("EN101", "Technical Communication", 2, 50)
        self.add_course("CS401", "Advanced Algorithms", 6, 25)
        self.add_course("CS402", "Machine Learning", 6, 25)
        self.add_course("CS501", "Operating Systems", 4, 35)
        self.add_course("CS502", "Computer Networks", 4, 30)
        self.add_course("CS503", "Compiler Design", 4, 25)
        self.add_course("CS504", "Cyber Security", 3, 20)
        self.add_course("CS505", "Artificial Intelligence", 4, 25)
        self.add_course("EC201", "Digital Electronics", 4, 30)
        self.add_course("EC202", "Signals and Systems", 4, 28)
        self.add_course("EC301", "Microprocessors and Microcontrollers", 4, 28)
        self.add_course("EC302", "Communication Engineering", 3, 30)
        self.add_course("EE201", "Electrical Machines", 4, 30)
        self.add_course("EE202", "Power Systems", 4, 25)
        self.add_course("ME201", "Thermodynamics", 4, 30)
        self.add_course("ME202", "Fluid Mechanics", 4, 28)
        self.add_course("CE201", "Structural Analysis", 4, 25)
        self.add_course("CE202", "Transportation Engineering", 3, 25)
        self.add_course("CS601", "Distributed Systems", 3, 22)
        self.add_course("CS602", "Software Engineering", 3, 25)
        self.add_course("CS603", "Database Security", 3, 18)
        self.add_course("CS604", "Cloud Computing", 4, 24)
        self.add_course("CS605", "Data Mining", 3, 20)
        self.add_course("EC401", "VLSI Design", 4, 24)
        self.add_course("EC402", "Embedded Systems", 4, 26)
        self.add_course("EC403", "Wireless Communication", 3, 20)
        self.add_course("EC404", "Digital Signal Processing", 4, 22)
        self.add_course("EE301", "Control Systems", 4, 22)
        self.add_course("EE302", "Renewable Energy", 3, 18)
        self.add_course("ME301", "Manufacturing Processes", 3, 20)
        self.add_course("ME302", "Machine Design", 4, 22)
        self.add_course("CE301", "Geotechnical Engineering", 4, 20)
        self.add_course("CE302", "Hydraulics and Hydrology", 4, 20)

        self.register_course("S101", "CS101")
        self.register_course("S101", "CS201")
        self.register_course("S102", "CS101")

    def save(self, path):
        data = {
            "students": [
                {"student_id": student.student_id, "name": student.name, "email": student.email}
                for student in self.students
            ],
            "courses": [
                {
                    "code": course.code,
                    "title": course.title,
                    "credits": course.credits,
                    "capacity": course.capacity,
                }
                for course in self.courses
            ],
            "registrations": [
                {"student_id": student.student_id, "course_code": course.code}
                for student in self.students
                for course in student.courses
            ],
        }
        path = Path(path)
        temporary_path = path.with_suffix(path.suffix + ".tmp")
        temporary_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary_path.replace(path)

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RegistrationError(f"Could not read saved data from {path}: {exc}") from exc

        system = cls()
        seen_courses = set()
        for course in data.get("courses", []):
            code = str(course.get("code", "")).strip()
            if not code or code in seen_courses:
                continue
            seen_courses.add(code)
            try:
                system.add_course(code, course["title"], course["credits"], course["capacity"])
            except RegistrationError:
                continue

        seen_students = set()
        for student in data.get("students", []):
            sid = str(student.get("student_id", "")).strip()
            if not sid or sid in seen_students:
                continue
            seen_students.add(sid)
            try:
                system.add_student(sid, student["name"], student["email"])
            except RegistrationError:
                continue

        for registration in data.get("registrations", []):
            sid = registration.get("student_id")
            code = registration.get("course_code")
            if sid is None or code is None:
                continue
            try:
                system.register_course(sid, code)
            except RegistrationError:
                continue
        return system


# ----------------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------------
class RegistrationApp(tk.Tk):
    """Main Tkinter application window with a tab for each operation."""

    DATA_FILE = Path(__file__).with_name("course_registration_data.json")

    def __init__(self):
        super().__init__()
        try:
            if self.DATA_FILE.exists():
                self.system = RegistrationSystem.load(self.DATA_FILE)
            else:
                self.system = RegistrationSystem()
                self.system.load_sample_data()
                self.system.save(self.DATA_FILE)
        except (RegistrationError, FileNotFoundError, OSError):
            self.system = RegistrationSystem()
            self.system.load_sample_data()
            self.system.save(self.DATA_FILE)

        self.title("College Course Registration System")
        self.geometry("880x560")
        self.minsize(760, 480)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.students_tab = ttk.Frame(notebook)
        self.courses_tab = ttk.Frame(notebook)
        self.register_tab = ttk.Frame(notebook)
        self.report_tab = ttk.Frame(notebook)

        notebook.add(self.students_tab, text="Students")
        notebook.add(self.courses_tab, text="Courses")
        notebook.add(self.register_tab, text="Register / Drop")
        notebook.add(self.report_tab, text="Report")

        self._build_students_tab()
        self._build_courses_tab()
        self._build_register_tab()
        self._build_report_tab()
        self._refresh_id_dropdowns()

        self._refresh_students_table()
        self._refresh_courses_table()

    # ---- helpers -----------------------------------------------------
    def _error(self, err):
        messagebox.showerror("Error", str(err))

    def _success(self, msg):
        messagebox.showinfo("Success", msg)

    def _clear_entries(self, *entries):
        for e in entries:
            e.delete(0, tk.END)

    # ---- Students tab --------------------------------------------------
    def _build_students_tab(self):
        frame = self.students_tab
        form = ttk.LabelFrame(frame, text="Add Student")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Student ID").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.sid_entry = ttk.Entry(form)
        self.sid_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Name").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.sname_entry = ttk.Entry(form)
        self.sname_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Email").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.semail_entry = ttk.Entry(form)
        self.semail_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form, text="Add Student", command=self._add_student).grid(
            row=0, column=6, padx=10, pady=5
        )

        columns = ("id", "name", "email", "credits")
        self.students_table = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        headings = {"id": "Student ID", "name": "Name", "email": "Email", "credits": "Credits"}
        for col in columns:
            self.students_table.heading(col, text=headings[col])
            self.students_table.column(col, width=150, anchor="center")
        self.students_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _add_student(self):
        try:
            student = self.system.add_student(
                self.sid_entry.get(), self.sname_entry.get(), self.semail_entry.get()
            )
            self.system.save(self.DATA_FILE)
            self._success(f"Student added: {student.student_id} - {student.name}")
            self._clear_entries(self.sid_entry, self.sname_entry, self.semail_entry)
            self._refresh_students_table()
            self._refresh_id_dropdowns()
        except RegistrationError as e:
            self._error(e)

    def _refresh_students_table(self):
        self.students_table.delete(*self.students_table.get_children())
        for s in self.system.students:
            self.students_table.insert(
                "", "end", values=(s.student_id, s.name, s.email, f"{s.total_credits}/{Student.MAX_CREDITS}")
            )

    # ---- Courses tab --------------------------------------------------
    def _build_courses_tab(self):
        frame = self.courses_tab
        form = ttk.LabelFrame(frame, text="Add Course")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Code").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cid_entry = ttk.Entry(form)
        self.cid_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Title").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ctitle_entry = ttk.Entry(form)
        self.ctitle_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Credits").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.ccredits_entry = ttk.Entry(form, width=6)
        self.ccredits_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Capacity").grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.ccapacity_entry = ttk.Entry(form, width=6)
        self.ccapacity_entry.grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(form, text="Add Course", command=self._add_course).grid(
            row=0, column=8, padx=10, pady=5
        )

        columns = ("code", "title", "credits", "seats")
        self.courses_table = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        headings = {"code": "Code", "title": "Title", "credits": "Credits", "seats": "Seats Available"}
        for col in columns:
            self.courses_table.heading(col, text=headings[col])
            self.courses_table.column(col, width=150, anchor="center")
        self.courses_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _add_course(self):
        try:
            credits_text = self.ccredits_entry.get().strip()
            capacity_text = self.ccapacity_entry.get().strip()
            if not credits_text.isdigit() or not capacity_text.isdigit():
                raise RegistrationError("Credits and capacity must be whole numbers.")
            course = self.system.add_course(
                self.cid_entry.get(), self.ctitle_entry.get(), int(credits_text), int(capacity_text)
            )
            self.system.save(self.DATA_FILE)
            self._success(f"Course added: {course.code} - {course.title}")
            self._clear_entries(self.cid_entry, self.ctitle_entry, self.ccredits_entry, self.ccapacity_entry)
            self._refresh_courses_table()
            self._refresh_id_dropdowns()
        except RegistrationError as e:
            self._error(e)

    def _refresh_courses_table(self):
        self.courses_table.delete(*self.courses_table.get_children())
        for c in self.system.courses:
            self.courses_table.insert(
                "", "end", values=(c.code, c.title, c.credits, f"{c.seats_available}/{c.capacity}")
            )

    # ---- Register / Drop tab -------------------------------------------
    def _build_register_tab(self):
        frame = self.register_tab
        form = ttk.LabelFrame(frame, text="Register or Drop a Course")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Student").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.reg_student_cb = ttk.Combobox(form, state="readonly", width=30)
        self.reg_student_cb.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form, text="Course").grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.reg_course_cb = ttk.Combobox(form, state="readonly", width=35)
        self.reg_course_cb.grid(row=0, column=3, padx=5, pady=8)

        ttk.Button(form, text="Register", command=self._do_register).grid(row=0, column=4, padx=5)
        ttk.Button(form, text="Drop", command=self._drop).grid(row=0, column=5, padx=5)

        self._refresh_id_dropdowns()

        info = ttk.LabelFrame(frame, text="Selected Student's Courses")
        info.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        columns = ("code", "title", "credits")
        self.student_courses_table = ttk.Treeview(info, columns=columns, show="headings", height=12)
        for col, label in zip(columns, ("Code", "Title", "Credits")):
            self.student_courses_table.heading(col, text=label)
            self.student_courses_table.column(col, width=150, anchor="center")
        self.student_courses_table.pack(fill="both", expand=True, padx=5, pady=5)

        self.reg_student_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_selected_student_courses())

    def _refresh_id_dropdowns(self):
        student_values = [f"{s.student_id} - {s.name}" for s in self.system.students]
        course_values = [f"{c.code} - {c.title}" for c in self.system.courses]
        self.reg_student_cb["values"] = student_values
        self.reg_course_cb["values"] = course_values
        # The Report tab's dropdown doesn't exist yet the first time this runs
        # (it's built after the Register tab), so only refresh it once it's there.
        if hasattr(self, "report_student_cb"):
            self.report_student_cb["values"] = student_values

    def _selected_id(self, combobox):
        value = combobox.get()
        if not value:
            raise RegistrationError("Please select a value first.")
        return value.split(" - ")[0]

    def _do_register(self):
        try:
            sid = self._selected_id(self.reg_student_cb)
            code = self._selected_id(self.reg_course_cb)
            student, course = self.system.register_course(sid, code)
            self.system.save(self.DATA_FILE)
            self._success(
                f"{student.name} registered for {course.code}. "
                f"Total credits: {student.total_credits}/{Student.MAX_CREDITS}"
            )
            self._refresh_students_table()
            self._refresh_courses_table()
            self._refresh_selected_student_courses()
        except RegistrationError as e:
            self._error(e)

    def _drop(self):
        try:
            sid = self._selected_id(self.reg_student_cb)
            code = self._selected_id(self.reg_course_cb)
            student, course = self.system.drop_course(sid, code)
            self.system.save(self.DATA_FILE)
            self._success(
                f"{student.name} dropped {course.code}. "
                f"Total credits: {student.total_credits}/{Student.MAX_CREDITS}"
            )
            self._refresh_students_table()
            self._refresh_courses_table()
            self._refresh_selected_student_courses()
        except RegistrationError as e:
            self._error(e)

    def _refresh_selected_student_courses(self):
        self.student_courses_table.delete(*self.student_courses_table.get_children())
        value = self.reg_student_cb.get()
        if not value:
            return
        sid = value.split(" - ")[0]
        try:
            student = self.system._get_student(sid)
        except RegistrationError:
            return
        for c in student.courses:
            self.student_courses_table.insert("", "end", values=(c.code, c.title, c.credits))

    # ---- Report tab -----------------------------------------------------
    def _build_report_tab(self):
        frame = self.report_tab
        form = ttk.LabelFrame(frame, text="Generate Registration Report")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Student").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.report_student_cb = ttk.Combobox(form, state="readonly", width=30)
        self.report_student_cb.grid(row=0, column=1, padx=5, pady=8)

        ttk.Button(form, text="Generate Report", command=self._generate_report).grid(
            row=0, column=2, padx=10
        )

        self.report_text = tk.Text(frame, height=20, font=("Courier New", 10))
        self.report_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.report_text.configure(state="disabled")

    def _generate_report(self):
        try:
            value = self.report_student_cb.get()
            if not value:
                raise RegistrationError("Please select a student first.")
            sid = value.split(" - ")[0]
            student = self.system._get_student(sid)

            lines = []
            lines.append("=" * 60)
            lines.append("REGISTRATION REPORT")
            lines.append("=" * 60)
            lines.append(f"Student ID : {student.student_id}")
            lines.append(f"Name       : {student.name}")
            lines.append(f"Email      : {student.email}")
            lines.append("-" * 60)
            lines.append(f"{'Code':<10}{'Course Title':<32}{'Credits':>8}")
            lines.append("-" * 60)
            if student.courses:
                for c in student.courses:
                    lines.append(f"{c.code:<10}{c.title:<32}{c.credits:>8}")
            else:
                lines.append("No courses registered.")
            lines.append("-" * 60)
            lines.append(f"{'Total Credits':<42}{student.total_credits:>8}")
            lines.append(f"{'Credit Limit':<42}{Student.MAX_CREDITS:>8}")
            lines.append(f"{'Remaining Credits':<42}{Student.MAX_CREDITS - student.total_credits:>8}")
            lines.append("=" * 60)

            self.report_text.configure(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, "\n".join(lines))
            self.report_text.configure(state="disabled")
        except RegistrationError as e:
            self._error(e)


if __name__ == "__main__":
    app = RegistrationApp()
    app.mainloop()
