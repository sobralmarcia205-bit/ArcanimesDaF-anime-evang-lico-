"""
Arquivo principal do projeto ArcanimesDaF.
Importar config.py valida automaticamente todas as variáveis de ambiente.
"""

from config import Config, validate_config

def main():
    """Função principal da aplicação."""
    try:
        # Validação automática ao importar config
        print("🚀 Iniciando ArcanimesDaF...\n")
        
        # Acessar as configurações
        print(f"OpenAI API: {'✅ Configurada' if Config.OPENAI_API_KEY else '❌ Não configurada'}")
        print(f"YouTube Client ID: {'✅ Configurado' if Config.YOUTUBE_CLIENT_ID else '❌ Não configurado'}")
        print(f"YouTube Client Secret: {'✅ Configurado' if Config.YOUTUBE_CLIENT_SECRET else '❌ Não configurado'}")
        print(f"Debug Mode: {Config.DEBUG}")
        print(f"Log Level: {Config.LOG_LEVEL}\n")
        
        print("📺 Seu projeto está pronto para funcionar!")
        
    except RuntimeError as e:
        print(f"\n{e}\n")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
