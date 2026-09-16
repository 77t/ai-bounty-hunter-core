import requests
import json

def ask_qwen(system_prompt, user_prompt, timeout=120):
    """Fungsi universal untuk panggil Qwen2.5 via Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen2.5:7b-instruct-q4_K_M",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "format": "json",
                "stream": False
            },
            timeout=timeout
        )
        return json.loads(response.json()['message']['content'])
    except Exception as e:
        return {"error": str(e)}
      
