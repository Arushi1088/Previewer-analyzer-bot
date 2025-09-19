#!/usr/bin/env python3
"""
List available Azure OpenAI deployments.
"""

import os
import requests

def list_azure_deployments():
    """List available deployments in Azure OpenAI."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not endpoint or not api_key:
        print("❌ Missing Azure OpenAI configuration")
        return
    
    # Clean endpoint URL
    if endpoint.endswith('/'):
        endpoint = endpoint[:-1]
    
    # List deployments endpoint
    url = f"{endpoint}/openai/deployments?api-version={api_version}"
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🔍 Checking deployments at: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            deployments = data.get('data', [])
            
            if deployments:
                print(f"✅ Found {len(deployments)} deployment(s):")
                for deployment in deployments:
                    name = deployment.get('id', 'Unknown')
                    model = deployment.get('model', 'Unknown')
                    status = deployment.get('status', 'Unknown')
                    print(f"  📦 {name} (Model: {model}, Status: {status})")
            else:
                print("❌ No deployments found")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error listing deployments: {e}")

if __name__ == "__main__":
    list_azure_deployments()




