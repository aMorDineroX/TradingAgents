"""
Application web Flask pour TradingAgents
Interface utilisateur pour contrôler et visualiser les agents de trading
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import queue
import time
import traceback

# Ajouter le répertoire parent au path pour importer TradingAgents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules TradingAgents
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Import du gestionnaire de configuration
from config_manager import ConfigManager

# Import du gestionnaire de base de données
from database import get_db_manager, init_database

# Import des systèmes d'automatisation
from automation_manager import automation_manager, AutomationTask, ScheduleType
from brokerage_manager import brokerage_manager, BrokerType, OrderSide, OrderType
from risk_manager import risk_manager, RiskLevel
from monitoring_system import monitoring_system, AlertLevel
from notification_system import notification_system, NotificationChannel, NotificationPriority
from backtesting_engine import backtest_engine, BacktestConfig

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading-agents-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration globale
RESULTS_DIR = Path("results")  # Chemin relatif depuis webapp/
RESULTS_DIR.mkdir(exist_ok=True)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser le gestionnaire de configuration
config_manager = ConfigManager()

# Initialiser la base de données
print("🗄️ Initialisation de la base de données...")
if init_database():
    db_manager = get_db_manager()
    print("✅ Base de données connectée avec succès")
else:
    print("⚠️ Fonctionnement sans base de données (mode fichiers)")
    db_manager = None

# Initialiser les systèmes d'automatisation
print("🤖 Initialisation des systèmes d'automatisation...")

# Configurer les callbacks entre les systèmes
def on_analysis_complete(task, result):
    """Callback quand une analyse automatique est terminée"""
    try:
        # Exécuter le signal de trading si configuré
        if task.trading_config.get('auto_execute', False):
            order = brokerage_manager.execute_trade_signal(result)
            if order:
                # Ajouter la position au monitoring
                monitoring_system.add_position_monitor(
                    symbol=result['ticker'],
                    entry_price=order.price or 0,
                    quantity=order.quantity,
                    stop_loss=risk_manager.set_stop_loss(result['ticker'], order.price or 0, order.quantity, order.side.value),
                    take_profit=risk_manager.set_take_profit(result['ticker'], order.price or 0, order.side.value)
                )

                # Envoyer une notification
                notification_system.send_notification(
                    title=f"Ordre exécuté: {result['ticker']}",
                    message=f"Signal {result['decision']} exécuté pour {result['ticker']}",
                    priority=NotificationPriority.HIGH
                )

        # Toujours envoyer une notification pour l'analyse terminée
        notification_system.send_notification(
            title=f"Analyse terminée: {result['ticker']}",
            message=f"Décision: {result['decision']} pour {result['ticker']}",
            priority=NotificationPriority.NORMAL
        )

    except Exception as e:
        logger.error(f"❌ Erreur callback analyse: {e}")

def on_stop_trigger(symbol, stop_type, current_price, trigger_price):
    """Callback quand un stop est déclenché"""
    try:
        # Exécuter l'ordre de sortie
        broker = brokerage_manager.get_active_broker()
        if broker:
            positions = broker.get_positions()
            for pos in positions:
                if pos.symbol == symbol:
                    side = OrderSide.SELL if pos.side == "long" else OrderSide.BUY
                    order = broker.place_order(symbol, abs(pos.quantity), side)

                    if order:
                        # Retirer de la surveillance
                        monitoring_system.remove_position_monitor(symbol)

                        # Notification critique
                        notification_system.send_notification(
                            title=f"{stop_type.upper()} déclenché: {symbol}",
                            message=f"Position fermée à ${current_price:.2f} (trigger: ${trigger_price:.2f})",
                            priority=NotificationPriority.CRITICAL
                        )
                    break

    except Exception as e:
        logger.error(f"❌ Erreur callback stop: {e}")

# Configurer les callbacks
automation_manager.on_analysis_complete = on_analysis_complete
monitoring_system.on_stop_trigger = on_stop_trigger

print("✅ Systèmes d'automatisation initialisés")

class TradingAgentsWebApp:
    """Classe principale pour gérer l'application web TradingAgents"""

    def __init__(self):
        self.active_sessions = {}
        self.analysis_queue = queue.Queue()
        self.analysis_results = {}
        self.agent_status_callbacks = []

    def create_trading_graph(self, config: Dict[str, Any]) -> TradingAgentsGraph:
        """Créer une instance de TradingAgentsGraph avec la configuration donnée"""
        selected_analysts = config.get('selected_analysts', ['market', 'social', 'news', 'fundamentals'])

        # Fusionner avec la configuration par défaut pour s'assurer que toutes les clés existent
        full_config = DEFAULT_CONFIG.copy()

        # Forcer Groq si disponible et pas d'autre provider spécifié
        if os.getenv('GROQ_API_KEY') and not config.get('llm_provider'):
            # Utiliser "openai" comme provider mais avec l'URL et la clé Groq
            full_config.update({
                'llm_provider': 'openai',  # Groq est compatible OpenAI
                'quick_think_llm': 'llama-3.1-8b-instant',
                'deep_think_llm': 'llama-3.1-8b-instant',  # Même modèle rapide
                'backend_url': 'https://api.groq.com/openai/v1',
                'openai_api_key': os.getenv('GROQ_API_KEY')  # Utiliser la clé Groq
            })

        full_config.update(config)

        return TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=True,
            config=full_config
        )

    def run_analysis(self, session_id: str, ticker: str, trade_date: str, config: Dict[str, Any]):
        """Exécuter l'analyse de trading pour un ticker donné"""
        try:
            # Sauvegarder l'analyse en base de données (statut: pending)
            if db_manager:
                db_manager.save_analysis_result(session_id, ticker, trade_date, config, 'running')

            # Créer le graphe de trading
            trading_graph = self.create_trading_graph(config)

            # Émettre le statut de démarrage
            socketio.emit('analysis_status', {
                'session_id': session_id,
                'status': 'started',
                'message': f'Démarrage de l\'analyse pour {ticker} le {trade_date}',
                'agent': 'system'
            })

            # Configurer les callbacks pour suivre le progrès
            self.setup_progress_tracking(session_id, trading_graph)

            # Exécuter l'analyse avec suivi du progrès
            final_state, decision = self.run_analysis_with_progress(trading_graph, ticker, trade_date, session_id)

            # Sauvegarder les résultats
            result = {
                'session_id': session_id,
                'ticker': ticker,
                'trade_date': trade_date,
                'final_state': final_state,
                'decision': decision,
                'timestamp': datetime.now().isoformat(),
                'config': config
            }

            self.analysis_results[session_id] = result

            # Sauvegarder dans un fichier (backup)
            result_file = RESULTS_DIR / f"{session_id}_{ticker}_{trade_date}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)

            # Mettre à jour en base de données
            if db_manager:
                db_manager.update_analysis_result(session_id, decision, final_state, 'completed')

            # Émettre les résultats
            socketio.emit('analysis_complete', {
                'session_id': session_id,
                'status': 'completed',
                'result': result
            })

        except Exception as e:
            error_msg = f"Erreur lors de l'analyse: {str(e)}"
            error_details = traceback.format_exc()
            print(f"Erreur détaillée: {error_details}")

            # Mettre à jour le statut d'erreur en base
            if db_manager:
                db_manager.update_analysis_result(session_id, status='error', error_message=error_msg)

            socketio.emit('analysis_error', {
                'session_id': session_id,
                'status': 'error',
                'error': error_msg
            })

    def setup_progress_tracking(self, session_id: str, trading_graph: TradingAgentsGraph):
        """Configurer le suivi du progrès de l'analyse"""
        # Cette méthode peut être étendue pour intercepter les messages du graphe
        pass

    def run_analysis_with_progress(self, trading_graph: TradingAgentsGraph, ticker: str, trade_date: str, session_id: str):
        """Exécuter l'analyse avec suivi du progrès"""
        try:
            # Simuler les étapes de progression
            steps = [
                ('market_analyst', 'Analyse du marché en cours...'),
                ('social_analyst', 'Analyse des sentiments sociaux...'),
                ('news_analyst', 'Analyse des actualités...'),
                ('fundamentals_analyst', 'Analyse fondamentale...'),
                ('research_team', 'Débat de l\'équipe de recherche...'),
                ('trader', 'Élaboration de la stratégie de trading...'),
                ('risk_management', 'Évaluation des risques...'),
                ('final_decision', 'Prise de décision finale...')
            ]

            progress_step = 0
            total_steps = len(steps)

            for step_name, step_message in steps:
                # Émettre le progrès
                progress_percentage = (progress_step / total_steps) * 100
                socketio.emit('analysis_progress', {
                    'session_id': session_id,
                    'progress': progress_percentage,
                    'current_step': step_message,
                    'agent': step_name
                })

                # Émettre le statut de l'agent
                socketio.emit('agent_update', {
                    'session_id': session_id,
                    'agent': step_name,
                    'status': 'running'
                })

                progress_step += 1

            # Exécuter l'analyse réelle
            final_state, decision = trading_graph.propagate(ticker, trade_date)

            # Émettre le progrès final
            socketio.emit('analysis_progress', {
                'session_id': session_id,
                'progress': 100,
                'current_step': 'Analyse terminée',
                'agent': 'system'
            })

            return final_state, decision

        except Exception as e:
            raise e

# Instance globale de l'application
trading_app = TradingAgentsWebApp()

@app.route('/')
def index():
    """Page d'accueil de l'application"""
    # Vérifier si on doit utiliser l'interface moderne
    use_modern = request.args.get('modern', 'true').lower() == 'true'

    if use_modern:
        return render_template('index_modern.html')
    else:
        return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Tableau de bord principal"""
    return render_template('dashboard.html')

@app.route('/config')
def config():
    """Page de configuration des agents"""
    current_config = config_manager.get_current_config()
    presets = config_manager.load_presets()
    return render_template('config.html',
                         default_config=DEFAULT_CONFIG,
                         current_config=current_config,
                         presets=presets)

@app.route('/demo')
def demo():
    """Page de démonstration de l'interface moderne"""
    return render_template('demo_modern.html')

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """API pour démarrer une nouvelle analyse"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['ticker', 'trade_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Générer un ID de session unique
        session_id = f"session_{int(time.time())}_{data['ticker']}"
        
        # Configuration par défaut ou personnalisée
        config = data.get('config', DEFAULT_CONFIG.copy())

        # Forcer l'utilisation de Groq si disponible
        if os.getenv('GROQ_API_KEY') and not config.get('llm_provider'):
            config['llm_provider'] = 'groq'
            config['quick_think_llm'] = 'llama-3.1-8b-instant'
            config['deep_think_llm'] = 'llama-3.1-70b-versatile'
            config['backend_url'] = 'https://api.groq.com/openai/v1'
        
        # Démarrer l'analyse dans un thread séparé
        analysis_thread = threading.Thread(
            target=trading_app.run_analysis,
            args=(session_id, data['ticker'], data['trade_date'], config)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Analyse démarrée avec succès'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_results/<session_id>')
def get_results(session_id):
    """API pour récupérer les résultats d'une analyse"""
    # Essayer d'abord la base de données
    if db_manager:
        result = db_manager.get_analysis_result(session_id)
        if result:
            return jsonify(result)

    # Fallback vers la mémoire
    if session_id in trading_app.analysis_results:
        return jsonify(trading_app.analysis_results[session_id])
    else:
        return jsonify({'error': 'Session non trouvée'}), 404

@app.route('/api/list_results')
def list_results():
    """API pour lister toutes les analyses disponibles"""
    # Essayer d'abord la base de données
    if db_manager:
        results = db_manager.list_analysis_results()
        if results:
            return jsonify(results)

    # Fallback vers les fichiers
    results = []
    for result_file in RESULTS_DIR.glob("*.json"):
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
                results.append({
                    'session_id': result.get('session_id'),
                    'ticker': result.get('ticker'),
                    'trade_date': result.get('trade_date'),
                    'timestamp': result.get('timestamp'),
                    'decision': result.get('decision')
                })
        except Exception as e:
            print(f"Erreur lors de la lecture de {result_file}: {e}")

    return jsonify(results)

@app.route('/api/agents_status')
def agents_status():
    """API pour obtenir le statut des agents"""
    # Cette fonction pourrait être étendue pour fournir des informations en temps réel
    return jsonify({
        'analyst_team': ['market', 'social', 'news', 'fundamentals'],
        'research_team': ['bull_researcher', 'bear_researcher'],
        'trading_team': ['trader'],
        'risk_management': ['risky_analyst', 'neutral_analyst', 'safe_analyst'],
        'portfolio_management': ['portfolio_manager']
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """API pour récupérer la configuration actuelle"""
    return jsonify(config_manager.get_current_config())

@app.route('/api/config', methods=['POST'])
def save_config():
    """API pour sauvegarder la configuration"""
    try:
        data = request.get_json()
        if config_manager.save_config(data):
            return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
        else:
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/update', methods=['POST'])
def update_config():
    """API pour mettre à jour partiellement la configuration"""
    try:
        data = request.get_json()
        if config_manager.update_config(data):
            return jsonify({'success': True, 'message': 'Configuration mise à jour'})
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    """API pour réinitialiser la configuration"""
    try:
        if config_manager.reset_to_default():
            return jsonify({'success': True, 'message': 'Configuration réinitialisée'})
        else:
            return jsonify({'error': 'Erreur lors de la réinitialisation'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets', methods=['GET'])
def get_presets():
    """API pour récupérer les préréglages"""
    return jsonify(config_manager.load_presets())

@app.route('/api/presets/<preset_name>', methods=['GET'])
def get_preset(preset_name):
    """API pour récupérer un préréglage spécifique"""
    preset = config_manager.get_preset(preset_name)
    if preset:
        return jsonify(preset)
    else:
        return jsonify({'error': 'Préréglage non trouvé'}), 404

@app.route('/api/presets', methods=['POST'])
def create_preset():
    """API pour créer un nouveau préréglage"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        config = data.get('config', {})

        if not name:
            return jsonify({'error': 'Nom du préréglage requis'}), 400

        if config_manager.create_preset(name, description, config):
            return jsonify({'success': True, 'message': 'Préréglage créé'})
        else:
            return jsonify({'error': 'Erreur lors de la création'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets/<preset_name>', methods=['DELETE'])
def delete_preset(preset_name):
    """API pour supprimer un préréglage"""
    try:
        if config_manager.delete_preset(preset_name):
            return jsonify({'success': True, 'message': 'Préréglage supprimé'})
        else:
            return jsonify({'error': 'Préréglage non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<provider>', methods=['GET'])
def get_models(provider):
    """API pour récupérer les modèles disponibles pour un fournisseur"""
    models = config_manager.get_available_models(provider)
    return jsonify({'models': models})

# ==================== ROUTES D'AUTOMATISATION ====================

@app.route('/automation')
def automation_dashboard():
    """Page du tableau de bord d'automatisation"""
    return render_template('automation.html')

@app.route('/api/automation/status', methods=['GET'])
def get_automation_status():
    """API pour obtenir le statut de l'automatisation"""
    return jsonify({
        'automation': automation_manager.get_status(),
        'monitoring': monitoring_system.get_monitoring_status(),
        'risk': risk_manager.get_risk_summary(),
        'notifications': notification_system.get_status()
    })

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """API pour démarrer l'automatisation"""
    try:
        automation_manager.start_automation()
        monitoring_system.start_monitoring()
        risk_manager.start_monitoring()

        notification_system.send_notification(
            title="Automatisation démarrée",
            message="Tous les systèmes d'automatisation sont maintenant actifs",
            priority=NotificationPriority.HIGH
        )

        return jsonify({'success': True, 'message': 'Automatisation démarrée'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """API pour arrêter l'automatisation"""
    try:
        automation_manager.stop_automation()
        monitoring_system.stop_monitoring()
        risk_manager.stop_monitoring()

        notification_system.send_notification(
            title="Automatisation arrêtée",
            message="Tous les systèmes d'automatisation ont été arrêtés",
            priority=NotificationPriority.HIGH
        )

        return jsonify({'success': True, 'message': 'Automatisation arrêtée'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/tasks', methods=['GET'])
def list_automation_tasks():
    """API pour lister les tâches d'automatisation"""
    tasks = automation_manager.list_tasks()
    return jsonify({
        'tasks': [
            {
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'ticker': task.ticker,
                'schedule_type': task.schedule_type.value,
                'enabled': task.enabled,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'run_count': task.run_count,
                'success_count': task.success_count,
                'error_count': task.error_count
            }
            for task in tasks
        ]
    })

@app.route('/api/automation/tasks', methods=['POST'])
def create_automation_task():
    """API pour créer une tâche d'automatisation"""
    try:
        data = request.get_json()

        task_id = automation_manager.create_task(
            name=data['name'],
            description=data.get('description', ''),
            ticker=data['ticker'],
            schedule_type=ScheduleType(data['schedule_type']),
            schedule_config=data.get('schedule_config', {}),
            trading_config=data.get('trading_config', {}),
            risk_config=data.get('risk_config', {})
        )

        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/tasks/<task_id>', methods=['PUT'])
def update_automation_task(task_id):
    """API pour mettre à jour une tâche d'automatisation"""
    try:
        data = request.get_json()
        success = automation_manager.update_task(task_id, **data)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Tâche non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/tasks/<task_id>', methods=['DELETE'])
def delete_automation_task(task_id):
    """API pour supprimer une tâche d'automatisation"""
    try:
        success = automation_manager.delete_task(task_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Tâche non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES DE TRADING ====================

@app.route('/api/brokerage/status', methods=['GET'])
def get_brokerage_status():
    """API pour obtenir le statut du courtage"""
    broker = brokerage_manager.get_active_broker()
    if broker:
        try:
            account_info = broker.get_account_info()
            positions = broker.get_positions()

            return jsonify({
                'connected': True,
                'active_broker': brokerage_manager.active_broker,
                'account_info': account_info,
                'positions': [
                    {
                        'symbol': pos.symbol,
                        'quantity': pos.quantity,
                        'avg_price': pos.avg_price,
                        'market_value': pos.market_value,
                        'unrealized_pnl': pos.unrealized_pnl,
                        'side': pos.side
                    }
                    for pos in positions
                ]
            })
        except Exception as e:
            return jsonify({'connected': False, 'error': str(e)})
    else:
        return jsonify({'connected': False, 'error': 'Aucun courtier actif'})

@app.route('/api/brokerage/execute_signal', methods=['POST'])
def execute_trade_signal():
    """API pour exécuter manuellement un signal de trading"""
    try:
        data = request.get_json()
        order = brokerage_manager.execute_trade_signal(data)

        if order:
            return jsonify({
                'success': True,
                'order': {
                    'id': order.id,
                    'symbol': order.symbol,
                    'quantity': order.quantity,
                    'side': order.side.value,
                    'status': order.status.value
                }
            })
        else:
            return jsonify({'error': 'Échec de l\'exécution du signal'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES DE MONITORING ====================

@app.route('/api/monitoring/positions', methods=['GET'])
def get_monitored_positions():
    """API pour obtenir les positions surveillées"""
    return jsonify(monitoring_system.get_position_summary())

@app.route('/api/monitoring/alerts', methods=['GET'])
def get_monitoring_alerts():
    """API pour obtenir les alertes de surveillance"""
    level = request.args.get('level')
    symbol = request.args.get('symbol')
    limit = int(request.args.get('limit', 50))

    alert_level = AlertLevel(level) if level else None
    alerts = monitoring_system.get_alerts(alert_level, symbol, limit)

    return jsonify({
        'alerts': [
            {
                'id': alert.id,
                'level': alert.level.value,
                'title': alert.title,
                'message': alert.message,
                'symbol': alert.symbol,
                'timestamp': alert.timestamp.isoformat(),
                'acknowledged': alert.acknowledged
            }
            for alert in alerts
        ]
    })

@app.route('/api/monitoring/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """API pour acquitter une alerte"""
    monitoring_system.acknowledge_alert(alert_id)
    return jsonify({'success': True})

# ==================== ROUTES DE GESTION DES RISQUES ====================

@app.route('/api/risk/parameters', methods=['GET'])
def get_risk_parameters():
    """API pour obtenir les paramètres de risque"""
    return jsonify(risk_manager.get_risk_summary())

@app.route('/api/risk/parameters', methods=['PUT'])
def update_risk_parameters():
    """API pour mettre à jour les paramètres de risque"""
    try:
        data = request.get_json()
        risk_manager.update_parameters(**data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk/validate_trade', methods=['POST'])
def validate_trade():
    """API pour valider un trade avant exécution"""
    try:
        data = request.get_json()

        # Obtenir les informations du portefeuille
        broker = brokerage_manager.get_active_broker()
        if not broker:
            return jsonify({'error': 'Aucun courtier actif'}), 400

        account_info = broker.get_account_info()
        positions = broker.get_positions()

        valid, message = risk_manager.validate_trade(
            symbol=data['symbol'],
            quantity=data['quantity'],
            price=data['price'],
            side=data['side'],
            portfolio_value=account_info['portfolio_value'],
            positions=positions
        )

        return jsonify({
            'valid': valid,
            'message': message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES DE NOTIFICATIONS ====================

@app.route('/api/notifications/history', methods=['GET'])
def get_notification_history():
    """API pour obtenir l'historique des notifications"""
    limit = int(request.args.get('limit', 50))
    return jsonify({
        'notifications': notification_system.get_notification_history(limit)
    })

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """API pour envoyer une notification manuelle"""
    try:
        data = request.get_json()

        notification_id = notification_system.send_notification(
            title=data['title'],
            message=data['message'],
            priority=NotificationPriority(data.get('priority', 'normal')),
            channels=[NotificationChannel(ch) for ch in data.get('channels', [])] if data.get('channels') else None
        )

        return jsonify({'success': True, 'notification_id': notification_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/configure', methods=['POST'])
def configure_notifications():
    """API pour configurer les canaux de notification"""
    try:
        data = request.get_json()

        notification_system.configure_channel(
            channel=NotificationChannel(data['channel']),
            enabled=data.get('enabled', True),
            config=data.get('config', {}),
            min_priority=NotificationPriority(data.get('min_priority', 'normal'))
        )

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES DE BACKTESTING ====================

@app.route('/backtesting')
def backtesting_dashboard():
    """Page du tableau de bord de backtesting"""
    # Vérifier si on doit utiliser l'interface moderne
    use_modern = request.args.get('modern', 'true').lower() == 'true'

    if use_modern:
        return render_template('backtesting_modern.html')
    else:
        return render_template('backtesting.html')

@app.route('/api/backtesting/list', methods=['GET'])
def list_backtests():
    """API pour lister les backtests"""
    return jsonify({
        'backtests': backtest_engine.list_backtests()
    })

@app.route('/api/backtesting/create', methods=['POST'])
def create_backtest():
    """API pour créer un nouveau backtest"""
    try:
        data = request.get_json()

        config = BacktestConfig(
            name=data['name'],
            description=data.get('description', ''),
            symbols=data['symbols'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            initial_capital=data.get('initial_capital', 100000),
            trading_config=data.get('trading_config', {}),
            risk_config=data.get('risk_config', {}),
            benchmark=data.get('benchmark', 'SPY'),
            commission=data.get('commission', 0.001),
            slippage=data.get('slippage', 0.0005)
        )

        backtest_id = backtest_engine.create_backtest(config)
        return jsonify({'success': True, 'backtest_id': backtest_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtesting/<backtest_id>/start', methods=['POST'])
def start_backtest(backtest_id):
    """API pour démarrer un backtest"""
    try:
        success = backtest_engine.start_backtest(backtest_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Impossible de démarrer le backtest'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtesting/<backtest_id>/status', methods=['GET'])
def get_backtest_status(backtest_id):
    """API pour obtenir le statut d'un backtest"""
    status = backtest_engine.get_backtest_status(backtest_id)
    if status:
        return jsonify(status)
    else:
        return jsonify({'error': 'Backtest non trouvé'}), 404

@app.route('/api/backtesting/<backtest_id>/results', methods=['GET'])
def get_backtest_results(backtest_id):
    """API pour obtenir les résultats d'un backtest"""
    result = backtest_engine.get_backtest_results(backtest_id)
    if result:
        return jsonify({
            'id': result.id,
            'config': {
                'name': result.config.name,
                'description': result.config.description,
                'symbols': result.config.symbols,
                'start_date': result.config.start_date,
                'end_date': result.config.end_date,
                'initial_capital': result.config.initial_capital
            },
            'status': result.status.value,
            'metrics': {
                'total_return': result.metrics.total_return,
                'annual_return': result.metrics.annual_return,
                'volatility': result.metrics.volatility,
                'sharpe_ratio': result.metrics.sharpe_ratio,
                'max_drawdown': result.metrics.max_drawdown,
                'win_rate': result.metrics.win_rate,
                'profit_factor': result.metrics.profit_factor,
                'total_trades': result.metrics.total_trades,
                'winning_trades': result.metrics.winning_trades,
                'losing_trades': result.metrics.losing_trades
            } if result.metrics else None,
            'trades_count': len(result.trades),
            'equity_curve': result.equity_curve,
            'created_at': result.created_at.isoformat(),
            'completed_at': result.completed_at.isoformat() if result.completed_at else None
        })
    else:
        return jsonify({'error': 'Résultats non trouvés'}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API pour récupérer les statistiques des analyses"""
    if db_manager:
        stats = db_manager.get_analysis_stats()
        return jsonify(stats)
    else:
        # Statistiques basiques depuis les fichiers
        results = []
        for result_file in RESULTS_DIR.glob("*.json"):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    results.append(result)
            except:
                continue

        total = len(results)
        completed = len([r for r in results if r.get('decision')])

        return jsonify({
            'total_analyses': total,
            'completed': completed,
            'success_rate': (completed / total * 100) if total > 0 else 0,
            'decisions': {
                'buy': len([r for r in results if 'buy' in str(r.get('decision', '')).lower()]),
                'sell': len([r for r in results if 'sell' in str(r.get('decision', '')).lower()]),
                'hold': len([r for r in results if 'hold' in str(r.get('decision', '')).lower()])
            }
        })

@socketio.on('connect')
def handle_connect():
    """Gérer les connexions WebSocket"""
    print(f'Client connecté: {request.sid}')
    emit('connected', {'message': 'Connexion établie avec succès'})

@socketio.on('disconnect')
def handle_disconnect():
    """Gérer les déconnexions WebSocket"""
    print(f'Client déconnecté: {request.sid}')

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('webapp/templates', exist_ok=True)
    os.makedirs('webapp/static/css', exist_ok=True)
    os.makedirs('webapp/static/js', exist_ok=True)
    
    # Démarrer l'application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
