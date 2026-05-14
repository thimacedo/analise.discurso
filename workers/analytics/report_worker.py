# workers/analytics/report_worker.py
import sys
import logging
from datetime import datetime
from core.supabase_service import get_supabase_client
from workers.core.base_worker import BaseWorker

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class ReportWorker(BaseWorker):
    """
    Worker especializado em gerar relatórios gerenciais E CALIBRAR o sistema de recompensas.
    Analisa a cobertura, produtividade e ajusta a prioridade_coleta dinamicamente.
    """
    def __init__(self):
        super().__init__(name="ReportWorker-Rewards")
        self.supabase = get_supabase_client()

    async def _run(self, *args, **kwargs):
        self.logger.info("📊 Iniciando auditoria e calibração de recompensas...")
        
        try:
            # 1. Busca todos os candidatos
            candidatos_res = self.supabase.table('candidatos').select('id, username, prioridade_coleta, last_scraped_at').execute()
            candidatos = candidatos_res.data
            
            # 2. Busca contagem de comentários por candidato
            comentarios_res = self.supabase.table('comentarios').select('candidato_id, is_hate').execute()
            comentarios_data = comentarios_res.data
            
            # Processamento de métricas
            stats_comentarios = {}
            for c in comentarios_data:
                cid = c['candidato_id']
                if not cid: continue
                if cid not in stats_comentarios:
                    stats_comentarios[cid] = {"total": 0, "hate": 0}
                stats_comentarios[cid]["total"] += 1
                if c['is_hate']: stats_comentarios[cid]["hate"] += 1

            # 3. Avaliação e Recompensa
            relatorio = []
            nunca_raspados = 0
            ajustes_realizados = 0
            
            for cand in candidatos:
                username = cand['username']
                last_scrape = cand.get('last_scraped_at')
                current_priority = cand.get('prioridade_coleta', 1)
                stats = stats_comentarios.get(username, {"total": 0, "hate": 0})
                
                # === LÓGICA DE RECOMPENSA DINÂMICA ===
                new_priority = current_priority
                
                if not last_scrape:
                    nunca_raspados += 1
                    status_operacional = "🔴 PENDENTE"
                    # Alvos nunca raspados mantêm a prioridade original (não punimos o desconhecido)
                    reward_reason = "Aguardando coleta inicial"
                else:
                    # Calcula a Nota de Inteligência (Valor Estratégico)
                    # Cada comentário vale 1 ponto, mas cada Alerta de Ódio vale 5 pontos (Recompensa)
                    intelligence_score = (stats["total"] * 1) + (stats["hate"] * 5)
                    
                    if intelligence_score > 50:
                        new_priority = 5 # Recompensa Máxima: Alvo Crítico de Alto Valor
                        status_operacional = "🟣 ALTO VALOR"
                        reward_reason = f"Score {intelligence_score} (Recompensa: Prioridade 5)"
                    elif intelligence_score > 20:
                        new_priority = 4 # Recompensa Alta
                        status_operacional = "🟢 COBERTO"
                        reward_reason = f"Score {intelligence_score} (Recompensa: Prioridade 4)"
                    elif intelligence_score > 5:
                        new_priority = 3 # Recompensa Média
                        status_operacional = "🟢 COBERTO"
                        reward_reason = f"Score {intelligence_score} (Recompensa: Prioridade 3)"
                    elif stats["total"] > 0:
                        new_priority = 2 # Baixo valor, reduz frequência de coleta
                        status_operacional = "🟡 BAIXO VALOR"
                        reward_reason = f"Score {intelligence_score} (Punição: Prioridade 2)"
                    else:
                        new_priority = 1 # Zona Morta: Extraiu e não rendeu NADA. Punição Máxima.
                        status_operacional = "⚫ ZONA MORTA"
                        reward_reason = "0 inteligência (Punição: Prioridade 1)"

                    # Atualiza no banco se a prioridade mudou
                    if new_priority != current_priority:
                        self.supabase.table('candidatos') \
                            .update({'prioridade_coleta': new_priority}) \
                            .eq('id', cand['id']).execute()
                        ajustes_realizados += 1

                relatorio.append({
                    "candidato": f"@{username}",
                    "status": status_operacional,
                    "prio_antiga": current_priority,
                    "prio_nova": new_priority,
                    "ultima_coleta": last_scrape[:16] if last_scrape else "Nunca",
                    "comentarios_coletados": stats["total"],
                    "alertas_hate": stats["hate"],
                    "recompensa": reward_reason
                })

            # Ordenação: Pendentes primeiro, depois por maior prioridade, depois por valor
            relatorio.sort(key=lambda x: (
                "🔴" in x['status'], "🟣" in x['status'], "🟢" in x['status'], 
                -x['prio_nova'], 
                -x['alertas_hate']
            ))

            # 4. Impressão do Sumário Executivo
            print("\n" + "="*100)
            print(f"🏛️  RELATÓRIO DE INTELIGÊNCIA E RECOMPENSAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            print("="*100)
            print(f"📈 COBERTURA: {len(candidatos) - nunca_raspados}/{len(candidatos)} alvos ({((len(candidatos)-nunca_raspados)/len(candidatos)*100):.1f}%)")
            print(f"🔄 AJUSTES DE PRIORIDADE REALIZADOS: {ajustes_realizados} (Sistema Calibrado)")
            print(f"🚨 ALVOS AINDA NÃO RASPADOS: {nunca_raspados}")
            print("-" * 100)
            print(f"{'CANDIDATO':<25} | {'STATUS':<15} | {'PRIO (→)':<9} | {'COMMS':<6} | {'HATE':<5} | {'RECOMPENSA/PUNIÇÃO'}")
            print("-" * 100)
            
            for item in relatorio:
                prio_change = f"{item['prio_antiga']}→{item['prio_nova']}" if item['prio_antiga'] != item['prio_nova'] else f" {item['prio_nova']}"
                print(f"{item['candidato']:<25} | {item['status']:<15} | {prio_change:<9} | {item['comentarios_coletados']:<6} | {item['alertas_hate']:<5} | {item['recompensa']}")
            
            print("="*100)
            print("💡 ALVOS '🟣 ALTO VALOR' terão mais recursos de raspagem alocados automaticamente.")
            print("💀 ALVOS '⚫ ZONA MORTA' foram punidos e não consumirão sessões do Playwright.")
            print("="*100 + "\n")

            return relatorio

        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar relatório: {e}")
            raise

if __name__ == "__main__":
    import asyncio
    worker = ReportWorker()
    asyncio.run(worker.execute())
