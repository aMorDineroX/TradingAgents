/**
 * TradingAgents Advanced UX Features
 * Fonctionnalités avancées d'expérience utilisateur
 */

class AdvancedUX {
    constructor() {
        this.preferences = this.loadPreferences();
        this.shortcuts = new Map();
        this.wizards = new Map();
        this.init();
    }

    init() {
        this.initPreferences();
        this.initShortcuts();
        this.initWizards();
        this.initDragAndDrop();
        this.initAutoSave();
        
        console.log('🚀 Advanced UX initialized');
    }

    // ========================================
    // Gestion des préférences utilisateur
    // ========================================
    
    initPreferences() {
        this.applyPreferences();
        
        // Écouter les changements de préférences
        document.addEventListener('preferenceChanged', (e) => {
            this.updatePreference(e.detail.key, e.detail.value);
        });
    }

    loadPreferences() {
        const defaultPreferences = {
            theme: 'light',
            language: 'fr',
            autoSave: true,
            notifications: true,
            soundEnabled: false,
            compactMode: false,
            showTooltips: true,
            animationsEnabled: true,
            defaultAnalysisDepth: 2,
            favoriteSymbols: ['SPY', 'QQQ', 'AAPL'],
            dashboardLayout: 'default'
        };

        const saved = localStorage.getItem('tradingagents_preferences');
        return saved ? { ...defaultPreferences, ...JSON.parse(saved) } : defaultPreferences;
    }

    savePreferences() {
        localStorage.setItem('tradingagents_preferences', JSON.stringify(this.preferences));
    }

    updatePreference(key, value) {
        this.preferences[key] = value;
        this.savePreferences();
        this.applyPreferences();
        
        // Émettre un événement pour les autres composants
        document.dispatchEvent(new CustomEvent('preferencesUpdated', {
            detail: { key, value, preferences: this.preferences }
        }));
    }

    applyPreferences() {
        // Appliquer le thème
        document.documentElement.setAttribute('data-theme', this.preferences.theme);
        
        // Mode compact
        if (this.preferences.compactMode) {
            document.body.classList.add('compact-mode');
        } else {
            document.body.classList.remove('compact-mode');
        }
        
        // Animations
        if (!this.preferences.animationsEnabled) {
            document.body.classList.add('no-animations');
        } else {
            document.body.classList.remove('no-animations');
        }
        
        // Tooltips
        if (!this.preferences.showTooltips) {
            document.body.classList.add('no-tooltips');
        } else {
            document.body.classList.remove('no-tooltips');
        }
    }

    // ========================================
    // Raccourcis clavier avancés
    // ========================================
    
    initShortcuts() {
        // Raccourcis par défaut
        this.registerShortcut('ctrl+shift+a', () => this.showAnalysisWizard());
        this.registerShortcut('ctrl+shift+b', () => this.showBacktestWizard());
        this.registerShortcut('ctrl+shift+p', () => this.showPreferences());
        this.registerShortcut('ctrl+shift+s', () => this.quickSave());
        this.registerShortcut('ctrl+shift+f', () => this.toggleFullscreen());
        this.registerShortcut('ctrl+shift+h', () => this.showHelp());
        this.registerShortcut('escape', () => this.closeModals());
        
        // Raccourcis pour les symboles favoris
        this.preferences.favoriteSymbols.forEach((symbol, index) => {
            if (index < 9) {
                this.registerShortcut(`ctrl+${index + 1}`, () => this.quickAnalysis(symbol));
            }
        });

        document.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    registerShortcut(combination, callback) {
        this.shortcuts.set(combination, callback);
    }

    handleKeydown(event) {
        const combo = this.getKeyCombo(event);
        const handler = this.shortcuts.get(combo);
        
        if (handler) {
            event.preventDefault();
            handler();
        }
    }

    getKeyCombo(event) {
        const parts = [];
        
        if (event.ctrlKey || event.metaKey) parts.push('ctrl');
        if (event.shiftKey) parts.push('shift');
        if (event.altKey) parts.push('alt');
        
        const key = event.key.toLowerCase();
        if (key !== 'control' && key !== 'shift' && key !== 'alt' && key !== 'meta') {
            parts.push(key);
        }
        
        return parts.join('+');
    }

    // ========================================
    // Assistants étape par étape
    // ========================================
    
    initWizards() {
        this.createAnalysisWizard();
        this.createBacktestWizard();
        this.createSetupWizard();
    }

    createAnalysisWizard() {
        const wizard = {
            id: 'analysis-wizard',
            title: 'Assistant d\'Analyse',
            steps: [
                {
                    title: 'Symbole',
                    content: this.createSymbolStep(),
                    validate: (data) => data.symbol && data.symbol.length > 0
                },
                {
                    title: 'Analystes',
                    content: this.createAnalystsStep(),
                    validate: (data) => data.analysts && data.analysts.length > 0
                },
                {
                    title: 'Configuration',
                    content: this.createConfigStep(),
                    validate: (data) => data.depth > 0
                },
                {
                    title: 'Confirmation',
                    content: this.createConfirmationStep(),
                    validate: () => true
                }
            ]
        };
        
        this.wizards.set('analysis', wizard);
    }

    createBacktestWizard() {
        const wizard = {
            id: 'backtest-wizard',
            title: 'Assistant de Backtesting',
            steps: [
                {
                    title: 'Stratégie',
                    content: this.createStrategyStep(),
                    validate: (data) => data.name && data.symbols.length > 0
                },
                {
                    title: 'Période',
                    content: this.createPeriodStep(),
                    validate: (data) => data.startDate && data.endDate
                },
                {
                    title: 'Paramètres',
                    content: this.createParametersStep(),
                    validate: (data) => data.capital > 0
                },
                {
                    title: 'Lancement',
                    content: this.createLaunchStep(),
                    validate: () => true
                }
            ]
        };
        
        this.wizards.set('backtest', wizard);
    }

    createSetupWizard() {
        const wizard = {
            id: 'setup-wizard',
            title: 'Configuration Initiale',
            steps: [
                {
                    title: 'Bienvenue',
                    content: this.createWelcomeStep(),
                    validate: () => true
                },
                {
                    title: 'API Keys',
                    content: this.createApiKeysStep(),
                    validate: (data) => data.groqKey || data.openaiKey
                },
                {
                    title: 'Préférences',
                    content: this.createPreferencesStep(),
                    validate: () => true
                },
                {
                    title: 'Terminé',
                    content: this.createCompletionStep(),
                    validate: () => true
                }
            ]
        };
        
        this.wizards.set('setup', wizard);
    }

    showWizard(wizardId) {
        const wizard = this.wizards.get(wizardId);
        if (!wizard) return;

        const modal = this.createWizardModal(wizard);
        document.body.appendChild(modal);
        
        setTimeout(() => modal.classList.add('active'), 10);
    }

    createWizardModal(wizard) {
        const modal = document.createElement('div');
        modal.className = 'wizard-overlay';
        modal.innerHTML = `
            <div class="wizard-modal">
                <div class="wizard-header">
                    <h2>${wizard.title}</h2>
                    <button class="wizard-close btn-icon">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="wizard-progress">
                    <div class="wizard-steps">
                        ${wizard.steps.map((step, index) => `
                            <div class="wizard-step ${index === 0 ? 'active' : ''}" data-step="${index}">
                                <div class="step-number">${index + 1}</div>
                                <div class="step-title">${step.title}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="wizard-content">
                    <div class="wizard-step-content">
                        ${wizard.steps[0].content}
                    </div>
                </div>
                <div class="wizard-footer">
                    <button class="btn btn-secondary wizard-prev" disabled>
                        <i class="fas fa-arrow-left"></i> Précédent
                    </button>
                    <button class="btn btn-primary wizard-next">
                        Suivant <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;

        this.initWizardEvents(modal, wizard);
        return modal;
    }

    initWizardEvents(modal, wizard) {
        let currentStep = 0;
        const wizardData = {};

        // Fermeture
        modal.querySelector('.wizard-close').addEventListener('click', () => {
            modal.remove();
        });

        // Navigation
        const prevBtn = modal.querySelector('.wizard-prev');
        const nextBtn = modal.querySelector('.wizard-next');
        const stepContent = modal.querySelector('.wizard-step-content');

        const updateStep = () => {
            // Mettre à jour les indicateurs de progression
            modal.querySelectorAll('.wizard-step').forEach((step, index) => {
                step.classList.toggle('active', index === currentStep);
                step.classList.toggle('completed', index < currentStep);
            });

            // Mettre à jour le contenu
            stepContent.innerHTML = wizard.steps[currentStep].content;

            // Mettre à jour les boutons
            prevBtn.disabled = currentStep === 0;
            nextBtn.textContent = currentStep === wizard.steps.length - 1 ? 'Terminer' : 'Suivant';

            // Pré-remplir avec les données existantes
            this.populateWizardStep(stepContent, wizardData);
        };

        nextBtn.addEventListener('click', () => {
            // Collecter les données de l'étape actuelle
            this.collectWizardStepData(stepContent, wizardData);

            // Valider
            const step = wizard.steps[currentStep];
            if (!step.validate(wizardData)) {
                showNotification('Veuillez remplir tous les champs requis', 'warning');
                return;
            }

            if (currentStep < wizard.steps.length - 1) {
                currentStep++;
                updateStep();
            } else {
                // Terminer le wizard
                this.completeWizard(wizard.id, wizardData);
                modal.remove();
            }
        });

        prevBtn.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                updateStep();
            }
        });

        updateStep();
    }

    // ========================================
    // Fonctions utilitaires
    // ========================================
    
    showAnalysisWizard() {
        this.showWizard('analysis');
    }

    showBacktestWizard() {
        this.showWizard('backtest');
    }

    showPreferences() {
        // Implémenter l'interface de préférences
        console.log('Showing preferences...');
    }

    quickSave() {
        if (this.preferences.autoSave) {
            // Sauvegarder l'état actuel
            showNotification('État sauvegardé', 'success');
        }
    }

    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            document.documentElement.requestFullscreen();
        }
    }

    showHelp() {
        // Afficher l'aide contextuelle
        console.log('Showing help...');
    }

    closeModals() {
        // Fermer toutes les modales ouvertes
        document.querySelectorAll('.modal-overlay.active, .wizard-overlay.active').forEach(modal => {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        });
    }

    quickAnalysis(symbol) {
        // Lancer une analyse rapide pour le symbole
        if (window.location.pathname === '/') {
            const tickerInput = document.getElementById('ticker');
            if (tickerInput) {
                tickerInput.value = symbol;
                tickerInput.dispatchEvent(new Event('input'));
            }
        } else {
            window.location.href = `/?ticker=${symbol}`;
        }
    }

    // ========================================
    // Drag & Drop
    // ========================================
    
    initDragAndDrop() {
        // Permettre le drag & drop de fichiers pour l'import de données
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
            document.body.classList.add('drag-over');
        });

        document.addEventListener('dragleave', (e) => {
            if (!e.relatedTarget) {
                document.body.classList.remove('drag-over');
            }
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            document.body.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            this.handleFilesDrop(files);
        });
    }

    handleFilesDrop(files) {
        files.forEach(file => {
            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                this.importCSVData(file);
            } else if (file.type === 'application/json' || file.name.endsWith('.json')) {
                this.importJSONData(file);
            }
        });
    }

    // ========================================
    // Auto-sauvegarde
    // ========================================
    
    initAutoSave() {
        if (this.preferences.autoSave) {
            setInterval(() => {
                this.autoSave();
            }, 30000); // Toutes les 30 secondes
        }
    }

    autoSave() {
        // Sauvegarder automatiquement l'état des formulaires
        const forms = document.querySelectorAll('form[data-autosave]');
        forms.forEach(form => {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
        });
    }

    restoreAutoSave(formId) {
        const saved = localStorage.getItem(`autosave_${formId}`);
        if (saved) {
            const data = JSON.parse(saved);
            const form = document.getElementById(formId);
            
            Object.entries(data).forEach(([name, value]) => {
                const input = form.querySelector(`[name="${name}"]`);
                if (input) {
                    input.value = value;
                }
            });
        }
    }

    // Méthodes de création de contenu pour les wizards (à implémenter)
    createSymbolStep() { return '<div>Étape symbole</div>'; }
    createAnalystsStep() { return '<div>Étape analystes</div>'; }
    createConfigStep() { return '<div>Étape configuration</div>'; }
    createConfirmationStep() { return '<div>Étape confirmation</div>'; }
    createStrategyStep() { return '<div>Étape stratégie</div>'; }
    createPeriodStep() { return '<div>Étape période</div>'; }
    createParametersStep() { return '<div>Étape paramètres</div>'; }
    createLaunchStep() { return '<div>Étape lancement</div>'; }
    createWelcomeStep() { return '<div>Étape bienvenue</div>'; }
    createApiKeysStep() { return '<div>Étape API keys</div>'; }
    createPreferencesStep() { return '<div>Étape préférences</div>'; }
    createCompletionStep() { return '<div>Étape terminé</div>'; }
    
    populateWizardStep(stepContent, wizardData) {}
    collectWizardStepData(stepContent, wizardData) {}
    completeWizard(wizardId, wizardData) {}
    importCSVData(file) {}
    importJSONData(file) {}
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.advancedUX = new AdvancedUX();
});
