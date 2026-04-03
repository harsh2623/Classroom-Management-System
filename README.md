# Classroom Occupancy Management System

A top-level web application built with Python Flask and vanilla CSS/JS to manage classrooms, students, lectures, and handle sophisticated constraints like scheduling conflicts and live occupancy metrics.

## Features
- **Modern UI/UX**: Custom premium aesthetic with glassmorphism, dynamic animations, modern typography (Inter), and fully responsive layout.
- **Backend Architecture**: REST API in Flask powered by SQLite.
- **Login Module**: Secure password hashing with session-based authentication.
- **Constraint Handling**: Prevents scheduling conflicts based on classroom and time slots.
- **Analytics Engine**: Calculates live capacity/occupancy rates (%) and bench area per student dynamically.
- **Real Reminders Module**: Automated real WhatsApp and Email notifications via Twilio & Smtplib.

## Setup Instructions

1. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Initialization Script** (Sets up DB and Admin User)
   ```bash
   python setup_db.py
   ```

3. **Configure Notifications Configuration (Optional)**
   Open `.env` and assign your Gmail/SMTP credentials or Twilio tokens to enable real emails and WhatsApp pings. Otherwise, it defaults to a logging simulation.

4. **Start Application Server**
   ```bash
   python app.py
   ```

5. **Usage**
   Open your browser to `http://127.0.0.1:5000/`.
   **Username:** admin
   **Password:** admin123
