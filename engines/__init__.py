import json, subprocess

class OllamaEngine:
    def __init__(self, model="qwen2.5:0.5b"):
        self.model = model
        self.url = "http://localhost:11434"
    
    def chat(self, messages, temperature=0.7):
        try:
            payload = json.dumps({"model": self.model, "messages": messages, "stream": False, "options": {"temperature": temperature}})
            result = subprocess.run(
                ["curl", "-s", f"{self.url}/api/chat", "-d", payload, "--max-time", "120"],
                capture_output=True, text=True, timeout=130
            )
            if result.stdout:
                data = json.loads(result.stdout)
                return data.get("message", {}).get("content", "")
            return "[Ollama: no response]"
        except Exception as e:
            return f"[Ollama error: {e}]"
    
    def generate(self, prompt, system="", temperature=0.7):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, temperature)
    
    def is_alive(self):
        try:
            r = subprocess.run(["curl", "-s", f"{self.url}/api/tags", "--max-time", "3"], capture_output=True, text=True, timeout=5)
            return r.returncode == 0 and "models" in r.stdout
        except:
            return False
