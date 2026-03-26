"""
Configuration file for the Agentic Feedback System
"""

# Classification Keywords and Thresholds
CLASSIFICATION_CONFIG = {
    "bug_keywords": ["crash", "error", "bug", "login", "freeze", "broken", "not working"],
    "feature_keywords": ["feature", "would love", "request", "add", "wish", "suggestion"],
    "praise_rating_threshold": 4,  # Ratings >= this are considered praise
    "complaint_rating_threshold": 2,  # Ratings <= this are considered complaints
}

# Priority Assignment Rules
PRIORITY_CONFIG = {
    "critical_keywords": ["crash", "error", "login", "security", "payment", "data loss"],
    "high_keywords": ["slow", "delay", "frustrating", "annoying"],
    "bug_priority": "Critical",
    "feature_priority": "Medium",
    "praise_priority": "Low",
    "complaint_priority": "High",
    "default_priority": "Medium",
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_file": "logs/app.log",
    "log_level": "INFO",
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5,
}

# Data Paths
DATA_PATHS = {
    "app_store_reviews": "data/app_store_reviews.csv",
    "support_emails": "data/support_emails.csv",
    "output_tickets": "outputs/generated_tickets.csv",
}

# CrewAI Configuration
CREWAI_CONFIG = {
    "max_iterations": 5,
    "verbose": True,
}
