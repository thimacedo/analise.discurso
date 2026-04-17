# local_qwen_classifier.py
import requests
import json
import os
import pandas as pd
from typing import List, Dict

class QwenLocalClassifier:
    """
    Classificador de Discurso de Ódio híbrido:
    1. Tenta o Ollama local (qwen2.5-coder:7b) para máxima privacidade e custo zero.
    2. Se falhar ou estiver no Vercel, usa a API Gratuita do Hugging Face (Qwen 2.5 Coder Online).
    """
    def __init__(self, model="qwen2.5-coder:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.local_url = f"{host}/api/generate"
        # Endpoint gratuito do Hugging Face (requer token gratuito no .env ou funciona limitado sem)
        self.hf_model = "Qwen/Qwen2.5-Coder-7B-Instruct"
        self.hf_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")

    def _get_system_prompt(self):
        return """
        Você é um Perito em Linguística Forense Digital especializado em detectar Discurso de Ódio em política brasileira.
        Classifique o comentário com base em: RACISMO, HOMOFOBIA/TRANSFOBIA, MISOGINIA, XENOFOBIA, ÓDIO POLÍTICO ou NEUTRO.
        
        Responda APENAS JSON:
        {
            "is_hate": true/false,
            "category": "NOME_DA_CATEGORIA",
            "score": 0.0-1.0,
            "confidence": 0.0-1.0,
            "justification": "Explicação técnica curta",
            "severity": 1-10
        }
        """

    def classify_online(self, text: str) -> Dict:
        """Fallback para a versão gratuita online do Qwen via Hugging Face."""
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        prompt = f"<|im_start|>system\n{self._get_system_prompt()}<|im_end|>\n<|im_start|>user\nAnalise: \"{text}\"<|im_end|>\n<|im_start|>assistant\n"
        
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200, "return_full_text": False}
        }
        
        try:
            response = requests.post(self.hf_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            # O HF retorna uma lista com o texto gerado
            result = response.json()
            generated_text = result[0]['generated_text'] if isinstance(result, list) else str(result)
            
            # Limpeza básica do JSON retornado
            json_match = generated_text[generated_text.find("{"):generated_text.rfind("}")+1]
            data = json.loads(json_match)
            data["provider"] = "Qwen Online (Free)"
            return data
        except Exception as e:
            return {
                "is_hate": False,
                "category": "IA_INDISPONIVEL",
                "score": 0.0,
                "confidence": 0.0,
                "justification": f"Limite de cota da IA Online atingido ou falha: {str(e)}",
                "severity": 0,
                "provider": "ERROR"
            }

    def classify_comment(self, text: str) -> Dict:
        """Tenta local primeiro, se falhar ou estiver no Vercel, vai para online."""
        is_vercel = os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
        
        # Se NÃO estiver no Vercel, tenta o Ollama Local
        if not is_vercel:
            payload = {
                "model": self.model,
                "prompt": f"{self._get_system_prompt()}\n\nAnalise: \"{text}\"\n\nJSON:",
                "stream": False,
                "format": "json"
            }
            try:
                response = requests.post(self.local_url, json=payload, timeout=5)
                response.raise_for_status()
                result_text = response.json().get("response", "{}")
                data = json.loads(result_text)
                data["provider"] = "Qwen Local (Ollama)"
                return data
            except requests.exceptions.ConnectionError:
                # Local offline, tenta o online
                pass
            except Exception:
                pass
        
        # Se chegou aqui, usa a versão gratuita online
        return self.classify_online(text)

    def classify_batch(self, texts: List[str]) -> pd.DataFrame:
        print(f"🚀 Iniciando classificação híbrida (Local/Online)...")
        results = []
        for i, text in enumerate(texts):
            analysis = self.classify_comment(text)
            analysis['original_text'] = text
            results.append(analysis)
            if (i + 1) % 10 == 0:
                print(f"✅ Processados {i + 1}/{len(texts)}...")
        return pd.DataFrame(results)

if __name__ == "__main__":
    classifier = QwenLocalClassifier()
    test_text = "Esse comentário é apenas um teste neutro."
    print(json.dumps(classifier.classify_comment(test_text), indent=2, ensure_ascii=False))
