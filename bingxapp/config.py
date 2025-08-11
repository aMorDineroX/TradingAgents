"""
Configuration pour l'application BingX
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class BingXConfig:
    """Configuration pour l'API BingX"""
    
    # Clés API BingX
    api_key: str = "EJV71q7OSJVf8imsnXDIIf83p0ULisEF4DWTvPKZIcMsRBvxkfSI4Sq8RjfoGqCQKxbszBflM2baCHjm6b25w"
    secret_key: str = "Sm8OgsYz4m0zrTpbAkORRtLx7SV5zpCiC4iXbZ5gSkYU84e3wJ6qXnfnGaU8djXvHxgQMPY5eXTXaiujH3Xw"
    
    # URLs de l'API BingX
    base_url: str = "https://open-api.bingx.com"
    testnet_url: str = "https://open-api-vst.bingx.com"
    
    # Configuration par défaut
    use_testnet: bool = False
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'BingXConfig':
        """Créer la configuration à partir des variables d'environnement"""
        return cls(
            api_key=os.getenv('BINGX_API_KEY', cls.api_key),
            secret_key=os.getenv('BINGX_SECRET_KEY', cls.secret_key),
            use_testnet=os.getenv('BINGX_USE_TESTNET', 'false').lower() == 'true',
            timeout=int(os.getenv('BINGX_TIMEOUT', '30'))
        )
    
    @property
    def api_url(self) -> str:
        """Retourne l'URL de l'API selon l'environnement"""
        return self.testnet_url if self.use_testnet else self.base_url


# Configuration globale
config = BingXConfig.from_env()
