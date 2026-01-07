#!/bin/bash

# Script para iniciar el servidor OneLink

echo "🚀 Starting OneLink API Server..."
echo ""

# Verificar que el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python -m venv venv"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar que las dependencias están instaladas
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not installed!"
    echo "   Installing requirements..."
    pip install -r requirements.txt
fi

# Iniciar servidor
echo "✅ Starting server at http://localhost:8000"
echo "📚 API Docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
