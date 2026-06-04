from flask import Flask, render_template, request, redirect, url_for, session
from database import db, Hospital, OPD, Token
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maharashtra123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db.init_app(app)

# Pehli baar database banega + 2 hospital add honge
with app.app_context():
    db.create_all()
    if Hospital.query.count() == 0:
        h1 = Hospital(name='JJ Hospital', city='Mumbai')
        h2 = Hospital(name='Sassoon Hospital', city='Pune')
        db.session.add_all([h1, h2])
        db.session.commit()
        
        opd_list = ['General Medicine','Surgery','Orthopedics','Pediatrics','Gynaecology','ENT','Eye','Skin','Dental','Psychiatry','TB-Chest','Radiology','Pathology','Cardiology','Dermatology']
        for h in [h1, h2]:
            for i, name in enumerate(opd_list, 1):
                db.session.add(OPD(hospital_id=h.id, opd_name=name, opd_code=f'OPD-{i}'))
        db.session.commit()

@app.route('/')
def home():
    hospitals = Hospital.query.all()
    return render_template('patient.html', hospitals=hospitals)

@app.route('/get_opd/<int:h_id>')
def get_opd(h_id):
    opds = OPD.query.filter_by(hospital_id=h_id).all()
    return {'opds': [{'id':o.id, 'name':o.opd_name, 'code':o.opd_code} for o in opds]}

@app.route('/generate_token', methods=['POST'])
def generate_token():
    h_id = request.form['hospital']
    o_id = request.form['opd']
    t_type = request.form['type']
    
    opd = OPD.query.get(o_id)
    fees = opd.emergency_fees if t_type=='Emergency' else opd.normal_fees
    
    last_token = Token.query.filter_by(opd_id=o_id, token_type=t_type).order_by(Token.token_no.desc()).first()
    new_no = 1 if not last_token else last_token.token_no + 1
    
    token = Token(hospital_id=h_id, opd_id=o_id, token_no=new_no, token_type=t_type, fees=fees)
    db.session.add(token)
    db.session.commit()
    
    hospital = Hospital.query.get(h_id)
    return render_template('token_slip.html', hospital=hospital, opd=opd, token=token, time=datetime.now())

@app.route('/doctor', methods=['GET','POST'])
def doctor():
    if request.method=='POST':
        if request.form['username']=='doctor' and request.form['password']=='1234':
            session['doctor']=True
            return redirect(url_for('dashboard'))
    return render_template('doctor_login.html')

@app.route('/dashboard')
def dashboard():
    if 'doctor' not in session: return redirect(url_for('doctor'))
    tokens = Token.query.filter_by(status='Waiting').order_by(Token.token_type, Token.token_no).all()
    return render_template('dashboard.html', tokens=tokens)

@app.route('/next/<int:t_id>')
def next_token(t_id):
    token = Token.query.get(t_id)
    token.status='Done'
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__=='__main__':
    app.run(debug=True)
