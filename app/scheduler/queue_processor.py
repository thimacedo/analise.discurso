"""
PASA v20 - Queue Processor: Motor de autonomia da fila de coleta
"""
import time
import threading
from app.database import supabase
from app.workers.instagram_worker import InstagramWorker
from app.workers.classifier_worker import ClassifierWorker

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
            
            # Futuro: elif platform == 'tiktok': ...

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

    def run_loop(self):
        """Loop contínuo de processamento da fila."""
        self.running = True
        print("[QueueProcessor] Motor de autonomia iniciado. Monitorando fila...")
        while self.running:
            self._process_next_item()
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
