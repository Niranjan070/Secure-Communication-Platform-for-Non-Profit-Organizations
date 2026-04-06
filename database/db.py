from flask_pymongo import PyMongo
from pymongo import ASCENDING, DESCENDING

mongo = PyMongo()


def init_indexes():
    """Create the indexes used by authentication, inbox lookups, and audit logs."""
    db = mongo.db
    db.users.create_index("email", unique=True)
    db.users.create_index([("role", ASCENDING)])
    db.messages.create_index([("recipient_id", ASCENDING), ("created_at", DESCENDING)])
    db.messages.create_index([("sender_id", ASCENDING), ("created_at", DESCENDING)])
    db.secure_files.create_index([("recipient_id", ASCENDING), ("created_at", DESCENDING)])
    db.secure_files.create_index([("sender_id", ASCENDING), ("created_at", DESCENDING)])
    db.activity_logs.create_index([("created_at", DESCENDING)])
    db.activity_logs.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
