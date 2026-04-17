# local_qwen_classifier.py
import requests
import json
import os
import re
import pandas as pd
from typing import List, Dict

class QwenLocalClassifier:
    """
    Classificador de Discurso de Ódio híbrido:
    1. Tenta o Ollama local (qwen2.5-coder:7b) para máxima privacidade e custo zero.
    2. Se falhar ou estiver no Vercel, tenta múltiplos modelos gratuitos no Hugging Face.
    """
    def __init__(self, model="qwen2.5-coder:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.local_url = f"{host}/api/generate"
        
        # Lista de modelos estáveis para fallback online (camada gratuita HF)
        self.online_models = [
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "google/gemma-2-9b-it",
            "microsoft/Phi-3-mini-4k-instruct"
        ]
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
        """Tenta múltiplos modelos na nuvem gratuita do Hugging Face para garantir resiliência."""
        headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        last_error = "Nenhum modelo online disponível"

        for model_id in self.online_models:
            url = f"https://api-inference.huggingface.co/models/{model_id}"
            # Formato de prompt chat-ml
            prompt = f"<|im_start|>system\n{self._get_system_prompt()}<|im_end|>\n<|im_start|>user\nAnalise este comentário: \"{text}\"<|im_end|>\n<|im_start|>assistant\n"
            
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 250, "return_full_text": False}
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=12)
                if response.status_code == 200:
                    result = response.json()
                    # Diferentes modelos no HF podem retornar estruturas variadas
                    generated_text = ""
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '')
                    elif isinstance(result, dict):
                        generated_text = result.get('generated_text', '')
                    
                    if generated_text:
                        # Extração robusta de JSON do texto gerado
                        match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                        if match:
                            data = json.loads(match.group())
                            data["provider"] = f"Cloud ({model_id})"
                            return data
                
                last_error = f"Modelo {model_id} retornou status {response.status_code}"
            except Exception as e:
                last_error = f"Erro em {model_id}: {str(e)}"
                continue

        return {
            "is_hate": False,
            "category": "IA_INDISPONIVEL",
            "score": 0.0,
            "confidence": 0.0,
            "justification": f"Todos os modelos online falharam ou estão em manutenção. {last_error}",
            "severity": 0,
            "provider": "ERROR"
        }

    def classify_comment(self, text: str) -> Dict:
        """Tenta local primeiro (Ollama), se falhar ou estiver no Vercel, vai para online."""
        is_vercel = os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
        
        if not is_vercel:
            # Local: tenta Ollama
            payload = {
                "model": self.model,
                "prompt": f"{self._get_system_prompt()}\n\nAnalise este comentário: \"{text}\"\n\nJSON:",
                "stream": False,
                "format": "json"
            }
            try:
                response = requests.post(self.local_url, json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    res_json = json.loads(data.get("response", "{}"))
                    res_json["provider"] = "Qwen Local (Ollama)"
                    return res_json
            except Exception:
                pass # Fallback para online se local falhar
        
        # Fallback Online Resiliente
        return self.classify_online(text)

    def classify_batch(self, texts: List[str]) -> pd.DataFrame:
        print(f"🚀 Iniciando classificação híbrida resiliente...")
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
    test_text = "Esse comentário é um teste de ódio simulado."
    print(json.dumps(classifier.classify_comment(test_text), indent=2, ensure_ascii=False))
