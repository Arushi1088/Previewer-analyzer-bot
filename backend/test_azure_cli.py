#!/usr/bin/env python3
"""
Simple CLI test for Azure OpenAI API key.
Usage: python test_azure_cli.py
"""

import os
import requests
import json

def main():
    print("🔧 Azure OpenAI API Key Test")
    print("=" * 40)
    
    # Check environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    if not all([endpoint, api_key, deployment, api_version]):
        print("❌ Environment variables not set!")
        print("Run: source ~/.zshrc")
        return False
    
    print(f"✅ Endpoint: {endpoint}")
    print(f"✅ Deployment: {deployment}")
    print(f"✅ API Version: {api_version}")
    print(f"✅ API Key: {api_key[:10]}...")
    print()
    
    # Test API call
    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    data = {
        "messages": [{"role": "user", "content": "Hello! Respond with 'Azure API working!'"}],
        "max_tokens": 20
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! Azure API key is working!")
            print(f"📄 Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    main()

