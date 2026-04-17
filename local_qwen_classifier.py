# local_qwen_classifier.py
import requests
import json
import pandas as pd
from typing import List, Dict

class QwenLocalClassifier:
    """
    Classificador de Discurso de Ódio utilizando Qwen 2.5 Coder 7B via Ollama.
    Focado em análise contextual e linguística forense local.
    """
    def __init__(self, model="qwen2.5-coder:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.url = f"{host}/api/generate"
        
    def classify_comment(self, text: str) -> Dict:
        """
        Envia um comentário para o Qwen Local e retorna a análise em JSON.
        """
        system_prompt = """
        Você é um Perito em Linguística Forense Digital especializado em detectar Discurso de Ódio em política brasileira.
        Sua tarefa é analisar comentários do Instagram e classificá-los com base em categorias periciais.
        
        CATEGORIAS:
        1. RACISMO (Ataques à raça, cor, etnia ou origem).
        2. HOMOFOBIA/TRANSFOBIA (Ataques à orientação sexual ou identidade de gênero).
        3. MISOGINIA (Ódio ou depreciação de mulheres).
        4. XENOFOBIA (Ataques a nordestinos, nortistas ou estrangeiros).
        5. ÓDIO POLÍTICO (Ameças de morte, agressão física ou desumanização por ideologia).
        6. NEUTRO (Comentários sem discurso de ódio).

        DIRETRIZES:
        - Seja rigoroso. Ironia e sarcasmo agressivo devem ser detectados.
        - Se não houver ódio, classifique como NEUTRO.
        
        Responda APENAS com um objeto JSON válido no formato:
        {
            "is_hate": true/false,
            "category": "NOME_DA_CATEGORIA",
            "score": 0.0-1.0 (nível de agressividade),
            "confidence": 0.0-1.0,
            "justification": "Explicação técnica curta",
            "severity": 1-10
        }
        """
        
        full_prompt = f"{system_prompt}\n\nComentário para análise: \"{text}\"\n\nJSON:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=5)
            response.raise_for_status()
            result_text = response.json().get("response", "{}")
            return json.loads(result_text)
        except requests.exceptions.ConnectionError:
            return {
                "is_hate": False,
                "category": "AGENTE_OFFLINE",
                "score": 0.0,
                "confidence": 0.0,
                "justification": "O motor de IA Local (Ollama) não foi detectado. Se você está usando a versão web, certifique-se de que o Agente Desktop está rodando localmente.",
                "severity": 0
            }
        except Exception as e:
            return {
                "is_hate": False,
                "category": "ERRO_IA",
                "score": 0.0,
                "confidence": 0.0,
                "justification": f"Falha na análise contextual: {str(e)}",
                "severity": 0
            }

    def classify_batch(self, texts: List[str]) -> pd.DataFrame:
        """
        Processa uma lista de textos em lote.
        """
        print(f"🚀 Iniciando classificação local com {self.model}...")
        results = []
        for i, text in enumerate(texts):
            analysis = self.classify_comment(text)
            analysis['original_text'] = text
            results.append(analysis)
            
            if (i + 1) % 10 == 0:
                print(f"✅ Processados {i + 1}/{len(texts)} comentários localmente...")
                
        return pd.DataFrame(results)

if __name__ == "__main__":
    # Teste rápido
    classifier = QwenLocalClassifier()
    test_text = "Esse candidato e seus seguidores nordestinos deveriam voltar para a seca."
    print(json.dumps(classifier.classify_comment(test_text), indent=2, ensure_ascii=False))
