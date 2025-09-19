#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI configuration.
"""

import os
import asyncio
from core.llm import _get_openai_client, call_llm

def test_azure_config():
    """Test Azure OpenAI configuration."""
    print("🔧 Testing Azure OpenAI Configuration")
    print("=" * 40)
    
    # Check environment variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "OPENAI_API_KEY", 
        "AZURE_OPENAI_DEPLOYMENT"
    ]
    
    print("Environment Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if "API_KEY" in var:
                print(f"  ✅ {var}: {value[:10]}...")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    print()
    
    # Test client creation
    print("Testing OpenAI Client Creation:")
    try:
        client = _get_openai_client()
        if client:
            print("  ✅ Azure OpenAI client created successfully!")
            print(f"  📍 Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
            print(f"  🚀 Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
            print(f"  📅 API Version: {os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')}")
        else:
            print("  ❌ Failed to create Azure OpenAI client")
            return False
    except Exception as e:
        print(f"  ❌ Error creating client: {e}")
        return False
    
    print()
    return True

async def test_llm_call():
    """Test a simple LLM call."""
    print("🧪 Testing LLM Call:")
    try:
        prompt = {
            "system": "You are a helpful assistant. Respond with valid JSON only.",
            "user": "Return a simple JSON object with a 'status' field set to 'success' and a 'message' field."
        }
        
        result = await call_llm(prompt)
        print("  ✅ LLM call successful!")
        print(f"  📄 Response: {result}")
        return True
        
    except Exception as e:
        print(f"  ❌ LLM call failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Azure OpenAI Setup Test")
    print("=" * 30)
    print()
    
    # Test configuration
    config_ok = test_azure_config()
    if not config_ok:
        print("\n❌ Configuration test failed. Please check your Azure OpenAI setup.")
        return
    
    print()
    
    # Test LLM call
    llm_ok = await test_llm_call()
    
    print()
    if config_ok and llm_ok:
        print("🎉 All tests passed! Azure OpenAI is ready to use.")
        print("\n🚀 To start the server:")
        print("source .venv/bin/activate && uvicorn app:app --reload --port 8080")
    else:
        print("❌ Some tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main())




