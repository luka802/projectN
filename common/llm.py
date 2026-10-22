"""Small OpenRouter client shared by both assignments."""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / '.env')
os.environ.setdefault('HF_HOME', str(PROJECT_ROOT / '.model-cache'))


class ServiceError(RuntimeError):
    """A safe, user-facing configuration or upstream service error."""


def chat(messages, *, temperature=0.5, max_tokens=500):
    key = os.getenv('OPENROUTER_API_KEY', '').strip()
    if not key:
        raise ServiceError('Set OPENROUTER_API_KEY in the project root .env file first.')
    primary = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3-8b-instruct')
    fallback = os.getenv('OPENROUTER_FALLBACK_MODEL', 'openrouter/free')
    models = list(dict.fromkeys([primary, fallback]))
    for position, model in enumerate(models):
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={'Authorization': f'Bearer {key}'},
                json={'model': model, 'messages': messages,
                      'temperature': temperature, 'max_tokens': max_tokens},
                timeout=(10, 60),
            )
        except requests.RequestException as exc:
            raise ServiceError('Cannot reach OpenRouter. Check your connection and try again.') from exc
        if response.status_code in (400, 402, 404, 429, 500, 502, 503, 504) and position < len(models) - 1:
            continue
        if not response.ok:
            raise ServiceError(f'OpenRouter returned HTTP {response.status_code}. Check your API key, model, and account limits.')
        try:
            content = response.json()['choices'][0]['message']['content']
            if not isinstance(content, str) or not content.strip():
                raise ValueError('empty response')
            return content.strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ServiceError('OpenRouter returned an empty or unexpected response. Please retry.') from exc
    raise ServiceError('No configured OpenRouter model is available.')
