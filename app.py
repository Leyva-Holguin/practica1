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
app.config['SECRET_KEY'] = 'la_primera_es_la_primera'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/educacion')
def educacion():
    return render_template('educacion.html')

@app.route('/modulo3')
def modulo3():
    return render_template('modulo3.html')

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

@app.route('/imc')
def imc():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    return render_template('imc.html', datos_usuario=datos_usuario)

@app.route('/tmb')
def tmb():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    return render_template('tmb.html', datos_usuario=datos_usuario)

@app.route('/gct')
def cgt():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    return render_template('gct.html', datos_usuario=datos_usuario)

@app.route('/icp')
def icp():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    return render_template('icp.html', datos_usuario=datos_usuario)

@app.route('/macro')
def macro():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    return render_template('macro.html', datos_usuario=datos_usuario)

@app.route('/analizador')
def analizador():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    return render_template('analizador.html', datos_usuario=datos_usuario)

@app.route('/cal_imc', methods=['POST'])
def cal_imc():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        peso = float(request.form.get('peso_imc'))
        altura = float(request.form.get('altura_imc')) / 100
        imc = peso / (altura ** 2)
        if imc < 18.5:
            clasificacion = "Bajo peso"
        elif imc < 25:
            clasificacion = "Peso normal"
        elif imc < 30:
            clasificacion = "Sobrepeso"
        else:
            clasificacion = "Obesidad"
        resultado = f'Tu IMC es: {imc:.1f} - {clasificacion}'
    except (ValueError, ZeroDivisionError):
        resultado = 'Por favor ingresa valores numéricos válidos'
    return render_template('imc.html', datos_usuario=datos_usuario, resultado_imc=resultado)

@app.route('/cal_tmb', methods=['POST'])
def cal_tmb():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        edad = int(request.form.get('edad_tmb'))
        peso = float(request.form.get('peso_tmb'))
        altura = float(request.form.get('altura_tmb'))
        genero = request.form.get('genero_tmb')
        if genero == 'hombre':
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161
        resultado = f'Tu Tasa Metabólica Basal es: {tmb:.0f} calorías/día'
    except ValueError:
        resultado = 'Por favor ingresa valores numéricos válidos'
    return render_template('tmb.html', datos_usuario=datos_usuario, resultado_tmb=resultado)

@app.route('/cal_gct', methods=['POST'])
def cal_gct():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        tmb = float(request.form.get('tmb_gct'))
        actividad = request.form.get('actividad_gct')
        factores = {
            'sedentario': 1.2,
            'ligero': 1.375,
            'moderado': 1.55,
            'activo': 1.725,
            'atleta': 1.9
        }
        gct = tmb * factores.get(actividad, 1.2)
        resultado = f'Tu Gasto Calórico Total es: {gct:.0f} calorías/día'
    except ValueError:
        resultado = 'Por favor ingresa valores numéricos válidos'
    return render_template('gct.html', datos_usuario=datos_usuario, resultado_gct=resultado)

@app.route('/cal_peso_ideal', methods=['POST'])
def cal_peso_ideal():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        altura = float(request.form.get('altura_pci'))
        genero = request.form.get('genero_pci')
        complexion = request.form.get('complexion_pci')
        if genero == 'hombre':
            peso_base = 50 + 0.91 * (altura - 152.4)
        else:
            peso_base = 45.5 + 0.91 * (altura - 152.4)
        peso_min = peso_base * 0.9
        peso_max = peso_base * 1.1
        resultado = f'Tu peso ideal aproximado: {peso_base:.1f} kg<br> Rango saludable: {peso_min:.1f} - {peso_max:.1f} kg'
    except ValueError:
        resultado = 'Por favor ingresa valores numéricos válidos'
    return render_template('icp.html', datos_usuario=datos_usuario, resultado_peso_ideal=resultado)

@app.route('/cal_macronutrientes', methods=['POST'])
def cal_macronutrientes():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        calorias = float(request.form.get('calorias_macro'))
        objetivo = request.form.get('objetivo_macro')
        actividad = request.form.get('actividad_macro')
        if objetivo == 'perder':
            proteina = (calorias * 0.4) / 4
            carbohidratos = (calorias * 0.3) / 4
            grasa = (calorias * 0.3) / 9
        elif objetivo == 'mantener':
            proteina = (calorias * 0.3) / 4
            carbohidratos = (calorias * 0.4) / 4
            grasa = (calorias * 0.3) / 9
        else:
            proteina = (calorias * 0.35) / 4
            carbohidratos = (calorias * 0.45) / 4
            grasa = (calorias * 0.2) / 9
        resultado = f'Macronutrientes diarios:<br>• Proteína: {proteina:.0f}g<br>• Carbohidratos: {carbohidratos:.0f}g<br>• Grasas: {grasa:.0f}g'
    except ValueError:
        resultado = 'Por favor ingresa valores numéricos válidos'
    
    return render_template('macro.html', datos_usuario=datos_usuario, resultado_macronutrientes=resultado)

@app.route('/analizar_receta', methods=['POST'])
def analizar_receta():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        titulo = request.form.get('titulo_receta', '').strip()
        texto_receta = request.form.get('texto_receta', '').strip()
        if not titulo or not texto_receta:
            resultado = 'Por favor ingresa tanto el título como los ingredientes'
        else:
            url_analisis = f"{API_BASE}/recipes/parseIngredients"
            params_url = {
                'apiKey': API_KEY, 
            }
            data_post = {
                'ingredientList': texto_receta, 
                'servings': 1,
                'includeNutrition': True
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response_receta = requests.post(
                url_analisis, 
                params=params_url,
                data=data_post, 
                headers=headers
            )
            
            if response_receta.status_code == 200:
                analisis_ingredientes_raw = response_receta.json()
                analisis_ingredientes = []
                total_calorias = 0
                total_proteinas = 0
                total_carbohidratos = 0
                total_grasas = 0
                total_fibra = 0
                total_azucar = 0
                contador_ingredientes = 1
                for ingrediente_info in analisis_ingredientes_raw:
                    nombre_original = ingrediente_info.get('original', 'Ingrediente no especificado')
                    nutricion = ingrediente_info.get('nutrition', {})
                    nutrientes = nutricion.get('nutrients', [])
                    info_ingrediente = {
                        'numero': contador_ingredientes,
                        'nombre': nombre_original,
                        'calorias': 0,
                        'proteinas': 0,
                        'carbohidratos': 0,
                        'grasas': 0,
                        'fibra': 0,
                        'azucar': 0,
                        'error': False
                    }
                    for nutriente in nutrientes:
                        name = nutriente.get('name', '').lower()
                        amount = nutriente.get('amount', 0)
                        if 'calorie' in name:
                            info_ingrediente['calorias'] = amount
                            total_calorias += amount
                        elif 'protein' in name:
                            info_ingrediente['proteinas'] = amount
                            total_proteinas += amount
                        elif 'carbohydrate' in name:
                            info_ingrediente['carbohidratos'] = amount
                            total_carbohidratos += amount
                        elif 'fat' in name and 'saturated' not in name: 
                            info_ingrediente['grasas'] = amount
                            total_grasas += amount
                        elif 'fiber' in name:
                            info_ingrediente['fibra'] = amount
                            total_fibra += amount
                        elif 'sugar' in name:
                            info_ingrediente['azucar'] = amount
                            total_azucar += amount
                    analisis_ingredientes.append(info_ingrediente)
                    contador_ingredientes += 1
                evaluacion = []
                alertas = []
                if total_grasas > 20:
                    evaluacion.append("Alto en grasas")
                    alertas.append(f"Grasas: {total_grasas:.1f}g (límite recomendado: 20g)")
                elif total_grasas > 10:
                    evaluacion.append("Moderado en grasas")
                else:
                    evaluacion.append("Bajo en grasas")
                if total_azucar > 15:
                    evaluacion.append("Alto en azúcar")
                    alertas.append(f"Azúcar: {total_azucar:.1f}g (límite recomendado: 15g)")
                elif total_azucar > 5:
                    evaluacion.append("Moderado en azúcar")
                else:
                    evaluacion.append("Bajo en azúcar")
                if total_fibra < 3:
                    evaluacion.append("Bajo en fibra")
                elif total_fibra > 8:
                    evaluacion.append("Alto en fibra")
                else:
                    evaluacion.append("Moderado en fibra")
                if total_proteinas > 25:
                    evaluacion.append("Alto en proteínas")
                elif total_proteinas < 10:
                    evaluacion.append("Bajo en proteínas")
                else:
                    evaluacion.append("Moderado en proteínas")
                if total_calorias > 600:
                    evaluacion.append("Alto en calorías")
                    alertas.append(f"Calorías: {total_calorias:.0f} (límite recomendado: 600 por porción)")
                elif total_calorias < 200:
                    evaluacion.append("Bajo en calorías")
                else:
                    evaluacion.append("Moderado en calorías")
                if len(alertas) >= 3:
                    etiqueta_general = "🔴 Poco saludable"
                    color_clase = "danger"
                elif len(alertas) >= 1:
                    etiqueta_general = "🟡 Moderadamente saludable" 
                    color_clase = "warning"
                else:
                    etiqueta_general = "🟢 Saludable"
                    color_clase = "success"
                resultado = f"""
                <div class='alert alert-success'>
                    <h4>Analisis Nutricional - {titulo}</h4>
                    <div class='alert alert-{color_clase}'>
                        <h5>Etiqueta Nutricional: {etiqueta_general}</h5>
                        <strong>Evaluación:</strong> {', '.join(evaluacion)}
                        {f"<br><strong>Alertas:</strong> {', '.join(alertas)}" if alertas else ""}
                    </div>
                    
                    <hr>
                    <h5>Resumen Total de la Receta:</h5>
                    <div class='table-responsive'>
                        <table class='table table-bordered'>
                            <thead class='table-light'>
                                <tr>
                                    <th>Calorias</th>
                                    <th>Proteinas</th>
                                    <th>Carbohidratos</th>
                                    <th>Grasas</th>
                                    <th>Fibra</th>
                                    <th>Azucar</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>{total_calorias:.0f}</strong></td>
                                    <td><strong>{total_proteinas:.1f}g</strong></td>
                                    <td><strong>{total_carbohidratos:.1f}g</strong></td>
                                    <td><strong>{total_grasas:.1f}g</strong></td>
                                    <td><strong>{total_fibra:.1f}g</strong></td>
                                    <td><strong>{total_azucar:.1f}g</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <hr>
                    <h5>Analisis por Ingrediente:</h5>
                """
                for ingrediente in analisis_ingredientes:
                    if ingrediente.get('error'): 
                        resultado += f"""
                        <div class='mb-2 p-2 border rounded bg-warning'>
                            <strong>{ingrediente['numero']}. {ingrediente['nombre']}</strong><br>
                            <span class='text-muted'>No se pudo analizar este ingrediente (Error de la API)</span>
                        </div>
                        """
                    else:
                        resultado += f"""
                        <div class='mb-2 p-2 border rounded'>
                            <strong>{ingrediente['numero']}. {ingrediente['nombre']}</strong><br>
                            <small>
                                Calorias: {ingrediente['calorias']:.0f} | 
                                Proteinas: {ingrediente['proteinas']:.1f}g | 
                                Carbohidratos: {ingrediente['carbohidratos']:.1f}g | 
                                Grasas: {ingrediente['grasas']:.1f}g
                                {f" | Fibra: {ingrediente['fibra']:.1f}g" if ingrediente['fibra'] > 0 else ""}
                                {f" | Azucar: {ingrediente['azucar']:.1f}g" if ingrediente['azucar'] > 0 else ""}
                            </small>
                        </div>
                        """
                resultado += """
                    <hr>
                    <small class='text-muted'>
                    <strong>Nota:</strong> Este analisis calcula los valores nutricionales sumando cada ingrediente por separado.
                    Los valores pueden variar segun el metodo de preparacion y porciones.
                    </small>
                </div>
                """ 
            else:
                try:
                    error_data = response_receta.json()
                    mensaje_error = error_data.get('message', 'No se pudo obtener el mensaje de error de la API.')
                except:
                    mensaje_error = "Respuesta de la API no es JSON o está vacía."
                resultado = f"""
                    <div class='alert alert-danger'>
                        Error de API. Código de estado: <strong>{response_receta.status_code}</strong>.
                        <br>Mensaje: {mensaje_error}
                    </div>
                """
    except Exception as e:
        resultado = f'<div class="alert alert-danger">Error inesperado en Flask: {str(e)}</div>'
    return render_template('analizador.html', datos_usuario=datos_usuario, resultado_receta=resultado)

@app.route('/buscar_receta2', methods=['POST'])
def buscar_receta2():
    datos_usuario = None
    if session.get('logueado'):
        usuario_correo = session.get('usuario_correo')
        if usuario_correo in USUARIOS_REGISTRADOS:
            datos_usuario = USUARIOS_REGISTRADOS[usuario_correo]
    resultado = None
    try:
        ingrediente = request.form.get('ingrediente_receta', '').strip().lower()
        minima = request.form.get('minima', '').strip()
        maxima = request.form.get('maxima', '').strip()
        dieta = request.form.get('dieta', '').strip().lower()
        tiempo = request.form.get('tiempo', '').strip()
        excluido = request.form.get('excluido', '').strip().lower()
        if not ingrediente:
            resultado = 'Por favor ingresa un ingrediente principal'
        else:
            url = f"{API_BASE}/recipes/complexSearch"
            params = {
                'apiKey': API_KEY,
                'query': ingrediente,
                'number': 3,
                'addRecipeInformation': True,
                'addRecipeNutrition': True,
                'fillIngredients': True,
                'instructionsRequired': True,
                'language': 'en',
            }
            if minima:
                params['minCalories'] = minima
            if maxima:
                params['maxCalories'] = maxima
            if dieta:
                params['diet'] = dieta
            if tiempo:
                params['maxReadyTime'] = tiempo
            if excluido:
                params['excludeIngredients'] = excluido
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                recetas = data.get('results', [])
                if recetas:
                    filtros = []
                    if minima: filtros.append(f"Mín: {minima} cal")
                    if maxima: filtros.append(f"Máx: {maxima} cal")
                    if dieta: filtros.append(f"Dieta: {dieta}")
                    if tiempo: filtros.append(f"Tiempo: {tiempo}min")
                    if excluido: filtros.append(f"Sin: {excluido}")
                    filtros_str = " | ".join(filtros) if filtros else "Sin filtros"
                    resultado = f"<strong>Recetas encontradas ({filtros_str}):</strong><br><br>"
                    contador_recetas = 1
                    for receta in recetas:
                        calorias_receta = {}
                        proteinas_receta = {}
                        carbohidratos_receta = {}
                        grasas_receta = {}
                        nutricion = receta.get('nutrition')
                        if nutricion:
                            for nutriente in nutricion.get('nutrients', []):
                                name = nutriente.get('name', '').lower()
                                if 'calorie' in name:
                                    calorias_receta = nutriente
                                elif 'protein' in name:
                                    proteinas_receta = nutriente
                                elif 'carbohydrate' in name:
                                    carbohidratos_receta = nutriente
                                elif 'fat' in name and 'saturated' not in name:
                                    grasas_receta = nutriente
                        calorias_amount = calorias_receta.get('amount', 'N/A')
                        if type(calorias_amount) == int or type(calorias_amount) == float:
                            calorias_str = f"{calorias_amount:.0f} calorías"
                        else:
                            calorias_str = "Calorías no disponibles"
                        ready_time = receta.get('readyInMinutes', 'N/A')
                        porciones = receta.get('servings', 'N/A')
                        ingredientes = receta.get('extendedIngredients', [])
                        ingredientes_str = ""
                        if ingredientes:
                            ingredientes_str = "<br><strong>Lista de ingredientes:</strong><br>"
                            contador_ingredientes = 1
                            for ingrediente_item in ingredientes:
                                ingrediente_original = ingrediente_item.get('original', '')
                                ingredientes_str += f"{contador_ingredientes}. {ingrediente_original}<br>"
                                contador_ingredientes += 1
                        else:
                            ingredientes_str = "<br><strong>Ingredientes:</strong><br>No disponibles"
                        instrucciones_str = ""
                        analyzed_instructions = receta.get('analyzedInstructions', [])
                        if analyzed_instructions and len(analyzed_instructions) > 0:
                            steps = analyzed_instructions[0].get('steps', [])
                            if steps:
                                instrucciones_str = "<br><strong>Instrucciones:</strong><br>"
                                contador_pasos = 1
                                for step in steps:
                                    instrucciones_str += f"<strong>Paso {contador_pasos}:</strong> {step.get('step', '')}<br>"
                                    contador_pasos += 1
                        else:
                            instrucciones_str = "<br><strong>Instrucciones:</strong><br>No disponibles"                   
                        resultado += f"""
                        <div class='mb-5 p-4 border rounded bg-light'>
                            <h4 class='text-primary'>{contador_recetas}. {receta['title']}</h4>                         
                            <div class='row mb-3'>
                                <div class='col-md-12'>
                                    <strong>Información nutricional por porción:</strong><br>
                                    <strong>Tiempo:</strong> {ready_time} minutos | 
                                    <strong>Porciones:</strong> {porciones} | 
                                    <strong>Calorías:</strong> {calorias_str}<br>
                                    <strong>Proteínas:</strong> {proteinas_receta.get('amount', 'N/A'):.1f}g | 
                                    <strong>Carbohidratos:</strong> {carbohidratos_receta.get('amount', 'N/A'):.1f}g | 
                                    <strong>Grasas:</strong> {grasas_receta.get('amount', 'N/A'):.1f}g
                                </div>
                            </div>
                            <div class='row'>
                                <div class='col-md-12'>
                                    {ingredientes_str}
                                </div>
                            </div>                      
                            <div class='row mt-2'>
                                <div class='col-md-12'>
                                    {instrucciones_str}
                                </div>
                            </div>
                            <div class='mt-3 text-end'>
                                <small class='text-muted'>
                                    ID: {receta.get('id', 'N/A')} | 
                                    Puntuación: {receta.get('spoonacularScore', 'N/A')}/100
                                </small>
                            </div>
                        </div>
                        <hr>
                        """  
                        contador_recetas += 1      
                else:
                    resultado = 'No se encontraron recetas con esos criterios. Intenta con filtros más amplios.'    
            else:
                resultado = f'Error al buscar recetas. Código: {response.status_code}'
    except Exception as e:
        resultado = f'Error inesperado: {str(e)}'  
    return render_template('modulo3.html', datos_usuario=datos_usuario, resultado_busqueda_receta=resultado)

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