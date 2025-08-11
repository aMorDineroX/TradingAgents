/**
 * TradingAgents Modern UI JavaScript
 * Gestion des interactions, animations et fonctionnalités avancées
 */

class ModernUI {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.initTheme();
        this.initNavigation();
        this.initTooltips();
        this.initKeyboardShortcuts();
        this.initNotifications();
        this.initSearch();
        this.initAnimations();
        this.initFormValidation();
        
        console.log('🎨 Modern UI initialized');
    }

    // ========================================
    // Gestion du thème
    // ========================================
    
    initTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
            this.updateThemeIcon();
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateThemeIcon();
        
        // Animation de transition
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    updateThemeIcon() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
        }
    }

    // ========================================
    // Navigation
    // ========================================
    
    initNavigation() {
        this.initMobileMenu();
        this.initActiveNavigation();
        this.initBreadcrumbs();
    }

    initMobileMenu() {
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        const mobileClose = document.querySelector('.mobile-menu-close');

        if (mobileToggle && mobileMenu) {
            mobileToggle.addEventListener('click', () => {
                mobileToggle.classList.toggle('active');
                mobileMenu.classList.toggle('active');
                document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
            });

            // Fermer en cliquant sur l'overlay
            mobileMenu.addEventListener('click', (e) => {
                if (e.target === mobileMenu) {
                    this.closeMobileMenu();
                }
            });

            if (mobileClose) {
                mobileClose.addEventListener('click', () => this.closeMobileMenu());
            }
        }
    }

    closeMobileMenu() {
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        
        if (mobileToggle) mobileToggle.classList.remove('active');
        if (mobileMenu) mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
    }

    initActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath || (currentPath !== '/' && href !== '/' && currentPath.startsWith(href))) {
                link.classList.add('active');
            }
        });
    }

    initBreadcrumbs() {
        const breadcrumbContainer = document.querySelector('.breadcrumb');
        if (!breadcrumbContainer) return;

        const path = window.location.pathname;
        const segments = path.split('/').filter(segment => segment);
        
        const breadcrumbs = [
            { name: 'Accueil', url: '/' }
        ];

        const pathMap = {
            'automation': 'Automatisation',
            'backtesting': 'Backtesting',
            'config': 'Configuration',
            'dashboard': 'Tableau de bord'
        };

        let currentPath = '';
        segments.forEach(segment => {
            currentPath += '/' + segment;
            breadcrumbs.push({
                name: pathMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1),
                url: currentPath
            });
        });

        this.renderBreadcrumbs(breadcrumbContainer, breadcrumbs);
    }

    renderBreadcrumbs(container, breadcrumbs) {
        container.innerHTML = breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1;
            return `
                <div class="breadcrumb-item">
                    ${isLast ? 
                        `<span class="breadcrumb-current">${crumb.name}</span>` :
                        `<a href="${crumb.url}" class="breadcrumb-link">${crumb.name}</a>`
                    }
                </div>
            `;
        }).join('');
    }

    // ========================================
    // Tooltips
    // ========================================
    
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => this.showTooltip(e));
            element.addEventListener('mouseleave', () => this.hideTooltip());
        });
    }

    showTooltip(event) {
        const element = event.target;
        const text = element.getAttribute('data-tooltip');
        const position = element.getAttribute('data-tooltip-position') || 'top';
        
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position}`;
        tooltip.textContent = text;
        tooltip.id = 'active-tooltip';
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 8;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 8;
                break;
        }
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
        
        setTimeout(() => tooltip.classList.add('visible'), 10);
    }

    hideTooltip() {
        const tooltip = document.getElementById('active-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    // ========================================
    // Raccourcis clavier
    // ========================================
    
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K pour la recherche
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
            
            // Ctrl/Cmd + D pour le tableau de bord
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                window.location.href = '/dashboard';
            }
            
            // Ctrl/Cmd + A pour l'automatisation
            if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
                e.preventDefault();
                window.location.href = '/automation';
            }
            
            // Ctrl/Cmd + T pour changer de thème
            if ((e.ctrlKey || e.metaKey) && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // Échap pour fermer les modales/menus
            if (e.key === 'Escape') {
                this.closeMobileMenu();
                this.hideSearch();
            }
        });
    }

    focusSearch() {
        const searchInput = document.querySelector('.global-search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    // ========================================
    // Notifications Toast
    // ========================================
    
    initNotifications() {
        this.createNotificationContainer();
    }

    createNotificationContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getNotificationIcon(type);
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icon}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // Animation d'entrée
        setTimeout(() => toast.classList.add('visible'), 10);
        
        // Auto-suppression
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('visible');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    // ========================================
    // Recherche globale
    // ========================================
    
    initSearch() {
        const searchInput = document.querySelector('.global-search-input');
        const searchResults = document.querySelector('.global-search-results');
        
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                
                if (query.length > 2) {
                    searchTimeout = setTimeout(() => this.performSearch(query), 300);
                } else {
                    this.hideSearch();
                }
            });
            
            searchInput.addEventListener('focus', () => {
                if (searchInput.value.trim().length > 2) {
                    this.showSearch();
                }
            });
            
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.global-search')) {
                    this.hideSearch();
                }
            });
        }
    }

    async performSearch(query) {
        // Ici, vous pouvez implémenter la logique de recherche
        // Pour l'instant, on simule une recherche
        const results = [
            { title: 'Analyse SPY', type: 'analysis', url: '/?ticker=SPY' },
            { title: 'Configuration Groq', type: 'config', url: '/config' },
            { title: 'Automatisation', type: 'automation', url: '/automation' }
        ].filter(item => item.title.toLowerCase().includes(query.toLowerCase()));
        
        this.displaySearchResults(results);
    }

    displaySearchResults(results) {
        const searchResults = document.querySelector('.global-search-results');
        if (!searchResults) return;
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-no-results">Aucun résultat trouvé</div>';
        } else {
            searchResults.innerHTML = results.map(result => `
                <a href="${result.url}" class="search-result-item">
                    <div class="search-result-title">${result.title}</div>
                    <div class="search-result-type">${result.type}</div>
                </a>
            `).join('');
        }
        
        this.showSearch();
    }

    showSearch() {
        const searchResults = document.querySelector('.global-search-results');
        if (searchResults) {
            searchResults.classList.add('active');
        }
    }

    hideSearch() {
        const searchResults = document.querySelector('.global-search-results');
        if (searchResults) {
            searchResults.classList.remove('active');
        }
    }

    // ========================================
    // Animations
    // ========================================
    
    initAnimations() {
        this.observeElements();
    }

    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.card, .metric-card').forEach(el => {
            observer.observe(el);
        });
    }

    // ========================================
    // Validation de formulaires
    // ========================================
    
    initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => this.validateForm(e));
            
            // Validation en temps réel
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });
        });
    }

    validateForm(event) {
        const form = event.target;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
        }
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        let isValid = true;
        let message = '';

        // Validation required
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'Ce champ est requis';
        }

        // Validation email
        if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Adresse email invalide';
        }

        // Validation numérique
        if (type === 'number' && value && isNaN(value)) {
            isValid = false;
            message = 'Valeur numérique requise';
        }

        this.showFieldError(field, isValid ? '' : message);
        return isValid;
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        if (message) {
            field.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = message;
            field.parentNode.appendChild(errorDiv);
        }
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentNode.querySelector('.form-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.modernUI = new ModernUI();
});

// Fonctions utilitaires globales
window.showNotification = (message, type, duration) => {
    if (window.modernUI) {
        window.modernUI.showNotification(message, type, duration);
    }
};

window.toggleTheme = () => {
    if (window.modernUI) {
        window.modernUI.toggleTheme();
    }
};
