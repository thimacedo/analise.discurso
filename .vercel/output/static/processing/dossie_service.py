import hashlib
import json
from datetime import datetime
from processing.report_generator import ReportGenerator
from core.db import db_client

class DossieService:
    """
    Serviço para geração de dossiês forenses com persistência estruturada.
    Diamond Edition v20.5.2 (Otimizado: Sem Pandas para compatibilidade Vercel)
    """
    def __init__(self):
        self.generator = ReportGenerator()

    async def generate_dossie(self, data, path, candidato_id: str):
        """
        Gera o PDF e persiste os metadados no banco de dados.
        Utiliza lógica nativa para evitar dependência do Pandas.
        """
        if not data:
            print("⚠️ [DossieService] Nenhum dado para gerar dossiê.")
            return None

        # 1. Calcula Metadados Forenses (Usando JSON nativo)
        data_str = json.dumps(data)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        total_comentarios = len(data)
        
        # Identifica coluna de ódio (is_hate ou is_hate_speech)
        total_hate = 0
        for item in data:
            if item.get('is_hate') is True or item.get('is_hate_speech') is True:
                total_hate += 1

        # 2. Gera o PDF físico
        # Nota: ReportGenerator deve ser adaptado para aceitar List[Dict] em vez de DataFrame
        pdf_path = self.generator.generate_pdf(data, path)
        
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
