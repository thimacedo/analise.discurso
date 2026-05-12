
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MetaAdService")

class MetaAdService:
    """
    Serviço core para interação com a Meta Ad Library API (Ads Archive).
    Documentação: https://developers.facebook.com/docs/marketing-api/ads-library-api-graph-api/
    """
    
    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.api_version = settings.META_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/ads_archive"

    async def search_ads(self, query: str, country: str = 'BR', limit: int = 25, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Busca anúncios na Meta Ad Library API com suporte a paginação.
        """
        if not self.access_token:
            logger.warning(f"⚠️ [MetaService] META_ACCESS_TOKEN ausente. Ignorando API para '{query}'.")
            return []

        all_normalized_ads = []
        current_url = self.base_url
        params = {
            'access_token': self.access_token,
            'search_terms': query,
            'ad_reached_countries': f"['{country}']",
            'ad_type': 'POLITICAL_AND_ISSUE_ADS',
            'ad_active_status': 'ALL',
            'fields': 'id,ad_creation_time,ad_delivery_start_time,ad_delivery_stop_time,ad_creative_bodies,page_id,page_name,spend,impressions,funding_entity',
            'limit': limit
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                page_count = 0
                while current_url and page_count < max_pages:
                    try:
                        response = await client.get(current_url, params=params if page_count == 0 else None)
                        response.raise_for_status()
                        data = response.json()
                        
                        ads = data.get('data', [])
                        logger.info(f"   📄 [MetaService] Página {page_count + 1}: {len(ads)} anúncios encontrados para '{query}'.")
                        
                        all_normalized_ads.extend([self._normalize_ad(ad, query) for ad in ads])
                        
                        current_url = data.get('paging', {}).get('next')
                        page_count += 1
                        
                        if not current_url:
                            break
                            
                    except httpx.HTTPStatusError as e:
                        logger.error(f"❌ [MetaService] Erro na API da Meta ({e.response.status_code}): {e.response.text}")
                        break
                    except Exception as e:
                        logger.error(f"❌ [MetaService] Erro na página {page_count+1}: {e}")
                        break

            logger.info(f"✅ [MetaService] Total final: {len(all_normalized_ads)} anúncios para '{query}'.")
        except Exception as e:
            logger.error(f"❌ [MetaService] Falha crítica na busca via API: {e}")
            return []
            
        return all_normalized_ads

    def _normalize_ad(self, raw_ad: Dict[str, Any], candidato_id: str) -> Dict[str, Any]:
        """
        Normaliza os dados da API para o schema da tabela 'anuncios'.
        """
        # Extrai valores de spend (Meta retorna como range {lower_bound, upper_bound})
        spend = raw_ad.get('spend', {})
        v_min = float(spend.get('lower_bound', 0))
        v_max = float(spend.get('upper_bound', 0))

        # Extrai valores de alcance (impressões)
        impressions = raw_ad.get('impressions', {})
        a_min = int(impressions.get('lower_bound', 0))
        a_max = int(impressions.get('upper_bound', 0))

        # Conteúdo criativo (corpo do anúncio)
        bodies = raw_ad.get('ad_creative_bodies', [])
        body_text = " ".join(bodies) if bodies else ""

        return {
            "ad_id": raw_ad.get('id'),
            "candidato_id": candidato_id,
            "pagador": raw_ad.get('funding_entity', "Desconhecido"),
            "valor_min": v_min,
            "valor_max": v_max,
            "status": "active" if not raw_ad.get('ad_delivery_stop_time') else "inactive",
            "alcance_min": a_min,
            "alcance_max": a_max,
            "corpo_anuncio": body_text,
            "criativo_url": None, # API de Arquivo não dá URL direta do criativo facilmente
            "page_name": raw_ad.get('page_name'),
            "data_inicio": raw_ad.get('ad_delivery_start_time'),
            "data_fim": raw_ad.get('ad_delivery_stop_time'),
            "updated_at": datetime.now().isoformat()
        }

meta_ad_service = MetaAdService()
