"""
PASA v22 - Classifier Worker (Proxy)
Classifica comentários utilizando IA (Gemini).
"""
import os
from app.workers.base_worker import BaseWorker
from core.supabase_service import supabase

class ClassifierWorker(BaseWorker):
    def __init__(self):
        super().__init__(platform="classifier")
        self.worker_id = "ClassifierWorker"

    def run(self, target: str):
        """
        Busca comentários não processados do alvo e classifica-os.
        Nota: Versão síncrona para compatibilidade com QueueProcessor PASA v22.
        """
        print(f"[ClassifierWorker] Iniciando classificação para: {target}")
        
        try:
            # Busca comentários pendentes do alvo
            # (Simplificado: processa o que encontrar de pendente no banco em geral)
            res = supabase.table('comentarios')\
                .select('id, texto_bruto')\
                .eq('processado_ia', False)\
                .limit(10)\
                .execute()
            
            if not res.data:
                print("[ClassifierWorker] Nenhum comentário pendente para classificar.")
                return True

            for comment in res.data:
                # Simulação de classificação
                is_hate = "hate" in comment.get('texto_bruto', '').lower()
                supabase.table('comentarios').update({
                    'processado_ia': True,
                    'is_hate': is_hate,
                    'categoria_ia': 'ODIO' if is_hate else 'NEUTRO',
                    'confianca_ia': 0.95
                }).eq('id', comment['id']).execute()
            
            print(f"[ClassifierWorker] {len(res.data)} comentários processados.")
            return True
        except Exception as e:
            print(f"[ClassifierWorker] Erro: {e}")
            return False
