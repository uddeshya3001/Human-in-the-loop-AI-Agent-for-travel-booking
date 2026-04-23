"""
LLM interaction utilities.
"""

import json
import os
from openai import OpenAI
from config.settings import LLM_MODEL, LLM_TEMPERATURE


# Initialize client as None - will be set when needed
_client = None


def get_client():
    """
    Get or create OpenAI client (lazy initialization).
    
    Returns:
        OpenAI client instance
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _client = OpenAI(api_key=api_key)
    return _client


def call_llm(prompt: str, model: str = LLM_MODEL, temperature: float = LLM_TEMPERATURE) -> str:
    """
    Call the LLM with a prompt and return the response.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name (default from settings)
        temperature: Temperature parameter (default from settings)
    
    Returns:
        Response text from the LLM
    
    Raises:
        Exception: If API call fails
    """
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"LLM API Error: {e}")


def parse_json_response(text: str) -> dict:
    """
    Parse JSON from LLM response, handling markdown code blocks.
    
    Args:
        text: Raw text response from LLM
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        json.JSONDecodeError: If parsing fails
    """
    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("```")
        if len(lines) >= 2:
            text = lines[1].replace("json", "").strip()
    
    return json.loads(text)