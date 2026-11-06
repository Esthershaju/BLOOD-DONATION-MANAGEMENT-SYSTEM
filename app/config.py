"""
Configuration module for Blood Donation Management System.
Handles database credentials, admin credentials, and system constants.
"""
import os

# Automatically load environment variables from .env file in project root if present
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    try:
        with open(_env_path, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ[_k.strip()] = _v.strip()
    except Exception:
        pass

# Database Connection Parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "blood_donation_db")

# Admin Authentication
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Domain Constants
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
GENDERS = ["Male", "Female", "Other"]
URGENCY_LEVELS = ["Normal", "Urgent", "Critical"]
REQUEST_STATUSES = ["Pending", "Processing", "Completed", "Cancelled"]

# Validation Rules
MIN_DONOR_AGE = 18
MAX_DONOR_AGE = 65

# Blood Group Compatibility Matrix
# Key: Recipient Blood Group -> Value: List of Compatible Donor Blood Groups
BLOOD_COMPATIBILITY = {
    "A+":  ["A+", "A-", "O+", "O-"],
    "A-":  ["A-", "O-"],
    "B+":  ["B+", "B-", "O+", "O-"],
    "B-":  ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], # Universal recipient
    "AB-": ["AB-", "A-", "B-", "O-"],
    "O+":  ["O+", "O-"],
    "O-":  ["O-"] # Universal donor
}

# Urgency Weightage for Dynamic Programming & Priority Matching
URGENCY_WEIGHTS = {
    "Critical": 10,
    "Urgent": 5,
    "Normal": 2
}
