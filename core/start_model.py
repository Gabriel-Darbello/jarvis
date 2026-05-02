import requests

def start_model():
    try:
        requests.post(
            'http://localhost:11434/api/generate',
            json={"model": "qwen2.5:3b",
            "prompt": "Olá tudo bem? tudo pronto para começar!"},
            timeout=10
        )
    except:
        pass
