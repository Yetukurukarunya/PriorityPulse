# PriorityPulse - Setup & Running Instructions

## ✅ All Errors Fixed!

This document contains everything you need to run the PriorityPulse Smart Complaint System successfully.

---

## 📋 What Was Fixed

### Major Issues Resolved:
1. ✅ **Missing API Endpoints** - Added 7 new routes (`/predict`, `/get_priority_queue`, `/get_analytics_data`, `/get_clusters`, `/get_heatmap`, `/reset_session`, `/update_status`)
2. ✅ **Data Mismatches** - Fixed template data structures to match database schema
3. ✅ **JavaScript Calls** - Updated API calls to match backend endpoints
4. ✅ **Template Data Passing** - Enhanced routes to pass proper data to templates

See `FIXES_SUMMARY.md` for complete details.

---

## 🚀 Quick Start Guide

### Prerequisites

1. **Python 3.8+** installed
2. **MySQL Server** running (XAMPP, WAMP, or standalone)
3. **Internet connection** for CDN resources (Bootstrap, FontAwesome, etc.)

---

### Step 1: Install Dependencies

```bash
cd smart-complaint-system
pip install -r requirements.txt
```

**Requirements include:**
- Flask
- Flask-MySQLDB
- Flask-Bcrypt
- pandas
- numpy
- scikit-learn
- pickle-mixin

---

### Step 2: Setup Database

#### Option A: Automatic Setup (Recommended)

```bash
python setup_database.py
```

You'll be prompted for:
- MySQL username (default: root)
- MySQL password
- Whether to create admin user (recommended: yes)

#### Option B: Manual Setup

1. Open MySQL command line or phpMyAdmin
2. Run the SQL commands from `setup_database.py` manually
3. Create admin user manually if needed

#### Verify Database Connection

```bash
python test_db.py
```

Expected output:
```
✓ Connected to MySQL successfully!
✓ Database 'prioritypulse_db' exists
✓ Tables in database:
  - complaints
  - login_attempts
  - users
  - user_sessions
```

---

### Step 3: Configure Database Credentials

Edit `config.py` if your MySQL credentials are different:

```python
MYSQL_USER = 'root'        # Your MySQL username
MYSQL_PASSWORD = ''        # Your MySQL password
MYSQL_DB = 'prioritypulse_db'
```

**Default XAMPP:** username='root', password=''  
**Default MAMP:** username='root', password='root'

---

### Step 4: Run the Application

```bash
python app.py
```

You should see:
```
ML Model loaded successfully!
* Running on http://0.0.0.0:5000
* Debug mode: on
```

---

### Step 5: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

---

### Step 6: Login

Use these demo credentials:

#### Admin Account
- **Email:** admin@prioritypulse.com
- **Password:** admin123

#### Officer Account
- **Email:** john.doe@city.gov
- **Password:** officer123

#### Citizen Account
- **Email:** jane.smith@email.com
- **Password:** citizen123

---

## 🧪 Testing the Application

### Test All Features

1. **Submit a Complaint**
   - Go to homepage
   - Fill in complaint description
   - Add location
   - Click "Analyze & Submit"
   - Should see severity prediction

2. **View Dashboard**
   - Check statistics cards
   - View priority queue
   - See recent complaints

3. **Test Analytics**
   - Navigate to Analytics page
   - Charts should load automatically
   - Data updates every 30 seconds

4. **Manage Complaints** (Officer/Admin only)
   - Go to Complaints page
   - Filter by status/priority
   - Update complaint status
   - Changes save automatically

5. **View Map**
   - Navigate to Map View
   - See complaint markers
   - Toggle heatmap view

6. **Generate Reports**
   - Go to Reports page
   - View executive summary
   - Export as CSV

---

## 🐛 Troubleshooting

### Error: "No module named 'flask'"
**Solution:** 
```bash
pip install flask flask-mysqldb flask-bcrypt
```

### Error: "Can't connect to MySQL server"
**Solutions:**
1. Make sure MySQL is running
2. Check credentials in `config.py`
3. For XAMPP: Start MySQL from control panel
4. For Windows: `net start MySQL`

### Error: "Database 'prioritypulse_db' doesn't exist"
**Solution:**
```bash
python setup_database.py
```

### Error: "ML Model not found"
**Solution:**
- This is a warning, not an error
- App will use keyword-based fallback
- To fix: Train model using `model_train.py`

### Error: "Access denied for user 'root'@'localhost'"
**Solution:**
- Update password in `config.py`
- Or reset MySQL root password

### Page shows no data / empty charts
**Solution:**
1. Submit some complaints first
2. Refresh the page
3. Wait for auto-refresh (30 seconds)

---

## 📁 Project Structure

```
PriorityPulse/
├── smart-complaint-system/
│   ├── app.py                 # Main Flask application ✅ FIXED
│   ├── config.py              # Configuration
│   ├── setup_database.py      # Database setup script
│   ├── test_db.py             # Database tester
│   ├── model_train.py         # ML model training
│   ├── requirements.txt       # Python dependencies
│   ├── data/
│   │   └── complaints.csv     # Training data
│   ├── models/
│   │   ├── complaint_model.pkl    # ML model
│   │   └── vectorizer.pkl         # Text vectorizer
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Styles (dark theme with gold)
│   │   └── js/
│   │       └── script.js      # JavaScript ✅ FIXED
│   └── templates/
│       ├── base.html          # Base template
│       ├── index.html         # Homepage ✅ FIXED
│       ├── login.html         # Login page
│       ├── register.html      # Registration
│       ├── citizen_dashboard.html  # Citizen dashboard ✅ FIXED
│       ├── officer_dashboard.html  # Officer dashboard
│       ├── admin_dashboard.html    # Admin dashboard
│       ├── analytics.html     # Analytics ✅ FIXED
│       ├── complaints.html    # Complaints list ✅ FIXED
│       ├── map_view.html      # Geographic map ✅ FIXED
│       ├── reports.html       # Reports ✅ FIXED
│       ├── forgot_password.html
│       └── reset_password.html
├── FIXES_SUMMARY.md           # Detailed fix documentation
├── test_routes.py             # API endpoint tester
└── README_SETUP.md            # This file
```

---

## 🔧 Development Tips

### Hot Reload
The app runs with `debug=True`, so changes auto-reload.

### Database Queries
All queries use parameterized statements to prevent SQL injection.

### Session Management
- Sessions last 7 days (configurable in `config.py`)
- Remember me extends session
- Logout clears session

### Adding New Features
1. Add route in `app.py`
2. Create/update template in `templates/`
3. Add CSS in `static/css/style.css`
4. Add JS in `static/js/script.js`

---

## 📊 Database Schema

### Users Table
- Stores all user accounts (citizens, officers, admins)
- Passwords hashed with bcrypt
- Roles: citizen, officer, admin

### Complaints Table
- Stores all complaints
- Severity scores (0-10)
- Categories: Emergency, High, Medium, Low Priority
- Status: pending, in_progress, resolved

---

## 🎨 Customization

### Change Color Scheme
Edit CSS variables in `static/css/style.css`:

```css
:root {
    --accent-gold: #D4AF37;  /* Change primary accent */
    --primary-dark: #0A0A0A; /* Change background */
}
```

### Change App Port
Edit last line of `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Change Session Duration
Edit `config.py`:
```python
PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Change as needed
```

---

## 📝 API Documentation

All endpoints documented in `FIXES_SUMMARY.md`. Key endpoints:

### Authentication
- POST `/login` - User login
- GET `/logout` - User logout
- POST `/register` - User registration

### Complaints
- POST `/submit-complaint` - Submit new complaint
- GET `/get-complaints` - Get all complaints
- POST `/update-status` - Update complaint status

### Analytics
- GET `/get_priority_queue` - Get prioritized list
- GET `/get_analytics_data` - Get statistics
- GET `/get_heatmap` - Get map data

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] MySQL server running
- [ ] Database created with all tables
- [ ] Admin user exists
- [ ] All dependencies installed
- [ ] Config.py has correct credentials
- [ ] App starts without errors
- [ ] Can login with demo accounts
- [ ] Can submit complaints
- [ ] Can view analytics
- [ ] Can update complaint status

---

## 🎉 Success Indicators

When everything works correctly:

1. ✅ App starts with "ML Model loaded successfully!"
2. ✅ Login page loads with dark theme and gold accents
3. ✅ Can login with demo credentials
4. ✅ Dashboard shows statistics
5. ✅ Complaint submission predicts severity
6. ✅ Analytics page shows charts
7. ✅ Can update complaint status
8. ✅ No console errors in browser

---

## 📞 Support

If you encounter any other issues:

1. Check `FIXES_SUMMARY.md` for known fixes
2. Run `test_db.py` to verify database
3. Run `test_routes.py` to verify endpoints
4. Check Flask console for error messages
5. Check browser console for JavaScript errors

---

## 🌟 Summary

**Status:** ✅ All Critical Errors Fixed

**What Works Now:**
- ✅ User authentication (login/register/logout)
- ✅ Password recovery
- ✅ Complaint submission with ML prediction
- ✅ Priority queue management
- ✅ Analytics dashboard with charts
- ✅ Geographic map visualization
- ✅ Reports and exports
- ✅ Role-based access control
- ✅ Status updates
- ✅ Auto-refresh data

**Ready to Run!** 🚀

Just follow the steps above and you're good to go!
