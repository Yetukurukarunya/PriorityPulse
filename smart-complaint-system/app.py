from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from functools import wraps
import secrets
from datetime import datetime, timedelta
import re
import pandas as pd
import numpy as np
import pickle
import os
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Initialize extensions
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Load ML model
model = None
vectorizer = None

def load_ml_model():
    """Load trained ML model"""
    global model, vectorizer
    try:
        with open('models/complaint_model_enhanced.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('models/vectorizer_enhanced.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        print("ML Model loaded successfully!")
        return True
    except:
        print("ML Model not found. Using fallback predictions.")
        return False

# Helper functions
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """Check if password meets strength requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

def predict_severity(complaint_text):
    """Predict severity score for a complaint"""
    if model and vectorizer:
        try:
            # Preprocess text
            text = complaint_text.lower()
            text_vectorized = vectorizer.transform([text])
            severity = model.predict(text_vectorized)[0]
            
            # Determine category
            if severity >= 8:
                category = "Emergency"
                priority = 1
            elif severity >= 5:
                category = "High Priority"
                priority = 2
            elif severity >= 3:
                category = "Medium Priority"
                priority = 3
            else:
                category = "Low Priority"
                priority = 4
            
            return {
                'severity_score': round(float(severity), 1),
                'category': category,
                'priority_level': priority
            }
        except:
            pass
    
    # Fallback prediction
    urgent_keywords = ['emergency', 'urgent', 'fire', 'accident', 'medical', 'gas leak', 'collapse']
    if any(keyword in complaint_text.lower() for keyword in urgent_keywords):
        return {'severity_score': 8.5, 'category': 'Emergency', 'priority_level': 1}
    else:
        return {'severity_score': 5.0, 'category': 'Medium Priority', 'priority_level': 3}

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('dashboard_redirect'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/dashboard')
def dashboard_redirect():
    """Redirect to appropriate dashboard based on role"""
    if 'user_role' in session:
        if session['user_role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['user_role'] == 'officer':
            return redirect(url_for('officer_dashboard'))
        else:
            return redirect(url_for('citizen_dashboard'))
    return redirect(url_for('login'))

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return dashboard_redirect()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return redirect(url_for('login'))
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, username, email, password_hash, full_name, role, is_active 
            FROM users 
            WHERE email = %s OR username = %s
        """, (email, email))
        user = cur.fetchone()
        cur.close()
        
        if user and user['is_active']:
            if bcrypt.check_password_hash(user['password_hash'], password):
                session.permanent = remember
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_email'] = user['email']
                session['user_fullname'] = user['full_name']
                session['user_role'] = user['role']
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return dashboard_redirect()
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Account not found or inactive', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role = request.form.get('role', 'citizen')
        
        if not all([username, email, password, confirm_password, full_name]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        is_strong, message = is_strong_password(password)
        if not is_strong:
            flash(message, 'danger')
            return redirect(url_for('register'))
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'danger')
            return redirect(url_for('register'))
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing = cur.fetchone()
        
        if existing:
            flash('Username or email already exists', 'danger')
            cur.close()
            return redirect(url_for('register'))
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            cur.execute("""
                INSERT INTO users (username, email, password_hash, full_name, phone, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, password_hash, full_name, phone, role))
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
        finally:
            cur.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        flash('Password reset link has been sent to your email (demo feature)', 'info')
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            flash('Password has been reset successfully! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# Citizen Dashboard
@app.route('/citizen-dashboard')
@login_required
def citizen_dashboard():
    if session['user_role'] != 'citizen':
        flash('Access denied', 'danger')
        return dashboard_redirect()
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT complaint_id, complaint_text, status, severity_score, category, created_at
            FROM complaints 
            WHERE user_id = %s 
            ORDER BY created_at DESC LIMIT 10
        """, (session['user_id'],))
        complaints = cur.fetchall()
        cur.close()
        
        return render_template('citizen_dashboard.html', complaints=complaints)
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'danger')
        return render_template('citizen_dashboard.html', complaints=[])

# Officer Dashboard
@app.route('/officer-dashboard')
@login_required
def officer_dashboard():
    if session['user_role'] != 'officer':
        flash('Access denied', 'danger')
        return dashboard_redirect()
    
    try:
        cur = mysql.connection.cursor()
        
        # Get ALL pending complaints (not assigned yet) + complaints assigned to this officer
        cur.execute("""
            SELECT c.complaint_id, c.complaint_text, c.status, c.severity_score, 
                   c.category, c.location, c.created_at, u.username as citizen_name
            FROM complaints c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.assigned_to = %s OR c.status = 'pending'
            ORDER BY 
                CASE WHEN c.status = 'pending' THEN 0 ELSE 1 END,
                c.severity_score DESC 
            LIMIT 50
        """, (session['user_id'],))
        complaints = cur.fetchall()
        
        # Get stats for ALL complaints (not just assigned ones)
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                AVG(severity_score) as avg_severity
            FROM complaints
        """)
        stats = cur.fetchone()
        
        # Get pending count separately
        cur.execute("""
            SELECT COUNT(*) as pending_count
            FROM complaints 
            WHERE status = 'pending'
        """)
        pending_data = cur.fetchone()
        cur.close()
        
        # Add pending count to stats
        if stats:
            stats = dict(stats)
            stats['pending_count'] = pending_data['pending_count'] if pending_data else 0
        
        return render_template('officer_dashboard.html', complaints=complaints, stats=stats)
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'danger')
        return render_template('officer_dashboard.html', complaints=[], stats=None)

# Admin Dashboard
@app.route('/admin-dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_complaints,
                COUNT(DISTINCT user_id) as total_users,
                AVG(severity_score) as avg_severity,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_complaints
            FROM complaints
        """)
        stats = cur.fetchone()
        
        cur.execute("""
            SELECT complaint_id, complaint_text, status, severity_score, created_at
            FROM complaints 
            ORDER BY created_at DESC LIMIT 10
        """)
        complaints = cur.fetchall()
        
        cur.execute("""
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role
        """)
        user_stats = cur.fetchall()
        
        cur.close()
        
        return render_template('admin_dashboard.html', stats=stats, complaints=complaints, user_stats=user_stats)
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'danger')
        return render_template('admin_dashboard.html', stats=None, complaints=[], user_stats=[])

# Complaint submission API
@app.route('/submit-complaint', methods=['POST'])
@login_required
def submit_complaint():
    try:
        print("\n=== COMPLAINT SUBMISSION STARTED ===")
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("ERROR: No data received")
            return jsonify({'error': 'Invalid submission format'}), 400
        
        complaint_text = data.get('complaint_text', '')
        location = data.get('location', 'Unknown')
        category = data.get('category', 'Other')
        contact = data.get('contact', '')
        
        print(f"Complaint text length: {len(complaint_text)}")
        print(f"Location: {location}")
        print(f"Category: {category}")
        print(f"User ID: {session.get('user_id')}")
        
        # Validate complaint text - minimum length
        if not complaint_text or len(complaint_text.strip()) < 10:
            print("ERROR: Text too short")
            return jsonify({'error': 'Complaint description must be at least 10 characters long'}), 400
        
        # Validate complaint text - maximum length (MySQL TEXT supports 65KB, but let's be reasonable)
        if len(complaint_text) > 50000:
            print("ERROR: Text too long")
            return jsonify({'error': 'Complaint description is too long (max 50,000 characters)'}), 400
        
        # Validate location
        if not location or len(location.strip()) == 0:
            print("ERROR: No location")
            return jsonify({'error': 'Location is required'}), 400
        
        # Get prediction
        prediction = predict_severity(complaint_text)
        print(f"Prediction: {prediction}")
        
        # Generate SHORTER complaint ID (max 20 chars to fit VARCHAR(20))
        # Format: C-YYMMDDHH-XXXX (15 characters total - well under limit!)
        timestamp = datetime.now().strftime('%y%m%d%H')  # 10 chars (YYMMDDHH)
        random_suffix = secrets.token_hex(2).upper()  # 4 chars
        complaint_id = f"C-{timestamp}-{random_suffix}"  # 1 + 1 + 10 + 1 + 4 = 17 chars
        print(f"Generated Complaint ID: {complaint_id} (length: {len(complaint_id)})")
        
        cur = mysql.connection.cursor()
        print("Executing database INSERT...")
        cur.execute("""
            INSERT INTO complaints (complaint_id, user_id, complaint_text, location, 
                                   severity_score, category, priority_level, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (complaint_id, session['user_id'], complaint_text, location,
              prediction['severity_score'], prediction['category'], prediction['priority_level']))
        mysql.connection.commit()
        cur.close()
        print("✓ Database INSERT successful!")
        
        result = {
            'success': True,
            'complaint_id': complaint_id,
            'prediction': {
                'severity_score': prediction['severity_score'],
                'category': prediction['category'],
                'priority_level': prediction['priority_level'],
                'response_time': 'Within 24 hours' if prediction['severity_score'] >= 8 else '3-5 business days'
            }
        }
        print(f"Returning success: {result}")
        print("=== COMPLAINT SUBMISSION COMPLETED ===\n")
        return jsonify(result)
        
    except Exception as e:
        print(f"\n❌ EXCEPTION IN SUBMISSION: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'Submission failed: {str(e)}'}), 500

# Get complaints API - Enhanced for all roles
@app.route('/get-complaints', methods=['GET'])
@login_required
def get_complaints():
    try:
        cur = mysql.connection.cursor()
        
        # Different queries based on user role
        if session['user_role'] == 'citizen':
            # Citizens see only their own complaints
            cur.execute("""
                SELECT complaint_id, complaint_text, location, status, severity_score, 
                       category, created_at
                FROM complaints 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (session['user_id'],))
            
        elif session['user_role'] == 'officer':
            # Officers see pending + assigned complaints
            cur.execute("""
                SELECT c.complaint_id, c.complaint_text, c.location, c.status, 
                       c.severity_score, c.category, c.created_at,
                       u.username as citizen_name
                FROM complaints c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.assigned_to = %s OR c.status = 'pending'
                ORDER BY 
                    CASE WHEN c.status = 'pending' THEN 0 ELSE 1 END,
                    c.severity_score DESC
            """, (session['user_id'],))
            
        elif session['user_role'] == 'admin':
            # Admins see ALL complaints
            cur.execute("""
                SELECT c.complaint_id, c.complaint_text, c.location, c.status, 
                       c.severity_score, c.category, c.created_at,
                       u.username as citizen_name
                FROM complaints c
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.created_at DESC
            """)
        
        complaints = cur.fetchall()
        cur.close()
        
        # Convert to list of dicts for JSON serialization
        complaint_list = []
        for complaint in complaints:
            complaint_dict = dict(complaint)
            # Format datetime if exists
            if 'created_at' in complaint_dict and complaint_dict['created_at']:
                complaint_dict['created_at_formatted'] = complaint_dict['created_at'].strftime('%Y-%m-%d %H:%M')
            complaint_list.append(complaint_dict)
        
        return jsonify({
            'success': True,
            'complaints': complaint_list,
            'count': len(complaint_list)
        })
        
    except Exception as e:
        print(f"Error fetching complaints: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Update complaint status
@app.route('/update-status', methods=['POST'])
@login_required
def update_status():
    try:
        data = request.get_json()
        complaint_id = data.get('complaint_id')
        new_status = data.get('status')
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE complaints SET status = %s, updated_at = NOW()
            WHERE complaint_id = %s
        """, (new_status, complaint_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get all officers (Admin only)
@app.route('/get-officers', methods=['GET'])
@login_required
@role_required('admin')
def get_officers():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, username, email, created_at,
                   COUNT(CASE WHEN c.assigned_to = u.id THEN 1 END) as active_cases,
                   SUM(CASE WHEN c.status = 'resolved' AND c.assigned_to = u.id THEN 1 ELSE 0 END) as resolved_cases
            FROM users u
            LEFT JOIN complaints c ON u.id = c.assigned_to
            WHERE u.role = 'officer'
            GROUP BY u.id
            ORDER BY resolved_cases DESC
        """)
        
        officers = cur.fetchall()
        cur.close()
        
        # Convert to list of dicts
        officers_list = []
        for officer in officers:
            officer_dict = dict(officer)
            # Convert datetime to string if exists
            if 'created_at' in officer_dict and officer_dict['created_at']:
                officer_dict['created_at'] = officer_dict['created_at'].strftime('%Y-%m-%d %H:%M')
            officers_list.append(officer_dict)
        
        return jsonify({
            'success': True,
            'officers': officers_list
        })
    except Exception as e:
        print(f"Error getting officers: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: Assign complaint to officer (Admin only)
@app.route('/assign-complaint', methods=['POST'])
@login_required
@role_required('admin')
def assign_complaint():
    try:
        data = request.get_json()
        complaint_id = data.get('complaint_id')
        officer_id = data.get('officer_id')
        
        if not complaint_id or not officer_id:
            return jsonify({'error': 'Missing complaint_id or officer_id'}), 400
        
        cur = mysql.connection.cursor()
        
        # Check if complaint exists
        cur.execute("SELECT status FROM complaints WHERE complaint_id = %s", (complaint_id,))
        result = cur.fetchone()
        
        if not result:
            cur.close()
            return jsonify({'error': 'Complaint not found'}), 404
        
        # Assign to officer
        cur.execute("""
            UPDATE complaints 
            SET assigned_to = %s, status = 'in_progress', updated_at = NOW()
            WHERE complaint_id = %s
        """, (officer_id, complaint_id))
        
        mysql.connection.commit()
        cur.close()
        
        print(f"✓ Complaint {complaint_id} assigned to officer {officer_id}")
        
        return jsonify({
            'success': True,
            'message': 'Complaint assigned successfully'
        })
    except Exception as e:
        print(f"Error assigning complaint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: Get all users (Admin only)
@app.route('/get-users', methods=['GET'])
@login_required
@role_required('admin')
def get_users():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, username, email, full_name, phone, role, is_active, created_at
            FROM users
            ORDER BY role, username
        """)
        users = cur.fetchall()
        cur.close()
        
        users_list = []
        for user in users:
            user_dict = dict(user)
            if 'created_at' in user_dict and user_dict['created_at']:
                user_dict['created_at'] = user_dict['created_at'].strftime('%Y-%m-%d %H:%M')
            users_list.append(user_dict)
            
        return jsonify({
            'success': True,
            'users': users_list
        })
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: Toggle user active status (Admin only)
@app.route('/toggle-user-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        is_active = data.get('is_active')
        
        if user_id is None or is_active is None:
            return jsonify({'error': 'Missing user_id or is_active'}), 400
            
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error toggling user status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: Update user role (Admin only)
@app.route('/update-user-role', methods=['POST'])
@login_required
@role_required('admin')
def update_user_role():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_role = data.get('role')
        
        if not user_id or not new_role:
            return jsonify({'error': 'Missing user_id or role'}), 400
            
        if new_role not in ['citizen', 'officer', 'admin']:
            return jsonify({'error': 'Invalid role specified'}), 400
            
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating user role: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Profile page
@app.route('/profile')
@login_required
def profile():
    return redirect(url_for('dashboard_redirect'))

# Analytics page
@app.route('/analytics')
@login_required
def analytics():
    cur = mysql.connection.cursor()
    
    # Get basic stats for initial render
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(severity_score) as avg_severity,
            SUM(CASE WHEN status != 'pending' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as response_rate,
            SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as resolution_rate
        FROM complaints
    """)
    stats_data = cur.fetchone()
    
    # By category
    cur.execute("""
        SELECT category, COUNT(*) as count 
        FROM complaints 
        GROUP BY category
    """)
    by_category = {row['category']: row['count'] for row in cur.fetchall()}
    
    cur.close()
    
    stats = {
        'total': stats_data['total'] or 0,
        'avg_severity': round(stats_data['avg_severity'], 1) if stats_data['avg_severity'] else 0,
        'response_rate': round(stats_data['response_rate'], 1) if stats_data['response_rate'] else 0,
        'resolution_rate': round(stats_data['resolution_rate'], 1) if stats_data['resolution_rate'] else 0,
        'by_category': by_category
    }
    
    return render_template('analytics.html', stats=stats)

# Map view page
@app.route('/map-view')
@login_required
def map_view():
    return render_template('map_view.html')

# Reports page
@app.route('/reports')
@login_required
def reports():
    cur = mysql.connection.cursor()
    
    # Get stats
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(severity_score) as avg_severity,
            SUM(CASE WHEN status != 'pending' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as response_rate,
            SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as resolution_rate
        FROM complaints
    """)
    stats_data = cur.fetchone()
    
    # By category
    cur.execute("""
        SELECT category, COUNT(*) as count 
        FROM complaints 
        GROUP BY category
    """)
    by_category = {row['category']: row['count'] for row in cur.fetchall()}
    
    cur.close()
    
    stats = {
        'total': stats_data['total'] or 0,
        'avg_severity': round(stats_data['avg_severity'], 1) if stats_data['avg_severity'] else 0,
        'response_rate': round(stats_data['response_rate'], 1) if stats_data['response_rate'] else 0,
        'resolution_rate': round(stats_data['resolution_rate'], 1) if stats_data['resolution_rate'] else 0,
        'by_category': by_category
    }
    
    # AI Insights
    insights = {'has_insights': False, 'insights': []}
    if stats['total'] > 0:
        insights['has_insights'] = True
        if stats['avg_severity'] >= 7:
            insights['insights'].append({
                'type': 'warning',
                'icon': 'exclamation-triangle',
                'title': 'High Average Severity',
                'message': f'Your average severity score is {stats["avg_severity"]}, which is above normal. Consider allocating more resources.'
            })
        if stats['resolution_rate'] < 50:
            insights['insights'].append({
                'type': 'info',
                'icon': 'clock',
                'title': 'Low Resolution Rate',
                'message': f'Only {stats["resolution_rate"]}% of complaints are resolved. Focus on closing pending complaints.'
            })
    
    return render_template('reports.html', stats=stats, insights=insights)

# Complaints page
@app.route('/complaints')
@login_required
def complaints_page():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.id, c.complaint_id, c.complaint_text, c.location, c.status, 
               c.severity_score, c.category, c.created_at, c.contact,
               u.username as citizen_name
        FROM complaints c
        LEFT JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    """)
    complaints = cur.fetchall()
    cur.close()
    return render_template('complaints.html', complaints=complaints)

# API: Predict severity
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.get_json()
        complaint_text = data.get('complaint_text', '')
        location = data.get('location', 'Unknown')
        
        if not complaint_text:
            return jsonify({'error': 'No complaint text provided'}), 400
        
        # Get prediction
        prediction = predict_severity(complaint_text)
        
        # Add color for UI
        if prediction['severity_score'] >= 8:
            prediction['color'] = 'danger'
            prediction['response_time'] = 'Immediate'
        elif prediction['severity_score'] >= 5:
            prediction['color'] = 'warning'
            prediction['response_time'] = '1-2 hours'
        elif prediction['severity_score'] >= 3:
            prediction['color'] = 'info'
            prediction['response_time'] = '24 hours'
        else:
            prediction['color'] = 'success'
            prediction['response_time'] = '3-5 days'
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get priority queue
@app.route('/get_priority_queue', methods=['GET'])
@login_required
def get_priority_queue():
    try:
        cur = mysql.connection.cursor()
        
        if session['user_role'] == 'citizen':
            cur.execute("""
                SELECT id, complaint_id, complaint_text as text, location, 
                       status, severity_score, category, created_at as timestamp
                FROM complaints 
                WHERE user_id = %s 
                ORDER BY severity_score DESC
            """, (session['user_id'],))
        elif session['user_role'] == 'officer':
            cur.execute("""
                SELECT id, complaint_id, complaint_text as text, location, 
                       status, severity_score, category, created_at as timestamp
                FROM complaints 
                WHERE assigned_to = %s OR status = 'pending'
                ORDER BY severity_score DESC
            """, (session['user_id'],))
        else:
            cur.execute("""
                SELECT id, complaint_id, complaint_text as text, location, 
                       status, severity_score, category, created_at as timestamp
                FROM complaints 
                ORDER BY severity_score DESC 
                LIMIT 50
            """)
        
        complaints = cur.fetchall()
        cur.close()
        
        # Add queue position
        for i, complaint in enumerate(complaints):
            complaint['queue_position'] = i + 1
        
        return jsonify({
            'success': True,
            'complaints': complaints,
            'total_count': len(complaints)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get analytics data
@app.route('/get_analytics_data', methods=['GET'])
@login_required
def get_analytics_data():
    try:
        cur = mysql.connection.cursor()
        
        # Basic stats
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(severity_score) as avg_severity,
                SUM(CASE WHEN status != 'pending' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as response_rate,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as resolution_rate
            FROM complaints
        """)
        stats = cur.fetchone()
        
        # By category
        cur.execute("""
            SELECT category, COUNT(*) as count 
            FROM complaints 
            GROUP BY category
        """)
        by_category = {row['category']: row['count'] for row in cur.fetchall()}
        
        # By location
        cur.execute("""
            SELECT location, COUNT(*) as count 
            FROM complaints 
            GROUP BY location
        """)
        by_location = {row['location']: row['count'] for row in cur.fetchall()}
        
        # Trend data (last 7 days)
        cur.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM complaints 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        trend_data = [{'date': row['date'].strftime('%Y-%m-%d'), 'count': row['count']} 
                      for row in cur.fetchall()]
        
        # Peak hours
        cur.execute("""
            SELECT HOUR(created_at) as hour, COUNT(*) as count 
            FROM complaints 
            GROUP BY HOUR(created_at)
            ORDER BY hour
        """)
        peak_hours = [[row['hour'], row['count']] for row in cur.fetchall()]
        
        cur.close()
        
        analytics = {
            'total': stats['total'] or 0,
            'avg_severity': round(stats['avg_severity'], 1) if stats['avg_severity'] else 0,
            'response_rate': round(stats['response_rate'], 1) if stats['response_rate'] else 0,
            'resolution_rate': round(stats['resolution_rate'], 1) if stats['resolution_rate'] else 0,
            'by_category': by_category,
            'by_location': by_location,
            'trend_data': trend_data,
            'peak_hours': peak_hours
        }
        
        return jsonify({
            'success': True,
            'stats': analytics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get clusters
@app.route('/get_clusters', methods=['GET'])
@login_required
def get_clusters():
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT 
                location,
                COUNT(*) as complaint_count,
                AVG(severity_score) as avg_severity,
                MODE() WITHIN GROUP (ORDER BY category) as common_category
            FROM complaints
            GROUP BY location
            ORDER BY avg_severity DESC
            LIMIT 10
        """)
        
        clusters = []
        for row in cur.fetchall():
            clusters.append({
                'location': row['location'],
                'complaint_count': row['complaint_count'],
                'avg_severity': float(row['avg_severity']),
                'common_category': row['common_category']
            })
        
        cur.close()
        
        return jsonify({
            'success': True,
            'clusters': clusters
        })
    except Exception as e:
        # Fallback for MySQL versions that don't support MODE()
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    location,
                    COUNT(*) as complaint_count,
                    AVG(severity_score) as avg_severity,
                    category as common_category
                FROM complaints
                GROUP BY location, category
                ORDER BY avg_severity DESC
                LIMIT 10
            """)
            
            clusters = []
            for row in cur.fetchall():
                clusters.append({
                    'location': row['location'],
                    'complaint_count': row['complaint_count'],
                    'avg_severity': float(row['avg_severity']),
                    'common_category': row['common_category']
                })
            
            cur.close()
            
            return jsonify({
                'success': True,
                'clusters': clusters
            })
        except Exception as e2:
            return jsonify({'error': str(e2)}), 500

# API: Get heatmap data
@app.route('/get_heatmap', methods=['GET'])
@login_required
def get_heatmap():
    try:
        cur = mysql.connection.cursor()
        
        # Check if we have lat/lon data
        cur.execute("""
            SELECT complaint_text, severity_score, latitude, longitude, location
            FROM complaints
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY severity_score DESC
            LIMIT 100
        """)
        
        heatmap_data = []
        for row in cur.fetchall():
            if row['latitude'] and row['longitude']:
                heatmap_data.append({
                    'lat': float(row['latitude']),
                    'lon': float(row['longitude']),
                    'complaint': row['complaint_text'][:100],
                    'severity': float(row['severity_score'])
                })
        
        # If no lat/lon data, use location-based dummy coordinates
        if not heatmap_data:
            cur.execute("""
                SELECT complaint_text, severity_score, location
                FROM complaints
                ORDER BY severity_score DESC
                LIMIT 100
            """)
            
            # Default to New York City area
            default_lat = 40.7128
            default_lon = -74.0060
            
            for i, row in enumerate(cur.fetchall()):
                # Create slight variations for demo purposes
                heatmap_data.append({
                    'lat': default_lat + (i * 0.01),
                    'lon': default_lon + (i * 0.01),
                    'complaint': row['complaint_text'][:100],
                    'severity': float(row['severity_score'])
                })
        
        cur.close()
        
        return jsonify({
            'success': True,
            'heatmap_data': heatmap_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Reset session
@app.route('/reset_session', methods=['POST'])
@login_required
@role_required('admin')
def reset_session():
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM complaints")
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Update complaint status (alias for update-status)
@app.route('/update_status', methods=['POST'])
@login_required
def update_status_alias():
    return update_status()

if __name__ == '__main__':
    load_ml_model()
    app.run(debug=True, host='0.0.0.0', port=5000)