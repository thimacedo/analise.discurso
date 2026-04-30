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
from core.supabase_client import get_supabase_client

class ElectionMonitor:
    """
    Monitora eleições através de fontes externas (notícias, pesquisas, redes sociais)
    Identifica novos candidatos e atualiza o cenário eleitoral
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self.rapidapi_key = settings.RAPIDAPI_KEY
        self.news_sources = [
            "google-news-br",
            "globo",
            "folha-de-sao-paulo"
        ]

    async def fetch_election_news(self, days_back: int = 7) -> List[Dict]:
        """
        Busca notícias sobre eleições nos últimos N dias
        """
        news_data = []

        # Busca em múltiplas fontes (sequencialmente para evitar rate limits)
        for source in self.news_sources:
            try:
                print(f"🔍 [ElectionMonitor] Buscando notícias em {source}...")
                articles = await self._fetch_from_newsapi(source, days_back)
                news_data.extend(articles)
                # Delay para evitar rate limits
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ [ElectionMonitor] Erro ao buscar de {source}: {e}")
                continue

        return news_data

    async def fetch_polling_data(self) -> List[Dict]:
        """
        Busca dados de pesquisas eleitorais
        """
        polling_data = []

        # Busca em fontes de pesquisa eleitoral
        sources = [
            "datafolha",
            "ibope",
            "pesquisa-censo",
            "atlas-politico"
        ]

        for source in sources:
            try:
                polls = await self._fetch_polls_from_source(source)
                polling_data.extend(polls)
            except Exception as e:
                print(f"⚠️ [ElectionMonitor] Erro ao buscar pesquisas de {source}: {e}")
                continue

        return polling_data

    async def identify_new_candidates(self, news_data: List[Dict], polling_data: List[Dict]) -> List[Dict]:
        """
        Identifica novos candidatos mencionados em notícias e pesquisas
        """
        new_candidates = []

        # Extrai nomes de candidatos das notícias
        mentioned_names = set()
        for article in news_data:
            candidates = await self._extract_candidates_from_text(article.get('title', '') + ' ' + article.get('description', ''))
            mentioned_names.update(candidates)

        # Extrai nomes das pesquisas
        for poll in polling_data:
            if 'candidates' in poll:
                mentioned_names.update(poll['candidates'])

        # Verifica quais nomes não existem no banco
        existing_candidates = self._get_existing_candidate_names()
        existing_names = {c['username'].lower().strip() for c in existing_candidates}

        for name in mentioned_names:
            if name.lower().strip() not in existing_names:
                candidate_info = await self._gather_candidate_info(name)
                if candidate_info:
                    new_candidates.append(candidate_info)

        return new_candidates

    async def update_competitor_coverage(self) -> List[str]:
        """
        Processo completo: busca externa + atualização de cobertura
        """
        print("🔍 [ElectionMonitor] Iniciando busca externa de dados eleitorais...")

        # 1. Busca notícias recentes
        news_data = await self.fetch_election_news(days_back=7)
        print(f"📄 [ElectionMonitor] Encontradas {len(news_data)} notícias sobre eleições")

        # 2. Busca dados de pesquisas
        polling_data = await self.fetch_polling_data()
        print(f"📊 [ElectionMonitor] Encontradas {len(polling_data)} pesquisas eleitorais")

        # 3. Identifica novos candidatos
        new_candidates = await self.identify_new_candidates(news_data, polling_data)
        print(f"👥 [ElectionMonitor] Identificados {len(new_candidates)} novos candidatos")

        # 4. Adiciona novos candidatos ao banco
        added_candidates = []
        for candidate in new_candidates:
            if self._add_candidate_to_database(candidate):
                added_candidates.append(candidate['username'])

        # 5. Atualiza cobertura de concorrentes baseada nos dados externos
        activated_candidates = self._update_coverage_based_on_external_data(news_data, polling_data)

        return added_candidates + activated_candidates

    async def _fetch_from_newsapi(self, source: str, days_back: int) -> List[Dict]:
        """
        Busca notícias de uma fonte específica
        """
        if not self.rapidapi_key:
            print("⚠️ [ElectionMonitor] RAPIDAPI_KEY não configurada - usando dados simulados")
            return self._get_mock_news_data(source)

        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        url = "https://newsapi50.p.rapidapi.com/v2/everything"
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "newsapi50.p.rapidapi.com"
        }
        params = {
            "q": "eleições OR candidatos OR pesquisa eleitoral OR disputa eleitoral",
            "sources": source,
            "from": from_date,
            "language": "pt",
            "sortBy": "relevancy"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('articles', [])
                else:
                    print(f"⚠️ [ElectionMonitor] Erro na API NewsAPI ({source}): {response.status_code} - {response.text[:200]}")
                    # Fallback para dados simulados
                    return self._get_mock_news_data(source)
        except Exception as e:
            print(f"⚠️ [ElectionMonitor] Exceção na API NewsAPI ({source}): {e}")
            # Fallback para dados simulados
            return self._get_mock_news_data(source)

    def _get_mock_news_data(self, source: str) -> List[Dict]:
        """
        Retorna dados simulados de notícias para desenvolvimento
        """
        # Dados simulados baseados em eleições brasileiras recentes
        mock_candidates = [
            "Lula", "Bolsonaro", "Ciro Gomes", "Simone Tebet",
            "João Doria", "Sergio Moro", "João Amoêdo", "José Maria Eymael"
        ]

        mock_articles = []
        for i, candidate in enumerate(mock_candidates[:3]):  # Apenas alguns para não sobrecarregar
            mock_articles.append({
                "title": f"{candidate} lidera pesquisa eleitoral em {source}",
                "description": f"Nova pesquisa mostra {candidate} na liderança da corrida eleitoral. Análise completa dos cenários políticos.",
                "source": {"name": source},
                "publishedAt": datetime.now().isoformat()
            })

        print(f"📄 [ElectionMonitor] Usando dados simulados para {source}: {len(mock_articles)} artigos")
        return mock_articles

    async def _fetch_polls_from_source(self, source: str) -> List[Dict]:
        """
        Busca dados de pesquisas de uma fonte específica
        """
        # Implementação específica por fonte
        # Por enquanto retorna dados mock para desenvolvimento
        return []

    async def _extract_candidates_from_text(self, text: str) -> List[str]:
        """
        Extrai nomes de candidatos de um texto usando IA
        """
        # Usar Qwen/Groq para extrair nomes de candidatos do texto
        from core.qwen_classifier import classify_with_smart_fallback

        prompt = f"""
        Analise o texto abaixo e extraia todos os nomes de candidatos políticos mencionados.
        Retorne apenas uma lista de nomes, um por linha, sem formatação adicional.

        Texto: {text}
        """

        try:
            response = classify_with_smart_fallback(prompt)
            names = [name.strip() for name in response.split('\n') if name.strip()]
            return names
        except Exception as e:
            print(f"⚠️ [ElectionMonitor] Erro ao extrair candidatos: {e}")
            return []

    def _get_existing_candidate_names(self) -> List[Dict]:
        """
        Busca nomes de candidatos existentes no banco
        """
        try:
            response = self.supabase.table('candidatos').select('username').execute()
            return response.data
        except Exception as e:
            print(f"⚠️ [ElectionMonitor] Erro ao buscar candidatos existentes: {e}")
            return []

    async def _gather_candidate_info(self, name: str) -> Optional[Dict]:
        """
        Reúne informações sobre um candidato usando busca externa
        """
        # Busca informações básicas do candidato
        candidate_info = {
            'username': name,
            'cargo': 'A Definir',
            'partido': 'A Definir',
            'status_monitoramento': 'ATIVO',
            'fonte_identificacao': 'monitor_eleitoral_externo',
            'data_identificacao': datetime.now().isoformat()
        }

        # Tenta identificar cargo e partido através de busca
        search_results = await self._search_candidate_info(name)

        if search_results:
            candidate_info.update(search_results)

        return candidate_info

    async def _search_candidate_info(self, name: str) -> Dict:
        """
        Busca informações adicionais sobre um candidato
        """
        # Implementação de busca adicional
        return {}

    def _add_candidate_to_database(self, candidate: Dict) -> bool:
        """
        Adiciona novo candidato ao banco de dados
        """
        try:
            response = self.supabase.table('candidatos').insert(candidate).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"⚠️ [ElectionMonitor] Erro ao adicionar candidato {candidate['username']}: {e}")
            return False

    def _update_coverage_based_on_external_data(self, news_data: List[Dict], polling_data: List[Dict]) -> List[str]:
        """
        Atualiza cobertura baseada em dados externos (notícias + pesquisas)
        """
        activated = []

        # Lógica para ativar candidatos baseada em menções em notícias e pesquisas
        # Por enquanto, ativa todos os candidatos identificados externamente

        return activated