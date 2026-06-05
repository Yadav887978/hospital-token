from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
from io import BytesIO
import os, base64

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
    hospital = db.Column(db.String(150), nullable=False)
    opd = db.Column(db.String(50), nullable=False)
    disease = db.Column(db.String(100), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, default=0)
    upi_id = db.Column(db.String(100), default='8879789073-2@ybl')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Render free plan ke liye auto table create
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

# Maharashtra ke Govt Hospital ka list
HOSPITAL_LIST = [
    'JJ Hospital, Mumbai',
    'KEM Hospital, Mumbai',
    'Sion Hospital, Mumbai',
    'Nair Hospital, Mumbai',
    'Cooper Hospital, Mumbai',
    'B.J. Medical College, Pune',
    'Sassoon Hospital, Pune',
    'Civil Hospital, Nagpur',
    'Mayo Hospital, Nagpur',
    'GMCH, Aurangabad',
    'Civil Hospital, Thane',
    'R.C.S.M. GMC, Kolhapur',
    'Civil Hospital, Nashik',
    'Civil Hospital, Solapur',
    'Civil Hospital, Jalgaon',
    'Civil Hospital, Dhule',
    'Civil Hospital, Ratnagiri',
    'Civil Hospital, Amravati',
    'GMCH, Akola',
    'GMCH, Chandrapur',
    'Civil Hospital, Yavatmal',
    'Civil Hospital, Sangli',
    'Civil Hospital, Satara',
    'Civil Hospital, Kolhapur',
    'Civil Hospital, Latur',
    'Civil Hospital, Beed',
    'Civil Hospital, Osmanabad',
    'Civil Hospital, Parbhani',
    'Civil Hospital, Hingoli',
    'Civil Hospital, Nanded'
]

OPD_LIST = [
    'OPD 101 - General Medicine',
    'OPD 102 - Orthopedics',
    'OPD 103 - ENT',
    'OPD 104 - Skin & VD',
    'OPD 105 - Dental',
    'OPD 106 - Eye/Opthalmology',
    'OPD 107 - Pediatrics',
    'OPD 108 - Gynecology',
    'OPD 109 - Surgery',
    'OPD 110 - Psychiatry',
    'OPD 111 - TB & Chest',
    'OPD 112 - Cardiology'
]

DISEASE_LIST = ['Fever', 'Cough & Cold', 'Body Pain', 'Stomach Pain', 'Skin Problem', 'Eye Problem', 'Tooth Pain', 'BP/Sugar Check', 'Headache', 'Other']

# TERA UPI ID
UPI_ID = '8879789073-2@ybl'
HOSPITAL_NAME = 'Hospital Token'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        hospital = request.form.get('hospital')
        opd = request.form.get('opd')
        disease = request.form.get('disease')
        patient_name = request.form.get('patient_name')
        address = request.form.get('address')
        amount = request.form.get('amount') or 0

        if hospital and opd and disease and patient_name and address and amount:
            new_patient = Patient(hospital=hospital, opd=opd, disease=disease,
                                patient_name=patient_name, address=address,
                                amount=amount, upi_id=UPI_ID)
            db.session.add(new_patient)
            db.session.commit()
            flash(f'Token #{new_patient.id} ready! ₹{amount} UPI pay karke slip dikhao', 'success')
        else:
            flash('Sab details bharo + Amount dalo bhai', 'error')
        return redirect(url_for('index'))

    patients = Patient.query.order_by(Patient.id.desc()).all()

    # UPI Scanner QR code
    upi_link = f"upi://pay?pa={UPI_ID}&pn={HOSPITAL_NAME}&am=&cu=INR"
    qr = qrcode.make(upi_link)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    qr_base64 = base64.b64encode(img_io.getvalue()).decode()

    return render_template('index.html', patients=patients,
                         hospital_list=HOSPITAL_LIST,
                         opd_list=OPD_LIST,
                         disease_list=DISEASE_LIST,
                         upi_id=UPI_ID, qr_code=qr_base64)

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
