#!/usr/bin/env python3
"""
Direct API test using requests library to bypass OpenAI client issues.
"""

import os
import requests
import json

def test_direct_api():
    """Test Azure OpenAI API directly using requests."""
    print("🧪 Testing Azure OpenAI API directly...")
    
    # Get environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    if not all([endpoint, api_key, deployment, api_version]):
        print("❌ Missing environment variables")
        return False
    
    # Construct the URL
    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    # Request body
    data = {
        "messages": [
            {"role": "user", "content": "Hello! Please respond with a simple JSON object containing a 'status' field set to 'success'."}
        ],
        "max_tokens": 100
    }
    
    print(f"📍 URL: {url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📄 Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_direct_api()

