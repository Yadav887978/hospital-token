from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'opdmitra_secret_2026_change_this'

def init_db():
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tokens
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  hospital TEXT,
                  opd TEXT,
                  disease TEXT,
                  patient_name TEXT,
                  address TEXT,
                  hospital_fee INTEGER,
                  service_fee INTEGER,
                  amount INTEGER,
                  status TEXT DEFAULT 'Waiting',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  called_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

DISEASES = ["Fever / Sardi Khasi", "Heart / BP", "Skin / Allergy", "Ortho / Haddi", "Gynecology"]

# ============== 36 HOSPITAL + OPD MAPPING ==============
# TODO: Tu hospital se asli OPD number confirm karke yaha bhar de
OPD_MAP = {
    # Mumbai
    "Sir J.J. Hospital Mumbai": {
        "Fever / Sardi Khasi": "OPD 15 - General Medicine",
        "Heart / BP": "OPD 22 - Cardiology",
        "Skin / Allergy": "OPD 8 - Dermatology",
        "Ortho / Haddi": "OPD 31 - Orthopedics",
        "Gynecology": "OPD 44 - Gynecology"
    },
    "KEM Hospital Mumbai": {
        "Fever / Sardi Khasi": "OPD 12 - General Medicine",
        "Heart / BP": "OPD 18 - Cardiology",
        "Skin / Allergy": "OPD 6 - Dermatology",
        "Ortho / Haddi": "OPD 27 - Orthopedics",
        "Gynecology": "OPD 40 - Gynecology"
    },
    "Lokmanya Tilak Municipal Hospital (Sion Hospital)": {
        "Fever / Sardi Khasi": "OPD 10 - General Medicine",
        "Heart / BP": "OPD 16 - Cardiology",
        "Skin / Allergy": "OPD 5 - Dermatology",
        "Ortho / Haddi": "OPD 24 - Orthopedics",
        "Gynecology": "OPD 35 - Gynecology"
    },
    "GT Hospital Mumbai": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "St George Hospital Mumbai": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    # Pune
    "Sassoon General Hospital Pune": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Naidu Hospital Pune": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "BJ Government Medical College Pune": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    # Nagpur
    "Government Medical College and Hospital Nagpur (GMCH)": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "Indira Gandhi Government Medical College Nagpur": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    # Aurangabad
    "Government Medical College and Hospital Aurangabad": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    # Nashik
    "District Civil Hospital Nashik": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Dr. Vasantrao Pawar Medical College Hospital Nashik": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    # Solapur
    "District Civil Hospital Solapur": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    # Amravati
    "District Civil Hospital Amravati": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    # Kolhapur
    "District Civil Hospital Kolhapur": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    # Jalgaon
    "District Civil Hospital Jalgaon": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    # Thane
    "Thane Civil Hospital": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Vashi Civil Hospital": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "NMMC Hospital Nerul": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Kalwa Hospital Thane": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    # Baaki 15 hospital - tu naam aur OPD bhar de
    "Shankarrao Chavan Govt Hospital": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "Cooper Hospital": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Bhabha Hospital": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "V.N. Desai Hospital": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "C.S.M. Hospital": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Central Hospital Ulhasnagar": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "Kasturba Hospital": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    "Bharat Ratna Dr. Babasaheb Ambedekar Hospital": {
        "Fever / Sardi Khasi": "OPD 1 - General Medicine",
        "Heart / BP": "OPD 2 - Cardiology",
        "Skin / Allergy": "OPD 3 - Dermatology",
        "Ortho / Haddi": "OPD 4 - Orthopedics",
        "Gynecology": "OPD 5 - Gynecology"
    },
    "Yashwantrao Chavan Memorial Hospital": {
        "Fever / Sardi Khasi": "OPD 101 - General Medicine",
        "Heart / BP": "OPD 201 - Cardiology",
        "Skin / Allergy": "OPD 301 - Dermatology",
        "Ortho / Haddi": "OPD 401 - Orthopedics",
        "Gynecology": "OPD 501 - Gynecology"
    },
    # 9 aur hospital yaha add kar sakte ho same format me
}

HOSPITALS = list(OPD_MAP.keys())

# ============== DOCTOR LOGIN PASSWORDS ==============
# TODO: Har OPD ka asli password hospital se leke yaha bhar de
OPD_PASSWORDS = {
    # J.J. Hospital
    "OPD 15 - General Medicine": "jj15",
    "OPD 22 - Cardiology": "jj22",
    "OPD 8 - Dermatology": "jj8",
    "OPD 31 - Orthopedics": "jj31",
    "OPD 44 - Gynecology": "jj44",
    # KEM Hospital
    "OPD 12 - General Medicine": "kem12",
    "OPD 18 - Cardiology": "kem18",
    "OPD 6 - Dermatology": "kem6",
    "OPD 27 - Orthopedics": "kem27",
    "OPD 40 - Gynecology": "kem40",
    # Sion Hospital
    "OPD 10 - General Medicine": "sion10",
    "OPD 16 - Cardiology": "sion16",
    "OPD 5 - Dermatology": "sion5",
    "OPD 24 - Orthopedics": "sion24",
    "OPD 35 - Gynecology": "sion35",
    # Baaki sab hospital ke OPD password yaha add kar de
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        hospital = request.form['hospital']
        disease = request.form['disease']
        opd = OPD_MAP[hospital][disease] # Auto OPD select
        patient_name = request.form['patient_name']
        address = request.form['address']
        hospital_fee = 20
        service_fee = 10
        amount = 30

        conn = sqlite3.connect('tokens.db')
        c = conn.cursor()
        c.execute("INSERT INTO tokens (hospital, opd, disease, patient_name, address, hospital_fee, service_fee, amount) VALUES (?,?,?,?,?,?,?,?)",
                  (hospital, opd, disease, patient_name, address, hospital_fee, service_fee, amount))
        token_id = c.lastrowid
        conn.commit()

        c.execute("SELECT * FROM tokens WHERE id=?", (token_id,))
        patient = c.fetchone()
        conn.close()

        return render_template('index.html', patient=patient, hospitals=HOSPITALS, diseases=DISEASES, opd_map=OPD_MAP)

    return render_template('index.html', patient=None, hospitals=HOSPITALS, diseases=DISEASES, opd_map=OPD_MAP)

@app.route('/checkin/<int:token_id>', methods=['POST'])
def checkin(token_id):
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute("UPDATE tokens SET status='Completed' WHERE id=?", (token_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        opd = request.form['opd']
        password = request.form['password']

        if opd in OPD_PASSWORDS and OPD_PASSWORDS[opd] == password:
            session['doctor_opd'] = opd
            return redirect('/doctor/panel')
        else:
            flash('Galat OPD ya Password')

    options = ''.join([f'<option value="{opd}">{opd}</option>' for opd in OPD_PASSWORDS.keys()])
    return f'''
    <html><head><title>Doctor Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{{font-family:Arial;background:#f0f2f5;padding:20px}}.box{{max-width:400px;margin:100px auto;background:white;padding:30px;border-radius:12px}}h2{{text-align:center;color:#007bff}}input,select{{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;font-size:16px}}button{{width:100%;padding:14px;background:#28a745;color:white;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}}.error{{color:red;margin-top:10px}}</style>
    </head><body>
    <div class="box"><h2>🏥 Doctor Login</h2>
    <form method="post">
    <label>OPD Select Kare:</label>
    <select name="opd" required><option value="">-- OPD Chuno --</option>{options}</select>
    <label>Password:</label><input type="password" name="password" placeholder="OPD ka password" required>
    <button type="submit">Login Kare</button></form>
    <div style="margin-top:15px;font-size:12px;color:#666">Note: Password OPD incharge se le. Ex: OPD 15 ka password = jj15</div>
    </div></body></html>'''

@app.route('/doctor/panel')
def doctor_panel():
    if 'doctor_opd' not in session:
        return redirect('/doctor/login')

    opd = session['doctor_opd']
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()

    c.execute("SELECT * FROM tokens WHERE opd=? AND status='Called' ORDER BY called_at DESC LIMIT 1", (opd,))
    current = c.fetchone()

    c.execute("SELECT * FROM tokens WHERE opd=? AND status='Waiting' ORDER BY id ASC LIMIT 10", (opd,))
    waiting = c.fetchall()

    c.execute("SELECT * FROM tokens WHERE opd=? AND status='Missed' ORDER BY called_at ASC", (opd,))
    missed = c.fetchall()

    conn.close()
    return render_template('doctor.html', opd=opd, current=current, waiting=waiting, missed=missed, missed_count=len(missed))

@app.route('/doctor/next', methods=['POST'])
def next_patient():
    if 'doctor_opd' not in session:
        return redirect('/doctor/login')

    opd = session['doctor_opd']
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()

    c.execute("UPDATE tokens SET status='Missed', called_at=? WHERE opd=? AND status='Called'",
              (datetime.now(), opd))

    c.execute("SELECT id FROM tokens WHERE opd=? AND status='Waiting' ORDER BY id ASC LIMIT 1", (opd,))
    next_token = c.fetchone()

    if next_token:
        c.execute("UPDATE tokens SET status='Called', called_at=? WHERE id=?",
                  (datetime.now(), next_token[0]))

    conn.commit()
    conn.close()
    return redirect('/doctor/panel')

@app.route('/doctor/call_missed', methods=['POST'])
def call_missed():
    if 'doctor_opd' not in session:
        return redirect('/doctor/login')

    opd = session['doctor_opd']
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()

    c.execute("SELECT id FROM tokens WHERE opd=? AND status='Missed' ORDER BY called_at ASC LIMIT 1", (opd,))
    missed_token = c.fetchone()

    if missed_token:
        c.execute("UPDATE tokens SET status='Called', called_at=? WHERE id=?",
                  (datetime.now(), missed_token[0]))

    conn.commit()
    conn.close()
    return redirect('/doctor/panel')

@app.route('/doctor/logout')
def doctor_logout():
    session.pop('doctor_opd', None)
    return redirect('/doctor/login')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
