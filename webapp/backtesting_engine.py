"""
Moteur de backtesting automatisé pour TradingAgents
Test des stratégies sur données historiques avant déploiement live
"""

import os
import json
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import yfinance as yf
import asyncio
import threading

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestStatus(Enum):
    """Statuts de backtest"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BacktestConfig:
    """Configuration de backtest"""
    name: str
    description: str
    symbols: List[str]
    start_date: str
    end_date: str
    initial_capital: float
    trading_config: Dict[str, Any]
    risk_config: Dict[str, Any]
    benchmark: str = "SPY"
    commission: float = 0.001  # 0.1% par trade
    slippage: float = 0.0005   # 0.05% de slippage
    
@dataclass
class Trade:
    """Trade de backtest"""
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    side: str  # "BUY" ou "SELL"
    pnl: Optional[float] = None
    commission: float = 0.0
    reason: str = ""  # Raison de sortie
    
@dataclass
class BacktestMetrics:
    """Métriques de performance du backtest"""
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    benchmark_return: float
    alpha: float
    beta: float

@dataclass
class BacktestResult:
    """Résultat complet de backtest"""
    id: str
    config: BacktestConfig
    status: BacktestStatus
    metrics: Optional[BacktestMetrics]
    trades: List[Trade]
    equity_curve: List[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DataProvider:
    """Fournisseur de données historiques"""
    
    def __init__(self):
        self.cache = {}
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Obtenir les données historiques d'un symbole"""
        try:
            cache_key = f"{symbol}_{start_date}_{end_date}"
            
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Télécharger les données avec yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"⚠️ Aucune donnée pour {symbol}")
                return None
            
            # Nettoyer les données
            data = data.dropna()
            data.index = pd.to_datetime(data.index)
            
            # Ajouter à la cache
            self.cache[cache_key] = data
            
            logger.info(f"📊 Données chargées pour {symbol}: {len(data)} jours")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données {symbol}: {e}")
            return None
    
    def get_multiple_symbols(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """Obtenir les données pour plusieurs symboles"""
        data = {}
        for symbol in symbols:
            symbol_data = self.get_historical_data(symbol, start_date, end_date)
            if symbol_data is not None:
                data[symbol] = symbol_data
        return data

class BacktestEngine:
    """Moteur principal de backtesting"""
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.active_backtests: Dict[str, BacktestResult] = {}
        self.completed_backtests: Dict[str, BacktestResult] = {}
        
        # Thread pool pour les backtests
        self.executor_threads: Dict[str, threading.Thread] = {}
        
        logger.info("🔬 BacktestEngine initialisé")
    
    def create_backtest(self, config: BacktestConfig) -> str:
        """Créer un nouveau backtest"""
        backtest_id = f"backtest_{int(datetime.now().timestamp())}"
        
        result = BacktestResult(
            id=backtest_id,
            config=config,
            status=BacktestStatus.PENDING,
            metrics=None,
            trades=[],
            equity_curve=[],
            created_at=datetime.now()
        )
        
        self.active_backtests[backtest_id] = result
        
        logger.info(f"📋 Backtest créé: {config.name} ({backtest_id})")
        return backtest_id
    
    def start_backtest(self, backtest_id: str) -> bool:
        """Démarrer un backtest"""
        if backtest_id not in self.active_backtests:
            return False
        
        result = self.active_backtests[backtest_id]
        if result.status != BacktestStatus.PENDING:
            return False
        
        # Démarrer le backtest dans un thread séparé
        thread = threading.Thread(
            target=self._run_backtest,
            args=(backtest_id,),
            daemon=True
        )
        
        self.executor_threads[backtest_id] = thread
        thread.start()
        
        logger.info(f"🚀 Backtest démarré: {backtest_id}")
        return True
    
    def _run_backtest(self, backtest_id: str):
        """Exécuter un backtest"""
        result = self.active_backtests[backtest_id]
        config = result.config
        
        try:
            result.status = BacktestStatus.RUNNING
            result.started_at = datetime.now()
            
            logger.info(f"🔬 Exécution backtest: {config.name}")
            
            # 1. Charger les données historiques
            logger.info("📊 Chargement des données historiques...")
            data = self.data_provider.get_multiple_symbols(
                config.symbols, config.start_date, config.end_date
            )
            
            if not data:
                raise Exception("Aucune donnée historique disponible")
            
            # 2. Initialiser le portefeuille
            portfolio = BacktestPortfolio(config.initial_capital, config.commission, config.slippage)
            
            # 3. Obtenir les dates de trading
            all_dates = set()
            for symbol_data in data.values():
                all_dates.update(symbol_data.index)
            
            trading_dates = sorted(list(all_dates))
            
            # 4. Simuler le trading jour par jour
            logger.info(f"📈 Simulation sur {len(trading_dates)} jours...")
            
            for i, current_date in enumerate(trading_dates):
                # Mettre à jour les prix du portefeuille
                current_prices = {}
                for symbol, symbol_data in data.items():
                    if current_date in symbol_data.index:
                        current_prices[symbol] = symbol_data.loc[current_date, 'Close']
                
                portfolio.update_prices(current_date, current_prices)
                
                # Simuler les signaux de trading (ici on simule)
                # En réalité, on appellerait TradingAgents pour chaque symbole
                signals = self._simulate_trading_signals(config, current_date, data, i)
                
                # Exécuter les trades
                for signal in signals:
                    trade = portfolio.execute_trade(
                        symbol=signal['symbol'],
                        side=signal['side'],
                        quantity=signal['quantity'],
                        price=signal['price'],
                        date=current_date,
                        reason=signal.get('reason', 'Signal')
                    )
                    
                    if trade:
                        result.trades.append(trade)
                
                # Enregistrer l'équité
                equity_point = {
                    'date': current_date.isoformat(),
                    'equity': portfolio.total_value,
                    'cash': portfolio.cash,
                    'positions_value': portfolio.positions_value
                }
                result.equity_curve.append(equity_point)
                
                # Progression
                if i % 50 == 0:
                    progress = (i / len(trading_dates)) * 100
                    logger.info(f"📊 Progression: {progress:.1f}%")
            
            # 5. Calculer les métriques finales
            logger.info("📊 Calcul des métriques...")
            result.metrics = self._calculate_metrics(result, config, data)
            
            # 6. Finaliser
            result.status = BacktestStatus.COMPLETED
            result.completed_at = datetime.now()
            
            # Déplacer vers les backtests terminés
            self.completed_backtests[backtest_id] = result
            del self.active_backtests[backtest_id]
            
            duration = (result.completed_at - result.started_at).total_seconds()
            logger.info(f"✅ Backtest terminé: {config.name} ({duration:.1f}s)")
            
        except Exception as e:
            result.status = BacktestStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now()
            
            logger.error(f"❌ Backtest échoué: {config.name} - {e}")
        
        finally:
            # Nettoyer le thread
            if backtest_id in self.executor_threads:
                del self.executor_threads[backtest_id]
    
    def _simulate_trading_signals(self, config: BacktestConfig, current_date: datetime, 
                                data: Dict[str, pd.DataFrame], day_index: int) -> List[Dict[str, Any]]:
        """Simuler des signaux de trading (à remplacer par TradingAgents)"""
        signals = []
        
        # Stratégie simple pour la simulation: momentum sur 20 jours
        if day_index < 20:
            return signals
        
        for symbol, symbol_data in data.items():
            if current_date not in symbol_data.index:
                continue
            
            # Calculer le momentum sur 20 jours
            end_idx = symbol_data.index.get_loc(current_date)
            if end_idx < 20:
                continue
            
            recent_data = symbol_data.iloc[end_idx-19:end_idx+1]
            current_price = recent_data['Close'].iloc[-1]
            avg_price = recent_data['Close'].mean()
            
            # Signal simple basé sur le momentum
            if current_price > avg_price * 1.02:  # 2% au-dessus de la moyenne
                signals.append({
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': 100,  # Quantité fixe pour la simulation
                    'price': current_price,
                    'reason': 'Momentum positif'
                })
            elif current_price < avg_price * 0.98:  # 2% en-dessous de la moyenne
                signals.append({
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': 100,
                    'price': current_price,
                    'reason': 'Momentum négatif'
                })
        
        return signals
    
    def _calculate_metrics(self, result: BacktestResult, config: BacktestConfig, 
                          data: Dict[str, pd.DataFrame]) -> BacktestMetrics:
        """Calculer les métriques de performance"""
        try:
            if not result.equity_curve:
                raise Exception("Pas de courbe d'équité")
            
            # Convertir la courbe d'équité en DataFrame
            equity_df = pd.DataFrame(result.equity_curve)
            equity_df['date'] = pd.to_datetime(equity_df['date'])
            equity_df.set_index('date', inplace=True)
            
            # Calculer les retours
            equity_df['returns'] = equity_df['equity'].pct_change().fillna(0)
            
            # Métriques de base
            total_return = (equity_df['equity'].iloc[-1] / config.initial_capital) - 1
            
            # Retour annualisé
            days = len(equity_df)
            annual_return = (1 + total_return) ** (252 / days) - 1
            
            # Volatilité annualisée
            volatility = equity_df['returns'].std() * np.sqrt(252)
            
            # Ratio de Sharpe (en supposant un taux sans risque de 2%)
            risk_free_rate = 0.02
            sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            # Drawdown maximum
            equity_df['peak'] = equity_df['equity'].cummax()
            equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
            max_drawdown = equity_df['drawdown'].min()
            
            # Métriques des trades
            completed_trades = [t for t in result.trades if t.exit_date is not None]
            winning_trades = [t for t in completed_trades if t.pnl and t.pnl > 0]
            losing_trades = [t for t in completed_trades if t.pnl and t.pnl < 0]
            
            win_rate = len(winning_trades) / len(completed_trades) if completed_trades else 0
            
            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            
            largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
            largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0
            
            # Profit factor
            total_wins = sum([t.pnl for t in winning_trades]) if winning_trades else 0
            total_losses = abs(sum([t.pnl for t in losing_trades])) if losing_trades else 0
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            
            # Benchmark (SPY par défaut)
            benchmark_return = 0
            alpha = 0
            beta = 0
            
            if config.benchmark in data:
                benchmark_data = data[config.benchmark]
                benchmark_start = benchmark_data['Close'].iloc[0]
                benchmark_end = benchmark_data['Close'].iloc[-1]
                benchmark_return = (benchmark_end / benchmark_start) - 1
                
                # Alpha et Beta (calcul simplifié)
                alpha = total_return - benchmark_return
                # Beta nécessiterait une régression plus complexe
                beta = 1.0  # Valeur par défaut
            
            return BacktestMetrics(
                total_return=total_return,
                annual_return=annual_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_trades=len(completed_trades),
                winning_trades=len(winning_trades),
                losing_trades=len(losing_trades),
                avg_win=avg_win,
                avg_loss=avg_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                benchmark_return=benchmark_return,
                alpha=alpha,
                beta=beta
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul métriques: {e}")
            # Retourner des métriques par défaut
            return BacktestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def get_backtest_status(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'un backtest"""
        result = None
        
        if backtest_id in self.active_backtests:
            result = self.active_backtests[backtest_id]
        elif backtest_id in self.completed_backtests:
            result = self.completed_backtests[backtest_id]
        
        if result:
            return {
                'id': result.id,
                'name': result.config.name,
                'status': result.status.value,
                'created_at': result.created_at.isoformat(),
                'started_at': result.started_at.isoformat() if result.started_at else None,
                'completed_at': result.completed_at.isoformat() if result.completed_at else None,
                'error_message': result.error_message,
                'total_trades': len(result.trades),
                'equity_points': len(result.equity_curve)
            }
        
        return None
    
    def get_backtest_results(self, backtest_id: str) -> Optional[BacktestResult]:
        """Obtenir les résultats complets d'un backtest"""
        if backtest_id in self.completed_backtests:
            return self.completed_backtests[backtest_id]
        return None
    
    def list_backtests(self) -> List[Dict[str, Any]]:
        """Lister tous les backtests"""
        all_backtests = []
        
        # Backtests actifs
        for result in self.active_backtests.values():
            all_backtests.append({
                'id': result.id,
                'name': result.config.name,
                'status': result.status.value,
                'created_at': result.created_at.isoformat(),
                'symbols': result.config.symbols
            })
        
        # Backtests terminés
        for result in self.completed_backtests.values():
            all_backtests.append({
                'id': result.id,
                'name': result.config.name,
                'status': result.status.value,
                'created_at': result.created_at.isoformat(),
                'symbols': result.config.symbols,
                'total_return': result.metrics.total_return if result.metrics else None
            })
        
        return sorted(all_backtests, key=lambda x: x['created_at'], reverse=True)

class BacktestPortfolio:
    """Portefeuille de simulation pour backtest"""
    
    def __init__(self, initial_capital: float, commission: float = 0.001, slippage: float = 0.0005):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.positions: Dict[str, int] = {}  # symbol -> quantity
        self.current_prices: Dict[str, float] = {}
        self.total_value = initial_capital
        self.positions_value = 0
    
    def update_prices(self, date: datetime, prices: Dict[str, float]):
        """Mettre à jour les prix actuels"""
        self.current_prices.update(prices)
        
        # Recalculer la valeur du portefeuille
        self.positions_value = sum(
            self.positions.get(symbol, 0) * price
            for symbol, price in self.current_prices.items()
        )
        
        self.total_value = self.cash + self.positions_value
    
    def execute_trade(self, symbol: str, side: str, quantity: int, price: float, 
                     date: datetime, reason: str = "") -> Optional[Trade]:
        """Exécuter un trade"""
        try:
            # Appliquer le slippage
            if side == 'BUY':
                execution_price = price * (1 + self.slippage)
            else:
                execution_price = price * (1 - self.slippage)
            
            trade_value = quantity * execution_price
            commission_cost = trade_value * self.commission
            
            if side == 'BUY':
                total_cost = trade_value + commission_cost
                
                if self.cash >= total_cost:
                    self.cash -= total_cost
                    self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                    
                    return Trade(
                        symbol=symbol,
                        entry_date=date,
                        exit_date=None,
                        entry_price=execution_price,
                        exit_price=None,
                        quantity=quantity,
                        side=side,
                        commission=commission_cost,
                        reason=reason
                    )
            
            elif side == 'SELL':
                current_position = self.positions.get(symbol, 0)
                
                if current_position >= quantity:
                    self.cash += trade_value - commission_cost
                    self.positions[symbol] = current_position - quantity
                    
                    if self.positions[symbol] == 0:
                        del self.positions[symbol]
                    
                    return Trade(
                        symbol=symbol,
                        entry_date=date,
                        exit_date=date,
                        entry_price=execution_price,
                        exit_price=execution_price,
                        quantity=quantity,
                        side=side,
                        commission=commission_cost,
                        reason=reason
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution trade: {e}")
            return None

# Instance globale
backtest_engine = BacktestEngine()
