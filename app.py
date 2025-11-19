"""
ARB-BOT - Aplicación Principal
Sistema de chatbot institucional con IA usando RAG
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
import logging

from config import config
from models.ai_model import AIModel
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

def get_ai_model():
    """Obtener modelo de IA (carga bajo demanda)"""
    global ai_model, content_generator
    if ai_model is None:
        logger.info("Cargando modelo de IA (primera vez)...")
        ai_model = AIModel(app.config['DEFAULT_MODEL'])
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
            if os.path.exists(INDEX_FILE):
                try:
                    logger.info(f"Intentando cargar índice desde: {INDEX_FILE}")
                    rag_service.load_index(INDEX_FILE)
                    logger.info("Documentos institucionales cargados desde índice")
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
# Usar disco persistente si está disponible (Render), sino usar directorio local
if os.path.exists('/persistent'):
    UPLOAD_FOLDER = '/persistent/documents'
    INDEX_FILE = '/persistent/rag_index.json'
    logger.info("Usando disco persistente de Render para almacenamiento")
else:
    UPLOAD_FOLDER = 'documents'
    INDEX_FILE = 'rag_index.json'
    logger.info("Usando almacenamiento local (desarrollo)")

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Crear directorio si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    """Pre-cargar modelos manualmente (útil para Render)"""
    try:
        logger.info("Iniciando warmup de modelos...")
        
        # Cargar modelo de IA
        get_ai_model()
        logger.info("Modelo de IA cargado")
        
        # Cargar RAG si hay documentos
        if os.path.exists(INDEX_FILE):
            get_rag_service()
            logger.info("Servicio RAG cargado")
        
        return jsonify({
            'status': 'success',
            'message': 'Modelos pre-cargados exitosamente',
            'ai_model_loaded': ai_model is not None,
            'rag_loaded': rag_service is not None
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
        try:
            rag = get_rag_service()
            if rag and rag.get_stats()['total_documents'] > 0:
                context = rag.get_context_for_query(processed_input, top_k=3)
                logger.info(f"Contexto encontrado: {len(context)} caracteres")
            else:
                logger.info("No hay documentos cargados en RAG - generando sin contexto")
        except Exception as e:
            logger.warning(f"Error obteniendo contexto RAG (continuando sin contexto): {str(e)}")
            context = ""
        
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
            'model_used': app.config['DEFAULT_MODEL'],
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
                model_used=app.config['DEFAULT_MODEL'],
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
        'models': app.config['AVAILABLE_MODELS'],
        'current_model': app.config['DEFAULT_MODEL']
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
                'active_model': app.config['DEFAULT_MODEL'],
                'system_status': 'operational',
                'last_interaction': last_interaction_time,
                'models_available': len(app.config['AVAILABLE_MODELS']),
                'models_loaded': ai_model is not None
            }
        })
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({
            'status': 'success',
            'stats': {
                'total_interactions': 0,
                'active_model': app.config['DEFAULT_MODEL'],
                'system_status': 'operational',
                'last_interaction': None,
                'models_available': len(app.config['AVAILABLE_MODELS']),
                'models_loaded': False
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
    """Cambiar el modelo de IA activo"""
    # Verificar autenticación
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        
        if not data or 'model' not in data:
            return jsonify({
                'error': 'Modelo requerido',
                'status': 'error'
            }), 400
        
        model_name = data['model']
        
        # Validar que el modelo existe
        if model_name not in app.config['AVAILABLE_MODELS']:
            return jsonify({
                'error': f'Modelo {model_name} no disponible',
                'status': 'error',
                'available_models': list(app.config['AVAILABLE_MODELS'].keys())
            }), 400
        
        # Cambiar modelo
        global ai_model, content_generator
        # Liberar modelo anterior si existe
        if ai_model is not None:
            del ai_model
            del content_generator
            import gc
            gc.collect()
        
        ai_model = AIModel(model_name)
        content_generator = ContentGenerator(ai_model, text_processor)
        app.config['DEFAULT_MODEL'] = model_name
        
        logger.info(f"Modelo cambiado a: {model_name}")
        
        return jsonify({
            'status': 'success',
            'message': f'Modelo cambiado a {model_name}',
            'current_model': model_name
        })
        
    except Exception as e:
        logger.error(f"Error cambiando modelo: {str(e)}")
        return jsonify({
            'error': 'Error al cambiar modelo',
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
            # Si el documento es muy grande, se procesará en lotes más pequeños
            try:
                # Determinar límite de páginas basado en el tamaño del archivo
                if file_size_mb > 5:
                    # Archivos grandes: procesar en lotes más pequeños
                    max_pages = 100
                    logger.info(f"Archivo grande ({file_size_mb:.2f} MB). Procesando hasta {max_pages} páginas por lote.")
                else:
                    # Archivos normales: procesar todo
                    max_pages = None  # Sin límite
                    logger.info(f"Procesando documento completo ({file_size_mb:.2f} MB)")
                
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
            rag = get_rag_service()
            batch_size = 20  # Procesar en lotes más pequeños (20 chunks)
            
            total_batches = (len(chunks) - 1) // batch_size + 1
            logger.info(f"Procesando {len(chunks)} chunks en {total_batches} lotes de {batch_size}...")
            
            import time
            start_time = time.time()
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                try:
                    rag.add_documents(batch)
                    elapsed = time.time() - start_time
                    logger.info(f"Procesado lote {i//batch_size + 1}/{total_batches} ({len(batch)} chunks) - Tiempo: {elapsed:.1f}s")
                except Exception as batch_error:
                    logger.error(f"Error procesando lote {i//batch_size + 1}: {str(batch_error)}")
                    # Continuar con el siguiente lote
                    continue
            
            # Guardar índice
            logger.info("Guardando índice...")
            rag.save_index(INDEX_FILE)
            
            return jsonify({
                'status': 'success',
                'message': f'Documento {filename} procesado exitosamente',
                'chunks_added': len(chunks),
                'total_documents': rag.get_stats()['total_documents']
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
    logger.info(f"Modelo por defecto: {app.config['DEFAULT_MODEL']}")
    
    # Obtener puerto de variable de entorno (para producción)
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['FLASK_DEBUG']
    )
