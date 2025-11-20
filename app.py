"""
ARB-BOT - Aplicación Principal
Sistema de chatbot institucional con IA usando RAG
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
import logging
import threading

from config import config
from models.api_model import APIModel
from services.text_processor import TextProcessor
from services.generator import ContentGenerator
from services.document_processor import DocumentProcessor
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
document_processor = DocumentProcessor()

# Modelos de IA se inicializarán bajo demanda (lazy loading)
ai_model = None
content_generator = None
rag_service = None

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

    if load_rag and os.path.exists(INDEX_FILE):
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
            
            # Cargar índice si existe (no crítico si falla)
            # IMPORTANTE: Si hay un índice viejo, puede estar cargando datos antiguos
            if os.path.exists(INDEX_FILE):
                try:
                    logger.info(f"⚠️ Intentando cargar índice desde: {INDEX_FILE}")
                    logger.info("⚠️ NOTA: Si acabas de procesar un documento nuevo, este índice puede ser viejo.")
                    logger.info("⚠️ El nuevo índice se guarda después del procesamiento, pero se carga al iniciar.")
                    rag_service.load_index(INDEX_FILE)
                    total_docs = len(rag_service.document_store) if rag_service.document_store else 0
                    logger.info(f"✅ Documentos institucionales cargados desde índice: {total_docs} documentos")
                    if total_docs > 0:
                        logger.info(f"   Si esperabas más documentos, puede que estés usando un índice viejo.")
                except Exception as e:
                    logger.warning(f"No se pudo cargar índice (continuando sin documentos): {e}")
                    # Continuar sin índice - se pueden agregar documentos después
            else:
                logger.info("No hay índice existente - servicio RAG listo para nuevos documentos")
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
    INDEX_FILE = '/persistent/rag_index.json'
    logger.info("Usando disco persistente para almacenamiento")
else:
    UPLOAD_FOLDER = 'documents'
    INDEX_FILE = 'rag_index.json'
    logger.info("Usando almacenamiento local (desarrollo)")

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
            if rag and rag.get_stats()['total_documents'] > 0:
                context = rag.get_context_for_query(processed_input, top_k=10)
                logger.info(f"Contexto encontrado: {len(context)} caracteres")
            else:
                logger.info("No hay documentos cargados en RAG - generando sin contexto")
        except Exception as e:
            logger.warning(f"Error obteniendo contexto RAG (continuando sin contexto): {str(e)}")
            context = ""
            rag = None
        
        # Paso 3: Generar contenido usando IA con contexto
        ai_model_instance, generator = get_ai_model()
        generated_content = generator.generate(
            processed_input,
            max_tokens=app.config['MAX_TOKENS'],
            temperature=app.config['TEMPERATURE'],
            context=context if context else None
        )
        logger.info("Contenido generado exitosamente")
        
        # Paso 3: Preparar respuesta
        response = {
            'status': 'success',
            'input': user_input,
            'processed_input': processed_input,
            'generated_content': generated_content,
            'model_used': f"{app.config.get('API_PROVIDER', 'groq')} - {ai_model_instance.model_name if ai_model_instance else 'N/A'}",
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'input_length': len(user_input),
                'output_length': len(generated_content),
                'processing_time': 'N/A',
                'context_used': len(context) > 0,
                'rag_documents': rag.get_stats()['total_documents'] if rag else 0
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
                model_used=f"{app.config.get('API_PROVIDER', 'groq')} - {ai_model_instance.model_name if ai_model_instance else 'N/A'}",
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

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Subir y procesar documento institucional"""
    # Verificar autenticación
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No se proporcionó archivo',
                'status': 'error'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No se seleccionó archivo',
                'status': 'error'
            }), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Leer contenido del archivo
            file_content = file.read()
            file_size = len(file_content)  # Obtener tamaño desde el contenido
            
            # Guardar archivo localmente (necesario para procesamiento)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            # También guardar en Supabase si está configurado (para persistencia)
            try:
                from services.storage_service import StorageService
                storage = StorageService()
                if storage.use_supabase:
                    # Determinar content type
                    content_type = 'application/pdf' if filename.endswith('.pdf') else \
                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if filename.endswith('.docx') else \
                                 'text/plain'
                    storage.upload_file(filepath, file_content, content_type)
                    logger.info(f"Archivo también guardado en Supabase para persistencia")
            except ImportError:
                pass  # Supabase no disponible, solo usar local
            
            logger.info(f"Procesando documento: {filename}")
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb > 10:
                logger.warning(f"Archivo grande detectado: {file_size_mb:.2f} MB. El procesamiento puede tardar varios minutos.")
            
            # Procesar documento completo
            # Procesar todas las páginas del documento (sin límite)
            try:
                max_pages = None  # Sin límite - procesar todo el documento
                logger.info(f"Procesando documento completo ({file_size_mb:.2f} MB) - todas las páginas")
                
                chunks = document_processor.process_document(filepath, max_pages=max_pages)
            except Exception as e:
                logger.error(f"Error procesando documento: {str(e)}")
                # Limpiar archivo si hay error
                try:
                    os.remove(filepath)
                except:
                    pass
                return jsonify({
                    'error': f'Error procesando documento: {str(e)}',
                    'status': 'error',
                    'hint': 'El documento puede ser muy grande o estar corrupto. Intenta con un archivo más pequeño o verifica que el PDF no esté protegido.'
                }), 500
            
            if not chunks or len(chunks) == 0:
                return jsonify({
                    'error': 'No se pudo extraer contenido del documento',
                    'status': 'error',
                    'hint': 'El documento puede estar vacío o protegido.'
                }), 400
            
            logger.info(f"Agregando {len(chunks)} chunks al sistema RAG...")
            
            # Agregar al sistema RAG en lotes más pequeños para evitar problemas de memoria
            try:
                rag = get_rag_service()
            except Exception as rag_error:
                logger.error(f"Error cargando servicio RAG: {str(rag_error)}")
                return jsonify({
                    'error': 'Error cargando sistema de búsqueda. El documento se guardó pero no se pudo procesar.',
                    'status': 'error',
                    'hint': 'El sistema puede estar sin memoria. Intenta más tarde o con un documento más pequeño.'
                }), 500
            
            # Procesar en lotes pequeños para ahorrar memoria y permitir procesamiento de documentos grandes
            batch_size = 20  # 20 chunks por lote (aumentado para Railway con más memoria)
            total_batches = (len(chunks) - 1) // batch_size + 1
            logger.info(f"Procesando {len(chunks)} chunks en {total_batches} lotes de {batch_size}...")
            
            import time
            import gc
            start_time = time.time()
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                try:
                    rag.add_documents(batch)
                    elapsed = time.time() - start_time
                    logger.info(f"Procesado lote {i//batch_size + 1}/{total_batches} ({len(batch)} chunks) - Tiempo: {elapsed:.1f}s")
                    
                    # Limpiar memoria después de cada lote para documentos grandes
                    if total_batches > 20:  # Solo para documentos con muchos lotes
                        gc.collect()
                except Exception as batch_error:
                    logger.error(f"Error procesando lote {i//batch_size + 1}: {str(batch_error)}")
                    # Continuar con el siguiente lote
                    continue
            
            # Guardar índice
            total_docs_before = rag.get_stats()['total_documents']
            logger.info(f"💾 Guardando índice nuevo con {len(chunks)} chunks en: {INDEX_FILE}")
            logger.info(f"   Total de documentos ANTES de guardar: {total_docs_before}")
            rag.save_index(INDEX_FILE)
            total_docs_after = rag.get_stats()['total_documents']
            logger.info(f"✅ Índice guardado exitosamente. Total de documentos DESPUÉS: {total_docs_after}")
            
            # IMPORTANTE: Forzar recarga del servicio RAG para que use el nuevo índice
            # Esto asegura que las siguientes búsquedas usen los nuevos documentos
            global rag_service
            logger.info("🔄 Recargando servicio RAG para usar el nuevo índice...")
            try:
                # Recargar el servicio RAG para que cargue el nuevo índice
                rag_service = None  # Limpiar instancia vieja
                rag = get_rag_service()  # Esto cargará el nuevo índice
                logger.info(f"✅ Servicio RAG recargado. Total de documentos ahora: {rag.get_stats()['total_documents']}")
            except Exception as reload_error:
                logger.warning(f"⚠️ No se pudo recargar RAG (continuando con instancia en memoria): {reload_error}")
                # Continuar con la instancia en memoria que ya tiene los nuevos documentos
            
            # Mensaje informativo
            message = f'Documento {filename} procesado exitosamente (todas las páginas)'
            
            return jsonify({
                'status': 'success',
                'message': message,
                'chunks_added': len(chunks),
                'total_documents': rag.get_stats()['total_documents'],
                'pages_processed': 'todas'
            })
        else:
            return jsonify({
                'error': 'Formato de archivo no permitido',
                'allowed_formats': list(ALLOWED_EXTENSIONS),
                'status': 'error'
            }), 400
            
    except Exception as e:
        logger.error(f"Error subiendo documento: {str(e)}")
        return jsonify({
            'error': 'Error procesando documento',
            'message': str(e),
            'status': 'error'
        }), 500

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
            # Verificar si hay índice sin cargar el servicio completo
            has_index = os.path.exists(INDEX_FILE)
            return jsonify({
                'status': 'success',
                'stats': {
                    'total_documents': 0,
                    'embeddings_model': 'N/A',
                    'has_index': has_index,
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
                'has_index': False,
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
