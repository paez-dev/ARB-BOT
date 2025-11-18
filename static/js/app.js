// ARB-BOT - JavaScript Principal

class ARBBot {
    constructor() {
        this.currentModel = 'distilgpt2';
        this.history = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadHistory();
        this.loadStats();
        this.loadRAGStats();
        this.checkSystemHealth();
        this.autoWarmup(); // Pre-cargar modelos automáticamente
    }

    setupEventListeners() {
        // Formulario de generación
        document.getElementById('generateForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateContent();
        });

        // Selector de modelo
        document.getElementById('modelSelector')?.addEventListener('change', (e) => {
            this.changeModel(e.target.value);
        });

        // Botón de limpiar
        document.getElementById('clearBtn')?.addEventListener('click', () => {
            this.clearInput();
        });

        // Botón de historial
        document.getElementById('showHistoryBtn')?.addEventListener('click', () => {
            this.toggleHistory();
        });

        // Formulario de carga de documentos
        document.getElementById('uploadForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadDocument();
        });
    }

    async generateContent() {
        const userInput = document.getElementById('userInput').value.trim();
        const inputElement = document.getElementById('userInput');

        // Validación
        if (!this.validateInput(userInput)) {
            return;
        }

        // Agregar mensaje del usuario al chat
        this.addMessageToChat(userInput, 'user');
        
        // Limpiar input
        inputElement.value = '';
        inputElement.style.height = 'auto';
        document.getElementById('charCount').textContent = '0/500';
        
        // Deshabilitar botón de envío
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = true;

        // Mostrar loading
        this.showLoading(true);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    input: userInput
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Agregar respuesta del bot al chat
                this.addMessageToChat(data.generated_content, 'bot', data);
                this.addToHistory(data);
                this.loadStats();
            } else {
                this.addMessageToChat(
                    `❌ Error: ${data.error || 'Error desconocido'}`,
                    'bot'
                );
            }

        } catch (error) {
            console.error('Error:', error);
            this.addMessageToChat(
                '❌ Error al comunicarse con el servidor. Por favor, intenta de nuevo.',
                'bot'
            );
        } finally {
            this.showLoading(false);
            sendBtn.disabled = false;
            inputElement.focus();
        }
    }

    validateInput(text) {
        if (text.length < 3) {
            this.showError('El texto debe tener al menos 3 caracteres');
            return false;
        }

        if (text.length > 500) {
            this.showError('El texto no puede exceder 500 caracteres');
            return false;
        }

        return true;
    }

    addMessageToChat(text, type, data = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const time = new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        let avatarIcon = type === 'user' ? '<i class="bi bi-person-fill"></i>' : '<i class="bi bi-robot"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatarIcon}
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll al final
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Si hay fuentes, agregarlas después
        if (data && data.metadata && data.metadata.context_used) {
            setTimeout(() => {
                this.showSourcesInChat(data, messageDiv);
            }, 500);
        }
    }

    formatMessage(text) {
        // Escapar HTML y convertir saltos de línea
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');
    }

    async showSourcesInChat(data, messageElement) {
        try {
            const response = await fetch('/api/search-documents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: data.input,
                    top_k: 3
                })
            });

            const searchData = await response.json();
            if (searchData.status === 'success' && searchData.results.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'mt-2 p-2 bg-light rounded';
                sourcesDiv.style.fontSize = '0.85rem';
                sourcesDiv.innerHTML = `
                    <strong>📄 Fuentes utilizadas:</strong>
                    ${searchData.results.map((result, index) => `
                        <div class="mt-1">
                            • ${result.source || 'Documento'} 
                            <small class="text-muted">(${(result.similarity * 100).toFixed(1)}% relevante)</small>
                        </div>
                    `).join('')}
                `;
                
                const messageContent = messageElement.querySelector('.message-content');
                messageContent.appendChild(sourcesDiv);
            }
        } catch (error) {
            console.error('Error obteniendo fuentes:', error);
        }
    }

    async showSources(data) {
        // Buscar fuentes utilizadas
        try {
            const response = await fetch('/api/search-documents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: data.input,
                    top_k: 3
                })
            });

            const searchData = await response.json();
            if (searchData.status === 'success' && searchData.results.length > 0) {
                const sourcesSection = document.getElementById('sourcesSection');
                const sourcesList = document.getElementById('sourcesList');
                
                sourcesList.innerHTML = searchData.results.map((result, index) => `
                    <div class="alert alert-light mb-2">
                        <strong>Fuente ${index + 1}:</strong> ${result.source || 'Documento'}<br>
                        <small class="text-muted">Similitud: ${(result.similarity * 100).toFixed(1)}%</small>
                        <div class="mt-2 small text-muted">
                            ${result.text.substring(0, 150)}${result.text.length > 150 ? '...' : ''}
                        </div>
                    </div>
                `).join('');
                
                sourcesSection.style.display = 'block';
            }
        } catch (error) {
            console.error('Error obteniendo fuentes:', error);
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        loading.style.display = show ? 'block' : 'none';
    }

    hideResult() {
        const resultCard = document.getElementById('resultCard');
        resultCard.style.display = 'none';
    }

    showError(message) {
        // Crear o actualizar alerta de error
        let alertDiv = document.getElementById('errorAlert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.id = 'errorAlert';
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
            alertDiv.setAttribute('role', 'alert');
            document.querySelector('.main-container').insertBefore(alertDiv, document.querySelector('.main-container').firstChild);
        }
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Auto-dismiss después de 5 segundos
        setTimeout(() => {
            if (alertDiv) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async changeModel(modelName) {
        try {
            const response = await fetch('/api/change-model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: modelName
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.currentModel = modelName;
                this.showSuccess(`Modelo cambiado a ${modelName}`);
            } else {
                this.showError(data.error || 'Error al cambiar modelo');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Error al cambiar modelo');
        }
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/history?limit=10');
            const data = await response.json();

            if (data.status === 'success') {
                this.history = data.history;
                this.displayHistory();
            }
        } catch (error) {
            console.error('Error cargando historial:', error);
        }
    }

    displayHistory() {
        const historyContainer = document.getElementById('historyContainer');
        if (!historyContainer) return;

        if (this.history.length === 0) {
            historyContainer.innerHTML = '<p class="text-muted">No hay historial disponible</p>';
            return;
        }

        historyContainer.innerHTML = this.history.map((item, index) => `
            <div class="history-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <strong>Input:</strong> ${item.user_input.substring(0, 100)}${item.user_input.length > 100 ? '...' : ''}<br>
                        <strong>Output:</strong> ${item.generated_output ? item.generated_output.substring(0, 100) + (item.generated_output.length > 100 ? '...' : '') : 'N/A'}<br>
                        <small class="text-muted">${new Date(item.timestamp).toLocaleString()}</small>
                    </div>
                    <span class="badge bg-primary">${item.model_used || 'N/A'}</span>
                </div>
            </div>
        `).join('');
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            if (data.status === 'success') {
                const stats = data.stats;
                document.getElementById('totalInteractions').textContent = stats.total_interactions || 0;
                document.getElementById('activeModel').textContent = stats.active_model || 'N/A';
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    async checkSystemHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            console.log('Sistema:', data);
        } catch (error) {
            console.error('Error verificando sistema:', error);
        }
    }

    addToHistory(data) {
        this.history.unshift({
            user_input: data.input,
            generated_output: data.generated_content,
            model_used: data.model_used,
            timestamp: data.timestamp
        });

        // Mantener solo los últimos 10
        if (this.history.length > 10) {
            this.history = this.history.slice(0, 10);
        }

        this.displayHistory();
    }

    clearInput() {
        document.getElementById('userInput').value = '';
        this.hideResult();
    }

    toggleHistory() {
        const historySection = document.getElementById('historySection');
        if (historySection) {
            historySection.style.display = historySection.style.display === 'none' ? 'block' : 'none';
        }
    }

    showSuccess(message) {
        // Similar a showError pero con alert-success
        let alertDiv = document.getElementById('successAlert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.id = 'successAlert';
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.setAttribute('role', 'alert');
            document.querySelector('.main-container').insertBefore(alertDiv, document.querySelector('.main-container').firstChild);
        }
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        setTimeout(() => {
            if (alertDiv) {
                alertDiv.remove();
            }
        }, 3000);
    }

    async uploadDocument() {
        const fileInput = document.getElementById('documentFile');
        const uploadStatus = document.getElementById('uploadStatus');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            this.showError('Por favor selecciona un archivo');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        uploadStatus.style.display = 'block';
        uploadStatus.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Procesando documento...';

        try {
            const response = await fetch('/api/upload-document', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                uploadStatus.innerHTML = `
                    <div class="alert alert-success">
                        ✅ ${data.message}<br>
                        <small>Chunks agregados: ${data.chunks_added} | Total documentos: ${data.total_documents}</small>
                    </div>
                `;
                this.loadRAGStats();
                fileInput.value = '';
            } else {
                uploadStatus.innerHTML = `
                    <div class="alert alert-danger">
                        ❌ Error: ${data.error || 'Error desconocido'}
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error:', error);
            uploadStatus.innerHTML = `
                <div class="alert alert-danger">
                    ❌ Error al comunicarse con el servidor
                </div>
            `;
        }
    }

    async loadRAGStats() {
        try {
            const response = await fetch('/api/rag-stats');
            const data = await response.json();

            if (data.status === 'success') {
                const stats = data.stats;
                const ragStatsDiv = document.getElementById('ragStats');
                
                if (stats.total_documents > 0) {
                    ragStatsDiv.innerHTML = `
                        <div class="mt-2">
                            <span class="badge bg-success">${stats.total_documents} documentos cargados</span><br>
                            <small class="text-muted">
                                Fuentes: ${stats.sources.join(', ')}
                            </small>
                        </div>
                    `;
                } else {
                    ragStatsDiv.innerHTML = `
                        <div class="alert alert-warning mt-2">
                            <small>⚠️ No hay documentos cargados. Sube documentos para que el sistema pueda responder preguntas.</small>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Error cargando stats RAG:', error);
        }
    }

    async autoWarmup() {
        /**
         * Pre-cargar modelos automáticamente al abrir la app
         * Solo se ejecuta una vez por sesión para evitar múltiples warmups
         */
        try {
            // Verificar si ya se hizo warmup en esta sesión
            if (sessionStorage.getItem('warmup_done') === 'true') {
                console.log('Modelos ya pre-cargados en esta sesión');
                return;
            }

            // Verificar si los modelos ya están cargados
            const healthResponse = await fetch('/api/health');
            const healthData = await healthResponse.json();
            
            if (healthData.models_loaded) {
                console.log('Modelos ya están cargados');
                sessionStorage.setItem('warmup_done', 'true');
                return;
            }

            // Mostrar indicador de progreso
            this.showWarmupProgress();
            
            // Hacer warmup con seguimiento de progreso
            this.startWarmupWithProgress();
            
        } catch (error) {
            // No es crítico si falla
            console.log('Warmup automático no disponible:', error);
        }
    }

    showWarmupProgress() {
        // Crear contenedor de progreso
        const progressContainer = document.createElement('div');
        progressContainer.id = 'warmupProgressContainer';
        progressContainer.className = 'warmup-progress-container';
        progressContainer.innerHTML = `
            <div class="warmup-progress-card">
                <div class="d-flex align-items-center mb-2">
                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <strong>Preparando modelos de IA...</strong>
                </div>
                <div class="progress mb-2" style="height: 6px;">
                    <div id="warmupProgressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 0%"></div>
                </div>
                <small class="text-muted" id="warmupStatus">Iniciando carga de modelos...</small>
            </div>
        `;
        document.body.appendChild(progressContainer);
    }

    async startWarmupWithProgress() {
        const progressBar = document.getElementById('warmupProgressBar');
        const statusText = document.getElementById('warmupStatus');
        
        // Simular progreso mientras se carga
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += Math.random() * 5;
                if (progress > 90) progress = 90;
                progressBar.style.width = progress + '%';
                
                // Actualizar mensajes según el progreso
                if (progress < 30) {
                    statusText.textContent = 'Descargando modelo de IA...';
                } else if (progress < 60) {
                    statusText.textContent = 'Cargando modelo de embeddings...';
                } else if (progress < 90) {
                    statusText.textContent = 'Inicializando servicios...';
                }
            }
        }, 500);

        try {
            // Hacer warmup
            const response = await fetch('/api/warmup', { 
                method: 'POST'
            });
            
            const data = await response.json();
            
            // Completar progreso
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-success');
            statusText.textContent = '✅ Modelos listos';
            
            if (data.status === 'success') {
                console.log('✅ Modelos pre-cargados exitosamente');
                sessionStorage.setItem('warmup_done', 'true');
                
                // Ocultar progreso después de 2 segundos
                setTimeout(() => {
                    this.hideWarmupProgress();
                    this.showWarmupSuccess();
                }, 2000);
            } else {
                statusText.textContent = '⚠️ Carga parcial (se cargarán bajo demanda)';
                setTimeout(() => {
                    this.hideWarmupProgress();
                }, 3000);
            }
        } catch (error) {
            // No es crítico si falla
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-warning');
            statusText.textContent = '⚠️ Los modelos se cargarán cuando los necesites';
            
            console.log('Warmup opcional falló (no crítico):', error);
            
            setTimeout(() => {
                this.hideWarmupProgress();
            }, 3000);
        }
    }

    hideWarmupProgress() {
        const container = document.getElementById('warmupProgressContainer');
        if (container) {
            container.style.opacity = '0';
            container.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                if (container.parentNode) {
                    container.remove();
                }
            }, 500);
        }
    }

    showWarmupSuccess() {
        // Mostrar notificación discreta de que los modelos están listos
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '300px';
        notification.innerHTML = `
            <small>✅ Modelos de IA listos</small>
            <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        // Auto-ocultar después de 3 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.arbBot = new ARBBot();
});

