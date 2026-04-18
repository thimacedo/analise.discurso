import pandas as pd
import re
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class HateSpeechClassifier:
    def __init__(self):
        # Banco de termos - palavras-chave para diferentes categorias
        self.hate_terms = {
            'racismo': {
                'termos': [
                    'macaco', 'preto', 'preta', 'crioulo', 'selvagem', 'mucura',
                    'negro', 'raça', 'inferior', 'escravo', 'senzala', 'quilombo',
                    'nega', 'neguinho', 'africano', 'tribo', 'primitivo', 'animal'
                ],
                'severidade': 8
            },
            'homofobia': {
                'termos': [
                    'viado', 'bicha', 'gay', 'lésbica', 'sapatão', 'bixa',
                    'veado', 'maricon', 'feminino', 'afeminado', 'baitola',
                    'boiola', 'queima rosca', 'lampiao', 'terceiro sexo'
                ],
                'severidade': 7
            },
            'transfobia': {
                'termos': [
                    'traveco', 'travesti', 'transexual', 'transformado',
                    'homem de saia', 'mulher de pênis', 'aberração', 'mutante',
                    'deformado', 'anormal', 'doente', 'falsa mulher'
                ],
                'severidade': 9
            },
            'misoginia': {
                'termos': [
                    'puta', 'vadia', 'cadela', 'vagabunda', 'prostituta',
                    'piranha', 'safada', 'mulher', 'feminista', 'lugar de mulher',
                    'cozinha', 'lavar louça', 'sexo frágil'
                ],
                'severidade': 6
            },
            'xenofobia': {
                'termos': [
                    'nordestino', 'baiano', 'paraíba', 'cearense', 'norte',
                    'sertanejo', 'migrante', 'refugiado', 'estrangeiro',
                    'forasteiro', 'invasor', 'sem terra', 'favelado'
                ],
                'severidade': 7
            }
        }
        
        # Inicializar cliente Claude (ou usar OpenAI)
        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic = Anthropic(api_key=api_key) if api_key else None
    
    def keyword_matching(self, text):
        """Detecção baseada em palavras-chave"""
        text_lower = text.lower()
        matches = []
        
        for category, data in self.hate_terms.items():
            for term in data['termos']:
                if term in text_lower:
                    matches.append({
                        'category': category,
                        'term': term,
                        'severity': data['severidade']
                    })
        
        return matches
    
    def classify_with_claude(self, text):
        """Classificação contextual usando Claude IA"""
        if not self.anthropic:
            return {
                "is_hate_speech": False,
                "category": None,
                "confidence": 0.0,
                "severity": 0,
                "justification": "API Key não configurada"
            }
            
        prompt = f"""
        Analise o seguinte comentário político e classifique-o como discurso de ódio ou não.
        
        Categorias de discurso de ódio:
        - racismo
        - homofobia  
        - transfobia
        - misoginia
        - xenofobia
        
        Comentário: "{text}"
        
        Responda APENAS em formato JSON:
        {{
            "is_hate_speech": true/false,
            "category": "categoria ou null",
            "confidence": 0.0-1.0,
            "severity": 1-10,
            "justification": "breve justificativa"
        }}
        """
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            import json
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            print(f"Erro na classificação: {e}")
            return {
                "is_hate_speech": False,
                "category": None,
                "confidence": 0.0,
                "severity": 0,
                "justification": "Erro na classificação"
            }
    
    def classify_batch(self, texts):
        """Classificação em lote para grande volume de dados"""
        results = []
        for i, text in enumerate(texts):
            keyword_matches = self.keyword_matching(text)
            claude_result = self.classify_with_claude(text)
            
            # Combinar resultados
            final_classification = {
                'text': text,
                'keyword_matches': keyword_matches,
                'claude_classification': claude_result,
                'is_hate_speech': claude_result['is_hate_speech'] or len(keyword_matches) > 0,
                'primary_category': claude_result['category'] if claude_result['category'] else (
                    keyword_matches[0]['category'] if keyword_matches else None
                ),
                'severity': max(claude_result['severity'], 
                               max([m['severity'] for m in keyword_matches]) if keyword_matches else 0)
            }
            results.append(final_classification)
            
            if i % 50 == 0:
                print(f"Processados {i} comentários...")
        
        return pd.DataFrame(results)