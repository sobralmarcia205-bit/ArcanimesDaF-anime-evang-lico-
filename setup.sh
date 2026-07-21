#!/bin/bash

# Script de configuração e ativação AUTOMÁTICA

echo "🎬 ARCANIMES DAF - ATIVAÇÃO AUTOMÁTICA TOTAL"
echo ""

# 1. Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# 2. Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 3. Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
fi

# 4. Executar automação total
echo ""
echo "🚀 Ativando TODAS as automações do YouTube..."
echo ""

python automacao_total.py

echo ""
echo "✅ SETUP COMPLETO!"
echo "🎬 ARCANIMES DAF está 100% automático!"
