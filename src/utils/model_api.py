"""
Model API module for interacting with different LLM providers.
Supports both Ollama and OpenAI APIs.
"""
import os
from typing import Optional

try:
    import ollama
except ImportError:
    ollama = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def prompt_model(prompt: str, model: str, provider: str = "ollama", api_key: Optional[str] = None) -> str:
    """
    Send a prompt to a model using the specified provider.
    
    Args:
        prompt: The prompt text to send to the model
        model: The model name/identifier
        provider: The provider to use ("ollama" or "openai")
        api_key: Optional API key for OpenAI (if not set, will use OPENAI_API_KEY env var)
    
    Returns:
        The model's response text
    
    Raises:
        ValueError: If provider is not supported or required libraries are missing
        RuntimeError: If API call fails
    """
    provider = provider.lower()
    
    if provider == "ollama":
        return _prompt_ollama(prompt, model)
    elif provider == "openai":
        return _prompt_openai(prompt, model, api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers are 'ollama' and 'openai'")


def _prompt_ollama(prompt: str, model: str) -> str:
    """Internal function to call Ollama API."""
    if ollama is None:
        raise ImportError("ollama package is not installed. Install it with: pip install ollama")
    
    try:
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        raw_output = response['message']['content']
        return raw_output
    except Exception as e:
        raise RuntimeError(f"Ollama API call failed: {e}")


def _prompt_openai(prompt: str, model: str, api_key: Optional[str] = None) -> str:
    """Internal function to call OpenAI API."""
    if OpenAI is None:
        raise ImportError("openai package is not installed. Install it with: pip install openai")
    
    # Use provided API key or fall back to environment variable
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
        )
        raw_output = response.choices[0].message.content
        return raw_output
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")


# Backward compatibility alias
def prompt_ollama(prompt: str, model: str) -> str:
    """
    Backward compatibility function that calls prompt_model with provider="ollama".
    This maintains compatibility with existing code.
    """
    return prompt_model(prompt, model, provider="ollama")

