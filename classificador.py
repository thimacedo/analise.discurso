import pandas as pd
import json
import os
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class ClassificadorOdio:
    def __init__(self):
        self.hate_terms = {
            'racismo': ['macaco', 'preto', 'crioulo', 'selvagem', 'negro', 'raça', 'inferior', 'escravo', 'senzala', 'quilombo', 'neguinho', 'africano', 'tribo', 'primitivo', 'animal'],
            'homofobia': ['viado', 'bicha', 'gay', 'lésbica', 'sapatão', 'bixa', 'veado', 'maricon', 'afeminado', 'baitola', 'boiola', 'queima rosca', 'lampiao'],
            'transfobia': ['traveco', 'travesti', 'transexual', 'transformado', 'homem de saia', 'mulher de pênis', 'aberração', 'mutante', 'deformado', 'anormal', 'doente', 'falsa mulher'],
            'misoginia': ['puta', 'vadia', 'cadela', 'vagabunda', 'prostituta', 'piranha', 'safada', 'feminista', 'lugar de mulher', 'cozinha', 'lavar louça', 'sexo frágil'],
            'xenofobia': ['nordestino', 'baiano', 'paraíba', 'cearense', 'norte', 'sertanejo', 'migrante', 'refugiado', 'estrangeiro', 'forasteiro', 'invasor', 'sem terra', 'favelado']
        }
        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic = Anthropic(api_key=api_key) if ANTHROPIC_AVAILABLE and api_key else None

    # CORREÇÃO #2: método _keyword_matches com acesso correto às listas
    def _keyword_matches(self, text):
        if not isinstance(text, str):
            return []
        text_lower = text.lower()
        matches = []
        for cat, termos in self.hate_terms.items():   # 'termos' é a lista
            for term in termos:
                if term in text_lower:
                    matches.append({'category': cat, 'term': term, 'severity': 7})
        return matches

    def _claude_classify(self, text):
        if not self.anthropic:
            return {'is_hate_speech': False, 'category': None, 'confidence': 0.0, 'severity': 0}
        prompt = f"""Analise o comentário e responda apenas JSON:
Comentário: "{text}"
JSON: {{"is_hate_speech": true/false, "category": "racismo|homofobia|transfobia|misoginia|xenofobia|null", "confidence": 0.0-1.0, "severity": 1-10}}"""
        try:
            resp = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(resp.content[0].text)
        except:
            return {'is_hate_speech': False, 'category': None, 'confidence': 0.0, 'severity': 0}

    # CORREÇÃO #6: usar .apply() para performance
    def classificar_dataframe(self, df, coluna_texto='texto_limpo'):
        print("🏷️ Classificando discurso de ódio...")
        def classificar_linha(texto):
            kw = self._keyword_matches(texto)
            claude = self._claude_classify(texto)
            is_hate = claude['is_hate_speech'] or len(kw) > 0
            cat = claude['category'] if claude['category'] else (kw[0]['category'] if kw else 'neutro')
            sev = max(claude['severity'], max((m['severity'] for m in kw), default=0))
            return pd.Series({'categoria_odio': cat, 'severidade': sev})
        df_result = df[coluna_texto].apply(classificar_linha)
        print(f"  → {len(df)} comentários classificados")
        return pd.concat([df.reset_index(drop=True), df_result], axis=1)