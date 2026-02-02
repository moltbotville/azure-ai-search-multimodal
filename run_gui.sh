#!/bin/bash
# Quick start script for Streamlit GUI

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your Azure credentials before running."
    exit 1
fi

# Check dependencies
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip install --break-system-packages -r requirements.txt
fi

# Launch Streamlit
# Note: .env is automatically loaded by python-dotenv in app.py
echo "🚀 Launching Azure AI Search GUI..."
echo "📍 Open browser to: http://localhost:8501"
echo ""
streamlit run app.py
