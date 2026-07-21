#!/bin/bash

# Script de configuração inicial do projeto

echo "🎬 Configurando ArcanimesDaF..."
echo ""

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
else
    echo "✅ Ambiente virtual já existe"
    source venv/bin/activate
fi

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  Abra o arquivo .env e preencha suas chaves!"
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Abra o arquivo .env e adicione suas chaves:"
echo "   - OPENAI_API_KEY"
echo "   - YOUTUBE_CLIENT_ID"
echo "   - YOUTUBE_CLIENT_SECRET"
echo ""
echo "2. Execute o projeto:"
echo "   python main.py"
echo ""
