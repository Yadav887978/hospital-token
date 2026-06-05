from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hospital_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

UPI_ID = "8879789073-2@ybl"
HOSPITAL_NAME = "Hospital Token"
FEE = 30

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital = db.Column(db.String(200), nullable=False)
    opd = db.Column(db.String(100), nullable=False)
    disease = db.Column(db.String(200), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    amount = db.Column(db.Integer, default=30)
    upi_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Booked')  # Booked, Arrived, Called
    created_at = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        hospital = request.form.get('hospital')
        opd = request.form.get('opd')
        disease = request.form.get('disease')
        patient_name = request.form.get('patient_name')
        address = request.form.get('address')
        amount = FEE  # Fixed ₹30

        if hospital and opd and disease and patient_name and address:
            new_patient = Patient(
                hospital=hospital, opd=opd, disease=disease,
                patient_name=patient_name, address=address,
                amount=amount, upi_id=UPI_ID
            )
            db.session.add(new_patient)
            db.session.commit()
            
            upi_link = f"upi://pay?pa={UPI_ID}&pn=Hospital Token&am={FEE}&cu=INR"
            qr_code = generate_qr(upi_link)
            
            flash(f'Token #{new_patient.id} generate ho gaya! ₹30 pay karke Check-In kar lena', 'success')
            return render_template('index.html', patient=new_patient, qr_code=qr_code, upi_link=upi_link, fee=FEE)
        else:
            flash('Sab details bharo bhai', 'error')
    
    return render_template('index.html', fee=FEE)

@app.route('/checkin/<int:id>')
def checkin(id):
    patient = Patient.query.get(id)
    if patient:
        patient.status = 'Arrived'
        db.session.commit()
        flash(f'Check-In ho gaya! Token #{id} ab doctor ke paas dikh raha hai', 'success')
    return redirect(url_for('index'))

@app.route('/doctor/<opd>')
def doctor_panel(opd):
    patients = Patient.query.filter_by(opd=opd, status='Arrived').order_by(Patient.id).all()
    booked = Patient.query.filter_by(opd=opd, status='Booked').count()
    return render_template('doctor.html', patients=patients, opd=opd, booked=booked)

@app.route('/call/<int:id>')
def call_patient(id):
    patient = Patient.query.get(id)
    if patient:
        patient.status = 'Called'
        db.session.commit()
    return redirect(url_for('doctor_panel', opd=patient.opd))

if __name__ == '__main__':
    app.run(debug=True)
