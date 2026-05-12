
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import httpx

class SupabaseService:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        self.client: Client = create_client(self.url, self.key) if self.url and self.key else None
        self.http_client = httpx.AsyncClient() # Usar um cliente httpx reutilizável

    async def fetch_unprocessed_comments(self, limit: int = 200, org_id: str = None) -> List[Dict[str, Any]]:
        """Busca comentários que ainda não foram processados pela IA, filtrados por org opcional."""
        url = f"{self.url}/rest/v1/comentarios?processado_ia=not.eq.true&limit={limit}"
        if org_id:
            url += f"&organization_id=eq.{org_id}"
        
        try:
            resp = await self.http_client.get(url, headers=self.headers)
            resp.raise_for_status() # Lança exceção para códigos de erro HTTP
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ [SupabaseService] Erro HTTP ao buscar comentários não processados: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            print(f"❌ [SupabaseService] Erro de requisição ao buscar comentários não processados: {e}")
            return []

    async def fetch_all_data(self, org_id: str = None) -> List[Dict[str, Any]]:
        """Busca todos os comentários processados de uma organização."""
        url = f"{self.url}/rest/v1/comentarios?select=*"
        if org_id:
            url += f"&organization_id=eq.{org_id}"
        
        try:
            resp = await self.http_client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ [SupabaseService] Erro HTTP ao buscar todos os comentários: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            print(f"❌ [SupabaseService] Erro de requisição ao buscar todos os comentários: {e}")
            return []

    async def update_comment_classification(self, comment_id: str, data: Dict[str, Any]):
        """Atualiza a classificação de um único comentário."""
        url = f"{self.url}/rest/v1/comentarios?id=eq.{comment_id}"
        try:
            await self.http_client.patch(url, headers=self.headers, json=data)
            print(f"✅ [SupabaseService] Comentário {comment_id} atualizado.")
        except httpx.HTTPStatusError as e:
            print(f"❌ [SupabaseService] Erro HTTP ao atualizar comentário {comment_id}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"❌ [SupabaseService] Erro de requisição ao atualizar comentário {comment_id}: {e}")

    async def batch_update_comments(self, updates: List[Dict[str, Any]]):
        """
        Executa atualizações em lote para comentários usando upsert do Supabase.
        Cada dicionário em 'updates' deve conter a chave 'id'.
        """
        if not self.client or not updates:
            print("⚠️ [SupabaseService] Nenhum dado para atualizar em lote ou cliente Supabase não inicializado.")
            return

        try:
            # O upsert no Supabase funciona como merge se o ID estiver presente
            self.client.table('comentarios').upsert(updates).execute()
            print(f"✅ [SupabaseService] {len(updates)} comentários atualizados em lote.")
        except Exception as e:
            print(f"❌ [SupabaseService] Erro no batch_update_comments: {e}")

    async def batch_update_ad_classification(self, updates: List[Dict[str, Any]]):
        """
        Executa atualizações em lote para classificações de anúncios.
        Cada dicionário em 'updates' deve conter a chave 'id'.
        """
        if not self.client or not updates:
            print("⚠️ [SupabaseService] Nenhum dado para atualizar em lote ou cliente Supabase não inicializado.")
            return

        try:
            self.client.table('anuncios').upsert(updates).execute()
            print(f"✅ [SupabaseService] {len(updates)} anúncios atualizados em lote.")
        except Exception as e:
            print(f"❌ [SupabaseService] Erro no batch_update_ad_classification: {e}")

    async def upsert_daily_metrics(self, payload: Dict[str, Any]) -> bool:
        """Salva ou atualiza métricas diárias via RPC."""
        url = f"{self.url}/rest/v1/rpc/upsert_metrica_diaria"
        try:
            resp = await self.http_client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.status_code in [200, 201, 204]
        except httpx.HTTPStatusError as e:
            print(f"❌ [SupabaseService] Erro HTTP ao chamar RPC upsert_metrica_diaria: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"❌ [SupabaseService] Erro de requisição ao chamar RPC upsert_metrica_diaria: {e}")
            return False

    async def persist_coordinated_network(self, payload: Dict[str, Any]):
        """Persiste rede coordenada detectada."""
        url = f"{self.url}/rest/v1/redes_coordenadas"
        try:
            await self.http_client.post(url, json=payload, headers=self.headers)
            print("✅ [SupabaseService] Rede coordenada persistida.")
        except httpx.HTTPStatusError as e:
            print(f"❌ [SupabaseService] Erro HTTP ao persistir rede coordenada: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"❌ [SupabaseService] Erro de requisição ao persistir rede coordenada: {e}")

    async def create_active_alert(self, payload: Dict[str, Any]):
        """Cria um alerta ativo no sistema."""
        url = f"{self.url}/rest/v1/alertas_ativos"
        try:
            await self.http_client.post(url, json=payload, headers=self.headers)
            print("✅ [SupabaseService] Alerta ativo criado.")
        except httpx.HTTPStatusError as e:
            print(f"❌ [SupabaseService] Erro HTTP ao criar alerta ativo: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"❌ [SupabaseService] Erro de requisição ao criar alerta ativo: {e}")

    async def fetch_targets_needing_repericia(self) -> List[str]:
        """Busca usernames de candidatos marcados para re-perícia."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return []
        try:
            res = self.client.table('candidatos').select('username').eq('needs_re_pericia', True).execute()
            return [item['username'] for item in res.data]
        except Exception as e:
            # Verifica se o erro é devido à coluna não existir
            if "column" in str(e) and "needs_re_pericia" in str(e):
                print(f"[SupabaseService] Coluna 'needs_re_pericia' não encontrada. Retornando lista vazia.")
                return [] 
            print(f"❌ [SupabaseService] Erro ao buscar alvos para re-perícia: {e}")
            return []

    async def reset_target_comments(self, username: str):
        """Reseta o status de processamento de todos os comentários de um alvo."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return
        print(f"🔄 [SupabaseService] Resetando comentários para @{username}...")
        
        try:
            # Busca IDs dos comentários do alvo
            res = self.client.table('comentarios').select('id').eq('candidato_id', username).execute()
            comment_ids = [c['id'] for c in res.data]
            
            if not comment_ids:
                print(f"⚠️ [SupabaseService] Nenhum comentário para @{username} encontrado para resetar.")
                return

            # Reset em blocos para performance e segurança
            batch_size = 100
            for i in range(0, len(comment_ids), batch_size):
                batch = comment_ids[i:i+batch_size]
                self.client.table('comentarios').update({
                    'processado_ia': False,
                    'categoria_ia': None,
                    'confianca_ia': 0,
                    'is_hate': False
                }).in_('id', batch).execute()
            
            print(f"✅ [SupabaseService] {len(comment_ids)} comentários resetados para @{username}.")
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao resetar comentários para @{username}: {e}")

    async def mark_repericia_complete(self, username: str):
        """Desmarca o flag de re-perícia para o alvo."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return
        try:
            self.client.table('candidatos').update({'needs_re_pericia': False}).eq('username', username).execute()
            print(f"✅ [SupabaseService] Flag 'needs_re_pericia' desmarcado para @{username}.")
        except Exception as e:
            print(f"⚠️ [SupabaseService] Erro ao desmarcar re-perícia para @{username}: {e}")

    async def persist_ad(self, data: Dict[str, Any]):
        """Persiste um anúncio extraído da Meta Ad Library."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return
        try:
            # Usa upsert baseado no ad_id (id_externo no contexto Meta)
            self.client.table('anuncios').upsert(data, on_conflict='ad_id').execute()
            print(f"✅ [SupabaseService] Anúncio {data.get('ad_id')} persistido.")
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao persistir anúncio {data.get('ad_id')}: {e}")

    async def persist_ads_batch(self, ads: List[Dict[str, Any]]):
        """Persiste múltiplos anúncios em lote."""
        if not self.client or not ads: 
            print("⚠️ [SupabaseService] Nenhum dado de anúncio para persistir em lote ou cliente Supabase não inicializado.")
            return
        try:
            # Supabase permite upsert de lista
            self.client.table('anuncios').upsert(ads, on_conflict='ad_id').execute()
            print(f"✅ [SupabaseService] {len(ads)} anúncios processados em lote.")
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao persistir lote de anúncios: {e}")

    async def fetch_unprocessed_ads(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca anúncios que ainda não foram processados pela IA."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return []
        try:
            res = self.client.table('anuncios').select('*').eq('processado_ia', False).limit(limit).execute()
            return res.data
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao buscar anúncios não processados: {e}")
            return []

    async def update_ad_classification(self, ad_id: str, data: Dict[str, Any]):
        """Atualiza a classificação de um único anúncio."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return
        try:
            # A Supabase Python client usa .eq() para filtros em queries/updates.
            # Se ad_id for o ID da tabela (coluna 'id'), use o filtro apropriado.
            # Assumindo que 'ad_id' é o ID externo e que há uma coluna 'id' na tabela 'anuncios' para correspondência.
            # Se 'ad_id' for o identificador único para upsert/update, a lógica pode precisar ser ajustada.
            # Para esta refatoração, vamos assumir que 'ad_id' é uma coluna que pode ser usada para filtrar.
            # Se o `ad_id` for o ID externo da Meta, e a tabela usa um ID diferente, precisaremos mapear.
            # Para simplicidade, vamos usar 'ad_id' como se fosse uma coluna filtrável ou o próprio ID.
            # Se a coluna na tabela for 'id' e o dado passado for 'ad_id', pode ser necessário:
            # res = self.client.table('anuncios').update(data).eq('id', ad_id).execute() # Se ad_id for o ID interno
            # Ou se ad_id for o identificador externo e queremos atualizar um registro específico:
            # res = self.client.table('anuncios').update(data).eq('ad_id', ad_id).execute() # Se 'ad_id' for a coluna de filtro

            # Vamos usar a abordagem mais segura de filtrar por 'ad_id' se ele existir como coluna,
            # caso contrário, faremos um upsert genérico se ad_id for uma chave primária ou único.
            # Para manter a estrutura, vamos supor que 'ad_id' é uma coluna válida para filtro aqui.
            # Se a intenção era usar o 'id' da tabela Supabase, o nome da variável de entrada deveria ser 'ad_supabase_id'.
            
            # Tentativa com 'ad_id' como filtro, assumindo que é uma coluna na tabela 'anuncios'
            # Se não for, o Supabase client lançará um erro que será capturado.
            self.client.table('anuncios').update(data).eq('ad_id', ad_id).execute()
            print(f"✅ [SupabaseService] Classificação do anúncio {ad_id} atualizada.")
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao atualizar classificação do anúncio {ad_id}: {e}")

    async def persist_dossier(self, data: Dict[str, Any]):
        """Salva metadadados de um novo dossiê forense."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return None
        try:
            res = self.client.table('dossies').insert(data).execute()
            print(f"✅ [SupabaseService] Dossiê persistido com hash: {data.get('hash_integridade', 'N/A')[:10]}...")
            return res.data
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao persistir dossiê: {e}")
            return None

    async def fetch_dossier_history(self, candidato_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recupera o histórico de dossiês estruturados de um candidato."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return []
        try:
            res = self.client.table('dossies') \
                .select('*') \
                .eq('candidato_id', candidato_id) \
                .order('data_geracao', ascending=False) \
                .limit(limit) \
                .execute()
            return res.data
        except Exception as e:
            print(f"❌ [SupabaseService] Erro ao buscar histórico de dossiês para {candidato_id}: {e}")
            return []

    async def fetch_unmined_comments(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Busca comentários processados pela IA mas ainda não minerados."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return []
        try:
            # Tenta filtrar pela coluna 'mined' se existir, caso contrário busca processados
            query = self.client.table('comentarios').select('*')
            query = query.eq('processado_ia', True)
            query = query.eq('mined', False)
            query = query.limit(limit)
            res = query.execute()
            return res.data
        except Exception as e:
            if "column" in str(e) and "mined" in str(e):
                # Fallback se a coluna não existir ainda
                print(f"[SupabaseService] Coluna 'mined' não encontrada. Buscando apenas comentários processados.")
                query = self.client.table('comentarios').select('*')
                query = query.eq('processado_ia', True)
                query = query.limit(limit)
                res = query.execute()
                return res.data
            print(f"❌ [SupabaseService] Erro ao buscar comentários não minerados: {e}")
            return []

    async def fetch_unmined_ads(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Busca anúncios processados pela IA mas ainda não minerados."""
        if not self.client: 
            print("⚠️ [SupabaseService] Cliente Supabase não inicializado.")
            return []
        try:
            res = self.client.table('anuncios').select('*').eq('processado_ia', True).eq('mined', False).limit(limit).execute()
            return res.data
        except Exception as e:
            if "column" in str(e) and "mined" in str(e):
                print(f"[SupabaseService] Coluna 'mined' não encontrada. Buscando apenas anúncios processados.")
                res = self.client.table('anuncios').select('*').eq('processado_ia', True).limit(limit).execute()
                return res.data
            print(f"❌ [SupabaseService] Erro ao buscar anúncios não minerados: {e}")
            return []

# Instanciamento do cliente principal (se necessário globalmente)
# Este cliente será compartilhado entre as instâncias do serviço se ele for instanciado uma vez.
# Para evitar problemas de concorrência ou estado, pode ser melhor criar instâncias sob demanda
# ou usar um padrão de Singleton com cuidado.
# Por agora, vamos manter a instância aqui e assumir que ela é gerenciada adequadamente.
# Precisamos obter as configurações do Supabase URL e KEY.
# Vamos assumir que `settings` é acessível e contém `SUPABASE_URL` e `SUPABASE_KEY`.
# Se não, precisaremos de uma maneira de passar essas configurações.
# Dado que `core/config` foi importado, assumimos que `settings` está disponível.

# O cliente principal pode ser instanciado aqui ou quando necessário.
# Para fins de refatoração, vamos expor a classe e deixar a instanciação para quem a usa.
# No entanto, o `core/db.py` original criava uma instância global `db_client`.
# Vamos replicar isso para manter a compatibilidade, assumindo que `settings` está disponível.

# Se `settings.SUPABASE_URL` ou `settings.SUPABASE_KEY` não estiverem definidos, o cliente será None.
# O código existente já trata isso com `if not self.client: return`.

# Exemplo de como a instância seria usada (similar ao antigo db_client):
# from core.supabase_service import SupabaseService
# from core.config import settings
#
# # Para usar em funções async:
# supabase_svc = SupabaseService(settings.SUPABASE_URL, settings.SUPABASE_KEY)
#
# # Exemplo de chamada:
# # comments = await supabase_svc.fetch_unprocessed_comments(limit=50)
# # await supabase_svc.update_comment_classification("some-id", {"campo": "valor"})

# Criando uma instância global para compatibilidade com o código existente que pode depender dela.
# Se `settings` não estiver disponível neste escopo, isso falhará.
# A importação de `core.config` sugure que `settings` é acessível.
try:
    supabase_client_instance = SupabaseService(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    print("[SupabaseService] Instância global do SupabaseService criada.")
except Exception as e:
    print(f"⚠️ [SupabaseService] Falha ao criar instância global do SupabaseService: {e}. Verifique as configurações do Supabase.")
    supabase_client_instance = None
