"""
Configuração centralizada do projeto ArcanimesDaF.
Valida todas as variáveis de ambiente necessárias.
"""

import os
from typing import List
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Chaves obrigatórias
REQUIRED_KEYS: List[str] = [
    "OPENAI_API_KEY",
    "YOUTUBE_CLIENT_ID",
    "YOUTUBE_CLIENT_SECRET",
]

# Validação
def validate_config() -> None:
    """Valida se todas as chaves obrigatórias estão configuradas."""
    missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    
    if missing:
        raise RuntimeError(
            f"❌ As seguintes chaves não foram configuradas: {', '.join(missing)}\n"
            f"📋 Crie um arquivo .env baseado em .env.example e preencha os valores."
        )
    
    print("✅ Configuração validada com sucesso!")


# Configurações da aplicação
class Config:
    """Classe com as configurações do projeto."""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
    
    # Configurações adicionais
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# Valida ao importar este módulo
if __name__ != "__main__":
    validate_config()
