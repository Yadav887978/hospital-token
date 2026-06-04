from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)

class OPD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    opd_name = db.Column(db.String(50), nullable=False)
    opd_code = db.Column(db.String(10), nullable=False)
    normal_fees = db.Column(db.Integer, default=20)
    emergency_fees = db.Column(db.Integer, default=30)

class Token(db.Model):
    id = db.Column(db.Integer, primary, key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    opd_id = db.Column(db.Integer, db.ForeignKey('opd.id'))
    token_no = db.Column(db.Integer, nullable=False)
    token_type = db.Column(db.String(10))  # Normal / Emergency
    fees = db.Column(db.Integer)
    status = db.Column(db.String(10), default='Waiting')
    created_at = db.Column(db.DateTime, default=datetime.now)
