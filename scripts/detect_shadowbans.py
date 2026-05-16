"""
PASA v46 - Shadowban Detector: Identifica silêncio suspeito em perfis de alto escalão
Se um alvo com muitos seguidores rendeu 0 comentários, provavelmente está shadowbanned.
"""
import requests
import logging
from core.supabase_service import get_supabase_client

logger = logging.getLogger("ShadowbanDetector")

CALLMEBOT_PHONE = "558496066876"
CALLMEBOT_APIKEY = "8552672"
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

def detect_shadowbans():
    db = get_supabase_client()
    
    # 1. Busca alvos de alto escalão (com seguidores mapeados)
    # P0: Alvos com mais de 100k seguidores
    try:
        targets = db.table('candidatos').select('username, seguidores, comentarios_totais_count').gt('seguidores', 100000).execute()
        
        if not targets.data:
            logger.info("Nenhum alvo de alto escalão (>100k) encontrado para monitoramento de shadowban.")
            return

        suspect_count = 0

        for t in targets.data:
            username = t['username']
            followers = t.get('seguidores', 0)
            # Nota: comentarios_totais_count deve ser atualizado periodicamente
            total_comments = t.get('comentarios_totais_count', 0)
            
            # 2. Lógica de Detecção: Perfil com +100k seguidores e 0 comentários totais detectados = Shadowban Suspeito
            # Em um cenário real, poderíamos olhar para comentários nas últimas 24h.
            if total_comments == 0 and followers > 100000:
                suspect_count += 1
                logger.warning(f"🚨 SUSPEITA DE SHADOWBAN: @{username} ({followers} seguidores, 0 comentários)")
                
                # 3. Registra a suspeita no banco para o Dashboard exibir
                db.table('candidatos').update({'shadowban_suspect': True}).eq('username', username).execute()
                
                # 4. Dispara Alerta WhatsApp para o alvo P0
                send_shadowban_alert(username, followers)
            else:
                # Limpa a flag se houver comentários (evita falso positivo persistente)
                db.table('candidatos').update({'shadowban_suspect': False}).eq('username', username).execute()
        
        if suspect_count == 0:
            logger.info("Nenhum shadowban suspeito detectado nesta rodada.")

    except Exception as e:
        logger.error(f"Erro na detecção de shadowban: {e}")

def send_shadowban_alert(username, followers):
    message = f"🚨 *SHADOWBAN SUSPEITO* 🚨\n\nO perfil *@{username}* ({followers:,} seg) rendeu *0 comentários* na última coleta.\n\nO Instagram pode estar ocultando interações deste alvo no PASA v46."
    
    params = {
        "phone": CALLMEBOT_PHONE,
        "apikey": CALLMEBOT_APIKEY,
        "text": message
    }
    try:
        # Silencioso para não travar o loop
        requests.get(CALLMEBOT_URL, params=params, timeout=10)
    except Exception as e:
        logger.error(f"Falha ao enviar alerta WhatsApp: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detect_shadowbans()
