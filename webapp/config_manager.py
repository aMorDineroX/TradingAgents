"""
Gestionnaire de configuration pour TradingAgents Web Interface
Gère la persistance et la validation des configurations
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import copy

class ConfigManager:
    """Gestionnaire de configuration pour l'application web TradingAgents"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Fichiers de configuration
        self.default_config_file = self.config_dir / "default.json"
        self.user_config_file = self.config_dir / "user.json"
        self.presets_file = self.config_dir / "presets.json"
        
        # Configuration par défaut
        self.default_config = {
            "llm_provider": "openai",  # Groq via API compatible OpenAI
            "quick_think_llm": "llama-3.1-8b-instant",
            "deep_think_llm": "llama-3.1-8b-instant",  # Utiliser le même modèle rapide
            "backend_url": "https://api.groq.com/openai/v1",
            "selected_analysts": ["market", "social", "news", "fundamentals"],
            "max_debate_rounds": 2,
            "max_risk_discuss_rounds": 2,
            "online_tools": True,
            "temperature": 0.7,
            "max_tokens": 4000,
            "timeout": 60,
            "results_dir": "results",
            "log_level": "INFO",
            "project_dir": ".",
            "debug": True
        }
        
        # Préréglages par défaut
        self.default_presets = {
            "fast": {
                "name": "Configuration Rapide",
                "description": "Analyse rapide avec modèles légers",
                "config": {
                    "llm_provider": "openai",
                    "quick_think_llm": "llama-3.1-8b-instant",
                    "deep_think_llm": "llama-3.1-8b-instant",
                    "max_debate_rounds": 1,
                    "max_risk_discuss_rounds": 1,
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "online_tools": False
                }
            },
            "balanced": {
                "name": "Configuration Équilibrée",
                "description": "Bon compromis vitesse/qualité",
                "config": {
                    "llm_provider": "openai",
                    "quick_think_llm": "llama-3.1-8b-instant",
                    "deep_think_llm": "llama-3.1-8b-instant",
                    "max_debate_rounds": 2,
                    "max_risk_discuss_rounds": 2,
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "online_tools": True
                }
            },
            "deep": {
                "name": "Configuration Approfondie",
                "description": "Analyse détaillée avec modèles avancés",
                "config": {
                    "llm_provider": "openai",
                    "quick_think_llm": "llama-3.1-8b-instant",
                    "deep_think_llm": "mixtral-8x7b-32768",
                    "max_debate_rounds": 3,
                    "max_risk_discuss_rounds": 3,
                    "temperature": 0.8,
                    "max_tokens": 6000,
                    "online_tools": True
                }
            }
        }
        
        self.initialize_configs()
    
    def initialize_configs(self):
        """Initialiser les fichiers de configuration s'ils n'existent pas"""
        if not self.default_config_file.exists():
            self.save_config(self.default_config, self.default_config_file)
        
        if not self.presets_file.exists():
            self.save_presets(self.default_presets)
    
    def load_config(self, config_file: Optional[Path] = None) -> Dict[str, Any]:
        """Charger une configuration depuis un fichier"""
        if config_file is None:
            config_file = self.user_config_file
        
        if not config_file.exists():
            return copy.deepcopy(self.default_config)
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Fusionner avec la configuration par défaut pour s'assurer que toutes les clés existent
            merged_config = copy.deepcopy(self.default_config)
            merged_config.update(config)
            
            return merged_config
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return copy.deepcopy(self.default_config)
    
    def save_config(self, config: Dict[str, Any], config_file: Optional[Path] = None):
        """Sauvegarder une configuration dans un fichier"""
        if config_file is None:
            config_file = self.user_config_file
        
        try:
            # Valider la configuration avant de la sauvegarder
            validated_config = self.validate_config(config)
            
            # Ajouter des métadonnées
            config_with_metadata = {
                "config": validated_config,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_with_metadata, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valider et nettoyer une configuration"""
        validated_config = copy.deepcopy(self.default_config)
        
        # Valider les types et valeurs
        for key, value in config.items():
            if key in validated_config:
                if key == "llm_provider" and value in ["openai", "anthropic", "google", "groq"]:
                    validated_config[key] = value
                elif key == "selected_analysts" and isinstance(value, list):
                    valid_analysts = ["market", "social", "news", "fundamentals"]
                    validated_config[key] = [a for a in value if a in valid_analysts]
                elif key in ["max_debate_rounds", "max_risk_discuss_rounds"] and isinstance(value, int) and 1 <= value <= 5:
                    validated_config[key] = value
                elif key == "temperature" and isinstance(value, (int, float)) and 0 <= value <= 2:
                    validated_config[key] = float(value)
                elif key == "max_tokens" and isinstance(value, int) and 100 <= value <= 8000:
                    validated_config[key] = value
                elif key == "timeout" and isinstance(value, int) and 10 <= value <= 300:
                    validated_config[key] = value
                elif key == "online_tools" and isinstance(value, bool):
                    validated_config[key] = value
                elif key in ["quick_think_llm", "deep_think_llm", "backend_url", "results_dir", "log_level", "project_dir"]:
                    validated_config[key] = str(value)
                elif key == "debug" and isinstance(value, bool):
                    validated_config[key] = value
        
        return validated_config
    
    def load_presets(self) -> Dict[str, Any]:
        """Charger les préréglages"""
        if not self.presets_file.exists():
            return copy.deepcopy(self.default_presets)
        
        try:
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des préréglages: {e}")
            return copy.deepcopy(self.default_presets)
    
    def save_presets(self, presets: Dict[str, Any]):
        """Sauvegarder les préréglages"""
        try:
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(presets, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des préréglages: {e}")
            return False
    
    def get_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer un préréglage spécifique"""
        presets = self.load_presets()
        return presets.get(preset_name)
    
    def create_preset(self, name: str, description: str, config: Dict[str, Any]) -> bool:
        """Créer un nouveau préréglage"""
        presets = self.load_presets()
        
        preset_key = name.lower().replace(" ", "_")
        presets[preset_key] = {
            "name": name,
            "description": description,
            "config": self.validate_config(config),
            "created_at": datetime.now().isoformat()
        }
        
        return self.save_presets(presets)
    
    def delete_preset(self, preset_name: str) -> bool:
        """Supprimer un préréglage"""
        presets = self.load_presets()
        
        if preset_name in presets:
            del presets[preset_name]
            return self.save_presets(presets)
        
        return False
    
    def export_config(self, config: Dict[str, Any], filename: str) -> bool:
        """Exporter une configuration vers un fichier"""
        try:
            export_path = self.config_dir / filename
            
            export_data = {
                "tradingagents_config": config,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return False
    
    def import_config(self, filename: str) -> Optional[Dict[str, Any]]:
        """Importer une configuration depuis un fichier"""
        try:
            import_path = self.config_dir / filename
            
            if not import_path.exists():
                return None
            
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire la configuration
            if "tradingagents_config" in data:
                config = data["tradingagents_config"]
            else:
                config = data
            
            return self.validate_config(config)
        except Exception as e:
            print(f"Erreur lors de l'import: {e}")
            return None
    
    def get_available_models(self, provider: str) -> List[str]:
        """Récupérer la liste des modèles disponibles pour un fournisseur"""
        models = {
            "openai": [
                "gpt-4o-mini",
                "gpt-4o",
                "o1-preview",
                "o1-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            "anthropic": [
                "claude-3-haiku-20240307",
                "claude-3-sonnet-20240229",
                "claude-3-opus-20240229",
                "claude-3-5-sonnet-20241022"
            ],
            "google": [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash"
            ],
            "groq": [
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "llama3-8b-8192",
                "llama3-70b-8192"
            ]
        }
        
        return models.get(provider, [])
    
    def get_current_config(self) -> Dict[str, Any]:
        """Récupérer la configuration actuelle"""
        return self.load_config()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Mettre à jour la configuration actuelle"""
        current_config = self.load_config()
        current_config.update(updates)
        return self.save_config(current_config)
    
    def reset_to_default(self) -> bool:
        """Réinitialiser la configuration aux valeurs par défaut"""
        return self.save_config(self.default_config)
