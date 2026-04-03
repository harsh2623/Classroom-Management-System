import sqlite3
from werkzeug.security import generate_password_hash
from database import init_db, get_db
import os

print("Initializing DB...")
init_db()

conn = get_db()

# Create default admin
pwd_hash = generate_password_hash('admin123')
try:
    conn.execute("INSERT INTO users (username, password_hash, role) VALUES ('admin', ?, 'admin')", (pwd_hash,))
    print("Admin user created (username: admin, password: admin123)")
except sqlite3.IntegrityError:
    print("Admin user already exists.")

# Sample Data
conn.execute("INSERT OR IGNORE INTO classrooms (id, name, capacity, total_area_sqft) VALUES (1, 'Room 101A (Lectures)', 60, 1200)")
conn.execute("INSERT OR IGNORE INTO classrooms (id, name, capacity, total_area_sqft) VALUES (2, 'Lab 2B (CS Lab)', 30, 800)")

conn.execute("INSERT OR IGNORE INTO students (id, name, email, phone) VALUES (1, 'John Doe', 'john.doe@example.com', '+1234567890')")
conn.execute("INSERT OR IGNORE INTO students (id, name, email, phone) VALUES (2, 'Alice Smith', 'alice@example.com', '+0987654321')")

conn.commit()
conn.close()

print("Database seeded completely.")
