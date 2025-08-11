/**
 * JavaScript principal pour TradingAgents Web Interface
 * Gère les interactions utilisateur, les WebSockets et les animations
 */

class TradingAgentsApp {
    constructor() {
        this.socket = null;
        this.currentSession = null;
        this.analysisInProgress = false;
        this.charts = {};
        this.config = this.loadConfig();
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.setupEventListeners();
        this.loadStoredData();
        this.initializeAnimations();
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connecté au serveur WebSocket');
            this.showNotification('Connexion établie', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Déconnecté du serveur WebSocket');
            this.showNotification('Connexion perdue', 'warning');
        });
        
        this.socket.on('analysis_status', (data) => {
            this.handleAnalysisStatus(data);
        });
        
        this.socket.on('analysis_progress', (data) => {
            this.handleAnalysisProgress(data);
        });
        
        this.socket.on('analysis_complete', (data) => {
            this.handleAnalysisComplete(data);
        });
        
        this.socket.on('analysis_error', (data) => {
            this.handleAnalysisError(data);
        });
        
        this.socket.on('agent_update', (data) => {
            this.handleAgentUpdate(data);
        });
    }
    
    setupEventListeners() {
        // Gestion des formulaires
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'analysisForm') {
                e.preventDefault();
                this.startAnalysis(e.target);
            }
        });
        
        // Gestion des clics sur les boutons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                const action = e.target.getAttribute('data-action');
                this.handleAction(action, e.target);
            }
        });
        
        // Gestion du redimensionnement de la fenêtre
        window.addEventListener('resize', () => {
            this.resizeCharts();
        });
        
        // Gestion de la visibilité de la page
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }
    
    loadStoredData() {
        // Charger la configuration depuis localStorage
        const storedConfig = localStorage.getItem('tradingagents_config');
        if (storedConfig) {
            try {
                this.config = { ...this.config, ...JSON.parse(storedConfig) };
            } catch (e) {
                console.error('Erreur lors du chargement de la configuration:', e);
            }
        }
        
        // Charger les sessions récentes
        const recentSessions = localStorage.getItem('tradingagents_recent_sessions');
        if (recentSessions) {
            try {
                this.recentSessions = JSON.parse(recentSessions);
                this.displayRecentSessions();
            } catch (e) {
                console.error('Erreur lors du chargement des sessions récentes:', e);
            }
        }
    }
    
    initializeAnimations() {
        // Animer l'apparition des éléments
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Observer tous les éléments avec la classe animate-on-scroll
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }
    
    startAnalysis(form) {
        if (this.analysisInProgress) {
            this.showNotification('Une analyse est déjà en cours', 'warning');
            return;
        }
        
        const formData = new FormData(form);
        const analysisData = this.prepareAnalysisData(formData);
        
        // Valider les données
        if (!this.validateAnalysisData(analysisData)) {
            return;
        }
        
        this.analysisInProgress = true;
        this.currentSession = `session_${Date.now()}_${analysisData.ticker}`;
        
        // Mettre à jour l'interface
        this.updateAnalysisUI(true);
        
        // Envoyer la requête
        fetch('/api/start_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.currentSession = result.session_id;
                this.showNotification('Analyse démarrée avec succès', 'success');
                this.trackAnalysisProgress();
            } else {
                throw new Error(result.error || 'Erreur inconnue');
            }
        })
        .catch(error => {
            this.handleAnalysisError({ error: error.message });
        });
    }
    
    prepareAnalysisData(formData) {
        // Récupérer les analystes sélectionnés
        const selectedAnalysts = [];
        const analystCheckboxes = document.querySelectorAll('input[name="analysts"]:checked');
        analystCheckboxes.forEach(checkbox => {
            selectedAnalysts.push(checkbox.value);
        });
        
        return {
            ticker: formData.get('ticker'),
            trade_date: formData.get('trade_date'),
            config: {
                ...this.config,
                selected_analysts: selectedAnalysts,
                max_debate_rounds: parseInt(formData.get('research_depth') || '2'),
                max_risk_discuss_rounds: parseInt(formData.get('research_depth') || '2')
            }
        };
    }
    
    validateAnalysisData(data) {
        if (!data.ticker || data.ticker.trim() === '') {
            this.showNotification('Veuillez entrer un symbole de ticker', 'danger');
            return false;
        }
        
        if (!data.trade_date) {
            this.showNotification('Veuillez sélectionner une date d\'analyse', 'danger');
            return false;
        }
        
        if (!data.config.selected_analysts || data.config.selected_analysts.length === 0) {
            this.showNotification('Veuillez sélectionner au moins un analyste', 'danger');
            return false;
        }
        
        // Vérifier que la date n'est pas dans le futur
        const selectedDate = new Date(data.trade_date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate > today) {
            this.showNotification('La date d\'analyse ne peut pas être dans le futur', 'danger');
            return false;
        }
        
        return true;
    }
    
    updateAnalysisUI(inProgress) {
        const startBtn = document.getElementById('startAnalysisBtn');
        const progressCard = document.getElementById('resultsCard');
        
        if (inProgress) {
            if (startBtn) {
                startBtn.disabled = true;
                startBtn.innerHTML = '<span class="loading-spinner-enhanced me-2"></span>Analyse en cours...';
            }
            
            if (progressCard) {
                progressCard.style.display = 'block';
                progressCard.classList.add('fade-in-up');
            }
            
            this.resetAgentStatuses();
        } else {
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Démarrer l\'Analyse';
            }
            
            this.analysisInProgress = false;
        }
    }
    
    resetAgentStatuses() {
        const statusIndicators = document.querySelectorAll('.status-indicator');
        statusIndicators.forEach(indicator => {
            indicator.className = 'status-indicator status-pending';
        });
    }
    
    trackAnalysisProgress() {
        // Simuler la progression de l'analyse
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (!this.analysisInProgress) {
                clearInterval(progressInterval);
                return;
            }
            
            progress += Math.random() * 10;
            if (progress > 95) progress = 95;
            
            this.updateProgressBar(progress);
        }, 1000);
    }
    
    updateProgressBar(percentage) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
        }
        
        if (progressText) {
            progressText.textContent = Math.round(percentage) + '%';
        }
    }
    
    handleAnalysisStatus(data) {
        console.log('Statut d\'analyse:', data);
        
        if (data.agent) {
            this.updateAgentStatus(data.agent, data.status);
        }
        
        if (data.message) {
            this.addLogMessage(data.message, 'info');
        }
    }
    
    handleAnalysisProgress(data) {
        if (data.progress !== undefined) {
            this.updateProgressBar(data.progress);
        }
        
        if (data.current_step) {
            this.updateCurrentStep(data.current_step);
        }
    }
    
    handleAnalysisComplete(data) {
        console.log('Analyse terminée:', data);
        
        this.updateProgressBar(100);
        this.updateAnalysisUI(false);
        
        // Afficher les résultats
        this.displayAnalysisResults(data.result);
        
        // Sauvegarder dans les sessions récentes
        this.saveRecentSession(data.result);
        
        this.showNotification('Analyse terminée avec succès!', 'success');
        
        // Animation de célébration
        this.celebrateCompletion();
    }
    
    handleAnalysisError(data) {
        console.error('Erreur d\'analyse:', data);
        
        this.updateAnalysisUI(false);
        this.showNotification('Erreur lors de l\'analyse: ' + data.error, 'danger');
        
        // Réinitialiser les statuts des agents
        this.resetAgentStatuses();
    }
    
    handleAgentUpdate(data) {
        if (data.agent && data.status) {
            this.updateAgentStatus(data.agent, data.status);
        }
        
        if (data.report) {
            this.updateAgentReport(data.agent, data.report);
        }
    }
    
    updateAgentStatus(agentName, status) {
        const statusElement = document.getElementById(`${agentName.toLowerCase()}-status`);
        if (statusElement) {
            statusElement.className = `status-indicator status-${status}`;
            
            // Ajouter une animation pour les changements de statut
            statusElement.classList.add('bounce-animation');
            setTimeout(() => {
                statusElement.classList.remove('bounce-animation');
            }, 1000);
        }
    }
    
    updateCurrentStep(step) {
        const stepElement = document.getElementById('currentStep');
        if (stepElement) {
            stepElement.textContent = step;
            stepElement.classList.add('slide-in-right');
            setTimeout(() => {
                stepElement.classList.remove('slide-in-right');
            }, 500);
        }
    }
    
    displayAnalysisResults(result) {
        const resultsDiv = document.getElementById('analysisResults');
        if (!resultsDiv) return;
        
        const html = `
            <div class="alert alert-success alert-enhanced">
                <h5><i class="fas fa-check-circle me-2"></i>Analyse Terminée</h5>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Ticker:</strong> ${result.ticker}</p>
                        <p><strong>Date:</strong> ${result.trade_date}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Décision:</strong> ${this.getDecisionBadge(result.decision)}</p>
                        <p><strong>Session:</strong> <code>${result.session_id}</code></p>
                    </div>
                </div>
            </div>
            <div class="text-center mt-3">
                <button class="btn btn-gradient-primary" onclick="window.location.href='/dashboard?session=${result.session_id}'">
                    <i class="fas fa-chart-line me-2"></i>Voir les Détails Complets
                </button>
                <button class="btn btn-outline-secondary ms-2" onclick="tradingApp.exportResults('${result.session_id}')">
                    <i class="fas fa-download me-2"></i>Exporter
                </button>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
        resultsDiv.classList.add('fade-in-up');
    }
    
    getDecisionBadge(decision) {
        if (!decision) return '<span class="badge bg-secondary">N/A</span>';
        
        const decisionUpper = decision.toUpperCase();
        let badgeClass = 'secondary';
        let icon = 'question';
        
        if (decisionUpper.includes('BUY')) {
            badgeClass = 'success';
            icon = 'arrow-up';
        } else if (decisionUpper.includes('SELL')) {
            badgeClass = 'danger';
            icon = 'arrow-down';
        } else if (decisionUpper.includes('HOLD')) {
            badgeClass = 'warning';
            icon = 'pause';
        }
        
        return `<span class="badge bg-${badgeClass}"><i class="fas fa-${icon} me-1"></i>${decision}</span>`;
    }
    
    saveRecentSession(result) {
        if (!this.recentSessions) {
            this.recentSessions = [];
        }
        
        // Ajouter la nouvelle session
        this.recentSessions.unshift({
            session_id: result.session_id,
            ticker: result.ticker,
            trade_date: result.trade_date,
            decision: result.decision,
            timestamp: new Date().toISOString()
        });
        
        // Garder seulement les 10 plus récentes
        this.recentSessions = this.recentSessions.slice(0, 10);
        
        // Sauvegarder dans localStorage
        localStorage.setItem('tradingagents_recent_sessions', JSON.stringify(this.recentSessions));
    }
    
    celebrateCompletion() {
        // Animation de confettis ou autre célébration
        const celebration = document.createElement('div');
        celebration.className = 'celebration-animation';
        celebration.innerHTML = '🎉';
        celebration.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 4rem;
            z-index: 9999;
            pointer-events: none;
            animation: bounce 1s ease-out;
        `;
        
        document.body.appendChild(celebration);
        
        setTimeout(() => {
            celebration.remove();
        }, 1000);
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.5s ease-out;
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    addLogMessage(message, type = 'info') {
        const logContainer = document.getElementById('logMessages');
        if (!logContainer) return;
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.innerHTML = `
            <span class="log-time">${new Date().toLocaleTimeString()}</span>
            <span class="log-message">${message}</span>
        `;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limiter le nombre d'entrées de log
        const logEntries = logContainer.querySelectorAll('.log-entry');
        if (logEntries.length > 100) {
            logEntries[0].remove();
        }
    }
    
    loadConfig() {
        return {
            llm_provider: 'openai',
            quick_think_llm: 'gpt-4o-mini',
            deep_think_llm: 'gpt-4o',
            max_debate_rounds: 2,
            max_risk_discuss_rounds: 2,
            online_tools: true,
            temperature: 0.7,
            max_tokens: 4000
        };
    }
    
    saveConfig(config) {
        this.config = { ...this.config, ...config };
        localStorage.setItem('tradingagents_config', JSON.stringify(this.config));
    }
    
    exportResults(sessionId) {
        fetch(`/api/get_results/${sessionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                this.showNotification('Erreur: ' + data.error, 'danger');
                return;
            }
            
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `analysis_${data.ticker}_${data.trade_date}.json`;
            link.click();
            
            this.showNotification('Résultats exportés avec succès', 'success');
        })
        .catch(error => {
            this.showNotification('Erreur lors de l\'export: ' + error.message, 'danger');
        });
    }
    
    resizeCharts() {
        // Redimensionner les graphiques si nécessaire
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }
    
    pauseUpdates() {
        // Mettre en pause les mises à jour automatiques
        this.updatesPaused = true;
    }
    
    resumeUpdates() {
        // Reprendre les mises à jour automatiques
        this.updatesPaused = false;
    }
    
    handleAction(action, element) {
        switch (action) {
            case 'refresh':
                this.refreshData();
                break;
            case 'export':
                this.exportCurrentData();
                break;
            case 'clear-logs':
                this.clearLogs();
                break;
            default:
                console.warn('Action non reconnue:', action);
        }
    }
    
    refreshData() {
        this.showNotification('Actualisation des données...', 'info');
        // Implémenter la logique de rafraîchissement
    }
    
    clearLogs() {
        const logContainer = document.getElementById('logMessages');
        if (logContainer) {
            logContainer.innerHTML = '';
        }
    }
}

// Initialiser l'application quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    window.tradingApp = new TradingAgentsApp();
});
