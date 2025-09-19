#!/bin/bash

echo "🔧 Azure OpenAI Setup Script"
echo "=============================="
echo ""

# Check if Azure OpenAI is already configured
if [ ! -z "$AZURE_OPENAI_ENDPOINT" ] && [ ! -z "$AZURE_OPENAI_DEPLOYMENT" ] && [ ! -z "$OPENAI_API_KEY" ]; then
    echo "✅ Azure OpenAI is already configured!"
    echo "Endpoint: $AZURE_OPENAI_ENDPOINT"
    echo "Deployment: $AZURE_OPENAI_DEPLOYMENT"
    echo "API Key: ${OPENAI_API_KEY:0:10}..."
    echo ""
    echo "To restart the server with Azure OpenAI:"
    echo "source .venv/bin/activate && uvicorn app:app --reload --port 8080"
    exit 0
fi

echo "Please provide your Azure OpenAI details:"
echo ""

# Get Azure OpenAI details
read -p "Azure OpenAI Endpoint (e.g., https://your-resource.openai.azure.com/): " AZURE_ENDPOINT
read -p "Azure API Key: " AZURE_API_KEY
read -p "Deployment Name (e.g., gpt-4o-deployment): " AZURE_DEPLOYMENT
read -p "API Version [2024-02-15-preview]: " AZURE_API_VERSION

# Set defaults
AZURE_API_VERSION=${AZURE_API_VERSION:-2024-02-15-preview}

echo ""
echo "Setting environment variables..."

# Export variables for current session
export AZURE_OPENAI_ENDPOINT="$AZURE_ENDPOINT"
export OPENAI_API_KEY="$AZURE_API_KEY"
export AZURE_OPENAI_DEPLOYMENT="$AZURE_DEPLOYMENT"
export AZURE_OPENAI_API_VERSION="$AZURE_API_VERSION"

echo "✅ Environment variables set for current session"
echo ""
echo "To make these permanent, add to your ~/.zshrc or ~/.bashrc:"
echo "export AZURE_OPENAI_ENDPOINT=\"$AZURE_ENDPOINT\""
echo "export OPENAI_API_KEY=\"$AZURE_API_KEY\""
echo "export AZURE_OPENAI_DEPLOYMENT=\"$AZURE_DEPLOYMENT\""
echo "export AZURE_OPENAI_API_VERSION=\"$AZURE_API_VERSION\""
echo ""

# Test the configuration
echo "🧪 Testing Azure OpenAI configuration..."
source .venv/bin/activate
python -c "
import os
from core.llm import _get_openai_client

client = _get_openai_client()
if client:
    print('✅ Azure OpenAI client created successfully!')
    print(f'Endpoint: {os.getenv(\"AZURE_OPENAI_ENDPOINT\")}')
    print(f'Deployment: {os.getenv(\"AZURE_OPENAI_DEPLOYMENT\")}')
else:
    print('❌ Failed to create Azure OpenAI client')
    print('Please check your configuration')
"

echo ""
echo "🚀 To start the server with Azure OpenAI:"
echo "source .venv/bin/activate && uvicorn app:app --reload --port 8080"




