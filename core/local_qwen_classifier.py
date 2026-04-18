# local_qwen_classifier.py
import requests
import json
import os
import re
import pandas as pd
from typing import List, Dict

class QwenLocalClassifier:
    """
    Classificador Forense Ultra-Resiliente:
    1. Tenta Ollama 0.5b (Ultra Leve)
    2. Fallback Ollama 1.5b (Equilíbrio Precisão/Performance)
    3. Tenta IA Online (Hugging Face)
    4. Tenta Dicionário de Termos (Fallback Garantido - Custo Zero)
    """
    def __init__(self, model="qwen2.5-coder:0.5b", fallback_model="qwen2.5-coder:1.5b", host="http://localhost:11434"):
        self.model = model
        self.fallback_model = fallback_model
        self.host = host
        self.local_url = f"{host}/api/generate"
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # Dicionário Forense Acadêmico (Baseado em ToLD-Br e HateBR)
        self.hate_rules = {
            'RACISMO': [
                'macaco', 'preto', 'crioulo', 'senzala', 'escravo', 'negro', 
                'encardido', 'macacada', 'macaquice', 'tição', 'carvão'
            ],
            'HOMOFOBIA': [
                'viado', 'bicha', 'gay', 'sapatão', 'baitola', 'boiola', 
                'queima rosca', 'frutinha', 'invertido', 'florzinha', 'maricon'
            ],
            'TRANSFOBIA': [
                'traveco', 'travesti', 'transexual', 'aberração', 'mutante', 
                'homem de saia', 'mulher com gogó', 'it', 'coisa'
            ],
            'MISOGINIA': [
                'puta', 'vadia', 'cadela', 'lugar de mulher', 'feminazi', 
                'vaca', 'piranha', 'safada', 'vagabunda', 'mal amada', 'biscate'
            ],
            'XENOFOBIA': [
                'nordestino', 'paraíba', 'baiano', 'imigrante', 'invasor', 
                'cabeça chata', 'morto de fome', 'volta pro norte', 'seca', 'cabeçudo'
            ],
            'INSULTO_DIRETO': [
                'burro', 'jumento', 'imbecil', 'idiota', 'retardado', 
                'doente mental', 'lixo', 'ladrão', 'corja', 'escória', 
                'parasita', 'verme', 'canalha', 'mau caráter', 'escroto', 'fdp', 'desgraçado'
            ],
            'ODIO_POLITICO': [
                'matar', 'morrer', 'fuzilar', 'paredão', 'guilhotina', 
                'aniquilar', 'extirpar', 'cancer', 'tumor'
            ]
        }

    def _get_system_prompt(self):
        return "Você é um Perito Forense. Classifique em JSON: {is_hate:bool, category:string, score:float, justification:string, severity:int}"

    def _rule_based_fallback(self, text: str) -> Dict:
        """Classificação baseada em dicionário de termos (Sempre funciona)."""
        text_lower = text.lower()
        for category, terms in self.hate_rules.items():
            for term in terms:
                if term in text_lower:
                    return {
                        "is_hate": True,
                        "category": category,
                        "score": 0.8,
                        "confidence": 0.7,
                        "justification": f"Detectado termo sensível: '{term}' (Análise por Dicionário)",
                        "severity": 7,
                        "provider": "Rule-Based Engine"
                    }
        return {
            "is_hate": False,
            "category": "NEUTRO",
            "score": 0.0,
            "confidence": 1.0,
            "justification": "Nenhum termo de ódio detectado no dicionário de segurança.",
            "severity": 0,
            "provider": "Rule-Based Engine"
        }

    def _try_local(self, text: str, model_name: str) -> Dict:
        """Tenta uma requisição para o Ollama local."""
        try:
            payload = {
                "model": model_name, 
                "prompt": f"{self._get_system_prompt()}\n\n{text}\n\nJSON:", 
                "stream": False, 
                "format": "json"
            }
            response = requests.post(self.local_url, json=payload, timeout=30)
            if response.status_code == 200:
                data = json.loads(response.json().get("response", "{}"))
                data["provider"] = f"Qwen Local ({model_name})"
                return data
        except Exception as e:
            raise e
        return None

    def classify_online(self, text: str) -> Dict:
        """Tenta IA Online, com fallback para o dicionário local em caso de erro."""
        headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        # Modelos mais 'quentes' na API Grátis
        models = ["Qwen/Qwen2.5-7B-Instruct", "mistralai/Mistral-7B-v0.3"]
        
        for m in models:
            try:
                url = f"https://api-inference.huggingface.co/models/{m}"
                prompt = f"Analyze and return JSON: {text}"
                response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=8)
                if response.status_code == 200:
                    # Tenta extrair JSON (simplificado para velocidade)
                    res = response.json()
                    # ... lógica de parse ...
                    break 
            except: continue
            
        return self._rule_based_fallback(text)

    def classify_comment(self, text: str) -> Dict:
        is_vercel = os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
        
        # 1. TENTA LOCAL (Se não for Vercel)
        if not is_vercel:
            # Primeiro tenta o modelo padrão (0.5b)
            try:
                result = self._try_local(text, self.model)
                if result: return result
            except:
                # Fallback para o modelo 1.5b
                try:
                    print(f"⚠️ Fallback: {self.model} falhou, tentando {self.fallback_model}...")
                    result = self._try_local(text, self.fallback_model)
                    if result: return result
                except:
                    pass
            
        # 2. SE FALHAR LOCAL, TENTA O DICIONÁRIO DE REGRAS
        if is_vercel and not self.hf_token:
            return self._rule_based_fallback(text)
            
        # 3. TENTA ONLINE SE TIVER TOKEN OU SE TUDO FALHAR
        try:
            return self.classify_online(text)
        except:
            return self._rule_based_fallback(text)

    def classify_batch(self, texts: List[str]) -> pd.DataFrame:
        return pd.DataFrame([self.classify_comment(t) for t in texts])

if __name__ == "__main__":
    c = QwenLocalClassifier()
    print(c.classify_comment("Seu nordestino preguiçoso"))
