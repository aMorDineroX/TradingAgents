"""
Gestionnaire de base de données pour TradingAgents Web Interface
Utilise PostgreSQL via Neon pour stocker les analyses et configurations
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class AnalysisResult(Base):
    """Modèle pour stocker les résultats d'analyses"""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    trade_date = Column(String(20), nullable=False)
    decision = Column(String(50))
    final_state = Column(JSON)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='pending')  # pending, running, completed, error
    error_message = Column(Text)

class Configuration(Base):
    """Modèle pour stocker les configurations"""
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    config_data = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSession(Base):
    """Modèle pour stocker les sessions utilisateur"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False)
    user_agent = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Gestionnaire de base de données pour TradingAgents"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL non définie")
        
        # Créer le moteur de base de données
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # Mettre à True pour voir les requêtes SQL
        )
        
        # Créer la session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Créer les tables
        self.create_tables()
    
    def create_tables(self):
        """Créer toutes les tables dans la base de données"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Tables de base de données créées avec succès")
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la création des tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Obtenir une session de base de données"""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Tester la connexion à la base de données"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                session.commit()
                logger.info("✅ Connexion à la base de données réussie")
                return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur de connexion à la base de données: {e}")
            return False
    
    # Méthodes pour les résultats d'analyses
    def save_analysis_result(self, session_id: str, ticker: str, trade_date: str, 
                           config: Dict[str, Any], status: str = 'pending') -> bool:
        """Sauvegarder un résultat d'analyse"""
        try:
            with self.get_session() as session:
                analysis = AnalysisResult(
                    session_id=session_id,
                    ticker=ticker,
                    trade_date=trade_date,
                    config=config,
                    status=status
                )
                session.add(analysis)
                session.commit()
                logger.info(f"✅ Analyse sauvegardée: {session_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    def update_analysis_result(self, session_id: str, decision: Optional[str] = None,
                             final_state: Optional[Dict] = None, status: Optional[str] = None,
                             error_message: Optional[str] = None) -> bool:
        """Mettre à jour un résultat d'analyse"""
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter_by(session_id=session_id).first()
                if analysis:
                    if decision is not None:
                        analysis.decision = decision
                    if final_state is not None:
                        analysis.final_state = final_state
                    if status is not None:
                        analysis.status = status
                    if error_message is not None:
                        analysis.error_message = error_message
                    analysis.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"✅ Analyse mise à jour: {session_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Analyse non trouvée: {session_id}")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la mise à jour: {e}")
            return False
    
    def get_analysis_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer un résultat d'analyse"""
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter_by(session_id=session_id).first()
                if analysis:
                    return {
                        'session_id': analysis.session_id,
                        'ticker': analysis.ticker,
                        'trade_date': analysis.trade_date,
                        'decision': analysis.decision,
                        'final_state': analysis.final_state,
                        'config': analysis.config,
                        'status': analysis.status,
                        'error_message': analysis.error_message,
                        'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                        'updated_at': analysis.updated_at.isoformat() if analysis.updated_at else None
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la récupération: {e}")
            return None
    
    def list_analysis_results(self, limit: int = 100, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lister les résultats d'analyses"""
        try:
            with self.get_session() as session:
                query = session.query(AnalysisResult)
                if ticker:
                    query = query.filter_by(ticker=ticker)
                analyses = query.order_by(AnalysisResult.created_at.desc()).limit(limit).all()
                
                return [{
                    'session_id': analysis.session_id,
                    'ticker': analysis.ticker,
                    'trade_date': analysis.trade_date,
                    'decision': analysis.decision,
                    'status': analysis.status,
                    'created_at': analysis.created_at.isoformat() if analysis.created_at else None
                } for analysis in analyses]
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la liste: {e}")
            return []
    
    # Méthodes pour les configurations
    def save_configuration(self, name: str, config_data: Dict[str, Any], 
                          description: str = "", is_default: bool = False) -> bool:
        """Sauvegarder une configuration"""
        try:
            with self.get_session() as session:
                config = Configuration(
                    name=name,
                    description=description,
                    config_data=config_data,
                    is_default=is_default
                )
                session.add(config)
                session.commit()
                logger.info(f"✅ Configuration sauvegardée: {name}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la sauvegarde de configuration: {e}")
            return False
    
    def get_configuration(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupérer une configuration"""
        try:
            with self.get_session() as session:
                config = session.query(Configuration).filter_by(name=name).first()
                if config:
                    return {
                        'name': config.name,
                        'description': config.description,
                        'config_data': config.config_data,
                        'is_default': config.is_default,
                        'created_at': config.created_at.isoformat() if config.created_at else None
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la récupération de configuration: {e}")
            return None
    
    def list_configurations(self) -> List[Dict[str, Any]]:
        """Lister toutes les configurations"""
        try:
            with self.get_session() as session:
                configs = session.query(Configuration).order_by(Configuration.created_at.desc()).all()
                return [{
                    'name': config.name,
                    'description': config.description,
                    'is_default': config.is_default,
                    'created_at': config.created_at.isoformat() if config.created_at else None
                } for config in configs]
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors de la liste des configurations: {e}")
            return []
    
    # Méthodes pour les statistiques
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques des analyses"""
        try:
            with self.get_session() as session:
                total = session.query(AnalysisResult).count()
                completed = session.query(AnalysisResult).filter_by(status='completed').count()
                pending = session.query(AnalysisResult).filter_by(status='pending').count()
                running = session.query(AnalysisResult).filter_by(status='running').count()
                errors = session.query(AnalysisResult).filter_by(status='error').count()
                
                # Statistiques par décision
                buy_count = session.query(AnalysisResult).filter(
                    AnalysisResult.decision.ilike('%buy%')
                ).count()
                sell_count = session.query(AnalysisResult).filter(
                    AnalysisResult.decision.ilike('%sell%')
                ).count()
                hold_count = session.query(AnalysisResult).filter(
                    AnalysisResult.decision.ilike('%hold%')
                ).count()
                
                return {
                    'total_analyses': total,
                    'completed': completed,
                    'pending': pending,
                    'running': running,
                    'errors': errors,
                    'success_rate': (completed / total * 100) if total > 0 else 0,
                    'decisions': {
                        'buy': buy_count,
                        'sell': sell_count,
                        'hold': hold_count
                    }
                }
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur lors du calcul des statistiques: {e}")
            return {}

# Instance globale du gestionnaire de base de données
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obtenir l'instance du gestionnaire de base de données"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_database():
    """Initialiser la base de données"""
    try:
        db = get_db_manager()
        if db.test_connection():
            logger.info("🗄️ Base de données Neon PostgreSQL initialisée avec succès")
            return True
        else:
            logger.error("❌ Échec de l'initialisation de la base de données")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        return False
