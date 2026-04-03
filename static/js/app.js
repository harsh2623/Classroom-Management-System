// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = type === 'success' ? 'ri-checkbox-circle-fill' : 'ri-error-warning-fill';
    let color = type === 'success' ? 'text-green-500' : 'text-red-500';
    
    toast.innerHTML = `<i class="${icon}" style="color: ${type === 'success' ? '#10b981' : '#ef4444'}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal handling
function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
    // optionally reset forms inside
}

// Tab Switching
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tab.dataset.target).classList.add('active');
        });
    });

    // Initial Data Fetch
    fetchClassrooms();
    fetchStudents();
    fetchUsers();
    fetchLectures();
});

// API Calls - Classrooms
async function fetchClassrooms() {
    const res = await fetch('/api/classrooms');
    const data = await res.json();
    
    const tbody = document.getElementById('classrooms-tbody');
    const select = document.getElementById('lecture-classroom-select');
    if(tbody) tbody.innerHTML = ''; 
    if(select) select.innerHTML = '';
    
    data.forEach((c, index) => {
        if(tbody) {
            tbody.innerHTML += `
                <tr>
                    <td>#${index + 1}</td>
                    <td><strong>${c.name}</strong></td>
                    <td>${c.capacity}</td>
                    <td>${c.total_area_sqft}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="deleteClassroom(${c.id})"><i class="ri-delete-bin-line"></i></button>
                    </td>
                </tr>
            `;
        }
        if (select) select.innerHTML += `<option value="${c.id}">${c.name} (Cap: ${c.capacity})</option>`;
    });
}

async function addClassroom(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    
    const res = await fetch('/api/classrooms', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if(res.ok) {
        showToast('Classroom added successfully', 'success');
        closeModal('classroomModal');
        e.target.reset();
        fetchClassrooms();
    } else {
        showToast('Error adding classroom', 'error');
    }
}

async function deleteClassroom(id) {
    if(!confirm('Delete this classroom?')) return;
    const res = await fetch(`/api/classrooms/${id}`, { method: 'DELETE' });
    if(res.ok) {
        showToast('Classroom deleted', 'success');
        fetchClassrooms();
        fetchLectures();
    }
}

// API Calls - Students
async function fetchStudents() {
    const res = await fetch('/api/students');
    const data = await res.json();
    
    const tbody = document.getElementById('students-tbody');
    const select = document.getElementById('enroll-student-select');
    if(tbody) tbody.innerHTML = ''; 
    if(select) select.innerHTML = '';
    
    data.forEach((s, index) => {
        if(tbody) {
            tbody.innerHTML += `
                <tr>
                    <td>#${index + 1}</td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.email || '-'}</td>
                    <td>${s.phone || '-'}</td>
                    <td style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm" onclick="openEditStudent(${s.id}, \`${s.name}\`, \`${s.email || ''}\`, \`${s.phone || ''}\`)"><i class="ri-edit-line"></i></button>
                        <button class="btn btn-danger btn-sm" onclick="deleteStudent(${s.id})"><i class="ri-delete-bin-line"></i></button>
                    </td>
                </tr>
            `;
        }
        if(select) select.innerHTML += `<option value="${s.id}">${s.name}</option>`;
    });
}

function openEditStudent(id, name, email, phone) {
    document.getElementById('edit-student-id').value = id;
    document.getElementById('edit-student-name').value = name;
    document.getElementById('edit-student-email').value = email;
    document.getElementById('edit-student-phone').value = phone;
    openModal('editStudentModal');
}

async function submitEditStudent(e) {
    e.preventDefault();
    const id = document.getElementById('edit-student-id').value;
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    
    const res = await fetch(`/api/students/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if(res.ok) {
        showToast('Student updated successfully', 'success');
        closeModal('editStudentModal');
        fetchStudents();
    } else {
        const error = await res.json();
        showToast(error.error || 'Error updating student', 'error');
    }
}

async function addStudent(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    
    const res = await fetch('/api/students', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if(res.ok) {
        showToast('Student added successfully', 'success');
        closeModal('studentModal');
        e.target.reset();
        fetchStudents();
    } else {
        showToast('Error adding student', 'error');
    }
}

async function deleteStudent(id) {
    if(!confirm('Delete this student?')) return;
    const res = await fetch(`/api/students/${id}`, { method: 'DELETE' });
    if(res.ok) {
        showToast('Student deleted', 'success');
        fetchStudents();
        fetchLectures();
    }
}

// API Calls - Users
async function fetchUsers() {
    const res = await fetch('/api/users');
    if(!res.ok) return;
    const data = await res.json();
    const tBody = document.getElementById('teachers-tbody');
    const sBody = document.getElementById('student-accounts-tbody');
    const teacherSelect = document.getElementById('lecture-teacher-select');
    const editTeacherSelect = document.getElementById('edit-lecture-teacher');
    
    if(tBody) tBody.innerHTML = '';
    if(sBody) sBody.innerHTML = '';
    if(teacherSelect) teacherSelect.innerHTML = '<option value="Not Assigned">None / Unassigned</option>';
    if(editTeacherSelect) editTeacherSelect.innerHTML = '<option value="Not Assigned">None / Unassigned</option>';
    
    let teacherCount = 0;
    let studentCount = 0;
    
    data.forEach(u => {
        let displayId = u.role === 'teacher' ? ++teacherCount : ++studentCount;
        let rowHtml = `
            <tr>
                <td>#${displayId}</td>
                <td><strong>${u.username}</strong></td>
                <td><code>${u.plain_password || ''}</code></td>
                <td style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-secondary btn-sm" onclick="openEditUser(${u.id}, \`${u.username}\`)"><i class="ri-edit-line"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteUser(${u.id})"><i class="ri-delete-bin-line"></i></button>
                </td>
            </tr>
        `;
        if (u.role === 'teacher') {
            if(tBody) tBody.innerHTML += rowHtml;
            if(teacherSelect) teacherSelect.innerHTML += `<option value="${u.username}">${u.username}</option>`;
            if(editTeacherSelect) editTeacherSelect.innerHTML += `<option value="${u.username}">${u.username}</option>`;
        } else if (u.role === 'student' && sBody) {
            sBody.innerHTML += rowHtml;
        }
    });
}

function openEditUser(id, username) {
    document.getElementById('edit-user-id').value = id;
    document.getElementById('edit-user-name').value = username;
    document.getElementById('edit-user-password').value = '';
    openModal('editUserModal');
}

async function submitEditUser(e) {
    e.preventDefault();
    const id = document.getElementById('edit-user-id').value;
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    
    const res = await fetch(`/api/users/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if(res.ok) {
        showToast('Username updated', 'success');
        closeModal('editUserModal');
        fetchUsers();
    } else {
        const error = await res.json();
        showToast(error.error || 'Error updating user', 'error');
    }
}

async function submitAddUser(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    const res = await fetch('/api/users', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if(res.ok) {
        showToast('Account added successfully', 'success');
        closeModal('addUserModal');
        e.target.reset();
        fetchUsers();
    } else {
        const error = await res.json();
        showToast(error.error || 'Error adding account', 'error');
    }
}

async function deleteUser(id) {
    if(!confirm('Permanently delete this user account?')) return;
    const res = await fetch(`/api/users/${id}`, { method: 'DELETE' });
    if(res.ok) {
        showToast('Account deleted', 'success');
        fetchUsers();
    } else {
        const error = await res.json();
        showToast(error.error || 'Error deleting account', 'error');
    }
}

// API Calls - Lectures
async function fetchLectures() {
    const res = await fetch('/api/lectures');
    const data = await res.json();
    
    const grid = document.getElementById('lectures-grid');
    grid.innerHTML = '';
    
    for (let l of data) {
        // Fetch live stats for each lecture
        const statRes = await fetch(`/api/lectures/${l.id}/stats`);
        const stats = statRes.ok ? await statRes.json() : { capacity: 0, enrolled: 0, occupancy_rate: 0, bench_area_per_student: 0 };
        
        let occClass = stats.occupancy_rate > 90 ? 'high' : (stats.occupancy_rate > 50 ? 'medium' : 'low');
        
        grid.innerHTML += `
            <div class="lecture-card">
                <div class="lecture-header">
                    <div class="lecture-title">${l.title}</div>
                    <div class="lecture-room"><i class="ri-map-pin-line"></i> ${l.classroom_name}</div>
                </div>
                <div class="text-sm text-dimmed mb-2"><i class="ri-presentation-line"></i> Teacher: <strong style="color:white;">${l.teacher_username || 'Not Assigned'}</strong></div>
                <div class="lecture-time">
                    <div><i class="ri-time-line"></i> ${new Date(l.start_time).toLocaleString()}</div>
                    <div><i class="ri-arrow-right-line"></i> ${new Date(l.end_time).toLocaleTimeString()}</div>
                </div>
                
                <div class="stats-box">
                    <div class="stat-row">
                        <span>Occupancy</span>
                        <strong>${stats.enrolled} / ${stats.capacity} (${stats.occupancy_rate}%)</strong>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${occClass}" style="width: ${Math.min(stats.occupancy_rate, 100)}%"></div>
                    </div>
                    <div class="stat-row text-sm text-dimmed">
                        <span>Bench Area / Student:</span>
                        <span>${stats.bench_area_per_student} sq.ft</span>
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="btn btn-secondary flex-1" onclick="openEnrollModal(${l.id})">
                        <i class="ri-user-add-line"></i> Enroll
                    </button>
                    <button class="btn btn-secondary" onclick="openEditLecture(${l.id}, \`${l.title}\`, ${l.classroom_id}, '${l.start_time}', '${l.end_time}', \`${l.teacher_username || ''}\`)">
                        <i class="ri-edit-line"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deleteLecture(${l.id})">
                        <i class="ri-delete-bin-line"></i>
                    </button>
                </div>
            </div>
        `;
    }
}

async function addLecture(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    
    const res = await fetch('/api/lectures', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    const responseData = await res.json();
    
    if(res.ok) {
        showToast('Lecture scheduled successfully', 'success');
        closeModal('lectureModal');
        e.target.reset();
        fetchLectures();
    } else {
        showToast(responseData.error || 'Conflict generating schedule', 'error');
    }
}

function openEditLecture(id, title, classroomId, startTime, endTime, teacherUsername) {
    document.getElementById('edit-lecture-id').value = id;
    document.getElementById('edit-lecture-title').value = title;
    
    // Copy classroom options from add modal
    document.getElementById('edit-lecture-classroom').innerHTML = document.getElementById('lecture-classroom-select').innerHTML;
    document.getElementById('edit-lecture-classroom').value = classroomId;
    
    if (teacherUsername) {
        document.getElementById('edit-lecture-teacher').value = teacherUsername;
    } else {
        document.getElementById('edit-lecture-teacher').value = 'Not Assigned';
    }
    
    document.getElementById('edit-lecture-start').value = startTime;
    document.getElementById('edit-lecture-end').value = endTime;
    
    openModal('editLectureModal');
}

async function submitEditLecture(e) {
    e.preventDefault();
    const id = document.getElementById('edit-lecture-id').value;
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData);
    
    const res = await fetch(`/api/lectures/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if(res.ok) {
        showToast('Lecture updated successfully', 'success');
        closeModal('editLectureModal');
        fetchLectures();
    } else {
        const error = await res.json();
        showToast(error.error || 'Conflict during update', 'error');
    }
}

async function deleteLecture(id) {
    if(!confirm('Delete this lecture?')) return;
    const res = await fetch(`/api/lectures/${id}`, { method: 'DELETE' });
    if(res.ok) {
        showToast('Lecture deleted', 'success');
        fetchLectures();
    }
}

function openEnrollModal(lectureId) {
    document.getElementById('enroll-lecture-id').value = lectureId;
    openModal('enrollModal');
}

async function enrollStudent(e) {
    e.preventDefault();
    const lectureId = document.getElementById('enroll-lecture-id').value;
    const studentId = document.getElementById('enroll-student-select').value;
    
    const res = await fetch(`/api/lectures/${lectureId}/enroll`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ student_id: studentId })
    });
    
    const data = await res.json();
    
    if(res.ok) {
        showToast(`Enrolled! Occupancy: ${data.occupancy_rate}%. Notified via Twilio/Email (simulated if keys missing).`, 'success');
        closeModal('enrollModal');
        fetchLectures();
    } else {
        showToast(data.error || 'Error enrolling', 'error');
    }
}
