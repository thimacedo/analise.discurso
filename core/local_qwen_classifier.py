# core/local_qwen_classifier.py
import requests
import json
import os
import pandas as pd
from typing import List, Dict

class QwenLocalClassifier:
    """
    Classificador Forense v5.5 (Inteligência Prioritária):
    Usa o modelo 1.5b por padrão para evitar falsos negativos críticos.
    """
    def __init__(self, model="qwen2.5-coder:1.5b", secondary_model="qwen2.5-coder:0.5b", host="http://localhost:11434"):
        self.model = model
        self.secondary_model = secondary_model
        self.host = host
        self.local_url = f"{host}/api/generate"
        self.VALID_CATEGORIES = ["RACISMO", "MISOGINIA", "XENOFOBIA", "HOMOFOBIA", "TRANSFOBIA", "ODIO_POLITICO", "INSULTO_DIRETO", "NEUTRO"]

    def _get_system_prompt(self):
        return f"""Você é um Perito Forense Digital. Classifique discursos de ódio.
        Categorias: {', '.join(self.VALID_CATEGORIES)}.
        
        CRITÉRIO: Xenofobia inclui ataques a grupos regionais (ex: nordestinos). 
        Se houver agressão, desejo de morte ou desumanização, is_hate=true.
        Responda em JSON: {{"is_hate":bool, "category":string, "score":float, "justification":string}}
        """

    def _try_local(self, text: str, model_name: str) -> Dict:
        try:
            payload = {"model": model_name, "prompt": f"{self._get_system_prompt()}\n\nTexto: '{text}'\n\nJSON:", "stream": False, "format": "json"}
            response = requests.post(self.local_url, json=payload, timeout=25)
            if response.status_code == 200:
                data = json.loads(response.json().get("response", "{}"))
                cat = str(data.get("category", "NEUTRO")).upper().replace(" ", "_")
                if cat not in self.VALID_CATEGORIES: cat = "NEUTRO"
                data["category"] = cat
                data["provider"] = f"Qwen Local ({model_name})"
                return data
        except: return None
        return None

    def classify_comment(self, text: str) -> Dict:
        # Prioridade para o 1.5b para maior rigor
        res = self._try_local(text, self.model)
        if res: return res
        
        # Secundário 0.5b se o 1.5b falhar
        return self._try_local(text, self.secondary_model) or {"is_hate": False, "category": "NEUTRO", "score": 0.0, "justification": "Erro"}

if __name__ == "__main__":
    c = QwenLocalClassifier()
    print(c.classify_comment("Nordestinos lixos devem morrer"))
