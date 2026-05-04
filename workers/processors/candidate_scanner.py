"""
Worker: CandidateScanner (Motor de Inteligência de Alvos)
Finalidade: Monitorar a pasta de pesquisas, extrair candidatos, calcular relevância e agendar coleta.
Protocolo Diamond: Herda de BaseWorker.
"""
import os
import re
import hashlib
import asyncio
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Dict

# Import do contrato BaseWorker e DB
import sys
sys.path.append(r"E:\Projetos\sentinela-democratica")
from workers.core.base_worker import BaseWorker
from core.db import db_client

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

class CandidateScannerWorker(BaseWorker):
    def __init__(self):
        super().__init__("CandidateScanner")
        self.base_path = Path(r"E:\Projetos\sentinela-democratica\bases_pesquisas")
        self.processed_table = "pesquisas_processadas"
        self.candidate_table = "candidatos"
        self.queue_table = "fila_coleta"

    async def _run(self, *args, **kwargs):
        if not PdfReader:
            self.logger.error("Biblioteca 'pypdf' não encontrada. Execute 'pip install pypdf'.")
            return

        self.logger.info(f"🔍 Escaneando diretório: {self.base_path}")
        files = list(self.base_path.glob("*.pdf"))
        
        for file_path in files:
            await self._process_file(file_path)

    async def _process_file(self, file_path: Path):
        file_name = file_path.name
        self.logger.info(f"📄 Analisando arquivo: {file_name}")

        # 1. Verificar se já foi processado (Hash)
        file_content = file_path.read_bytes()
        file_hash = hashlib.sha256(file_content).hexdigest()

        existing = db_client.client.table(self.processed_table).select("id").eq("hash_sha256", file_hash).execute()
        if existing.data:
            self.logger.info(f"⏩ Arquivo já processado anteriormente. Pulando.")
            return

        # 2. Extrair Texto do PDF
        try:
            reader = PdfReader(str(file_path))
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            
            # 3. Detectar Candidatos e Intenções (%)
            candidates = self._extract_candidates(full_text)
            self.logger.info(f"🎯 Detectados {len(candidates)} potenciaos alvos.")

            # 4. Salvar Registro da Pesquisa
            res_pesquisa = db_client.client.table(self.processed_table).insert({
                "arquivo": file_name,
                "hash_sha256": file_hash,
                "candidatos_detectados": len(candidates),
                "status": "PROCESSADO"
            }).execute()
            
            pesquisa_id = res_pesquisa.data[0]['id'] if res_pesquisa.data else None

            # 5. Processar cada candidato detectado
            for candidate in candidates:
                await self._handle_candidate(candidate, pesquisa_id)

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar {file_name}: {e}")
            db_client.client.table(self.processed_table).insert({
                "arquivo": file_name,
                "hash_sha256": file_hash,
                "status": "ERRO"
            }).execute()

    def _extract_candidates(self, text: str) -> List[Dict]:
        """
        Regex robusto para capturar: Nome do Candidato e Intenção de Voto.
        Exemplo esperado no texto: "Lula 45,5%", "Bolsonaro 38%", "Ciro Gomes (10,2%)"
        """
        results = []
        # Padrão: Nome seguido de um número decimal ou inteiro com %
        # Tenta capturar nomes próprios capitulares
        pattern = r"([A-Z][a-zà-ú]+(?:\s+[A-Z][a-zà-ú]+)*)\s*\(?(\d+(?:[,\.]\d+)?)\s*%\)?"
        matches = re.findall(pattern, text)

        # Filtro de Stopwords e validação mínima
        stopwords = ["Pesquisa", "Instituto", "Margem", "Erro", "Total", "Votos", "Brancos", "Nulos"]
        
        for name, value in matches:
            if name in stopwords or len(name) < 3:
                continue
            
            val_float = float(value.replace(",", "."))
            results.append({
                "nome": name.strip(),
                "intencao": val_float,
                "cargo": self._infer_cargo(text, name)
            })
        
        # Remove duplicatas mantendo o maior valor
        unique_candidates = {}
        for r in results:
            if r['nome'] not in unique_candidates or r['intencao'] > unique_candidates[r['nome']]['intencao']:
                unique_candidates[r['nome']] = r
                
        return list(unique_candidates.values())

    def _infer_cargo(self, text: str, name: str) -> str:
        """Tenta inferir o cargo baseado no contexto do PDF."""
        context = text.lower()
        if "presidente" in context: return "Presidente"
        if "governador" in context: return "Governador"
        if "senador" in context: return "Senador"
        return "Candidato"

    async def _handle_candidate(self, info: Dict, pesquisa_id: str):
        """Calcula prioridade, enriquece e salva."""
        nome = info['nome']
        intencao = info['intencao']
        cargo = info['cargo']
        
        # 1. Cálculo de Relevância (Sistema de Recompensas do Motor)
        # Nota: (CargoWeight * 10) + Intencao
        cargo_weight = {"Presidente": 5, "Governador": 4, "Senador": 3, "Candidato": 1}
        nota = (cargo_weight.get(cargo, 1) * 10) + intencao
        
        # Determinar prioridade de coleta (1 a 5)
        prioridade = 1
        if intencao > 5 or cargo in ["Presidente", "Governador"]: prioridade = 3
        if intencao > 15: prioridade = 4
        if intencao > 30: prioridade = 5

        # 2. Busca de Rede Social (Simulada via Nome)
        username = self._generate_handle(nome)

        self.logger.info(f"💎 Target: @{username} | Nota: {nota:.2f} | Prioridade: {prioridade}")

        # 3. Upsert no Supabase
        db_client.client.table(self.candidate_table).upsert({
            "username": username,
            "nome_completo": nome,
            "cargo": cargo,
            "intencao_voto": intencao,
            "nota_relevancia": nota,
            "prioridade_coleta": prioridade,
            "ultima_pesquisa_id": pesquisa_id,
            "status_monitoramento": "Ativo" if prioridade >= 3 else "Observação",
            "updated_at": datetime.now(UTC).isoformat()
        }, on_conflict="username").execute()

        # 4. Adicionar à Fila de Coleta do Dia se for relevante
        if prioridade >= 3:
            try:
                db_client.client.table(self.queue_table).upsert({
                    "candidato_id": username,
                    "prioridade": prioridade,
                    "status": "PENDENTE",
                    "data_agendada": datetime.now(UTC).date().isoformat()
                }, on_conflict="candidato_id,data_agendada").execute()
            except Exception as e:
                self.logger.warning(f"⚠️ Não foi possível agendar coleta para {username}: {e}")

    def _generate_handle(self, nome: str) -> str:
        """Gera um handle provisório. Em produção, isso usaria uma busca real."""
        clean = re.sub(r'[^a-zA-Z0-9]', '', nome.lower())
        return clean

if __name__ == "__main__":
    worker = CandidateScannerWorker()
    asyncio.run(worker.execute())
