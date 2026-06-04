from flask import Flask, render_template, request, redirect, url_for
import random
import time

app = Flask(__name__)

# Sample data for demonstration
doctors = {
    'Dr. Smith': {'department': 'Cardiology', 'available': True},
    'Dr. Johnson': {'department': 'Neurology', 'available': True},
    'Dr. Williams': {'department': 'Pediatrics', 'available': True},
}

appointments = []

@app.route('/')
def index():
    return render_template('index.html', doctors=doctors)

@app.route('/book/<doctor_name>')
def book(doctor_name):
    if doctor_name in doctors and doctors[doctor_name]['available']:
        token = f"TKN-{random.randint(1000, 9999)}"
        appointments.append({'doctor': doctor_name, 'token': token, 'time': time.strftime('%H:%M:%S')})
        doctors[doctor_name]['available'] = False
        return f"Appointment booked with {doctor_name}. Your token: {token}"
    return "Doctor not available"

@app.route('/status')
def status():
    return render_template('status.html', appointments=appointments)

if __name__ == '__main__':
    app.run(debug=True)
