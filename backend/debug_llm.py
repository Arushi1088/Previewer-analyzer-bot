#!/usr/bin/env python3
"""
Debug script to test LLM calls in the same context as FastAPI app.
"""

import os
import asyncio
from core.llm import _get_openai_client, call_llm

async def debug_llm():
    """Debug LLM configuration and calls."""
    print("🔧 Debugging LLM Configuration")
    print("=" * 40)
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', '')[:10]}...")
    print(f"  AZURE_OPENAI_DEPLOYMENT: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
    print(f"  AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    print()
    
    # Test client creation
    print("Testing Client Creation:")
    try:
        client = _get_openai_client()
        if client:
            print(f"  ✅ Client created successfully")
            print(f"  📍 Base URL: {client.base_url}")
        else:
            print("  ❌ Failed to create client")
            return
    except Exception as e:
        print(f"  ❌ Error creating client: {e}")
        return
    
    # Test direct API call
    print("\nTesting Direct API Call:")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello! Respond with 'Direct call working!'"}],
            max_tokens=20
        )
        print("  ✅ Direct call successful!")
        print(f"  📄 Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"  ❌ Direct call failed: {e}")
        return
    
    # Test call_llm function
    print("\nTesting call_llm Function:")
    try:
        prompt = {
            "system": "You are a helpful assistant. Respond with valid JSON only.",
            "user": "Return a simple JSON object with a 'status' field set to 'success'."
        }
        
        result = await call_llm(prompt)
        print("  ✅ call_llm successful!")
        print(f"  📄 Response: {result}")
    except Exception as e:
        print(f"  ❌ call_llm failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_llm())
