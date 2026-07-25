import os
from datetime import timedelta

class Config:
    # ============================================
    # MYSQL DATABASE CONFIGURATION
    # ============================================
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'        # Change to your MySQL username
    MYSQL_PASSWORD = 'karunya599@'        # Change to your MySQL password
    MYSQL_DB = 'prioritypulse_db'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # ============================================
    # APPLICATION CONFIGURATION
    # ============================================
    SECRET_KEY = 'your-secret-key-change-this-in-production-2024'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True