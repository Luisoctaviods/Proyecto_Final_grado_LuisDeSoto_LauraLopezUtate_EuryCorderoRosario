#!/usr/bin/env python3
"""
Script de configuración para el chatbot inchat
"""

import os
import sys
import subprocess
from pymongo import MongoClient

def check_python_version():
    """Verificar que se esté usando Python 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        sys.exit(1)
    print("✅ Versión de Python compatible")

def install_requirements():
    """Instalar dependencias de requirements.txt"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar dependencias")
        sys.exit(1)

def setup_environment():
    """Configurar archivo .env"""
    if not os.path.exists('.env'):
        print("⚙️ Configurando archivo de entorno...")
        
        # Copiar archivo de ejemplo
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as example:
                content = example.read()
            
            # Solicitar configuraciones al usuario
            print("\n🔧 Configuración requerida:")
            openai_key = input("Ingresa tu API Key de OpenAI: ").strip()
            secret_key = input("Ingresa una clave secreta para Flask (deja vacío para generar una): ").strip()
            
            if not secret_key:
                import secrets
                secret_key = secrets.token_hex(32)
                print(f"🔑 Clave secreta generada automáticamente")
            
            mongo_uri = input("URI de MongoDB (presiona Enter para usar por defecto): ").strip()
            if not mongo_uri:
                mongo_uri = "mongodb://localhost:27017/inchat_db"
            
            # Reemplazar valores en el contenido
            content = content.replace('tu_clave_de_openai_aqui', openai_key)
            content = content.replace('tu_clave_secreta_super_segura_aqui', secret_key)
            content = content.replace('mongodb://localhost:27017/inchat_db', mongo_uri)
            
            # Escribir archivo .env
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ Archivo .env creado correctamente")
        else:
            print("❌ No se encontró .env.example")
            sys.exit(1)
    else:
        print("✅ Archivo .env ya existe")

def setup_mongodb():
    """Configurar MongoDB y crear colecciones"""
    print("🗄️ Configurando MongoDB...")
    
    try:
        # Leer URI de MongoDB del archivo .env
        mongo_uri = "mongodb://localhost:27017/inchat_db"
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('MONGO_URI='):
                        mongo_uri = line.split('=', 1)[1].strip()
                        break
        
        # Conectar a MongoDB
        client = MongoClient(mongo_uri)
        db = client.get_default_database()
        
        # Crear colecciones con índices
        collections = ['users', 'chat_sessions', 'messages', 'knowledge_base']
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✅ Colección '{collection_name}' creada")
            else:
                print(f"✅ Colección '{collection_name}' ya existe")
        
        # Crear índices
        db.users.create_index("email", unique=True)
        db.chat_sessions.create_index("user_id")
        db.messages.create_index("session_id")
        db.knowledge_base.create_index("activo")
        
        print("✅ Índices de MongoDB creados")
        
        # Insertar datos de ejemplo en knowledge_base
        if db.knowledge_base.count_documents({}) == 0:
            ejemplo_knowledge = [
                {
                    "titulo": "Información General de la Universidad",
                    "contenido": "Nuestra universidad es una institución de educación superior comprometida con la excelencia académica. Ofrecemos programas de pregrado y posgrado en diversas áreas del conocimiento.",
                    "tipo": "documento",
                    "url": "",
                    "activo": True,
                    "fecha_subida": "2024-01-01T00:00:00"
                },
                {
                    "titulo": "Horarios de Atención",
                    "contenido": "La universidad está abierta de lunes a viernes de 7:00 AM a 9:00 PM, y los sábados de 8:00 AM a 4:00 PM. Las oficinas administrativas atienden de lunes a viernes de 8:00 AM a 5:00 PM.",
                    "tipo": "documento",
                    "url": "",
                    "activo": True,
                    "fecha_subida": "2024-01-01T00:00:00"
                },
                {
                    "titulo": "Proceso de Admisiones",
                    "contenido": "Para ingresar a la universidad, los estudiantes deben completar el proceso de admisión que incluye: envío de documentos, examen de admisión, entrevista y pago de matrícula.",
                    "tipo": "documento",
                    "url": "",
                    "activo": True,
                    "fecha_subida": "2024-01-01T00:00:00"
                }
            ]
            
            db.knowledge_base.insert_many(ejemplo_knowledge)
            print("✅ Datos de ejemplo agregados a la base de conocimiento")
        
        client.close()
        print("✅ MongoDB configurado correctamente")
        
    except Exception as e:
        print(f"❌ Error al configurar MongoDB: {e}")
        print("💡 Asegúrate de que MongoDB esté ejecutándose")

def create_directory_structure():
    """Crear estructura de directorios necesaria"""
    directories = ['templates', 'static', 'static/css', 'static/js']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Directorio '{directory}' creado")
        else:
            print(f"📁 Directorio '{directory}' ya existe")

def show_final_instructions():
    """Mostrar instrucciones finales"""
    print("\n🎉 ¡Configuración completada!")
    print("\n📋 Para ejecutar la aplicación:")
    print("1. Asegúrate de que MongoDB esté ejecutándose")
    print("2. Ejecuta: python app.py")
    print("3. Abre tu navegador en: http://localhost:5000")
    print("\n🔧 Para administrar la base de conocimiento:")
    print("   Visita: http://localhost:5000/admin/knowledge")
    print("\n💡 Consejos:")
    print("   - Puedes agregar más documentos a la base de conocimiento")
    print("   - Modifica el prompt del sistema en app.py según tus necesidades")
    print("   - El chatbot responderá basándose en los documentos que agregues")

def main():
    """Función principal de configuración"""
    print("🚀 Configurando chatbot inchat...\n")
    
    # Verificaciones y configuración
    check_python_version()
    create_directory_structure()
    install_requirements()
    setup_environment()
    setup_mongodb()
    show_final_instructions()

if __name__ == "__main__":
    main()