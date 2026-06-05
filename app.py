from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'hospital_secret_key_123'

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    hospital = db.Column(db.String(100), nullable=False)
    opd = db.Column(db.String(50), nullable=False)
    disease = db.Column(db.String(100), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    payment = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Yaha apna data change kar lena
HOSPITAL_LIST = ['ABC Hospital', 'XYZ Hospital', 'City Care Hospital']
OPD_LIST = ['OPD 101 - General', 'OPD 102 - Ortho', 'OPD 103 - ENT', 'OPD 104 - Skin', 'OPD 105 - Dental']
DISEASE_LIST = ['Fever', 'Cough & Cold', 'Body Pain', 'Stomach Pain', 'Skin Problem', 'Ear Pain', 'Tooth Pain', 'Other']
PAYMENT_LIST = ['Cash', 'UPI/PhonePe', 'Card', 'Free/PMJAY']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        hospital = request.form.get('hospital')
        opd = request.form.get('opd')
        disease = request.form.get('disease')
        patient_name = request.form.get('patient_name')
        address = request.form.get('address')
        payment = request.form.get('payment')
        amount = request.form.get('amount') or 0

        if hospital and opd and disease and patient_name and address and payment:
            new_patient = Patient(hospital=hospital, opd=opd, disease=disease, 
                                patient_name=patient_name, address=address, 
                                payment=payment, amount=amount)
            db.session.add(new_patient)
            db.session.commit()
            flash(f'Token #{new_patient.id} ready! {hospital} - {opd} me jao', 'success')
        else:
            flash('Sab details bharo bhai', 'error')
        return redirect(url_for('index'))

    patients = Patient.query.order_by(Patient.id.desc()).all()
    return render_template('index.html', patients=patients, 
                         hospital_list=HOSPITAL_LIST, 
                         opd_list=OPD_LIST, 
                         disease_list=DISEASE_LIST,
                         payment_list=PAYMENT_LIST)

@app.route('/qr')
def qr_code():
    url = request.url_root
    qr = qrcode.make(url)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
