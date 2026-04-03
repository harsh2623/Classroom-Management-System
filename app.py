import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db
from notifications import send_email, send_whatsapp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key-high-security')

@app.before_request
def load_user():
    g.user = session.get('user_id')
    g.role = session.get('role')

@app.route('/')
def home():
    if not g.user:
        return redirect(url_for('login'))
    if g.role == 'student':
        return render_template('viewer.html')
    return render_template('dashboard.html', role=g.role)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db()
        
        if role not in ['student', 'teacher']:
            return render_template('signup.html', error="Invalid role selected")
            
        try:
            db.execute('INSERT INTO users (username, password_hash, role, plain_password) VALUES (?, ?, ?, ?)',
                       (username, generate_password_hash(password), role, password))
            db.commit()
            return redirect(url_for('login', msg="Account created successfully. Please login."))
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Username already exists")
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- REST API: USERS / ACCOUNTS ---
@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if g.role not in ['admin', 'teacher']: return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    if request.method == 'POST':
        if g.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        try:
            db.execute('INSERT INTO users (username, password_hash, role, plain_password) VALUES (?, ?, ?, ?)',
                       (data['username'], generate_password_hash(data['password']), data['role'], data['password']))
            db.commit()
            return jsonify({'msg': 'User created'})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 400
    
    users = db.execute('SELECT id, username, role, plain_password FROM users WHERE role != "admin"').fetchall()
    return jsonify([dict(r) for r in users])

@app.route('/api/users/<int:id>', methods=['PUT', 'DELETE'])
def manage_user(id):
    if not g.user: return jsonify({'error': 'Session Expired! Please refresh the page and login again.'}), 401
    if g.role != 'admin': return jsonify({'error': f'Unauthorized Action! Your active session role is {g.role}.'}), 403
    db = get_db()
    
    if request.method == 'PUT':
        data = request.json
        try:
            new_pass = data.get('password', '').strip()
            if new_pass:
                db.execute('UPDATE users SET username = ?, password_hash = ?, plain_password = ? WHERE id = ?', 
                           (data['username'], generate_password_hash(new_pass), new_pass, id))
            else:
                db.execute('UPDATE users SET username = ? WHERE id = ?', (data['username'], id))
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 400
        return jsonify({'msg': 'User updated'})
        
    elif request.method == 'DELETE':
        db.execute('DELETE FROM users WHERE id = ?', (id,))
        db.commit()
        return jsonify({'msg': 'User deleted'})

# --- REST API: CLASSROOMS ---
@app.route('/api/classrooms', methods=['GET', 'POST'])
def api_classrooms():
    if not g.user: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    if request.method == 'POST':
        if g.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        cur = db.execute('INSERT INTO classrooms (name, capacity, total_area_sqft) VALUES (?, ?, ?)',
                   (data['name'], data['capacity'], data['total_area_sqft']))
        db.commit()
        return jsonify({'id': cur.lastrowid, 'msg': 'Classroom added'}), 201
    
    rooms = db.execute('SELECT * FROM classrooms').fetchall()
    return jsonify([dict(r) for r in rooms])

@app.route('/api/classrooms/<int:id>', methods=['DELETE'])
def delete_classroom(id):
    if g.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    db.execute('DELETE FROM classrooms WHERE id = ?', (id,))
    db.commit()
    return jsonify({'msg': 'Deleted'})

# --- REST API: STUDENTS ---
@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    if not g.user: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    if request.method == 'POST':
        if g.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        try:
            cur = db.execute('INSERT INTO students (name, email, phone) VALUES (?, ?, ?)',
                       (data['name'], data.get('email') or None, data.get('phone') or None))
            db.commit()
            return jsonify({'id': cur.lastrowid, 'msg': 'Student added'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Email or Phone is already in use.'}), 400
    
    students = db.execute('SELECT * FROM students').fetchall()
    return jsonify([dict(r) for r in students])

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    if g.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    data = request.json
    try:
        db.execute('UPDATE students SET name = ?, email = ?, phone = ? WHERE id = ?',
                   (data['name'], data.get('email') or None, data.get('phone') or None, id))
        db.commit()
        return jsonify({'msg': 'Student updated'})
    except sqlite3.IntegrityError as e:
        return jsonify({'error': f"Error: Email or Phone is already in use by another student."}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    if g.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    db.execute('DELETE FROM students WHERE id = ?', (id,))
    db.commit()
    return jsonify({'msg': 'Deleted'})

# --- REST API: LECTURES ---
@app.route('/api/lectures', methods=['GET', 'POST'])
def api_lectures():
    if not g.user: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    if request.method == 'POST':
        if g.role not in ['admin', 'teacher']: return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        conflict = db.execute('''
            SELECT * FROM lectures WHERE classroom_id = ? 
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
        ''', (data['classroom_id'], data['start_time'], data['start_time'], data['end_time'], data['end_time'])).fetchone()
        
        if conflict: return jsonify({'error': 'Schedule conflict in selected classroom!'}), 400

        cur = db.execute('INSERT INTO lectures (title, classroom_id, teacher_username, start_time, end_time) VALUES (?, ?, ?, ?, ?)',
                   (data['title'], data['classroom_id'], data.get('teacher_username', 'Not Assigned'), data['start_time'], data['end_time']))
        db.commit()
        return jsonify({'id': cur.lastrowid, 'msg': 'Lecture created successfully'}), 201
    
    lectures = db.execute('''
        SELECT l.*, c.name as classroom_name 
        FROM lectures l 
        JOIN classrooms c ON l.classroom_id = c.id
        ORDER BY l.start_time
    ''').fetchall()
    return jsonify([dict(r) for r in lectures])

@app.route('/api/lectures/<int:id>', methods=['PUT', 'DELETE'])
def manage_lecture(id):
    if g.role not in ['admin', 'teacher']: return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    if request.method == 'PUT':
        data = request.json
        conflict = db.execute('''
            SELECT * FROM lectures WHERE classroom_id = ? AND id != ?
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
        ''', (data['classroom_id'], id, data['start_time'], data['start_time'], data['end_time'], data['end_time'])).fetchone()
        if conflict: return jsonify({'error': 'Schedule conflict during update!'}), 400
        
        db.execute('UPDATE lectures SET title=?, classroom_id=?, teacher_username=?, start_time=?, end_time=? WHERE id=?',
                   (data['title'], data['classroom_id'], data.get('teacher_username', 'Not Assigned'), data['start_time'], data['end_time'], id))
        db.commit()
        return jsonify({'msg': 'Lecture updated'})
        
    elif request.method == 'DELETE':
        db.execute('DELETE FROM lectures WHERE id = ?', (id,))
        db.commit()
        return jsonify({'msg': 'Deleted'})

# --- LECTURE ENROLLMENT ---
@app.route('/api/lectures/<int:id>/enroll', methods=['POST'])
def enroll_student(id):
    if not g.user: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    data = request.json
    student_id = data['student_id']
    
    try:
        db.execute('INSERT INTO lecture_students (lecture_id, student_id) VALUES (?, ?)', (id, student_id))
        db.commit()
        
        # Calculate new occupancy and bench area
        lecture = db.execute('SELECT * FROM lectures WHERE id = ?', (id,)).fetchone()
        classroom = db.execute('SELECT * FROM classrooms WHERE id = ?', (lecture['classroom_id'],)).fetchone()
        student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
        count = db.execute('SELECT COUNT(*) as c FROM lecture_students WHERE lecture_id = ?', (id,)).fetchone()['c']
        
        occupancy_rate = (count / classroom['capacity']) * 100
        bench_area_per_student = classroom['total_area_sqft'] / count if count > 0 else classroom['total_area_sqft']
        
        # Send Real Reminder (Email/WhatsApp)
        if student['email']:
            send_email(student['email'], f"Enrolled in {lecture['title']}", f"Hello {student['name']},\n\nYou have been enrolled in {lecture['title']}. Location: {classroom['name']}.\nTiming: {lecture['start_time']} to {lecture['end_time']}.")
            
        if student['phone']:
             send_whatsapp(student['phone'], f"Hello {student['name']}, you are enrolled in {lecture['title']} at {classroom['name']}. ({lecture['start_time']} - {lecture['end_time']})")

        return jsonify({
            'msg': 'Student enrolled', 
            'occupancy_rate': round(occupancy_rate, 2),
            'bench_area_per_student': round(bench_area_per_student, 2)
        })
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Student already enrolled'}), 400

@app.route('/api/lectures/<int:id>/stats', methods=['GET'])
def lecture_stats(id):
    if not g.user: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    lecture = db.execute('SELECT * FROM lectures WHERE id = ?', (id,)).fetchone()
    if not lecture: return jsonify({'error': 'Not found'}), 404
    
    classroom = db.execute('SELECT * FROM classrooms WHERE id = ?', (lecture['classroom_id'],)).fetchone()
    count = db.execute('SELECT COUNT(*) as c FROM lecture_students WHERE lecture_id = ?', (id,)).fetchone()['c']
    
    occupancy_rate = (count / classroom['capacity']) * 100 if classroom['capacity'] > 0 else 0
    bench_area_per_student = classroom['total_area_sqft'] / count if count > 0 else classroom['total_area_sqft']
    
    enrolled_students = db.execute('''
        SELECT s.id, s.name, s.email, s.phone 
        FROM students s
        JOIN lecture_students ls ON s.id = ls.student_id
        WHERE ls.lecture_id = ?
    ''', (id,)).fetchall()
    
    return jsonify({
        'capacity': classroom['capacity'],
        'enrolled': count,
        'occupancy_rate': round(occupancy_rate, 2),
        'bench_area_per_student': round(bench_area_per_student, 2),
        'students': [dict(s) for s in enrolled_students]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
