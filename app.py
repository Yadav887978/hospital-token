from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from database import db, Hospital, OPD, Token

app = Flask(__name__)
app.secret_key = 'maharashtra123'

# Render pe SQLite file nahi banti, isliye :memory: use kar rahe
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Tables banane + sample data
with app.app_context():
    db.create_all()
    if Hospital.query.count() == 0:
        h1 = Hospital(name='Sai Hospital', city='Pune')
        h2 = Hospital(name='City Care', city='Mumbai')
        db.session.add_all([h1, h2])
        db.session.commit()
        
        opd1 = OPD(hospital_id=1, opd_name='General', opd_code='GEN', normal_fees=50, emergency_fees=200)
        opd2 = OPD(hospital_id=1, opd_name='Dental', opd_code='DEN', normal_fees=100, emergency_fees=300)
        opd3 = OPD(hospital_id=2, opd_name='General', opd_code='GEN', normal_fees=60, emergency_fees=250)
        db.session.add_all([opd1, opd2, opd3])
        db.session.commit()

@app.route('/')
def index():
    hospitals = Hospital.query.all()
    return render_template('index.html', hospitals=hospitals)

@app.route('/hospital/<int:hospital_id>')
def hospital_opd(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    opds = OPD.query.filter_by(hospital_id=hospital_id).all()
    return render_template('hospital.html', hospital=hospital, opds=opds)

@app.route('/book/<int:opd_id>', methods=['GET', 'POST'])
def book_token(opd_id):
    opd = OPD.query.get_or_404(opd_id)
    hospital = Hospital.query.get(opd.hospital_id)
    
    if request.method == 'POST':
        token_type = request.form['token_type']
        fees = opd.emergency_fees if token_type == 'Emergency' else opd.normal_fees
        
        last_token = Token.query.filter_by(opd_id=opd_id).order_by(Token.token_no.desc()).first()
        token_no = 1 if not last_token else last_token.token_no + 1
        
        new_token = Token(
            hospital_id=hospital.id,
            opd_id=opd.id,
            token_no=token_no,
            token_type=token_type,
            fees=fees
        )
        db.session.add(new_token)
        db.session.commit()
        
        return render_template('token_slip.html', hospital=hospital, opd=opd, token=new_token, time=datetime.now())
    
    return render_template('book.html', opd=opd, hospital=hospital)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
