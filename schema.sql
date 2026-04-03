CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    plain_password TEXT DEFAULT 'Hidden'
);

CREATE TABLE IF NOT EXISTS classrooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    total_area_sqft REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS lectures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    classroom_id INTEGER NOT NULL,
    teacher_username TEXT DEFAULT 'Not Assigned',
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    FOREIGN KEY(classroom_id) REFERENCES classrooms(id)
);

CREATE TABLE IF NOT EXISTS lecture_students (
    lecture_id INTEGER,
    student_id INTEGER,
    PRIMARY KEY(lecture_id, student_id),
    FOREIGN KEY(lecture_id) REFERENCES lectures(id),
    FOREIGN KEY(student_id) REFERENCES students(id)
);
