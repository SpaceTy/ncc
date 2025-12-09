import requests
import config

def call_openrouter(messages, max_tokens=150, temperature=1.0):
    """
    Helper to call OpenRouter API.
    Returns the content string or raises Exception.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
    }
    data = {
        "model": config.LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "reasoning": {
            "enabled": False
        }
    }

    try:
        response = requests.post(
            config.OPENROUTER_API_URL, headers=headers, json=data, timeout=30
        )
        response.raise_for_status()
        response_json = response.json()

        if "error" in response_json and response_json["error"]:
            raise Exception(f"API Error: {response_json['error'].get('message', 'Unknown error')}")

        content = (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        return content

    except Exception as e:
        print(f"❌ LLM API error: {e}")
        return None

