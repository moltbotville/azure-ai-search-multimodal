#!/bin/bash
# Quick start script for Streamlit GUI

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your Azure credentials before running."
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Check dependencies
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Launch Streamlit
echo "🚀 Launching Azure AI Search GUI..."
echo "📍 Open browser to: http://localhost:8501"
streamlit run app.py
