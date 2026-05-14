"""
PASA v20 - Queue Processor: Motor de autonomia da fila de coleta
"""
import time
import threading
from app.database import supabase
from app.workers.instagram_worker import InstagramWorker
from app.workers.classifier_worker import ClassifierWorker
from scripts.fetch_pending import process_pending_comments

class QueueProcessor:
    def __init__(self, poll_interval: int = 30):
        self.poll_interval = poll_interval
        self.running = False

    def _process_next_item(self):
        """Busca o próximo item pendente e despacha o worker correto."""
        # Busca item travando a linha (simulação de lock via status)
        item = supabase.table('fila_coleta')\
            .update({'status': 'processing'})\
            .eq('status', 'pending')\
            .neq('status', 'paused_auth_fail')\
            .order('created_at')\
            .limit(1)\
            .execute()

        if not item.data:
            return # Fila vazia ou pausada

        target_id = item.data[0]['target_id']
        platform = item.data[0]['plataforma']
        item_id = item.data[0]['id']

        try:
            if platform == 'instagram':
                worker = InstagramWorker()
                success = worker.run(target=target_id)
            # PASA v22: Expansão congelada até o Instagram ser perfeito
            # elif platform == 'youtube':
            #     worker = YouTubeScraper()
            #     success = worker.run(target=target_id)
            else:
                print(f"[QueueProcessor] Plataforma {platform} congelada ou inexistente. Pulando.")
                supabase.table('fila_coleta').update({'status': 'PAUSADO_ESTRATEGICO'}).eq('id', item_id).execute()
                return

            if success:
                # Após coleta bem sucedida, agenda classificação
                classifier = ClassifierWorker()
                classifier.run(target=target_id)
                
                supabase.table('fila_coleta').update({'status': 'completed'}).eq('id', item_id).execute()
            else:
                supabase.table('fila_coleta').update({'status': 'failed'}).eq('id', item_id).execute()

        except Exception as e:
            print(f"[QueueProcessor] Erro fatal ao processar {target_id}: {e}")
            supabase.table('fila_coleta').update({'status': 'failed'}).eq('id', item_id).execute()

    def _check_global_pause(self):
        """PASA v24: Verifica se a sessão do Instagram está marcada como expirada antes de processar."""
        try:
            session = supabase.table('worker_sessions').select('status').eq('plataforma', 'instagram').execute()
            if session.data and session.data[0]['status'] == 'expired':
                print("[QueueProcessor] Sessão do Instagram expirada. Aguardando injeção de cookies via Dashboard...")
                return True
        except Exception as e:
            # Se a tabela não existir ainda, ignora o pause
            pass
        return False

    def run_loop(self):
        """Loop contínuo de processamento da fila."""
        self.running = True
        print("[QueueProcessor] Motor de autonomia iniciado. Monitorando fila...")
        while self.running:
            if not self._check_global_pause():
                self._process_next_item()
                # PASA v25: Após processar um alvo, tenta esvaziar a fila de classificação em lote
                process_pending_comments()
            time.sleep(self.poll_interval)

    def start_async(self):
        """Inicia o processador em uma thread dedicada."""
        thread = threading.Thread(target=self.run_loop, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Interrompe o motor de autonomia."""
        self.running = False
        print("[QueueProcessor] Motor de autonomia desligado.")
