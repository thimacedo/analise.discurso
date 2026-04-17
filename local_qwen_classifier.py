# local_qwen_classifier.py
import requests
import json
import os
import re
import pandas as pd
from typing import List, Dict

class QwenLocalClassifier:
    """
    Classificador de Discurso de Ódio híbrido e resiliente:
    1. Local: Ollama (qwen2.5-coder:7b)
    2. Online: Múltiplos fallbacks na camada gratuita do Hugging Face.
    """
    def __init__(self, model="qwen2.5-coder:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.local_url = f"{host}/api/generate"
        
        # Lista de modelos por ordem de disponibilidade na API Gratuita do HF
        self.online_models = [
            "Qwen/Qwen2.5-1.5B-Instruct",     # Muito estável (pequeno)
            "Qwen/Qwen2.5-7B-Instruct",       # Médio
            "mistralai/Mistral-7B-v0.3",      # Backup de alta disponibilidade
            "meta-llama/Llama-3.2-1B-Instruct" # Backup final ultra-leve
        ]
        # Tenta pegar o token das variáveis de ambiente do Vercel/Local
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")

    def _get_system_prompt(self):
        return """
        Você é um Perito Forense Digital. Classifique este comentário em JSON:
        CATEGORIAS: RACISMO, HOMOFOBIA, MISOGINIA, XENOFOBIA, ODIO_POLITICO ou NEUTRO.
        
        RETORNE APENAS JSON:
        {
            "is_hate": true/false,
            "category": "NOME",
            "score": 0.0-1.0,
            "confidence": 0.0-1.0,
            "justification": "Explicação curta",
            "severity": 1-10
        }
        """

    def classify_online(self, text: str) -> Dict:
        """Tenta modelos na nuvem com tratamento de erro aprimorado."""
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
            
        last_error = ""
        token_info = " (DICA: Adicione HUGGINGFACE_TOKEN no Vercel para maior estabilidade)" if not self.hf_token else ""

        for model_id in self.online_models:
            url = f"https://api-inference.huggingface.co/models/{model_id}"
            # Prompt otimizado para modelos menores
            prompt = f"System: {self._get_system_prompt()}\nUser: Analise: \"{text}\"\nAssistant: {{"
            
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 150, "return_full_text": False}
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=8)
                
                if response.status_code == 200:
                    result = response.json()
                    gen_text = ""
                    if isinstance(result, list): gen_text = result[0].get('generated_text', '')
                    elif isinstance(result, dict): gen_text = result.get('generated_text', '')
                    
                    # Garante que o JSON comece com { para o parser
                    if not gen_text.startswith("{"): gen_text = "{" + gen_text
                    
                    match = re.search(r'\{.*\}', gen_text, re.DOTALL)
                    if match:
                        data = json.loads(match.group())
                        data["provider"] = f"Cloud ({model_id})"
                        return data
                
                last_error = f"Status {response.status_code} em {model_id}"
            except Exception as e:
                last_error = str(e)
                continue

        return {
            "is_hate": False,
            "category": "IA_OFFLINE",
            "score": 0.0,
            "confidence": 0.0,
            "justification": f"A nuvem gratuita está instável agora. {last_error}{token_info}",
            "severity": 0,
            "provider": "ERROR"
        }

    def classify_comment(self, text: str) -> Dict:
        is_vercel = os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
        
        # Local (Apenas se não for Vercel)
        if not is_vercel:
            try:
                payload = {
                    "model": self.model,
                    "prompt": f"{self._get_system_prompt()}\n\nAnalise: \"{text}\"\n\nJSON:",
                    "stream": False, "format": "json"
                }
                response = requests.post(self.local_url, json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    res = json.loads(data.get("response", "{}"))
                    res["provider"] = "Qwen Local (Ollama)"
                    return res
            except: pass
        
        # Fallback Online
        return self.classify_online(text)

    def classify_batch(self, texts: List[str]) -> pd.DataFrame:
        results = [self.classify_comment(t) for t in texts]
        return pd.DataFrame(results)

if __name__ == "__main__":
    c = QwenLocalClassifier()
    print(c.classify_comment("Teste"))
