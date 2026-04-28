from flask import Flask, request, render_template_string, redirect, session, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
# CAMBIO DE SEGURIDAD: Clave genérica para la versión pública en GitHub
app.secret_key = "clave_secreta_para_despliegue_publico"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cdi_zamora.db")

def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes
        (cedula TEXT PRIMARY KEY, nombre TEXT, edad INTEGER,
         sector TEXT, diagnostico TEXT, doctor TEXT, fecha TEXT)''')
    conn.commit()
    return conn

PLANTILLA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CDI Zamora | Sistema Médico</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0f172a; --accent: #38bdf8; --bg: #f1f5f9; }
        body { background: var(--bg); font-family: 'Inter', sans-serif; color: var(--primary); }
        .glass { background: rgba(255,255,255,0.8); backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); }
        .btn-accent { background: var(--accent); color: white; border-radius: 12px; font-weight: 700; transition: 0.3s; }
        .btn-accent:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(56,189,248,0.3); }
        .stat-card { background: white; border-radius: 15px; padding: 20px; border-left: 5px solid var(--accent); }
    </style>
</head>
<body class="p-3 p-md-5">
    <div class="container max-w-5xl">
        {% if seccion == 'login' %}
        <div class="row justify-content-center">
            <div class="col-md-5 glass p-5 text-center shadow-lg">
                <h1 class="fw-800 mb-4">CDI ZAMORA</h1>
                <form action="/login" method="POST">
                    <input type="text" name="user" class="form-control mb-3" placeholder="Usuario" required>
                    <input type="password" name="pass" class="form-control mb-3" placeholder="Contraseña" required>
                    <button class="btn btn-accent w-100 py-3">ENTRAR AL SISTEMA</button>
                </form>
            </div>
        </div>
        {% else %}
        <div class="d-flex justify-content-between align-items-center mb-5">
            <div>
                <h2 class="fw-800 m-0">PANEL MÉDICO</h2>
                <p class="text-muted">Gestión de pacientes de la comunidad</p>
            </div>
            <a href="/logout" class="btn btn-outline-danger">Cerrar Sesión</a>
        </div>

        <div class="row g-4 mb-5">
            <div class="col-md-4"><div class="stat-card shadow-sm"><h5>Niños</h5><h2 class="fw-800 text-primary">{{ censo_vivo.ninos }}</h2></div></div>
            <div class="col-md-4"><div class="stat-card shadow-sm"><h5>Adultos</h5><h2 class="fw-800 text-primary">{{ censo_vivo.adultos }}</h2></div></div>
            <div class="col-md-4"><div class="stat-card shadow-sm"><h5>Mayores</h5><h2 class="fw-800 text-primary">{{ censo_vivo.mayores }}</h2></div></div>
        </div>

        <div class="glass p-4 shadow-sm mb-5">
            <h4 class="fw-700 mb-4">{{ 'EDITAR REGISTRO' if edit else 'REGISTRAR PACIENTE' }}</h4>
            <form action="/guardar" method="POST" class="row g-3">
                <div class="col-md-3"><input type="text" name="cedula" class="form-control" placeholder="Cédula" value="{{ edit[0] if edit else '' }}" required></div>
                <div class="col-md-3"><input type="text" name="nombre" class="form-control" placeholder="Nombre Completo" value="{{ edit[1] if edit else '' }}" required></div>
                <div class="col-md-2"><input type="number" name="edad" class="form-control" placeholder="Edad" value="{{ edit[2] if edit else '' }}" required></div>
                <div class="col-md-4"><input type="text" name="sector" class="form-control" placeholder="Sector / Calle" value="{{ edit[3] if edit else '' }}" required></div>
                <div class="col-md-6"><input type="text" name="diagnostico" class="form-control" placeholder="Diagnóstico" value="{{ edit[4] if edit else '' }}" required></div>
                <div class="col-md-4"><input type="text" name="doctor" class="form-control" placeholder="Doctor Tratante" value="{{ edit[5] if edit else '' }}" required></div>
                <div class="col-md-2"><button class="btn btn-accent w-100">{{ 'ACTUALIZAR' if edit else 'GUARDAR' }}</button></div>
            </form>
        </div>

        <div class="glass p-4 shadow-sm">
            <div class="d-flex justify-content-between mb-4">
                <h4 class="fw-700">LISTADO RECIENTE</h4>
                <form action="/dashboard" method="GET" class="d-flex">
                    <input type="text" name="q" class="form-control me-2" placeholder="Buscar por cédula..." value="{{ busca }}">
                    <button class="btn btn-dark">Buscar</button>
                </form>
            </div>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light"><tr><th>Cédula</th><th>Nombre</th><th>Edad</th><th>Sector</th><th>Diagnóstico</th><th>Acciones</th></tr></thead>
                    <tbody>
                        {% for p in pacientes %}
                        <tr>
                            <td class="fw-700 text-primary">{{ p[0] }}</td>
                            <td>{{ p[1] }}</td>
                            <td><span class="badge bg-light text-dark border">{{ p[2] }} años</span></td>
                            <td>{{ p[3] }}</td>
                            <td>{{ p[4] }}</td>
                            <td>
                                <a href="/editar/{{ p[0] }}" class="btn btn-sm btn-warning">Editar</a>
                                <a href="/eliminar/{{ p[0] }}" class="btn btn-sm btn-danger" onclick="return confirm('¿Eliminar registro?')">X</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def inicio():
    if session.get('auth'): return redirect(url_for('dashboard'))
    return render_template_string(PLANTILLA, seccion='login')

@app.route('/login', methods=['POST'])
def login():
    # CAMBIO DE SEGURIDAD: Credenciales genéricas para GitHub
    if request.form['user'] == "admin" and request.form['pass'] == "admin123":
        session['auth'] = True
        return redirect(url_for('dashboard'))
    return redirect(url_for('inicio'))

@app.route('/logout')
def logout():
    session.pop('auth', None)
    return redirect(url_for('inicio'))

@app.route('/dashboard')
def dashboard():
    if not session.get('auth'): return redirect('/')
    busca = request.args.get('q', '')
    conn = conectar_db(); cursor = conn.cursor()
    
    if busca:
        cursor.execute("SELECT * FROM pacientes WHERE cedula LIKE ? ORDER BY fecha DESC", ('%'+busca+'%',))
    else:
        cursor.execute("SELECT * FROM pacientes ORDER BY fecha DESC")
    
    p_todos = cursor.fetchall()
    
    # Censo dinámico
    v_ninos = sum(1 for p in p_todos if p[2] <= 12)
    v_adultos = sum(1 for p in p_todos if 12 < p[2] < 60)
    v_mayores = sum(1 for p in p_todos if p[2] >= 60)
    
    conn.close()
    return render_template_string(PLANTILLA, seccion='dash', pacientes=p_todos, busca=busca, edit=None,
                                 censo_vivo={'ninos': v_ninos, 'adultos': v_adultos, 'mayores': v_mayores})

@app.route('/guardar', methods=['POST'])
def guardar():
    if not session.get('auth'): return redirect('/')
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    datos = (request.form['cedula'], request.form['nombre'], int(request.form['edad']),
             request.form['sector'], request.form['diagnostico'], request.form['doctor'], fecha)
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO pacientes VALUES (?,?,?,?,?,?,?)", datos)
    conn.commit(); conn.close()
    return redirect(url_for('dashboard'))

@app.route('/editar/<cedula>')
def editar(cedula):
    if not session.get('auth'): return redirect('/')
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE cedula=?", (cedula,))
    p_edit = cursor.fetchone()
    cursor.execute("SELECT * FROM pacientes ORDER BY fecha DESC")
    p_todos = cursor.fetchall()

    v_ninos = sum(1 for pers in p_todos if pers[2] <= 12)
    v_adultos = sum(1 for pers in p_todos if 12 < pers[2] < 60)
    v_mayores = sum(1 for pers in p_todos if pers[2] >= 60)

    conn.close()
    return render_template_string(PLANTILLA, seccion='dash', pacientes=p_todos, busca='', edit=p_edit,
                                 censo_vivo={'ninos': v_ninos, 'adultos': v_adultos, 'mayores': v_mayores})

@app.route('/eliminar/<cedula>')
def eliminar(cedula):
    if not session.get('auth'): return redirect('/')
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("DELETE FROM pacientes WHERE cedula=?", (cedula,))
    conn.commit(); conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
