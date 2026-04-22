from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os 
import Gestor_Tareas

API_KEY = "f464ff8b2ff24730ab822bdd2da02bbd"
API_BASE = "https://api.spoonacular.com"

app = Flask(__name__) 
USUARIOS_REGISTRADOS = {
    'daniel@correo.com':{
        'password': "daniel",
        'nombre': "daniel",
        'correo': "daniel@correo.com",
        'edad': 16,
    }
}
app.config['SECRET_KEY'] = 'Ladrillos_que_ruedan_nueces_que_vuelan'

@app.route('/')
def index():
    return render_template('iniciar.html')

@app.route('/validaLogin', methods=['GET','POST'])
def validar():
    if request.method == "POST":
        correo = request.form.get("correo", '').strip()
        password = request.form.get("password", '')
        if not correo or not password:
            flash('Por favor ingresa email y contraseña', 'error')
            return render_template('iniciar.html')
        elif correo in USUARIOS_REGISTRADOS:
            usuario = USUARIOS_REGISTRADOS[correo]
            if usuario['password'] == password:
                session['logueado'] = True
                session['usuario'] = usuario['nombre']
                session['usuario_correo'] = correo
                flash(f'¡Bienvenido {usuario["nombre"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Contraseña incorrecta', 'error')
        else:
            flash('Usuario no encontrado', 'error')
        return render_template('iniciar.html')
    return redirect(url_for('iniciar'))

#evento click del inicio de sesion
#@app.route('/evento', methods=['GET','POST'])
#def index():
    gestor = Gestor_Tareas()
    if gestor:
        if gestor.obtener_usuario2("daniel@correo.com", "daniel"):
            return render_template("iniciar.html")
        else:
            1
    else:
        return render_template("iniciar.html")

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

#@app.route('/validaCorreo', methods=['GET','POST'])
#def C():
    if request.method == "POST":
        correo = request.form.get("correo", '').strip()
        if not correo:
            flash('Por favor ingresa el email', 'error')
            return render_template('recuperar.html')
        elif correo in USUARIOS_REGISTRADOS:
            usuario = USUARIOS_REGISTRADOS[correo]
            if usuario['correo'] == correo:
                session['logueado'] = True
                session['usuario_correo'] = correo
                flash(f'¡Bienvenido {usuario["nombre"]}!', 'success')
                return redirect(url_for('recuperar'))
        else:
            flash('Usuario no encontrado', 'error')
        return render_template('iniciar.html')
    return redirect(url_for('iniciar'))

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        error = None
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dia = request.form['dia']
        mes = request.form['mes']
        year = request.form['year']
        correo = request.form['correo']
        password = request.form['password']
        confirmPassword = request.form.get("confirmPassword")
        edad = 2026 - int(year)
        if password != confirmPassword:
            error = "Las contraseñas no coinciden"
        elif correo in USUARIOS_REGISTRADOS:
            error = "Este correo ya está registrado"
        if error is not None:
            flash(error, 'error')
            return render_template('registro.html')
        else:
            USUARIOS_REGISTRADOS[correo] = {
                'password': password,
                'nombre': f"{nombre} {apellido}",
                'dia': dia,
                'mes': mes,
                'year': year,
                'correo': correo,
                'edad': edad,
            }
            flash(f"Registro exitoso: {nombre}. Ahora puedes iniciar sesión.", 'success')
            return redirect(url_for('iniciar'))

@app.route("/iniciar")
def iniciar():
    if session.get('logueado'):
        return render_template('iniciar.html')
    return render_template('iniciar.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('iniciar'))

@app.route('/agregar_tarea', methods=['POST'])
def agregar_tarea():
    titulo = request.form['titulo']
    # Guardar en MongoDB proximamante
    flash('Tarea añadida correctamente', 'success')
    return redirect(url_for('tareas'))

@app.route('/editar_tarea/<tarea_id>', methods=['POST'])
def editar_tarea(tarea_id):
    titulo = request.form['titulo']
    estado = request.form['estado']
    fecha_fin = request.form.get('fecha_fin')
    # Actualizar en MongoDB proximamente
    flash('Tarea actualizada correctamente', 'success')
    return redirect(url_for('tareas'))

@app.route('/eliminar_tarea/<tarea_id>')
def eliminar_tarea(tarea_id):
    # Eliminar de MongoDB proximamante
    flash('Tarea eliminada correctamente', 'success')
    return redirect(url_for('tareas'))

# Ejemplo de uso
def ejemplo_uso():
    # Inicializar gestor
    gestor = Gestor_Tareas()
    
    # Crear usuario
    usuario_id = gestor.crear_usuario("Ana García", "ana@email.com")
    print(f"Usuario creado con ID: {usuario_id}")
    
    if usuario_id:
        # Crear tareas
        tarea1 = gestor.crear_tarea(
            usuario_id, 
            "Aprender MongoDB", 
            "Completar tutorial de PyMongo",
            datetime.now() + timedelta(days=3)
        )
        print(f"Tarea creada: {tarea1}")
        
        tarea2 = gestor.crear_tarea(
            usuario_id,
            "Hacer ejercicio",
            "Ir al gimnasio 3 veces esta semana"
        )
        
        # Agregar etiqueta
        gestor.agregar_etiqueta(tarea1, "programación")
        gestor.agregar_etiqueta(tarea1, "estudio")
        
        # Listar tareas
        tareas = gestor.obtener_tareas_usuario(usuario_id)
        print(f"\nTareas de {usuario_id}:")
        for t in tareas:
            print(f"  - {t['titulo']} [{t['estado']}]")
        
        # Actualizar estado
        gestor.actualizar_estado_tarea(tarea1, "en_progreso")
        
        # Estadísticas
        stats = gestor.estadisticas_usuario(usuario_id)
        print(f"\nEstadísticas: {stats}")
        
        # Tareas urgentes
        urgentes = gestor.tareas_urgentes(72)
        print(f"\nTareas urgentes próximos 3 días: {len(urgentes)}")
    
    # Cerrar conexión
    gestor.cerrar_conexion()

#if __name__ == "__main__":
#    ejemplo_uso()

if __name__ == '__main__':
    app.run(debug=True)