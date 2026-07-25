import mysql.connector
from getpass import getpass

def setup_database():
    print("=" * 60)
    print("PriorityPulse Database Setup")
    print("=" * 60)
    
    # Get MySQL credentials
    mysql_user = input("Enter MySQL username (default: root): ").strip() or 'root'
    mysql_password = getpass("Enter MySQL password: ")
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host='localhost',
            user=mysql_user,
            password=mysql_password
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS prioritypulse_db")
        cursor.execute("USE prioritypulse_db")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                role ENUM('citizen', 'officer', 'admin') DEFAULT 'citizen',
                department VARCHAR(100),
                profile_pic VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                reset_token VARCHAR(255),
                reset_token_expiry DATETIME,
                last_login DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_username (username),
                INDEX idx_role (role)
            )
        """)
        
        # Create complaints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INT PRIMARY KEY AUTO_INCREMENT,
                complaint_id VARCHAR(20) UNIQUE NOT NULL,
                user_id INT,
                complaint_text TEXT NOT NULL,
                location VARCHAR(200),
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                severity_score DECIMAL(3,1),
                priority_level INT,
                category VARCHAR(50),
                status ENUM('pending', 'assigned', 'in_progress', 'resolved', 'closed') DEFAULT 'pending',
                assigned_to INT,
                assigned_at TIMESTAMP NULL,
                resolved_at TIMESTAMP NULL,
                response_time_hours INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_status (status),
                INDEX idx_user (user_id),
                INDEX idx_assigned (assigned_to)
            )
        """)
        
        # Create user_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                user_agent TEXT,
                ip_address VARCHAR(45),
                expires_at DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_token (session_token)
            )
        """)
        
        # Create login_attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(100),
                ip_address VARCHAR(45),
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.commit()
        print("\n✓ Database tables created successfully!")
        
        # Ask if user wants to create default admin
        create_admin = input("\nCreate default admin user? (y/n): ").lower() == 'y'
        
        if create_admin:
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            
            admin_password = getpass("Enter admin password (default: admin123): ") or 'admin123'
            password_hash = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, is_active, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """, ('admin', 'admin@prioritypulse.com', password_hash, 'System Administrator', 'admin', True, True))
            
            conn.commit()
            print("✓ Admin user created successfully!")
            print("  Username: admin@prioritypulse.com")
            print("  Password: " + admin_password)
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Database setup completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease make sure MySQL is installed and running.")
        print("If you haven't installed MySQL, download it from: https://dev.mysql.com/downloads/")

if __name__ == "__main__":
    setup_database()