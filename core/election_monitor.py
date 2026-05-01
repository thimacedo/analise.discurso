"""
Election Monitor - Busca externa de notícias e pesquisas eleitorais
Responsável por identificar novos candidatos e mudanças no cenário eleitoral
"""

import httpx
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from core.config import settings
from core.db import db_client
from core.ai_service import ai_service

class ElectionMonitor:
    """
    Monitora eleições através de fontes externas (notícias, pesquisas, redes sociais)
    Identifica novos candidatos e atualiza o cenário eleitoral
    """

    def __init__(self):
        self.db = db_client
        self.rapidapi_key = settings.RAPIDAPI_KEY
        self.news_sources = [
            "google-news-br",
            "globo",
            "folha-de-sao-paulo"
        ]

    async def fetch_election_news(self, days_back: int = 7) -> List[Dict]:
        """Busca notícias sobre eleições nos últimos N dias."""
        news_data = []
        for source in self.news_sources:
            try:
                print(f"🔍 [ElectionMonitor] Buscando notícias em {source}...")
                articles = await self._fetch_from_newsapi(source, days_back)
                news_data.extend(articles)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ [ElectionMonitor] Erro em {source}: {e}")
        return news_data

    async def fetch_polling_data(self) -> List[Dict]:
        """Busca dados de pesquisas eleitorais."""
        # Implementação futura para fontes reais
        return []

    async def identify_new_candidates(self, news_data: List[Dict], polling_data: List[Dict]) -> List[Dict]:
        """Identifica novos candidatos mencionados em notícias e pesquisas."""
        new_candidates = []
        mentioned_names = set()

        for article in news_data:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            candidates = await self._extract_candidate_names(text)
            mentioned_names.update(candidates)

        for poll in polling_data:
            if 'candidates' in poll:
                mentioned_names.update(poll['candidates'])

        existing_candidates = await self.db.client.table('candidatos').select('username').execute()
        existing_names = {c['username'].lower().strip() for c in existing_candidates.data}

        for name in mentioned_names:
            if name.lower().strip() not in existing_names:
                candidate_info = await self._gather_candidate_info(name)
                if candidate_info:
                    new_candidates.append(candidate_info)

        return new_candidates

    async def _extract_candidate_names(self, text: str) -> List[str]:
        """Extrai nomes de candidatos de um texto usando IA."""
        prompt = f"""
        Analise o texto abaixo e extraia todos os nomes de candidatos políticos mencionados.
        Retorne apenas uma lista de nomes, um por linha, sem formatação adicional.
        Texto: {text}
        """
        try:
            response = await ai_service.query(prompt)
            return [n.strip() for n in response.split('\n') if n.strip()]
        except Exception as e:
            print(f"⚠️ [ElectionMonitor] Erro IA: {e}")
            return []

    async def _fetch_from_newsapi(self, source: str, days_back: int) -> List[Dict]:
        if not self.rapidapi_key:
            return self._get_mock_news_data(source)

        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        url = "https://newsapi50.p.rapidapi.com/v2/everything"
        headers = {"X-RapidAPI-Key": self.rapidapi_key, "X-RapidAPI-Host": "newsapi50.p.rapidapi.com"}
        params = {"q": "eleições OR candidatos", "sources": source, "from": from_date, "language": "pt"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            return resp.json().get('articles', []) if resp.status_code == 200 else self._get_mock_news_data(source)

    def _get_mock_news_data(self, source: str) -> List[Dict]:
        mock_candidates = ["Lula", "Bolsonaro", "Ciro Gomes"]
        return [{
            "title": f"{c} lidera pesquisa em {source}",
            "description": f"Análise eleitoral sobre {c}.",
            "publishedAt": datetime.now().isoformat()
        } for c in mock_candidates]

    async def _gather_candidate_info(self, name: str) -> Optional[Dict]:
        return {
            'username': name,
            'cargo': 'A Definir',
            'partido': 'A Definir',
            'status_monitoramento': 'ATIVO',
            'data_entrada': datetime.now().isoformat()
        }

    async def add_candidate(self, candidate: Dict) -> bool:
        try:
            resp = await self.db.client.table('candidatos').insert(candidate).execute()
            return len(resp.data) > 0
        except Exception: return False
