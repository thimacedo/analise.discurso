
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import hashlib
import pandas as pd
from datetime import datetime
from processing.report_generator import ReportGenerator
from core.db import db_client

class DossieService:
    """
    Serviço para geração de dossiês forenses com persistência estruturada.
    Diamond Edition v20.5.2
    """
    def __init__(self):
        self.generator = ReportGenerator()

    async def generate_dossie(self, data, path, candidato_id: str):
        """
        Gera o PDF e persiste os metadados no banco de dados.
        """
        if not data:
            print("⚠️ [DossieService] Nenhum dado para gerar dossiê.")
            return None

        df = pd.DataFrame(data)
        
        # 1. Calcula Metadados Forenses
        data_str = df.to_json()
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        total_comentarios = len(df)
        
        # Verifica se as colunas existem antes de contar
        is_hate_col = 'is_hate_speech' if 'is_hate_speech' in df.columns else 'is_hate'
        total_hate = int(df[df[is_hate_col] == True].shape[0]) if is_hate_col in df.columns else 0

        # 2. Gera o PDF físico
        pdf_path = self.generator.generate_pdf(df, path)
        
        if pdf_path:
            # 3. Persistência Estruturada no Supabase
            dossie_meta = {
                "candidato_id": candidato_id,
                "hash_integridade": data_hash,
                "total_comentarios": total_comentarios,
                "total_hate": total_hate,
                "arquivo_path": pdf_path,
                "versao_pasa": "v16.4"
            }
            await db_client.persist_dossier(dossie_meta)
            print(f"✨ [DossieService] Inteligência do dossiê {data_hash[:10]} persistida no repositório.")
            
        return pdf_path
