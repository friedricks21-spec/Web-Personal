# EDC Monitoring Web App (Professional Version)

from flask import Flask, render_template_string, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database (SQLite for simplicity, can upgrade to MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edc.db'
db = SQLAlchemy(app)

# ===================== DATABASE MODEL =====================
class Monitoring(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    lan = db.Column(db.String(50))
    mandiri = db.Column(db.String(50))
    mti = db.Column(db.String(50))
    bca = db.Column(db.String(50))
    idm = db.Column(db.String(50))
    suhu = db.Column(db.String(50))
    ups = db.Column(db.String(50))
    progress = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===================== LOGIN DATA =====================
VALID_NIK = "2015259593"
VALID_PASS = "210298"
VALID_USER = "Jondry Friedriks"

# ===================== LOGIN PAGE =====================
login_page = """
<!DOCTYPE html>
<html>
<head>
<title>Login EDC</title>
<style>
body { font-family: Arial; background:#f4f4f4; text-align:center; }
.box { margin:100px auto; width:320px; padding:20px; background:white; border-radius:12px; box-shadow:0 0 10px rgba(0,0,0,0.2);} 
input { width:90%; padding:10px; margin:10px 0; }
button { background:red; color:white; padding:10px 20px; border:none; }
</style>
</head>
<body>
<div class="box">
<img src="https://upload.wikimedia.org/wikipedia/commons/9/9e/Indomaret_logo.png" width="150">
<h3>Monitoring EDC</h3>
<form method="POST">
<input name="nik" placeholder="NIK" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>
<p style="color:red;">{{error}}</p>
</div>
</body>
</html>
"""

# ===================== DASHBOARD =====================
dashboard_page = """
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<style>
body { font-family: Arial; background:#eef; }
table { width:95%; margin:20px auto; border-collapse: collapse; }
th, td { padding:10px; border:1px solid #333; text-align:center; }
th { background:#333; color:white; }
form { text-align:center; }
input { margin:5px; padding:8px; }
button { padding:8px 15px; }
.topbar { text-align:center; margin-top:20px; }
</style>
</head>
<body>
<div class="topbar">
<h2>Dashboard Monitoring EDC</h2>
<p>User: {{user}}</p>
<a href="/export">Download Excel</a> |
<a href="/logout">Logout</a>
</div>

<form method="POST">
<input name="lan" placeholder="LAN Speed" required>
<input name="mandiri" placeholder="EDC Mandiri" required>
<input name="mti" placeholder="EDC MTI" required>
<input name="bca" placeholder="EDC BCA" required>
<input name="idm" placeholder="IDM Listener" required>
<input name="suhu" placeholder="Suhu" required>
<input name="ups" placeholder="UPS" required>
<input name="progress" placeholder="Progress" required>
<button>Tambah</button>
</form>

<table>
<tr>
<th>User</th>
<th>LAN</th>
<th>Mandiri</th>
<th>MTI</th>
<th>BCA</th>
<th>IDM</th>
<th>Suhu</th>
<th>UPS</th>
<th>Progress</th>
<th>Waktu</th>
</tr>
{% for d in data %}
<tr>
<td>{{d.user}}</td>
<td>{{d.lan}}</td>
<td>{{d.mandiri}}</td>
<td>{{d.mti}}</td>
<td>{{d.bca}}</td>
<td>{{d.idm}}</td>
<td>{{d.suhu}}</td>
<td>{{d.ups}}</td>
<td>{{d.progress}}</td>
<td>{{d.created_at}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

# ===================== ROUTES =====================
@app.route('/', methods=['GET','POST'])
def login():
    error = ""
    if request.method == 'POST':
        if request.form['nik'] == VALID_NIK and request.form['password'] == VALID_PASS:
            session['user'] = VALID_USER
            return redirect('/dashboard')
        else:
            error = "Login gagal"
    return render_template_string(login_page, error=error)

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        data = Monitoring(
            user=session['user'],
            lan=request.form['lan'],
            mandiri=request.form['mandiri'],
            mti=request.form['mti'],
            bca=request.form['bca'],
            idm=request.form['idm'],
            suhu=request.form['suhu'],
            ups=request.form['ups'],
            progress=request.form['progress']
        )
        db.session.add(data)
        db.session.commit()

    data = Monitoring.query.order_by(Monitoring.created_at.desc()).all()
    return render_template_string(dashboard_page, user=session['user'], data=data)

@app.route('/export')
def export():
    data = Monitoring.query.all()
    df = pd.DataFrame([{
        'User': d.user,
        'LAN': d.lan,
        'Mandiri': d.mandiri,
        'MTI': d.mti,
        'BCA': d.bca,
        'IDM': d.idm,
        'Suhu': d.suhu,
        'UPS': d.ups,
        'Progress': d.progress,
        'Waktu': d.created_at
    } for d in data])

    file = 'report.xlsx'
    df.to_excel(file, index=False)
    return send_file(file, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ===================== RUN =====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
