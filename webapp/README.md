# TradingAgents Web Interface

Interface web moderne pour contrôler et visualiser les agents de trading multi-agents alimentés par LLM du framework TradingAgents.

## 🌟 Fonctionnalités

### 🎯 Interface de Contrôle des Agents
- **Démarrage/Arrêt des Analyses**: Contrôlez facilement vos agents de trading
- **Configuration Flexible**: Sélectionnez les analystes, configurez les paramètres LLM
- **Suivi en Temps Réel**: Visualisez le progrès des analyses en direct

### 📊 Tableau de Bord Complet
- **Métriques de Performance**: Taux de réussite, temps moyen, analyses totales
- **Graphiques Interactifs**: Visualisation des performances et répartition des décisions
- **Historique Détaillé**: Accès à toutes les analyses précédentes

### ⚙️ Configuration Avancée
- **Modèles LLM**: Support pour OpenAI, Anthropic, Google
- **Paramètres des Agents**: Profondeur de recherche, tours de débat
- **Préréglages**: Configurations rapide, équilibrée, approfondie

### 🔄 Intégration Complète
- **WebSockets**: Mises à jour en temps réel
- **Export/Import**: Sauvegarde et partage des configurations et résultats
- **API REST**: Intégration avec d'autres systèmes

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.10+
- Variables d'environnement requises:
  ```bash
  export OPENAI_API_KEY=your_openai_api_key
  export FINNHUB_API_KEY=your_finnhub_api_key
  ```

### Installation
1. **Installer les dépendances du projet principal**:
   ```bash
   cd /path/to/TradingAgents
   pip install -r requirements.txt
   ```

2. **Installer les dépendances web supplémentaires**:
   ```bash
   cd webapp
   pip install -r requirements.txt
   ```

### Démarrage
```bash
cd webapp
python run.py
```

L'application sera disponible sur: http://localhost:5000

## 📱 Utilisation

### 1. Page d'Accueil
- **Nouvelle Analyse**: Configurez et lancez une analyse de trading
- **Sélection des Analystes**: Choisissez parmi les analystes disponibles
- **Statut des Agents**: Visualisez l'état de tous les agents en temps réel

### 2. Tableau de Bord
- **Métriques Globales**: Vue d'ensemble des performances
- **Graphiques**: Tendances et répartitions des décisions
- **Historique**: Liste complète des analyses avec détails

### 3. Configuration
- **Modèles LLM**: Configurez les fournisseurs et modèles
- **Paramètres des Agents**: Ajustez la profondeur d'analyse
- **Préréglages**: Chargez des configurations prédéfinies

## 🏗️ Architecture

### Structure des Fichiers
```
webapp/
├── app.py                 # Application Flask principale
├── run.py                 # Script de démarrage
├── requirements.txt       # Dépendances web
├── README.md             # Documentation
├── templates/            # Templates HTML
│   ├── base.html         # Template de base
│   ├── index.html        # Page d'accueil
│   ├── dashboard.html    # Tableau de bord
│   └── config.html       # Configuration
├── static/               # Fichiers statiques
│   ├── css/
│   │   └── custom.css    # Styles personnalisés
│   └── js/
│       └── app.js        # JavaScript principal
└── results/              # Résultats des analyses
```

### Composants Principaux

#### TradingAgentsWebApp
Classe principale qui gère:
- Création des instances TradingAgentsGraph
- Exécution des analyses avec suivi du progrès
- Communication WebSocket
- Sauvegarde des résultats

#### Interface Utilisateur
- **Bootstrap 5**: Framework CSS moderne
- **Chart.js**: Graphiques interactifs
- **Socket.IO**: Communication temps réel
- **Font Awesome**: Icônes

## 🔧 API Endpoints

### REST API
- `POST /api/start_analysis` - Démarrer une nouvelle analyse
- `GET /api/get_results/<session_id>` - Récupérer les résultats
- `GET /api/list_results` - Lister toutes les analyses
- `GET /api/agents_status` - Statut des agents

### WebSocket Events
- `analysis_status` - Statut de l'analyse
- `analysis_progress` - Progrès de l'analyse
- `analysis_complete` - Analyse terminée
- `analysis_error` - Erreur d'analyse
- `agent_update` - Mise à jour d'un agent

## 🎨 Personnalisation

### Thèmes et Styles
Modifiez `static/css/custom.css` pour personnaliser:
- Couleurs et gradients
- Animations
- Mise en page

### Fonctionnalités Supplémentaires
Étendez `static/js/app.js` pour ajouter:
- Nouvelles interactions
- Graphiques personnalisés
- Intégrations externes

## 🔍 Débogage

### Logs
- Les logs de l'application Flask sont affichés dans la console
- Les erreurs détaillées sont capturées avec traceback
- Les résultats sont sauvegardés dans `webapp/results/`

### Mode Debug
Le mode debug est activé par défaut et permet:
- Rechargement automatique du code
- Messages d'erreur détaillés
- Inspection des variables

## 🤝 Contribution

Pour contribuer à l'interface web:

1. **Fork** le projet
2. **Créez** une branche pour votre fonctionnalité
3. **Testez** vos modifications
4. **Soumettez** une pull request

### Guidelines
- Suivez les conventions de nommage existantes
- Ajoutez des commentaires pour les nouvelles fonctionnalités
- Testez sur différents navigateurs
- Maintenez la compatibilité avec le framework TradingAgents

## 📄 Licence

Cette interface web fait partie du projet TradingAgents et suit la même licence.

## 🆘 Support

Pour obtenir de l'aide:
- Consultez la documentation du projet principal
- Ouvrez une issue sur GitHub
- Rejoignez la communauté Discord

---

**Développé avec ❤️ pour la communauté TradingAgents**
