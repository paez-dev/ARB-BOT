"""
ARB-BOT - Aplicación Principal
Sistema de chatbot institucional con IA usando RAG
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
import logging
import threading
import uuid

from config import config
from models.api_model import APIModel
from services.text_processor import TextProcessor
from services.generator import ContentGenerator
from services.rag_service import RAGService
from database.db import init_db, get_db_session, save_interaction, get_recent_interactions
from werkzeug.utils import secure_filename
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, static_folder='static', template_folder='templates')

# Cargar configuración
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Inicializar base de datos
init_db(app.config['DATABASE_URL'])

# Inicializar servicios (modelos se cargarán bajo demanda para ahorrar memoria)
text_processor = TextProcessor()
# DocumentProcessor eliminado - el procesamiento se hace en Colab, no en Railway

# Modelos de IA se inicializarán bajo demanda (lazy loading)
ai_model = None
content_generator = None
rag_service = None

# Sistema de procesamiento asíncrono para documentos grandes
# Sistema de procesamiento de documentos eliminado
# Todo el procesamiento se hace en Google Colab, no en Railway
# Ver: ARQUITECTURA_CORRECTA.md

def _load_services(load_rag: bool = False):
    """
    Cargar modelos principales (IA + RAG opcional)

    Args:
        load_rag: Si es True, intenta precargar RAG e índice

    Returns:
        Tupla (rag_cargado: bool, mensaje: str)
    """
    rag_loaded = False
    rag_message = "Servicio RAG se cargará automáticamente cuando se necesite."

    # Cargar modelo de IA
    get_ai_model()
    logger.info("Modelo de IA disponible.")

    if load_rag:
        try:
            get_rag_service()
            rag_loaded = True
            rag_message = "Servicio RAG pre-cargado correctamente."
            logger.info("Servicio RAG disponible.")
        except Exception as rag_error:
            rag_message = f"No se pudo cargar RAG durante la precarga: {rag_error}"
            logger.warning(rag_message)

    return rag_loaded, rag_message

def _preload_services_async(load_rag: bool = False):
    """Iniciar precarga en segundo plano para no bloquear el arranque"""
    def _run():
        try:
            logger.info("Iniciando precarga de modelos en segundo plano...")
            rag_loaded, _ = _load_services(load_rag)
            logger.info("Precarga finalizada (RAG cargado: %s)", rag_loaded)
        except Exception as preload_error:
            logger.error(f"Error precargando servicios: {preload_error}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

def get_ai_model():
    """Obtener modelo de IA mediante API (solo Groq)"""
    global ai_model, content_generator
    if ai_model is None:
        logger.info("Inicializando modelo mediante API Groq...")
        provider = app.config.get('API_PROVIDER', 'groq')
        model_name = app.config.get('API_MODEL_NAME') or None
        
        # Obtener API key según el proveedor
        api_key = None
        if provider == 'groq':
            api_key = app.config.get('GROQ_API_KEY') or os.getenv('GROQ_API_KEY')
            if not api_key:
                logger.error("GROQ_API_KEY no encontrada en configuración ni variables de entorno")
                raise ValueError("GROQ_API_KEY no configurada. Agrega GROQ_API_KEY en Railway → Settings → Variables")
        elif provider == 'huggingface':
            api_key = app.config.get('HUGGINGFACE_API_KEY') or os.getenv('HUGGINGFACE_API_KEY')
        elif provider == 'gemini':
            api_key = app.config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        logger.info(f"Inicializando {provider} con API key: {'Configurada' if api_key else 'NO ENCONTRADA'}")
        ai_model = APIModel(provider=provider, model_name=model_name, api_key=api_key)
        logger.info(f"Modelo API inicializado: {provider} - {ai_model.model_name}")
        content_generator = ContentGenerator(ai_model, text_processor)
    return ai_model, content_generator

def get_rag_service():
    """Obtener servicio RAG (carga bajo demanda)"""
    global rag_service
    if rag_service is None:
        logger.info("Cargando servicio RAG (primera vez)...")
        try:
            rag_service = RAGService()
            logger.info("Servicio RAG inicializado")
            
            # Con Supabase pgvector, el índice se carga automáticamente
            # Verificar si hay documentos disponibles
            try:
                stats = rag_service.get_stats()
                total_docs = stats.get('total_documents', 0)
                vector_store = stats.get('vector_store', 'unknown')
                if total_docs and total_docs != 'unknown' and total_docs > 0:
                    logger.info(f"✅ Documentos institucionales disponibles en RAG: {total_docs} documentos (vector store: {vector_store})")
                else:
                    logger.info(f"ℹ️ No hay documentos procesados aún. Vector store: {vector_store}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo verificar documentos (continuando): {e}")
                # Continuar sin verificar - se pueden agregar documentos después
        except Exception as e:
            logger.error(f"Error crítico cargando servicio RAG: {str(e)}")
            # Crear un servicio RAG vacío para que la app no falle
            # El usuario podrá agregar documentos después
            raise
    return rag_service

# Directorio para documentos
# Usar disco persistente si está disponible, sino usar directorio local
if os.path.exists('/persistent'):
    UPLOAD_FOLDER = '/persistent/documents'
    logger.info("Usando disco persistente para almacenamiento")
else:
    UPLOAD_FOLDER = 'documents'
    logger.info("Usando almacenamiento local (desarrollo)")

# Nota: Con Supabase pgvector, no se necesita INDEX_FILE
# Los índices se guardan automáticamente en Supabase

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Crear directorio si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de precarga (controlable por variables de entorno)
PRELOAD_MODELS_ON_STARTUP = os.getenv('PRELOAD_MODELS_ON_STARTUP', 'true').lower() == 'true'
PRELOAD_RAG_ON_STARTUP = os.getenv('PRELOAD_RAG_ON_STARTUP', 'true').lower() == 'true'

if PRELOAD_MODELS_ON_STARTUP:
    _preload_services_async(load_rag=PRELOAD_RAG_ON_STARTUP)

def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud del sistema"""
    return jsonify({
        'status': 'healthy',
        'service': 'ARB-BOT',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': ai_model is not None
    })

@app.route('/api/warmup', methods=['POST'])
def warmup():
    """Pre-cargar modelos manualmente (útil para optimizar primera carga)"""
    try:
        load_rag = request.args.get('load_rag', 'false').lower() == 'true'
        logger.info("Iniciando warmup de modelos...")

        rag_loaded, rag_message = _load_services(load_rag)

        return jsonify({
            'status': 'success',
            'message': 'Modelos base pre-cargados exitosamente',
            'ai_model_loaded': ai_model is not None,
            'rag_loaded': rag_loaded,
            'rag_message': rag_message
        })
    except Exception as e:
        logger.error(f"Error en warmup: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """
    Endpoint principal para generación de contenido
    """
    try:
        data = request.get_json()
        
        if not data or 'input' not in data:
            return jsonify({
                'error': 'Input requerido',
                'status': 'error'
            }), 400
        
        user_input = data['input']
        
        # Validar input
        if len(user_input) < app.config['MIN_INPUT_LENGTH']:
            return jsonify({
                'error': f'Input muy corto. Mínimo {app.config["MIN_INPUT_LENGTH"]} caracteres',
                'status': 'error'
            }), 400
        
        if len(user_input) > app.config['MAX_INPUT_LENGTH']:
            return jsonify({
                'error': f'Input muy largo. Máximo {app.config["MAX_INPUT_LENGTH"]} caracteres',
                'status': 'error'
            }), 400
        
        logger.info(f"Procesando input: {user_input[:50]}...")
        
        # Paso 1: Procesar el texto de entrada
        processed_input = text_processor.process(user_input)
        logger.info("Texto procesado exitosamente")
        
        # Paso 2: Buscar contexto relevante en documentos (RAG)
        context = ""
        rag = None
        try:
            rag = get_rag_service()
            if rag:
                # Intentar obtener stats, pero no confiar completamente en él
                try:
                    stats = rag.get_stats()
                    total_docs = stats.get('total_documents', 0)
                    if isinstance(total_docs, str):
                        total_docs = 0
                    logger.debug(f"📊 RAG stats: {total_docs} documentos reportados")
                except Exception as stats_error:
                    logger.warning(f"⚠️ Error obteniendo stats RAG: {stats_error}")
                    total_docs = 0
                
                # Intentar buscar contexto siempre (por si get_stats() falló pero hay documentos)
                # Si no hay documentos, la búsqueda retornará lista vacía
                try:
                    context = rag.get_context_for_query(processed_input, top_k=10, max_context_length=2500)
                    if context and len(context.strip()) > 0:
                        logger.info(f"✅ Contexto encontrado: {len(context)} caracteres")
                    else:
                        if total_docs == 0:
                            logger.info("No hay documentos cargados en RAG - generando sin contexto")
                        else:
                            logger.warning(f"⚠️ Hay {total_docs} documentos pero no se encontró contexto relevante para la consulta")
                except Exception as search_error:
                    logger.warning(f"⚠️ Error buscando contexto: {search_error}")
                    context = ""
            else:
                logger.info("No hay servicio RAG disponible - generando sin contexto")
        except Exception as e:
            logger.warning(f"Error obteniendo contexto RAG (continuando sin contexto): {str(e)}")
            context = ""
            rag = None
        
        # Información de RAG para decisiones posteriores
        rag_documents = rag.get_stats()['total_documents'] if rag else 0
        context_available = bool(context.strip()) if context else False
        
        # Paso 3: Generar contenido usando IA con contexto (o respuesta institucional si no hay contexto)
        ai_model_instance = None
        generated_content = ""
        model_used_label = ""
        
        if rag_documents > 0 and not context_available:
            logger.info("No se encontró contexto en RAG para la consulta. Usando respuesta institucional de contacto.")
            generated_content = (
                "Lo siento, esa información no aparece en el manual ni en los documentos institucionales. "
                "Para recibir ayuda personalizada comunícate con un asesor administrativo al 333-333-3333. "
                "Solo puedo responder preguntas relacionadas con la institución."
            )
            model_used_label = "RAG-Fallback (sin modelo)"
        else:
            ai_model_instance, generator = get_ai_model()
            generated_content = generator.generate(
                processed_input,
                max_tokens=app.config['MAX_TOKENS'],
                temperature=app.config['TEMPERATURE'],
                context=context if context else None
            )
            logger.info("Contenido generado exitosamente")
            model_used_label = f"{app.config.get('API_PROVIDER', 'groq')} - {ai_model_instance.model_name if ai_model_instance else 'N/A'}"
        
        # Paso 3: Preparar respuesta
        response = {
            'status': 'success',
            'input': user_input,
            'processed_input': processed_input,
            'generated_content': generated_content,
            'model_used': model_used_label if model_used_label else f"{app.config.get('API_PROVIDER', 'groq')} - {ai_model_instance.model_name if ai_model_instance else 'N/A'}",
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'input_length': len(user_input),
                'output_length': len(generated_content),
                'processing_time': 'N/A',
                'context_used': len(context) > 0,
                'rag_documents': rag_documents
            }
        }
        
        # Guardar en base de datos
        try:
            import time
            start_time = time.time()
            processing_time = time.time() - start_time
            
            save_interaction(
                user_input=user_input,
                generated_output=generated_content,
                model_used=response['model_used'],
                processing_time=processing_time,
                metadata={
                    'input_length': len(user_input),
                    'output_length': len(generated_content),
                    'temperature': app.config['TEMPERATURE']
                }
            )
        except Exception as e:
            logger.warning(f"No se pudo guardar en BD: {e}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en generación: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """Listar modelos disponibles"""
    return jsonify({
        'status': 'success',
        'api_providers': app.config['AVAILABLE_API_PROVIDERS'],
        'current_provider': app.config.get('API_PROVIDER', 'groq'),
        'current_model': ai_model.model_name if ai_model else 'N/A'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        with get_db_session() as db_session:
            cursor = db_session.cursor()
            
            # Contar total de interacciones
            cursor.execute('SELECT COUNT(*) as total FROM interactions')
            total_interactions = cursor.fetchone()['total']
            
            # Obtener última interacción
            cursor.execute('SELECT timestamp FROM interactions ORDER BY timestamp DESC LIMIT 1')
            last_interaction = cursor.fetchone()
            last_interaction_time = last_interaction['timestamp'] if last_interaction else None
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_interactions': total_interactions,
                'active_provider': app.config.get('API_PROVIDER', 'groq'),
                'active_model': ai_model.model_name if ai_model else 'N/A',
                'system_status': 'operational',
                'last_interaction': last_interaction_time,
                'providers_available': len(app.config['AVAILABLE_API_PROVIDERS']),
                'api_loaded': ai_model is not None
            }
        })
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({
            'status': 'success',
            'stats': {
                'total_interactions': 0,
                'active_provider': app.config.get('API_PROVIDER', 'groq'),
                'active_model': 'N/A',
                'system_status': 'operational',
                'last_interaction': None,
                'providers_available': len(app.config['AVAILABLE_API_PROVIDERS']),
                'api_loaded': False
            }
        })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Obtener historial de interacciones"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = get_recent_interactions(limit)
        
        return jsonify({
            'status': 'success',
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/change-model', methods=['POST'])
def change_model():
    """Cambiar el proveedor de API (Groq, Hugging Face, Gemini)"""
    # Verificar autenticación
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        
        if not data or 'provider' not in data:
            return jsonify({
                'error': 'Proveedor requerido',
                'status': 'error'
            }), 400
        
        provider = data['provider'].lower()
        model_name = data.get('model_name')  # Opcional
        
        # Validar proveedor
        valid_providers = ['groq', 'huggingface', 'gemini']
        if provider not in valid_providers:
            return jsonify({
                'error': f'Proveedor {provider} no válido',
                'status': 'error',
                'available_providers': valid_providers
            }), 400
        
        # Cambiar modelo
        global ai_model, content_generator
        # Liberar modelo anterior si existe
        if ai_model is not None:
            del ai_model
            del content_generator
            import gc
            gc.collect()
        
        # Obtener API key según el proveedor
        api_key = None
        if provider == 'groq':
            api_key = app.config.get('GROQ_API_KEY')
        elif provider == 'huggingface':
            api_key = app.config.get('HUGGINGFACE_API_KEY')
        elif provider == 'gemini':
            api_key = app.config.get('GEMINI_API_KEY')
        
        ai_model = APIModel(provider=provider, model_name=model_name, api_key=api_key)
        content_generator = ContentGenerator(ai_model, text_processor)
        app.config['API_PROVIDER'] = provider
        if model_name:
            app.config['API_MODEL_NAME'] = model_name
        
        logger.info(f"Proveedor API cambiado a: {provider} - {ai_model.model_name}")
        
        return jsonify({
            'status': 'success',
            'message': f'Proveedor API cambiado a {provider}',
            'current_provider': provider,
            'current_model': ai_model.model_name
        })
        
    except Exception as e:
        logger.error(f"Error cambiando proveedor API: {str(e)}")
        return jsonify({
            'error': 'Error al cambiar proveedor API',
            'message': str(e),
            'status': 'error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'status': 'error'
    }), 404

def require_admin():
    """Verificar que el usuario esté autenticado como admin"""
    if not session.get('admin_authenticated', False):
        return jsonify({
            'error': 'Autenticación requerida',
            'status': 'auth_required'
        }), 401
    return None

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Login para panel de administración"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_authenticated'] = True
            return jsonify({
                'status': 'success',
                'message': 'Autenticación exitosa'
            })
        else:
            return jsonify({
                'error': 'Contraseña incorrecta',
                'status': 'error'
            }), 401
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({
            'error': 'Error en autenticación',
            'status': 'error'
        }), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Logout del panel de administración"""
    session.pop('admin_authenticated', None)
    return jsonify({
        'status': 'success',
        'message': 'Sesión cerrada'
    })

@app.route('/api/admin/check-auth', methods=['GET'])
def check_admin_auth():
    """Verificar si el usuario está autenticado"""
    return jsonify({
        'authenticated': session.get('admin_authenticated', False)
    })

# Función _process_document_async eliminada
# El procesamiento de documentos se hace en Google Colab, no en Railway
# Ver: ARQUITECTURA_CORRECTA.md

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """
    ⚠️ DESHABILITADO EN PRODUCCIÓN
    
    El procesamiento de documentos NO debe hacerse en Railway.
    Todo el procesamiento (PDF → chunks → embeddings) debe hacerse en Google Colab.
    
    Ver: ARQUITECTURA_CORRECTA.md
    """
    # Verificar autenticación
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    # Deshabilitar en producción - todo debe procesarse en Colab
    return jsonify({
        'error': 'El procesamiento de documentos está deshabilitado en producción.',
        'message': 'Por favor, usa Google Colab para procesar documentos. Ver: ARQUITECTURA_CORRECTA.md',
        'status': 'error',
        'instructions': {
            'correct_flow': 'Google Colab → Procesar PDF → Generar embeddings → Subir a Supabase',
            'bot_role': 'Railway solo consulta Supabase y genera respuestas',
            'documentation': 'Ver INGESTA_FINAL_RAG.ipynb para procesar documentos'
        }
    }), 400

# Endpoint /api/upload-status eliminado
# El procesamiento de documentos se hace en Google Colab, no en Railway
# Ver: ARQUITECTURA_CORRECTA.md

@app.route('/api/rag-stats', methods=['GET'])
def get_rag_stats():
    """Obtener estadísticas del sistema RAG (sin cargar el servicio si no está cargado)"""
    try:
        # Solo obtener stats si el servicio ya está cargado
        # No forzar la carga del RAG aquí para evitar timeouts
        if rag_service is not None:
            stats = rag_service.get_stats()
            return jsonify({
                'status': 'success',
                'stats': stats
            })
        else:
            # Retornar stats vacías si el servicio no está cargado
            # Esto evita cargar el RAG solo para ver stats
            # Con Supabase pgvector, no hay archivo de índice local
            return jsonify({
                'status': 'success',
                'stats': {
                    'total_documents': 0,
                    'embeddings_model': 'N/A',
                    'vector_store': 'not_loaded',
                    'sources': [],
                    'service_loaded': False,
                    'message': 'Servicio RAG no cargado. Se cargará cuando sea necesario.'
                }
            })
    except Exception as e:
        logger.error(f"Error obteniendo stats RAG: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'stats': {
                'total_documents': 0,
                'embeddings_model': 'N/A',
                'vector_store': 'error',
                'sources': [],
                'service_loaded': False
            }
        }), 500

@app.route('/api/search-documents', methods=['POST'])
def search_documents():
    """Buscar en documentos sin generar respuesta"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Query requerido',
                'status': 'error'
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 3)
        
        rag = get_rag_service()
        results = rag.search(query, top_k)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error buscando documentos: {str(e)}")
        return jsonify({
            'error': 'Error en búsqueda',
            'message': str(e),
            'status': 'error'
        }), 500

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    return jsonify({
        'error': 'Error interno del servidor',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    logger.info("Iniciando ARB-BOT...")
    logger.info(f"Modo: {config_name}")
    logger.info(f"Proveedor API: {app.config.get('API_PROVIDER', 'groq')}")
    
    # Obtener puerto de variable de entorno (para producción)
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['FLASK_DEBUG']
    )
