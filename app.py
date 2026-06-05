from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
import base64
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'hospital_secret_key_123'

# Database - Render pe SQLite file ban jayegi
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ===== MODELS =====
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    opds = db.relationship('OPD', backref='hospital', lazy=True)

class OPD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    tokens = db.relationship('Token', backref='opd', lazy=True)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    token_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Waiting')
    created_at = db.Column(db.DateTime, default=datetime.now)
    opd_id = db.Column(db.Integer, db.ForeignKey('opd.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)

# ===== ROUTES =====
@app.route('/')
def home():
    hospitals = Hospital.query.all()
    if not hospitals:
        # First time - sample data add karega
        h1 = Hospital(name='City General Hospital', address='Main Road, Pune')
        h2 = Hospital(name='Shree Ram Hospital', address='MG Road, Delhi')
        h3 = Hospital(name='Life Care Hospital', address='Civil Lines, Mumbai')
        db.session.add_all([h1, h2, h3])
        db.session.commit()
        
        db.session.add_all([
            OPD(name='General Medicine', hospital_id=h1.id),
            OPD(name='Dental', hospital_id=h1.id),
            OPD(name='Pediatrics', hospital_id=h2.id),
            OPD(name='Orthopedic', hospital_id=h3.id)
        ])
        db.session.commit()
        hospitals = Hospital.query.all()
    return render_template('dashboard.html', hospitals=hospitals)  # <-- dashboard.html set hai

@app.route('/book_token/<int:hospital_id>')
def book_token(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    opds = OPD.query.filter_by(hospital_id=hospital_id).all()
    return render_template('book_token.html', hospital=hospital, opds=opds)

@app.route('/generate_token', methods=['POST'])
def generate_token():
    name = request.form['name']
    age = request.form['age']
    phone = request.form['phone']
    opd_id = request.form['opd_id']
    
    opd = OPD.query.get(opd_id)
    hospital_id = opd.hospital_id
    
    last_token = Token.query.filter_by(opd_id=opd_id).order_by(Token.token_number.desc()).first()
    token_num = 1 if not last_token else last_token.token_number + 1
    
    new_token = Token(
        patient_name=name, 
        age=age, 
        phone=phone, 
        token_number=token_num,
        opd_id=opd_id, 
        hospital_id=hospital_id
    )
    db.session.add(new_token)
    db.session.commit()
    
    # QR Code banega
    qr_data = f"Token: {token_num}\nName: {name}\nHospital: {opd.hospital.name}\nOPD: {opd.name}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_img = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('token_slip.html', token=new_token, hospital=opd.hospital, opd=opd, qr_img=qr_img)

@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'doctor' and password == '1234':
            return redirect(url_for('doctor_panel'))
        else:
            flash('Galat username ya password!', 'danger')
    return render_template('doctor_login.html')

@app.route('/doctor_panel')
def doctor_panel():
    tokens = Token.query.order_by(Token.created_at.desc()).limit(20).all()
    return render_template('doctor_panel.html', tokens=tokens)

@app.route('/call_token/<int:token_id>')
def call_token(token_id):
    token = Token.query.get_or_404(token_id)
    token.status = 'Called'
    db.session.commit()
    return redirect(url_for('doctor_panel'))

# ===== START APP =====
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
