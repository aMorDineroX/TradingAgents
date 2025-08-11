# Guide d'Installation - TradingAgents Web Interface

Ce guide vous accompagne dans l'installation et la configuration de l'interface web TradingAgents.

## 📋 Prérequis

### Système
- **Python**: Version 3.10 ou supérieure
- **Système d'exploitation**: Linux, macOS, ou Windows
- **Mémoire**: Minimum 4 GB RAM (8 GB recommandé)
- **Espace disque**: Minimum 2 GB d'espace libre

### Clés API Requises
Vous devez obtenir les clés API suivantes avant de commencer:

1. **OpenAI API Key** (obligatoire)
   - Rendez-vous sur: https://platform.openai.com/api-keys
   - Créez une nouvelle clé API
   - Notez votre clé (commence par `sk-`)

2. **FinnHub API Key** (obligatoire)
   - Rendez-vous sur: https://finnhub.io/register
   - Créez un compte gratuit
   - Récupérez votre clé API

3. **Anthropic API Key** (optionnel)
   - Rendez-vous sur: https://console.anthropic.com/
   - Créez une clé API si vous voulez utiliser Claude

4. **Google AI API Key** (optionnel)
   - Rendez-vous sur: https://makersuite.google.com/app/apikey
   - Créez une clé API si vous voulez utiliser Gemini

## 🚀 Installation Étape par Étape

### Étape 1: Cloner le Projet
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

### Étape 2: Créer un Environnement Virtuel
```bash
# Créer l'environnement virtuel
python -m venv tradingagents-env

# Activer l'environnement (Linux/macOS)
source tradingagents-env/bin/activate

# Activer l'environnement (Windows)
tradingagents-env\Scripts\activate
```

### Étape 3: Installer les Dépendances du Projet Principal
```bash
# Installer les dépendances TradingAgents
pip install -r requirements.txt
```

### Étape 4: Installer les Dépendances Web
```bash
# Aller dans le dossier webapp
cd webapp

# Installer les dépendances web supplémentaires
pip install -r requirements.txt
```

### Étape 5: Configurer les Variables d'Environnement

#### Option A: Fichier .env (Recommandé)
Créez un fichier `.env` dans le répertoire racine du projet:

```bash
# Créer le fichier .env
touch .env
```

Ajoutez vos clés API dans le fichier `.env`:
```env
# Clés API obligatoires
OPENAI_API_KEY=sk-votre-cle-openai-ici
FINNHUB_API_KEY=votre-cle-finnhub-ici

# Clés API optionnelles
ANTHROPIC_API_KEY=votre-cle-anthropic-ici
GOOGLE_API_KEY=votre-cle-google-ici

# Configuration optionnelle
FLASK_ENV=development
FLASK_DEBUG=1
```

#### Option B: Variables d'Environnement Système
```bash
# Linux/macOS
export OPENAI_API_KEY=sk-votre-cle-openai-ici
export FINNHUB_API_KEY=votre-cle-finnhub-ici

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-votre-cle-openai-ici"
$env:FINNHUB_API_KEY="votre-cle-finnhub-ici"

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-votre-cle-openai-ici
set FINNHUB_API_KEY=votre-cle-finnhub-ici
```

### Étape 6: Tester l'Installation
```bash
# Depuis le dossier webapp
python test_app.py
```

Ce script vérifiera que tous les composants sont correctement installés.

### Étape 7: Démarrer l'Application
```bash
# Depuis le dossier webapp
python run.py
```

L'application sera accessible sur: http://localhost:5000

## 🔧 Configuration Avancée

### Configuration des Modèles LLM

#### OpenAI (Par défaut)
```python
config = {
    "llm_provider": "openai",
    "quick_think_llm": "gpt-4o-mini",
    "deep_think_llm": "gpt-4o",
    "backend_url": "https://api.openai.com/v1"
}
```

#### Anthropic Claude
```python
config = {
    "llm_provider": "anthropic",
    "quick_think_llm": "claude-3-haiku-20240307",
    "deep_think_llm": "claude-3-sonnet-20240229",
    "backend_url": "https://api.anthropic.com"
}
```

#### Google Gemini
```python
config = {
    "llm_provider": "google",
    "quick_think_llm": "gemini-1.5-flash",
    "deep_think_llm": "gemini-1.5-pro",
    "backend_url": "https://generativelanguage.googleapis.com/v1"
}
```

### Configuration du Port et de l'Hôte
Modifiez `webapp/run.py` pour changer le port:
```python
socketio.run(
    app, 
    debug=True, 
    host='0.0.0.0',  # Accessible depuis d'autres machines
    port=8080,       # Changer le port
    allow_unsafe_werkzeug=True
)
```

### Configuration de Production

Pour un déploiement en production, créez un fichier `webapp/wsgi.py`:
```python
from app import app, socketio

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
```

Puis utilisez un serveur WSGI comme Gunicorn:
```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:app
```

## 🐛 Résolution des Problèmes

### Problème: "Module not found"
**Solution**: Vérifiez que vous êtes dans le bon environnement virtuel et que toutes les dépendances sont installées.
```bash
pip list | grep -E "(flask|tradingagents|langchain)"
```

### Problème: "API Key not found"
**Solution**: Vérifiez que vos variables d'environnement sont correctement définies.
```bash
echo $OPENAI_API_KEY
echo $FINNHUB_API_KEY
```

### Problème: "Port already in use"
**Solution**: Changez le port dans `run.py` ou arrêtez le processus utilisant le port 5000.
```bash
# Trouver le processus utilisant le port 5000
lsof -i :5000

# Arrêter le processus (remplacez PID par l'ID du processus)
kill -9 PID
```

### Problème: "Permission denied"
**Solution**: Assurez-vous d'avoir les permissions d'écriture dans le répertoire.
```bash
chmod +x webapp/run.py
```

### Problème: Erreurs de connexion WebSocket
**Solution**: Vérifiez que les ports ne sont pas bloqués par un firewall.
```bash
# Tester la connectivité
curl http://localhost:5000/api/agents_status
```

## 📊 Vérification de l'Installation

### Test Rapide
1. Ouvrez http://localhost:5000 dans votre navigateur
2. Vous devriez voir la page d'accueil TradingAgents
3. Naviguez vers "Configuration" pour vérifier les paramètres
4. Essayez de démarrer une analyse de test avec le ticker "SPY"

### Test Complet
```bash
# Exécuter la suite de tests complète
python test_app.py
```

### Vérification des Logs
Les logs de l'application s'affichent dans la console. Recherchez:
- ✅ Messages de démarrage réussi
- ⚠️ Avertissements de configuration
- ❌ Erreurs d'API ou de connexion

## 🔄 Mise à Jour

Pour mettre à jour l'application:
```bash
# Mettre à jour le code
git pull origin main

# Mettre à jour les dépendances
pip install -r requirements.txt
cd webapp
pip install -r requirements.txt

# Redémarrer l'application
python run.py
```

## 📞 Support

Si vous rencontrez des problèmes:

1. **Consultez les logs** pour des messages d'erreur détaillés
2. **Vérifiez la documentation** du projet principal TradingAgents
3. **Ouvrez une issue** sur GitHub avec:
   - Votre système d'exploitation
   - Version de Python
   - Messages d'erreur complets
   - Étapes pour reproduire le problème

## 🎉 Félicitations!

Si vous êtes arrivé jusqu'ici, votre installation de TradingAgents Web Interface est prête!

Vous pouvez maintenant:
- 🚀 Démarrer des analyses de trading
- 📊 Visualiser les performances dans le tableau de bord
- ⚙️ Configurer vos agents selon vos besoins
- 💾 Sauvegarder et partager vos configurations

Bon trading! 📈
