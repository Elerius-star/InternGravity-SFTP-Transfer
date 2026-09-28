// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('authToken');

// Check if user is logged in (for dashboard)
if (window.location.pathname.includes('dashboard.html') && !authToken) {
    window.location.href = 'index.html';
}

// Login Form Handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('errorMessage');
        
        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('authToken', data.token);
                window.location.href = 'dashboard.html';
            } else {
                errorDiv.textContent = data.error || 'Login failed';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Login error:', error);
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.style.display = 'block';
        }
    });
}

// Dashboard Logic
if (window.location.pathname.includes('dashboard.html')) {
    // Load employees on page load
    loadEmployees();
    
    // Employee Form Handler
    const employeeForm = document.getElementById('employeeForm');
    if (employeeForm) {
        employeeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const employeeData = {
                employee_id: document.getElementById('empId').value,
                name: document.getElementById('empName').value,
                email: document.getElementById('empEmail').value,
                position: document.getElementById('empPosition').value,
                department: document.getElementById('empDepartment').value,
                salary: parseFloat(document.getElementById('empSalary').value)
            };
            
            try {
                const response = await fetch(`${API_BASE_URL}/employees`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify(employeeData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Clear form
                    employeeForm.reset();
                    // Reload employee list
                    loadEmployees();
                    showMessage('Employee added successfully!', 'success');
                } else {
                    showMessage(data.error || 'Failed to add employee', 'error');
                }
            } catch (error) {
                console.error('Error adding employee:', error);
                showMessage('Connection error', 'error');
            }
        });
    }
    
    // Logout Handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('authToken');
            window.location.href = 'index.html';
        });
    }
    
    // Modal Close Handler
    const modal = document.getElementById('editModal');
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    // Edit Form Handler
    const editForm = document.getElementById('editForm');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const employeeId = document.getElementById('editId').value;
            const employeeData = {
                name: document.getElementById('editName').value,
                email: document.getElementById('editEmail').value,
                position: document.getElementById('editPosition').value,
                department: document.getElementById('editDepartment').value,
                salary: parseFloat(document.getElementById('editSalary').value)
            };
            
            try {
                const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify(employeeData)
                });
                
                if (response.ok) {
                    modal.style.display = 'none';
                    loadEmployees();
                    showMessage('Employee updated successfully!', 'success');
                } else {
                    const data = await response.json();
                    showMessage(data.error || 'Update failed', 'error');
                }
            } catch (error) {
                console.error('Error updating employee:', error);
                showMessage('Connection error', 'error');
            }
        });
    }
}

// Function to load employees
async function loadEmployees() {
    const tableBody = document.getElementById('employeeTableBody');
    if (!tableBody) return;
    
    // Show loading
    tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center;"><div class="spinner"></div>Loading...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/employees`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.status === 401) {
            // Unauthorized - redirect to login
            localStorage.removeItem('authToken');
            window.location.href = 'index.html';
            return;
        }
        
        const employees = await response.json();
        
        if (employees.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No employees found</td></tr>';
            return;
        }
        
        tableBody.innerHTML = '';
        employees.forEach(emp => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${emp.id}</td>
                <td>${emp.employee_id}</td>
                <td>${emp.name}</td>
                <td>${emp.email}</td>
                <td>${emp.position}</td>
                <td>${emp.department}</td>
                <td>$${emp.salary.toFixed(2)}</td>
                <td>
                    <button class="action-btn edit-btn" onclick="editEmployee(${emp.id})">Edit</button>
                    <button class="action-btn delete-btn" onclick="deleteEmployee(${emp.id})">Delete</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading employees:', error);
        tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #8b0000;">Error loading employees</td></tr>';
    }
}

// Function to edit employee
window.editEmployee = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const employee = await response.json();
        
        // Fill modal with employee data
        document.getElementById('editId').value = employee.id;
        document.getElementById('editName').value = employee.name;
        document.getElementById('editEmail').value = employee.email;
        document.getElementById('editPosition').value = employee.position;
        document.getElementById('editDepartment').value = employee.department;
        document.getElementById('editSalary').value = employee.salary;
        
        // Show modal
        document.getElementById('editModal').style.display = 'block';
    } catch (error) {
        console.error('Error fetching employee:', error);
        showMessage('Error loading employee data', 'error');
    }
}

// Function to delete employee
window.deleteEmployee = async function(id) {
    if (!confirm('Are you sure you want to delete this employee?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            loadEmployees();
            showMessage('Employee deleted successfully!', 'success');
        } else {
            const data = await response.json();
            showMessage(data.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Error deleting employee:', error);
        showMessage('Connection error', 'error');
    }
}

// Function to show messages
function showMessage(message, type) {
    // Create message element
    const msgDiv = document.createElement('div');
    msgDiv.textContent = message;
    msgDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;
    
    msgDiv.style.backgroundColor = type === 'success' ? '#4CAF50' : '#8b0000';
    
    document.body.appendChild(msgDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        msgDiv.remove();
    }, 3000);
}