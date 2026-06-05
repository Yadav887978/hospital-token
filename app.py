from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret123hospitalkey'

db = SQLAlchemy(app)

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

# ========== ROUTES ==========
@app.route('/', methods=['GET', 'POST'])
def index():
    hospitals = Hospital.query.all()
    
    # Agar database khali hai to demo hospital add kar de
    if len(hospitals) == 0:
        h1 = Hospital(name="City Care Hospital", city="Mumbai", address="Andheri West")
        h2 = Hospital(name="General Hospital", city="Delhi", address="Connaught Place")
        h3 = Hospital(name="LifeLine Hospital", city="Lucknow", address="Gomti Nagar")
        db.session.add_all([h1, h2, h3])
        db.session.commit()
        
        # OPD bhi add kar de
        opd1 = OPD(hospital_id=1, name="General Medicine", doctor_name="Dr. Sharma", timing="10AM-2PM")
        opd2 = OPD(hospital_id=1, name="Orthopedic", doctor_name="Dr. Verma", timing="2PM-6PM")
        opd3 = OPD(hospital_id=2, name="Cardiology", doctor_name="Dr. Gupta", timing="11AM-3PM")
        opd4 = OPD(hospital_id=3, name="Pediatrics", doctor_name="Dr. Singh", timing="9AM-1PM")
        db.session.add_all([opd1, opd2, opd3, opd4])
        db.session.commit()
        
        hospitals = Hospital.query.all()
    
    return render_template('dashboard.html', hospitals=hospitals)

@app.route('/book_token/<int:hospital_id>', methods=['GET', 'POST'])
def book_token(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    opds = OPD.query.filter_by(hospital_id=hospital_id).all()
    
    if request.method == 'POST':
        opd_id = request.form['opd_id']
        token_type = request.form['token_type']
        patient_name = request.form['patient_name']
        patient_age = request.form['patient_age']
        
        fees = 200 if token_type == 'Emergency' else 50
        
        # Last token no nikal ke +1 kar de
        last_token = Token.query.filter_by(opd_id=opd_id).order_by(Token.token_no.desc()).first()
        token_no = 1 if not last_token else last_token.token_no + 1
        
        new_token = Token(
            hospital_id=hospital_id,
            opd_id=opd_id,
            token_no=token_no,
            token_type=token_type,
            patient_name=patient_name,
            patient_age=patient_age,
            fees=fees
        )
        db.session.add(new_token)
        db.session.commit()
        
        # QR Code generate kare
        qr_data = f"Token:{token_no} | Hospital:{hospital.name} | Patient:{patient_name} | Type:{token_type} | Fees:₹{fees}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_img = base64.b64encode(buffered.getvalue()).decode()
        
        return render_template('token_slip.html', token=new_token, hospital=hospital, opd=OPD.query.get(opd_id), qr_img=qr_img)
    
    return render_template('book_token.html', hospital=hospital, opds=opds)

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

@app.route('/complete_token/<int:token_id>')
def complete_token(token_id):
    token = Token.query.get_or_404(token_id)
    token.status = 'Done'
    db.session.commit()
    return redirect(url_for('doctor_panel'))

# ========== DATABASE CREATE ==========
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
