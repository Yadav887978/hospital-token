from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ========== DATABASE MODELS ==========
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))

class OPD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100))
    timing = db.Column(db.String(50))
    
    hospital = db.relationship('Hospital', backref=db.backref('opds', lazy=True))

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    opd_id = db.Column(db.Integer, db.ForeignKey('opd.id'), nullable=False)
    token_no = db.Column(db.Integer, nullable=False)
    token_type = db.Column(db.String(20), nullable=False)  # Emergency / Normal
    patient_name = db.Column(db.String(100))
    patient_age = db.Column(db.Integer)
    fees = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Waiting')  # Waiting / Called / Done
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    hospital = db.relationship('Hospital', backref=db.backref('tokens', lazy=True))
    opd = db.relationship('OPD', backref=db.backref('tokens', lazy=True))
