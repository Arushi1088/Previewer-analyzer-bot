
import os, json
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

def _get_openai_client():
    """Initialize OpenAI client with support for both OpenAI and Azure OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    
    # Check if using Azure OpenAI
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    if azure_endpoint and azure_deployment:
        # Azure OpenAI configuration - use the base endpoint without the full path
        # The AsyncOpenAI client will add /chat/completions automatically
        endpoint = azure_endpoint.rstrip('/')
        base_url = f"{endpoint}/openai/deployments/{azure_deployment}"
        return AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={"api-key": api_key}
        )
    else:
        # Standard OpenAI configuration
        return AsyncOpenAI(api_key=api_key)

def _validate_json_response(response_text: str) -> dict:
    """Validate and parse JSON response from LLM."""
    try:
        parsed = json.loads(response_text)
        
        # Validate required keys
        required_keys = ["bugs", "steps", "assumptions", "metadata"]
        missing_keys = [key for key in required_keys if key not in parsed]
        
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        # Validate steps structure
        if not isinstance(parsed.get("steps"), list):
            raise ValueError("'steps' must be a list")
        
        for i, step in enumerate(parsed["steps"]):
            if not isinstance(step, dict):
                raise ValueError(f"Step {i} must be a dictionary")
            if "step_no" not in step or "summary" not in step or "frames" not in step:
                raise ValueError(f"Step {i} missing required fields: step_no, summary, frames")
        
        # Validate bugs structure
        if not isinstance(parsed.get("bugs"), list):
            raise ValueError("'bugs' must be a list")
        
        return parsed
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Response validation failed: {e}")

async def call_llm(prompt_dict: dict) -> dict:
    """
    Call LLM with system and user prompts, return validated JSON response.
    
    Args:
        prompt_dict: Dictionary with 'system' and 'user' keys containing prompt content
        
    Returns:
        Parsed and validated JSON response
        
    Raises:
        ValueError: If API key not configured or response validation fails
    """
    # Validate input
    if not isinstance(prompt_dict, dict):
        raise ValueError("prompt_dict must be a dictionary")
    
    if "system" not in prompt_dict or "user" not in prompt_dict:
        raise ValueError("prompt_dict must contain 'system' and 'user' keys")
    
    # Get OpenAI client
    client = _get_openai_client()
    if not client:
        # Return a stub so the pipeline runs end-to-end for dev
        logger.warning("No OpenAI API key configured, returning stub response")
        return {
            "bugs": [],
            "steps": [{"step_no": 1, "summary": "Stub: LLM not configured", "frames": [0]}],
            "assumptions": "No API key configured",
            "metadata": {"model_hint": "stub", "version": "v0"}
        }
    
    # Determine model
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    if os.getenv("AZURE_OPENAI_DEPLOYMENT"):
        # For Azure, use the deployment name as model
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling LLM (attempt {attempt + 1}/{max_retries})")
            
            # Make the API call
            # For Azure OpenAI, we need to add the API version as a query parameter
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            api_key = os.getenv("OPENAI_API_KEY")
            
            # Parse the user prompt to extract images and text content
            import json
            user_data = json.loads(prompt_dict["user"])
            
            # Build messages with images
            messages = [{"role": "system", "content": prompt_dict["system"]}]
            
            # Create user message content
            user_content = []
            
            # Add text content first
            text_content = {
                "type": "text",
                "text": f"Please analyze these mobile app screenshots for QA issues. Here's the scenario context:\n\nScenario: {user_data['scenario']['id']}\nSource apps: {', '.join(user_data['scenario']['source_apps'])}\nFile size: {user_data['scenario']['file_size_bucket']}\nProtection: {user_data['scenario']['protection_level']}\nFile type: {user_data['scenario']['file_type']}\n\nPlease examine each screenshot and identify any bugs, issues, or violations. Return your analysis in the specified JSON format."
            }
            user_content.append(text_content)
            
            # Add images from frames
            for frame in user_data.get("frames", []):
                if "image_base64" in frame:
                    image_content = {
                        "type": "image_url",
                        "image_url": {
                            "url": frame["image_base64"]
                        }
                    }
                    user_content.append(image_content)
            
            messages.append({"role": "user", "content": user_content})
            
            if azure_endpoint and azure_deployment:
                # Use the full URL with API version for Azure
                import httpx
                url = f"{azure_endpoint.rstrip('/')}/openai/deployments/{azure_deployment}/chat/completions?api-version={azure_api_version}"
                headers = {
                    "Content-Type": "application/json",
                    "api-key": api_key
                }
                data = {
                    "messages": messages,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
                
                async with httpx.AsyncClient(timeout=120.0) as http_client:
                    response = await http_client.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                    # Convert to OpenAI format
                    class MockResponse:
                        def __init__(self, data):
                            self.choices = [type('Choice', (), {
                                'message': type('Message', (), {
                                    'content': data['choices'][0]['message']['content']
                                })()
                            })()]
                    response = MockResponse(response_data)
            else:
                # Standard OpenAI call
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,  # Low temperature for consistent JSON output
                    response_format={"type": "json_object"}  # Force JSON response
                )
            
            response_text = response.choices[0].message.content
            
            # Validate and parse the response
            parsed_response = _validate_json_response(response_text)
            logger.info("LLM response validated successfully")
            return parsed_response
            
        except Exception as e:
            logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:
                # Last attempt failed, raise the error
                raise ValueError(f"LLM call failed after {max_retries} attempts: {e}")
            
            # For JSON validation errors, try to fix by asking the model
            if "Invalid JSON format" in str(e) or "Response validation failed" in str(e):
                logger.info("Attempting to fix JSON response")
                fix_prompt = f"""
The previous response had JSON validation errors: {e}

Please provide a corrected JSON response that follows this exact structure:
{{
    "bugs": [{{"bug_id": "string", "description": "string", "severity": "string", "step_no": number}}],
    "steps": [{{"step_no": number, "summary": "string", "frames": [number]}}],
    "assumptions": "string",
    "metadata": {{"model_hint": "string", "version": "string"}}
}}

Original response: {response_text}
"""
                prompt_dict["user"] = fix_prompt
            else:
                # For other errors, wait before retry
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
