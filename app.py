from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
import base64
from io import BytesIO
import os

app = Flask(__name__)

app.secret_key = 'hospital_secret_key_123'

# Database - Render Postgres use karega, local pe SQLite
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model - Table ka naam 'hospital' rahega
class Hospital(db.Model):
    __tablename__ = 'hospital'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hospital_address = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Table auto-create ho jayegi Render pe
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        if name and address:
            new_patient = Hospital(name=name, hospital_address=address)
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient add ho gaya!', 'success')
        return redirect(url_for('index'))
    
    patients = Hospital.query.order_by(Hospital.id.desc()).all()
    return render_template('index.html', patients=patients)

@app.route('/qr')
def qr_code():
    url = request.url_root # Teri site ka link khud le lega
    qr = qrcode.make(url)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
