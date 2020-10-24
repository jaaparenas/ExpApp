import datetime
from app import db

class BaseModel():
    created_at = db.Column(db.DateTime, nullable=True)
    modify_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    modify_by = db.Column(db.Integer, nullable=True)