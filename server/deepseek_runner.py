import requests

def run_deepseek(prompt, model="deepseek-local"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()

        return data.get("response", "").strip()

    except Exception as e:
        return f"Error: {e}"
