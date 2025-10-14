from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import openai
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/inchat_db'

mongo = PyMongo(app)

# Configurar OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        # Validar datos
        if not all([data.get('nombre_completo'), data.get('email'), data.get('password')]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        # Verificar si el email ya existe
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'success': False, 'message': 'El email ya está registrado'})
        
        # Crear usuario
        user_data = {
            'nombre_completo': data['nombre_completo'],
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'fecha_registro': datetime.now(),
            'activo': True
        }
        
        result = mongo.db.users.insert_one(user_data)
        
        if result.inserted_id:
            return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al crear usuario'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        
        user = mongo.db.users.find_one({'email': data['email']})
        
        if user and check_password_hash(user['password'], data['password']):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['nombre_completo']
            return jsonify({'success': True, 'redirect': url_for('chat')})
        else:
            return jsonify({'success': False, 'message': 'Credenciales inválidas'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    # Obtener sesiones de chat del usuario
    chat_sessions = list(mongo.db.chat_sessions.find(
        {'user_id': ObjectId(session['user_id'])},
        {'titulo': 1, 'fecha_creacion': 1}
    ).sort('fecha_creacion', -1))
    
    return render_template('chat.html', 
                         user_name=session['user_name'],
                         chat_sessions=chat_sessions)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    # Crear nueva sesión de chat
    chat_data = {
        'user_id': ObjectId(session['user_id']),
        'titulo': 'Nuevo Chat',
        'fecha_creacion': datetime.now(),
        'activa': True
    }
    
    result = mongo.db.chat_sessions.insert_one(chat_data)
    
    if result.inserted_id:
        return jsonify({'success': True, 'session_id': str(result.inserted_id)})
    else:
        return jsonify({'success': False, 'message': 'Error al crear chat'})

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id')
    
    if not message or not session_id:
        return jsonify({'success': False, 'message': 'Mensaje y sesión requeridos'})
    
    try:
        # Guardar mensaje del usuario
        user_message = {
            'session_id': ObjectId(session_id),
            'tipo': 'user',
            'contenido': message,
            'timestamp': datetime.now()
        }
        mongo.db.messages.insert_one(user_message)
        
        # Obtener contexto de la base de conocimiento
        knowledge_context = get_knowledge_context()
        
        # Obtener historial de mensajes para contexto
        chat_history = list(mongo.db.messages.find(
            {'session_id': ObjectId(session_id)},
            {'tipo': 1, 'contenido': 1}
        ).sort('timestamp', 1).limit(20))
        
        # Preparar contexto para OpenAI
        system_message = f"""Eres un asistente virtual de inchat para una universidad. 
        Utiliza la siguiente información de la base de conocimiento para responder:
        
        {knowledge_context}
        
        Responde de manera útil y amigable, basándote en la información proporcionada."""
        
        messages = [{"role": "system", "content": system_message}]
        
        # Agregar historial de chat
        for msg in chat_history[:-1]:  # Excluir el último mensaje que acabamos de agregar
            role = "user" if msg['tipo'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['contenido']})
        
        messages.append({"role": "user", "content": message})
        
        # Llamar a OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Guardar respuesta del asistente
        assistant_message = {
            'session_id': ObjectId(session_id),
            'tipo': 'assistant',
            'contenido': ai_response,
            'timestamp': datetime.now()
        }
        mongo.db.messages.insert_one(assistant_message)
        
        return jsonify({
            'success': True, 
            'response': ai_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_messages/<session_id>')
def get_messages(session_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    messages = list(mongo.db.messages.find(
        {'session_id': ObjectId(session_id)},
        {'tipo': 1, 'contenido': 1, 'timestamp': 1}
    ).sort('timestamp', 1))
    
    # Formatear mensajes para el frontend
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'tipo': msg['tipo'],
            'contenido': msg['contenido'],
            'timestamp': msg['timestamp'].strftime('%H:%M')
        })
    
    return jsonify({'success': True, 'messages': formatted_messages})

def get_knowledge_context():
    """Obtiene información relevante de la base de conocimiento"""
    knowledge_docs = list(mongo.db.knowledge_base.find(
        {'activo': True},
        {'titulo': 1, 'contenido': 1}
    ).limit(10))
    
    context = ""
    for doc in knowledge_docs:
        context += f"Documento: {doc['titulo']}\nContenido: {doc['contenido']}\n\n"
    
    return context

@app.route('/admin/knowledge', methods=['GET', 'POST'])
def manage_knowledge():
    # Esta ruta sería para administrar la base de conocimiento
    # Implementar autenticación de admin según se necesite
    if request.method == 'POST':
        data = request.get_json()
        
        knowledge_data = {
            'titulo': data['titulo'],
            'contenido': data['contenido'],
            'tipo': data.get('tipo', 'documento'),
            'url': data.get('url', ''),
            'activo': True,
            'fecha_subida': datetime.now()
        }
        
        mongo.db.knowledge_base.insert_one(knowledge_data)
        return jsonify({'success': True})
    
    # GET: mostrar interfaz de administración
    knowledge_docs = list(mongo.db.knowledge_base.find({'activo': True}))
    return render_template('admin_knowledge.html', docs=knowledge_docs)

if __name__ == '__main__':
    app.run(debug=True)