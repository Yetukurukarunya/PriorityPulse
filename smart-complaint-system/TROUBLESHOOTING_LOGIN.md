# 🔧 Login Error Troubleshooting Guide

## ✅ Fixes Applied

I've just added **comprehensive error handling** to all dashboard routes. The application will now gracefully handle database errors and show helpful error messages instead of breaking.

---

## 🚨 Common Login Errors & Solutions

### Error 1: "Dashboard Error" Message After Login

**What it means:** The dashboard is trying to load data from the database, but the tables might not exist yet.

**Solution:** Run the database setup script:

```bash
cd c:\Users\ykaru\OneDrive\Desktop\PriorityPulse\smart-complaint-system
python setup_database.py
```

This will:
- Create the `prioritypulse_db` database if it doesn't exist
- Create all necessary tables (users, complaints)
- Set up proper indexes and constraints

---

### Error 2: Blank White Page After Login

**Possible Causes:**
1. Database connection failed
2. MySQL server not running
3. Wrong credentials in config.py

**Solution:**

1. **Check if MySQL is running:**
   - Open XAMPP/WAMP control panel
   - Make sure MySQL service is started (green indicator)

2. **Verify database credentials:**
   - Open `config.py`
   - Check these lines:
   ```python
   MYSQL_USER = 'root'  # Your MySQL username
   MYSQL_PASSWORD = 'karunya599@'  # Your MySQL password
   MYSQL_DB = 'prioritypulse_db'
   ```
   - Update if needed (default XAMPP: password is empty '')

3. **Test database connection:**
   ```bash
   python test_db.py
   ```
   This will tell you exactly what's wrong.

---

### Error 3: "Access Denied" or "404 Not Found"

**What it means:** You might be trying to access a dashboard directly without logging in first.

**Solution:**
1. Go to http://localhost:5000/login
2. Login with your credentials
3. You'll be automatically redirected to the correct dashboard

---

### Error 4: JavaScript Errors in Browser Console

**How to check:**
1. Press F12 in your browser
2. Click on "Console" tab
3. Look for red error messages

**Common fixes:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh the page (Ctrl+F5)
- Make sure all CDN resources are loading (check internet connection)

---

## 📋 Step-by-Step Testing Process

### Step 1: Verify MySQL is Running
```bash
# Run the test script
python test_db.py
```

**Expected output:**
```
✓ Connected to MySQL successfully!
✓ Database 'prioritypulse_db' exists
✓ Tables in database:
  - users
  - complaints
✓ Users in database: X
✓ Complaints in database: X
```

### Step 2: Setup Database (if needed)
```bash
python setup_database.py
```

### Step 3: Start the Application
The app should already be running at http://localhost:5000

If not:
```bash
cd c:\Users\ykaru\OneDrive\Desktop\PriorityPulse\smart-complaint-system
python app.py
```

### Step 4: Test Registration
1. Go to http://localhost:5000/register
2. Fill in the form:
   - Username: testuser
   - Email: test@example.com
   - Full Name: Test User
   - Phone: +1234567890
   - **Role: Citizen** (for testing)
   - Password: StrongPassword123!
3. Click "Create Account"

### Step 5: Test Login
1. Go to http://localhost:5000/login
2. Enter your email/username and password
3. Click "Sign In"

**Expected Result:**
- You should be redirected to http://localhost:5000/citizen-dashboard
- You'll see statistics cards and recent activity table

### Step 6: If You See an Error Message

With the new error handling, you should see a yellow alert box at the top saying something like:
```
⚠️ Dashboard error: Table 'prioritypulse_db.complaints' doesn't exist
```

This is helpful! It tells you exactly what's wrong. Then run:
```bash
python setup_database.py
```

---

## 🎯 What Each Dashboard Should Show

### Citizen Dashboard (7 Tabs)
1. **Overview** - Statistics cards + recent complaints table
2. **My Complaints** - All your submitted complaints with search/filter
3. **Submit Complaint** - Form to submit new complaints
4. **Analytics** - Charts showing your complaint statistics
5. **Map View** - Interactive map of complaints
6. **Reports** - Export options (PDF/CSV/Print)
7. **Settings** - Profile management

### Officer Dashboard (7 Tabs)
1. **Overview** - Performance metrics
2. **Assigned Complaints** - Complaints assigned to you
3. **All Complaints** - City-wide view
4. **Analytics** - Performance tracking
5. **Map View** - Geographic distribution
6. **Reports** - Performance reports
7. **Team** - Team management

### Admin Dashboard (8 Tabs)
1. **Overview** - System-wide statistics
2. **All Complaints** - Complete oversight
3. **Users** - User management
4. **Officers** - Officer assignment
5. **Analytics** - Comprehensive analytics
6. **Map View** - System mapping
7. **Reports** - Administrative reports
8. **System Settings** - Configuration

---

## 🔍 Still Having Issues?

### Enable Debug Mode
The app is already in debug mode, so check the terminal output for detailed error messages.

### Check Flask Logs
Look at the PowerShell terminal where you ran `python app.py`. Any errors will show up there.

### Common Terminal Errors:

**Error:** `ModuleNotFoundError: No module named 'flask'`
**Fix:** 
```bash
pip install flask flask-mysqldb flask-bcrypt pandas numpy scikit-learn
```

**Error:** `Can't connect to MySQL server`
**Fix:** Start MySQL service via XAMPP/WAMP

**Error:** `Table doesn't exist`
**Fix:** Run `python setup_database.py`

---

## 💡 Pro Tips

1. **Always start MySQL first** before running the app
2. **Keep the terminal open** to see real-time error logs
3. **Use the preview browser** button in Qoder to test easily
4. **Check browser console** (F12) for frontend errors
5. **The error messages are your friend** - they tell you exactly what's wrong now!

---

## 📞 Quick Reference

| Issue | Command to Fix |
|-------|---------------|
| Database not set up | `python setup_database.py` |
| Test connection | `python test_db.py` |
| Install dependencies | `pip install flask flask-mysqldb flask-bcrypt` |
| Start app manually | `python app.py` |
| Check MySQL status | Open XAMPP → Check if MySQL is green |

---

## ✅ Success Indicators

You know everything is working when:
1. ✅ No error messages after login
2. ✅ Dashboard shows statistics cards (Total Complaints, Resolved, etc.)
3. ✅ You can navigate between tabs smoothly
4. ✅ Tables show complaint data (or "No complaints yet" message)
5. ✅ No red errors in browser console (F12)

---

**Remember:** The error handling I just added will show you exactly what's wrong if something breaks. Before, it would just crash silently. Now you'll get helpful messages!
