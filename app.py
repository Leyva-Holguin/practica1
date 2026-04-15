from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os 

API_KEY = "f464ff8b2ff24730ab822bdd2da02bbd"
API_BASE = "https://api.spoonacular.com"

app = Flask(__name__) 
USUARIOS_REGISTRADOS = {
    'daniel@correo.com':{
        'password': "daniel",
        'nombre': "daniel",
        'dia': 10,
        'mes': 10,
        'year': 2009,
        'genero': "hombre",
        'peso': 60,
        'altura': 165,
        'correo': "daniel@correo.com",
        'edad': 16,
    }
}
app.config['SECRET_KEY'] = 'Ladrillos_que_ruedan'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/tareas')
def tareas():
    return render_template('tareas.html')

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
        genero = request.form['genero']
        peso = request.form['peso']
        altura = request.form['altura']
        objetivo = request.form['objetivo']
        alergias = request.form.get('alergias', 'Nulo')
        intolerancias = request.form.get('intolerancias', 'Nulo')
        nivel_actividad = request.form['nivel_actividad']
        alimentos_no_gusta = request.form.get('alimentos_no_gusta', 'Nulo')
        correo = request.form['correo']
        password = request.form['password']
        dieta = request.form.get('dietas', 'Nulo')
        confirmPassword = request.form.get("confirmPassword")
        edad = 2025 - int(year)
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
                'genero': genero,
                'peso': peso,
                'altura': altura,
                'objetivo': objetivo,
                'nivel_actividad': nivel_actividad,
                'correo': correo,
                'edad': edad,
                'alergias': alergias,
                'intolerancias': intolerancias, 
                'alimentos_no_gusta': alimentos_no_gusta, 
                'dieta': dieta
            }
            flash(f"Registro exitoso: {nombre}. Ahora puedes iniciar sesión.", 'success')
            return redirect(url_for('iniciar'))
        
@app.route("/iniciar")
def iniciar():
    if session.get('logueado'):
        return render_template('index.html')
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

@app.route("/logout")
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))
class GestorTareas:
    def __init__(self, uri: str = 'mongodb://localhost:27017/'):
        """Inicializar conexión a MongoDB"""
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.cliente.admin.command('ping')
            self.db = self.cliente['gestor_tareas']
            self.tareas = self.db['tareas']
            self.usuarios = self.db['usuarios']
            
            # Crear índices necesarios
            self._crear_indices()
            print("✅ Conectado a MongoDB")
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB")
            raise
    
    def _crear_indices(self):
        """Crear índices para mejorar rendimiento"""
        self.usuarios.create_index("email", unique=True)
        self.tareas.create_index([("usuario_id", 1), ("fecha_creacion", -1)])
        self.tareas.create_index("estado")
    
    def crear_usuario(self, nombre: str, email: str) -> Optional[str]:
        """Crear un nuevo usuario"""
        try:
            resultado = self.usuarios.insert_one({
                "nombre": nombre,
                "email": email,
                "fecha_registro": datetime.now(),
                "activo": True
            })
            return str(resultado.inserted_id)
        except DuplicateKeyError:
            print(f"❌ Error: El email {email} ya está registrado")
            return None
    
    def obtener_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Obtener usuario por ID"""
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(usuario_id)})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def crear_tarea(self, usuario_id: str, titulo: str, descripcion: str = "", 
        fecha_limite: Optional[datetime] = None) -> Optional[str]:
        """Crear una nueva tarea para un usuario"""
        # Verificar que el usuario existe
        if not self.obtener_usuario(usuario_id):
            print(f"❌ Error: Usuario {usuario_id} no existe")
            return None
        
        tarea = {
            "usuario_id": ObjectId(usuario_id),
            "titulo": titulo,
            "descripcion": descripcion,
            "estado": "pendiente",
            "fecha_creacion": datetime.now(),
            "fecha_limite": fecha_limite or datetime.now() + timedelta(days=7),
            "completada": False,
            "etiquetas": []
        }
        
        resultado = self.tareas.insert_one(tarea)
        return str(resultado.inserted_id)
    
    def obtener_tareas_usuario(self, usuario_id: str, estado: Optional[str] = None) -> List[Dict]:
        """Obtener tareas de un usuario, opcionalmente filtradas por estado"""
        filtro = {"usuario_id": ObjectId(usuario_id)}
        if estado:
            filtro["estado"] = estado
        
        tareas = self.tareas.find(filtro).sort("fecha_creacion", -1)
        resultado = []
        for t in tareas:
            t['_id'] = str(t['_id'])
            t['usuario_id'] = str(t['usuario_id'])
            resultado.append(t)
        return resultado
    
    def actualizar_estado_tarea(self, tarea_id: str, nuevo_estado: str) -> bool:
        """Actualizar el estado de una tarea"""
        estados_validos = ["pendiente", "en_progreso", "completada", "cancelada"]
        if nuevo_estado not in estados_validos:
            print(f"❌ Error: Estado '{nuevo_estado}' no válido")
            return False
        
        resultado = self.tareas.update_one(
            {"_id": ObjectId(tarea_id)},
            {
                "$set": {
                    "estado": nuevo_estado,
                    "completada": nuevo_estado == "completada",
                    "fecha_actualizacion": datetime.now()
                }
            }
        )
        return resultado.modified_count > 0
    
    def agregar_etiqueta(self, tarea_id: str, etiqueta: str) -> bool:
        """Agregar etiqueta a una tarea"""
        resultado = self.tareas.update_one(
            {"_id": ObjectId(tarea_id)},
            {"$addToSet": {"etiquetas": etiqueta}}
        )
        return resultado.modified_count > 0
    
    def eliminar_tarea(self, tarea_id: str) -> bool:
        """Eliminar una tarea"""
        resultado = self.tareas.delete_one({"_id": ObjectId(tarea_id)})
        return resultado.deleted_count > 0
    
    def estadisticas_usuario(self, usuario_id: str) -> Dict:
        """Obtener estadísticas de tareas de un usuario"""
        pipeline = [
            {"$match": {"usuario_id": ObjectId(usuario_id)}},
            {"$group": {
                "_id": "$estado",
                "cantidad": {"$sum": 1},
                "fecha_ultima": {"$max": "$fecha_creacion"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        resultados = list(self.tareas.aggregate(pipeline))
        
        # Formatear resultados
        estadisticas = {
            "total": 0,
            "por_estado": {},
            "ultima_actividad": None
        }
        
        for r in resultados:
            estado = r['_id']
            cantidad = r['cantidad']
            estadisticas["por_estado"][estado] = cantidad
            estadisticas["total"] += cantidad
            
            if not estadisticas["ultima_actividad"] or r['fecha_ultima'] > estadisticas["ultima_actividad"]:
                estadisticas["ultima_actividad"] = r['fecha_ultima']
        
        return estadisticas
    
    def buscar_tareas(self, texto: str) -> List[Dict]:
        """Buscar tareas por texto en título o descripción"""
        # Requiere índice de texto en 'titulo' y 'descripcion'
        tareas = self.tareas.find({
            "$text": {"$search": texto}
        }).sort({"score": {"$meta": "textScore"}})
        
        resultado = []
        for t in tareas:
            t['_id'] = str(t['_id'])
            t['usuario_id'] = str(t['usuario_id'])
            resultado.append(t)
        return resultado
    
    def tareas_urgentes(self, horas: int = 24) -> List[Dict]:
        """Encontrar tareas que vencen en las próximas N horas"""
        ahora = datetime.now()
        limite = ahora + timedelta(hours=horas)
        
        tareas = self.tareas.find({
            "estado": {"$ne": "completada"},
            "fecha_limite": {"$gte": ahora, "$lte": limite}
        }).sort("fecha_limite", 1)
        
        resultado = []
        for t in tareas:
            t['_id'] = str(t['_id'])
            t['usuario_id'] = str(t['usuario_id'])
            resultado.append(t)
        return resultado
    
    def cerrar_conexion(self):
        """Cerrar conexión a MongoDB"""
        if self.cliente:
            self.cliente.close()
            print("🔌 Conexión cerrada")

# Ejemplo de uso
def ejemplo_uso():
    # Inicializar gestor
    gestor = GestorTareas()
    
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