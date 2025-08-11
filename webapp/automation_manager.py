"""
Gestionnaire d'automatisation pour TradingAgents
Système central pour l'automatisation des analyses et du trading
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomationStatus(Enum):
    """Statuts d'automatisation"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class ScheduleType(Enum):
    """Types de planification"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class TradingMode(Enum):
    """Modes de trading"""
    PAPER = "paper"  # Trading simulé
    LIVE = "live"    # Trading réel

@dataclass
class AutomationTask:
    """Tâche d'automatisation"""
    id: str
    name: str
    description: str
    ticker: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    trading_config: Dict[str, Any]
    risk_config: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = None
    last_run: datetime = None
    next_run: datetime = None
    run_count: int = 0
    success_count: int = 0
    error_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self._calculate_next_run()
    
    def _calculate_next_run(self):
        """Calculer la prochaine exécution"""
        now = datetime.now()
        
        if self.schedule_type == ScheduleType.ONCE:
            if self.last_run is None:
                self.next_run = now + timedelta(minutes=1)  # Exécuter dans 1 minute
            else:
                self.next_run = None  # Plus d'exécution
                
        elif self.schedule_type == ScheduleType.DAILY:
            hour = self.schedule_config.get('hour', 9)
            minute = self.schedule_config.get('minute', 30)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            self.next_run = next_run
            
        elif self.schedule_type == ScheduleType.WEEKLY:
            weekday = self.schedule_config.get('weekday', 0)  # 0 = Lundi
            hour = self.schedule_config.get('hour', 9)
            minute = self.schedule_config.get('minute', 30)
            
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:  # La date cible est aujourd'hui ou dans le passé
                days_ahead += 7
            
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            self.next_run = next_run
            
        elif self.schedule_type == ScheduleType.CUSTOM:
            interval_minutes = self.schedule_config.get('interval_minutes', 60)
            self.next_run = now + timedelta(minutes=interval_minutes)

class AutomationManager:
    """Gestionnaire principal d'automatisation"""
    
    def __init__(self, config_dir: str = "automation"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.tasks: Dict[str, AutomationTask] = {}
        self.status = AutomationStatus.STOPPED
        self.worker_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks pour les événements
        self.on_analysis_complete: Optional[Callable] = None
        self.on_trade_signal: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Charger les tâches existantes
        self.load_tasks()
        
        logger.info("🤖 AutomationManager initialisé")
    
    def load_tasks(self):
        """Charger les tâches depuis les fichiers"""
        tasks_file = self.config_dir / "tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                
                for task_data in tasks_data:
                    # Convertir les dates
                    if task_data.get('created_at'):
                        task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
                    if task_data.get('last_run'):
                        task_data['last_run'] = datetime.fromisoformat(task_data['last_run'])
                    if task_data.get('next_run'):
                        task_data['next_run'] = datetime.fromisoformat(task_data['next_run'])
                    
                    # Convertir les enums
                    task_data['schedule_type'] = ScheduleType(task_data['schedule_type'])
                    
                    task = AutomationTask(**task_data)
                    self.tasks[task.id] = task
                
                logger.info(f"✅ {len(self.tasks)} tâches chargées")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement des tâches: {e}")
    
    def save_tasks(self):
        """Sauvegarder les tâches dans un fichier"""
        tasks_file = self.config_dir / "tasks.json"
        try:
            tasks_data = []
            for task in self.tasks.values():
                task_dict = asdict(task)
                # Convertir les dates en string
                if task_dict.get('created_at'):
                    task_dict['created_at'] = task_dict['created_at'].isoformat()
                if task_dict.get('last_run'):
                    task_dict['last_run'] = task_dict['last_run'].isoformat()
                if task_dict.get('next_run'):
                    task_dict['next_run'] = task_dict['next_run'].isoformat()
                
                # Convertir les enums
                task_dict['schedule_type'] = task_dict['schedule_type'].value
                
                tasks_data.append(task_dict)
            
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"✅ {len(tasks_data)} tâches sauvegardées")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des tâches: {e}")
    
    def create_task(self, name: str, description: str, ticker: str, 
                   schedule_type: ScheduleType, schedule_config: Dict[str, Any],
                   trading_config: Dict[str, Any], risk_config: Dict[str, Any]) -> str:
        """Créer une nouvelle tâche d'automatisation"""
        task_id = f"task_{int(time.time())}_{ticker}"
        
        task = AutomationTask(
            id=task_id,
            name=name,
            description=description,
            ticker=ticker,
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            trading_config=trading_config,
            risk_config=risk_config
        )
        
        self.tasks[task_id] = task
        self.save_tasks()
        
        logger.info(f"✅ Tâche créée: {name} ({task_id})")
        return task_id
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Mettre à jour une tâche"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Recalculer la prochaine exécution si nécessaire
        if 'schedule_type' in kwargs or 'schedule_config' in kwargs:
            task._calculate_next_run()
        
        self.save_tasks()
        logger.info(f"✅ Tâche mise à jour: {task_id}")
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Supprimer une tâche"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            logger.info(f"✅ Tâche supprimée: {task_id}")
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[AutomationTask]:
        """Récupérer une tâche"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, enabled_only: bool = False) -> List[AutomationTask]:
        """Lister les tâches"""
        tasks = list(self.tasks.values())
        if enabled_only:
            tasks = [t for t in tasks if t.enabled]
        return sorted(tasks, key=lambda t: t.created_at)
    
    def start_automation(self):
        """Démarrer l'automatisation"""
        if self.status == AutomationStatus.RUNNING:
            logger.warning("⚠️ L'automatisation est déjà en cours")
            return
        
        self.status = AutomationStatus.RUNNING
        self.stop_event.clear()
        
        self.worker_thread = threading.Thread(target=self._automation_worker, daemon=True)
        self.worker_thread.start()
        
        logger.info("🚀 Automatisation démarrée")
    
    def stop_automation(self):
        """Arrêter l'automatisation"""
        if self.status != AutomationStatus.RUNNING:
            return
        
        self.status = AutomationStatus.STOPPED
        self.stop_event.set()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        logger.info("🛑 Automatisation arrêtée")
    
    def pause_automation(self):
        """Mettre en pause l'automatisation"""
        if self.status == AutomationStatus.RUNNING:
            self.status = AutomationStatus.PAUSED
            logger.info("⏸️ Automatisation mise en pause")
    
    def resume_automation(self):
        """Reprendre l'automatisation"""
        if self.status == AutomationStatus.PAUSED:
            self.status = AutomationStatus.RUNNING
            logger.info("▶️ Automatisation reprise")
    
    def _automation_worker(self):
        """Worker principal d'automatisation"""
        logger.info("🔄 Worker d'automatisation démarré")
        
        while not self.stop_event.is_set():
            try:
                if self.status == AutomationStatus.RUNNING:
                    self._check_and_execute_tasks()
                
                # Attendre 30 secondes avant la prochaine vérification
                self.stop_event.wait(30)
                
            except Exception as e:
                logger.error(f"❌ Erreur dans le worker d'automatisation: {e}")
                self.status = AutomationStatus.ERROR
                if self.on_error:
                    self.on_error(e)
                break
        
        logger.info("🔄 Worker d'automatisation arrêté")
    
    def _check_and_execute_tasks(self):
        """Vérifier et exécuter les tâches dues"""
        now = datetime.now()
        
        for task in self.tasks.values():
            if not task.enabled or not task.next_run:
                continue
            
            if task.next_run <= now:
                logger.info(f"🎯 Exécution de la tâche: {task.name} ({task.ticker})")
                self._execute_task(task)
    
    def _execute_task(self, task: AutomationTask):
        """Exécuter une tâche d'automatisation"""
        try:
            task.run_count += 1
            task.last_run = datetime.now()
            
            # Ici, nous appellerons l'analyse TradingAgents
            # Pour l'instant, simulons l'exécution
            logger.info(f"📊 Analyse en cours pour {task.ticker}...")
            
            # Simuler une analyse (à remplacer par l'appel réel)
            analysis_result = {
                'ticker': task.ticker,
                'decision': 'HOLD',  # Simulé
                'confidence': 0.75,
                'timestamp': datetime.now().isoformat()
            }
            
            # Callback pour l'analyse terminée
            if self.on_analysis_complete:
                self.on_analysis_complete(task, analysis_result)
            
            task.success_count += 1
            task._calculate_next_run()  # Calculer la prochaine exécution
            
            logger.info(f"✅ Tâche exécutée avec succès: {task.name}")
            
        except Exception as e:
            task.error_count += 1
            logger.error(f"❌ Erreur lors de l'exécution de la tâche {task.name}: {e}")
            
            if self.on_error:
                self.on_error(e)
        
        finally:
            self.save_tasks()
    
    def get_status(self) -> Dict[str, Any]:
        """Obtenir le statut de l'automatisation"""
        return {
            'status': self.status.value,
            'total_tasks': len(self.tasks),
            'enabled_tasks': len([t for t in self.tasks.values() if t.enabled]),
            'next_execution': min([t.next_run for t in self.tasks.values() 
                                 if t.enabled and t.next_run], default=None),
            'total_runs': sum(t.run_count for t in self.tasks.values()),
            'total_successes': sum(t.success_count for t in self.tasks.values()),
            'total_errors': sum(t.error_count for t in self.tasks.values())
        }

# Instance globale
automation_manager = AutomationManager()
