from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-super-secreta-render')

# ==================== CONFIGURACIÓN POSTGRESQL (Render) ====================
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada")
    # Render usa URLs que empiezan con postgres://
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Crear tabla si no existe
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Inicializar la base de datos al arrancar
with app.app_context():
    init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM contacts ORDER BY nombre')
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO contacts (nombre, telefono, email) VALUES (%s, %s, %s)',
                    (nombre, telefono, email))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✅ Contacto agregado correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit(contact_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        
        cur.execute('UPDATE contacts SET nombre=%s, telefono=%s, email=%s WHERE id=%s',
                    (nombre, telefono, email, contact_id))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✏️ Contacto actualizado correctamente', 'success')
        return redirect(url_for('index'))
    
    cur.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:contact_id>')
def delete(contact_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM contacts WHERE id = %s', (contact_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('🗑️ Contacto eliminado correctamente', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)   # En Render debug debe estar en False