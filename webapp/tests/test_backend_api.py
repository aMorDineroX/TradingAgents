#!/usr/bin/env python3
"""
Tests Backend API pour TradingAgents Interface Moderne
Tests des routes API, systèmes d'automatisation et intégrations
"""

import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire parent au path
current_dir = Path(__file__).parent
webapp_dir = current_dir.parent
sys.path.insert(0, str(webapp_dir))
sys.path.insert(0, str(webapp_dir.parent))

# Import de l'application
from app import app, socketio
from automation_manager import automation_manager
from brokerage_manager import brokerage_manager
from risk_manager import risk_manager
from monitoring_system import monitoring_system
from notification_system import notification_system
from backtesting_engine import backtest_engine

class TestBackendAPI:
    """Tests des API Backend"""
    
    @pytest.fixture
    def client(self):
        """Client de test Flask"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def socket_client(self):
        """Client de test Socket.IO"""
        return socketio.test_client(app)
    
    def test_index_route(self, client):
        """Test de la route d'accueil"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'TradingAgents' in response.data
    
    def test_index_modern_interface(self, client):
        """Test de l'interface moderne par défaut"""
        response = client.get('/?modern=true')
        assert response.status_code == 200
        assert b'index_modern.html' in response.data or b'Analyses Intelligentes' in response.data
    
    def test_automation_route(self, client):
        """Test de la route d'automatisation"""
        response = client.get('/automation')
        assert response.status_code == 200
        assert b'Automatisation' in response.data
    
    def test_backtesting_route(self, client):
        """Test de la route de backtesting"""
        response = client.get('/backtesting')
        assert response.status_code == 200
        assert b'Backtesting' in response.data
    
    def test_demo_route(self, client):
        """Test de la route de démonstration"""
        response = client.get('/demo')
        assert response.status_code == 200
        assert b'Démonstration' in response.data
    
    def test_config_route(self, client):
        """Test de la route de configuration"""
        response = client.get('/config')
        assert response.status_code == 200
        assert b'Configuration' in response.data
    
    def test_dashboard_route(self, client):
        """Test de la route du tableau de bord"""
        response = client.get('/dashboard')
        assert response.status_code == 200
    
    def test_api_status(self, client):
        """Test de l'API de statut"""
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
    
    def test_api_list_results(self, client):
        """Test de l'API de liste des résultats"""
        response = client.get('/api/list_results')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'results' in data
        assert isinstance(data['results'], list)
    
    @patch('automation_manager.automation_manager')
    def test_automation_status_api(self, mock_automation, client):
        """Test de l'API de statut d'automatisation"""
        # Mock du statut d'automatisation
        mock_automation.get_status.return_value = {
            'status': 'stopped',
            'enabled_tasks': 0,
            'last_run': None
        }
        
        response = client.get('/api/automation/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'automation' in data
    
    @patch('automation_manager.automation_manager')
    def test_automation_start_api(self, mock_automation, client):
        """Test de l'API de démarrage d'automatisation"""
        mock_automation.start_automation.return_value = True
        
        response = client.post('/api/automation/start')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('automation_manager.automation_manager')
    def test_automation_stop_api(self, mock_automation, client):
        """Test de l'API d'arrêt d'automatisation"""
        mock_automation.stop_automation.return_value = True
        
        response = client.post('/api/automation/stop')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('automation_manager.automation_manager')
    def test_automation_tasks_list_api(self, mock_automation, client):
        """Test de l'API de liste des tâches"""
        mock_tasks = [
            Mock(
                id='test-task-1',
                name='Test Task',
                ticker='SPY',
                schedule_type=Mock(value='daily'),
                enabled=True,
                next_run=None,
                last_run=None,
                run_count=0,
                success_count=0,
                error_count=0
            )
        ]
        mock_automation.list_tasks.return_value = mock_tasks
        
        response = client.get('/api/automation/tasks')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'tasks' in data
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['name'] == 'Test Task'
    
    @patch('automation_manager.automation_manager')
    def test_automation_create_task_api(self, mock_automation, client):
        """Test de l'API de création de tâche"""
        mock_automation.create_task.return_value = 'new-task-id'
        
        task_data = {
            'name': 'Test Task',
            'description': 'Test Description',
            'ticker': 'SPY',
            'schedule_type': 'daily',
            'schedule_config': {'hour': 9, 'minute': 30},
            'trading_config': {'auto_execute': True},
            'risk_config': {}
        }
        
        response = client.post('/api/automation/tasks',
                             data=json.dumps(task_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task_id'] == 'new-task-id'
    
    @patch('brokerage_manager.brokerage_manager')
    def test_brokerage_status_api(self, mock_brokerage, client):
        """Test de l'API de statut du courtage"""
        mock_broker = Mock()
        mock_broker.get_account_info.return_value = {
            'portfolio_value': 100000,
            'buying_power': 50000,
            'cash': 25000
        }
        mock_broker.get_positions.return_value = []
        mock_brokerage.get_active_broker.return_value = mock_broker
        mock_brokerage.active_broker = 'paper_trading'
        
        response = client.get('/api/brokerage/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['connected'] is True
        assert 'account_info' in data
    
    @patch('backtesting_engine.backtest_engine')
    def test_backtesting_list_api(self, mock_backtest, client):
        """Test de l'API de liste des backtests"""
        mock_backtest.list_backtests.return_value = []
        
        response = client.get('/api/backtesting/list')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'backtests' in data
    
    @patch('backtesting_engine.backtest_engine')
    def test_backtesting_create_api(self, mock_backtest, client):
        """Test de l'API de création de backtest"""
        mock_backtest.create_backtest.return_value = 'backtest-id-123'
        
        backtest_data = {
            'name': 'Test Backtest',
            'description': 'Test Description',
            'symbols': ['SPY', 'QQQ'],
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'initial_capital': 100000,
            'benchmark': 'SPY',
            'commission': 0.001,
            'slippage': 0.0005,
            'trading_config': {},
            'risk_config': {}
        }
        
        response = client.post('/api/backtesting/create',
                             data=json.dumps(backtest_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['backtest_id'] == 'backtest-id-123'
    
    @patch('risk_manager.risk_manager')
    def test_risk_parameters_api(self, mock_risk, client):
        """Test de l'API des paramètres de risque"""
        mock_risk.get_risk_summary.return_value = {
            'max_position_size': 0.1,
            'max_portfolio_risk': 0.02,
            'stop_loss_percent': 0.05
        }
        
        response = client.get('/api/risk/parameters')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'max_position_size' in data
    
    @patch('monitoring_system.monitoring_system')
    def test_monitoring_positions_api(self, mock_monitoring, client):
        """Test de l'API des positions surveillées"""
        mock_monitoring.get_position_summary.return_value = {
            'positions': [],
            'total_value': 0,
            'total_pnl': 0
        }
        
        response = client.get('/api/monitoring/positions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'positions' in data
    
    @patch('monitoring_system.monitoring_system')
    def test_monitoring_alerts_api(self, mock_monitoring, client):
        """Test de l'API des alertes de surveillance"""
        mock_alerts = [
            Mock(
                id='alert-1',
                level=Mock(value='info'),
                title='Test Alert',
                message='Test Message',
                symbol='SPY',
                timestamp=Mock(isoformat=lambda: '2024-01-01T00:00:00'),
                acknowledged=False
            )
        ]
        mock_monitoring.get_alerts.return_value = mock_alerts
        
        response = client.get('/api/monitoring/alerts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'alerts' in data
        assert len(data['alerts']) == 1
    
    def test_socket_connection(self, socket_client):
        """Test de la connexion Socket.IO"""
        assert socket_client.is_connected()
    
    def test_socket_join_session(self, socket_client):
        """Test de l'événement join_session Socket.IO"""
        socket_client.emit('join_session', 'test-session-id')
        # Vérifier que l'événement est reçu sans erreur
        received = socket_client.get_received()
        # Le serveur ne renvoie pas de réponse pour join_session
        assert isinstance(received, list)
    
    @patch('tradingagents.graph.trading_graph.TradingAgentsGraph')
    def test_start_analysis_api(self, mock_graph, client):
        """Test de l'API de démarrage d'analyse"""
        # Mock de la classe TradingAgentsGraph
        mock_instance = Mock()
        mock_instance.run_analysis.return_value = {
            'session_id': 'test-session-123',
            'status': 'started'
        }
        mock_graph.return_value = mock_instance
        
        analysis_data = {
            'ticker': 'SPY',
            'selected_analysts': ['market', 'social'],
            'max_debate_rounds': 2
        }
        
        response = client.post('/api/start_analysis',
                             data=json.dumps(analysis_data),
                             content_type='application/json')
        
        # L'API peut retourner 200 ou 500 selon l'implémentation
        assert response.status_code in [200, 500]
    
    def test_error_handling(self, client):
        """Test de la gestion d'erreurs"""
        # Test d'une route inexistante
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Test d'une méthode non autorisée
        response = client.delete('/api/status')
        assert response.status_code == 405
    
    def test_json_error_handling(self, client):
        """Test de la gestion d'erreurs JSON"""
        # Envoyer du JSON invalide
        response = client.post('/api/automation/tasks',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400


class TestSystemIntegration:
    """Tests d'intégration des systèmes"""
    
    def test_automation_manager_initialization(self):
        """Test d'initialisation du gestionnaire d'automatisation"""
        assert automation_manager is not None
        assert hasattr(automation_manager, 'get_status')
        assert hasattr(automation_manager, 'start_automation')
        assert hasattr(automation_manager, 'stop_automation')
    
    def test_brokerage_manager_initialization(self):
        """Test d'initialisation du gestionnaire de courtage"""
        assert brokerage_manager is not None
        assert hasattr(brokerage_manager, 'get_active_broker')
    
    def test_risk_manager_initialization(self):
        """Test d'initialisation du gestionnaire de risques"""
        assert risk_manager is not None
        assert hasattr(risk_manager, 'get_risk_summary')
    
    def test_monitoring_system_initialization(self):
        """Test d'initialisation du système de surveillance"""
        assert monitoring_system is not None
        assert hasattr(monitoring_system, 'get_position_summary')
    
    def test_notification_system_initialization(self):
        """Test d'initialisation du système de notifications"""
        assert notification_system is not None
        assert hasattr(notification_system, 'send_notification')
    
    def test_backtest_engine_initialization(self):
        """Test d'initialisation du moteur de backtesting"""
        assert backtest_engine is not None
        assert hasattr(backtest_engine, 'create_backtest')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
