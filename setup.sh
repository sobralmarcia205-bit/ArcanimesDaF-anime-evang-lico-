#!/bin/bash

# Script de ATIVAÇÃO AUTOMÁTICA TOTAL
# Executa TUDO sem necessidade de intervenção

echo ""
echo "🎬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━🎬"
echo "     ARCANIMES DAF - ATIVAÇÃO AUTOMÁTICA TOTAL"
echo "🎬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━🎬"
echo ""

# 1. Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 ETAPA 1: Criando ambiente virtual..."
    python3 -m venv venv
    echo "   ✅ Ambiente virtual criado"
else
    echo "📦 ETAPA 1: Ambiente virtual já existe"
    echo "   ✅ Pulando..."
fi

echo ""

# 2. Ativar ambiente virtual
echo "🔌 ETAPA 2: Ativando ambiente virtual..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
echo "   ✅ Ambiente virtual ativado"

echo ""

# 3. Instalar dependências
echo "📥 ETAPA 3: Instalando dependências..."
pip install --upgrade pip -q 2>/dev/null
pip install -r requirements.txt -q 2>/dev/null
echo "   ✅ Todas as dependências instaladas"

echo ""

# 4. Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 ETAPA 4: Criando arquivo .env..."
    cp .env.example .env
    echo "   ✅ Arquivo .env criado"
else
    echo "📝 ETAPA 4: Arquivo .env já existe"
    echo "   ✅ Pulando..."
fi

echo ""

# 5. Validar configuração
echo "🔍 ETAPA 5: Validando configuração..."
python main.py
CONFIG_STATUS=$?

echo ""

# 6. Executar automação total
if [ $CONFIG_STATUS -eq 0 ]; then
    echo "🚀 ETAPA 6: Ativando automação total do YouTube..."
    echo ""
    python automacao_total.py
    AUTOMATION_STATUS=$?
    echo ""
    
    if [ $AUTOMATION_STATUS -eq 0 ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ ATIVAÇÃO COMPLETA COM SUCESSO!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "🎬 ARCANIMES DAF está 100% automático!"
        echo "💰 Monetização YouTube: ATIVADA"
        echo "📺 Canal: PRONTO PARA FUNCIONAR"
        echo "🤖 Sistema: 100% AUTOMÁTICO 24/7"
        echo ""
        echo "✨ Você não precisa fazer mais nada!"
        echo ""
    else
        echo "❌ Erro durante automação"
        exit 1
    fi
else
    echo "❌ Erro na validação de configuração"
    echo "📋 Verifique o arquivo .env e tente novamente"
    exit 1
fi
