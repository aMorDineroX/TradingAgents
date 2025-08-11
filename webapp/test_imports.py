#!/usr/bin/env python3
"""
Test des imports pour vérifier que tous les modules sont disponibles
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def test_basic_imports():
    """Tester les imports de base"""
    print("🧪 Test des imports de base...")
    
    try:
        import os
        import json
        import logging
        from datetime import datetime
        from pathlib import Path
        print("✅ Imports Python de base: OK")
    except Exception as e:
        print(f"❌ Imports Python de base: {e}")
        return False
    
    try:
        from flask import Flask
        from flask_socketio import SocketIO
        print("✅ Imports Flask: OK")
    except Exception as e:
        print(f"❌ Imports Flask: {e}")
        return False
    
    try:
        import requests
        import pandas as pd
        import numpy as np
        print("✅ Imports data/web: OK")
    except Exception as e:
        print(f"❌ Imports data/web: {e}")
        return False
    
    return True

def test_tradingagents_imports():
    """Tester les imports TradingAgents"""
    print("\n🧪 Test des imports TradingAgents...")
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        print("✅ Imports TradingAgents: OK")
    except Exception as e:
        print(f"❌ Imports TradingAgents: {e}")
        return False
    
    return True

def test_automation_imports():
    """Tester les imports des systèmes d'automatisation"""
    print("\n🧪 Test des imports d'automatisation...")
    
    try:
        from automation_manager import automation_manager, AutomationTask, ScheduleType
        print("✅ AutomationManager: OK")
    except Exception as e:
        print(f"❌ AutomationManager: {e}")
        return False
    
    try:
        from brokerage_manager import brokerage_manager, BrokerType, OrderSide, OrderType
        print("✅ BrokerageManager: OK")
    except Exception as e:
        print(f"❌ BrokerageManager: {e}")
        return False
    
    try:
        from risk_manager import risk_manager, RiskLevel
        print("✅ RiskManager: OK")
    except Exception as e:
        print(f"❌ RiskManager: {e}")
        return False
    
    try:
        from monitoring_system import monitoring_system, AlertLevel
        print("✅ MonitoringSystem: OK")
    except Exception as e:
        print(f"❌ MonitoringSystem: {e}")
        return False
    
    try:
        from notification_system import notification_system, NotificationChannel, NotificationPriority
        print("✅ NotificationSystem: OK")
    except Exception as e:
        print(f"❌ NotificationSystem: {e}")
        return False
    
    try:
        from backtesting_engine import backtest_engine, BacktestConfig
        print("✅ BacktestEngine: OK")
    except Exception as e:
        print(f"❌ BacktestEngine: {e}")
        return False
    
    return True

def test_database_imports():
    """Tester les imports de base de données"""
    print("\n🧪 Test des imports de base de données...")
    
    try:
        from database import get_db_manager, init_database
        print("✅ Database: OK")
    except Exception as e:
        print(f"❌ Database: {e}")
        return False
    
    return True

def test_config_imports():
    """Tester les imports de configuration"""
    print("\n🧪 Test des imports de configuration...")
    
    try:
        from config_manager import ConfigManager
        print("✅ ConfigManager: OK")
    except Exception as e:
        print(f"❌ ConfigManager: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🔍 Test des imports pour TradingAgents Automation")
    print("=" * 60)
    
    all_tests = [
        test_basic_imports,
        test_tradingagents_imports,
        test_automation_imports,
        test_database_imports,
        test_config_imports
    ]
    
    passed = 0
    total = len(all_tests)
    
    for test in all_tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les imports sont OK!")
        print("✅ L'application devrait démarrer sans problème")
        return True
    else:
        print("❌ Certains imports échouent")
        print("💡 Installez les dépendances manquantes:")
        print("   pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
