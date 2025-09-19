#!/bin/bash

echo "🚀 Starting Previewer Analyzer Bot Server"
echo "========================================"

# Kill any existing uvicorn processes
pkill -f uvicorn 2>/dev/null || true

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Load environment variables
echo "🔧 Loading environment variables..."
source ~/.zshrc

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Test imports
echo "🧪 Testing imports..."
python -c "import rapidfuzz; print('✅ rapidfuzz imported successfully')"
python -c "import app; print('✅ app imported successfully')"

# Start server
echo "🌐 Starting server on http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""

.venv/bin/uvicorn app:app --port 8080 --host 127.0.0.1


