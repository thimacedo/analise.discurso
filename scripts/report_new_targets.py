
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from core.db import db_client
import asyncio

async def report():
    # Busca candidatos que possuem uma pesquisa associada (ultima_pesquisa_id não é nulo)
    # Valor correto: not_null (sem ponto, conforme erro PGRST100)
    res = db_client.client.table('candidatos')\
        .select('username, nome_completo, cargo, intenção_voto, ultima_pesquisa_id')\
        .filter('ultima_pesquisa_id', 'is', 'not_null')\
        .order('intenção_voto', desc=True)\
        .execute()
    
    # Busca nomes dos arquivos das pesquisas
    pesquisas = db_client.client.table('pesquisas_processadas')\
        .select('id, arquivo')\
        .execute()
    
    p_map = {p['id']: p['arquivo'] for p in pesquisas.data}
    
    print("\n📋 RELATÓRIO DE NOVOS ALVOS DETECTADOS:\n")
    print(f"{'HANDLE':<20} | {'NOME':<30} | {'CARGO':<15} | {'INTENÇÃO':<10} | {'FONTE'}")
    print("-" * 110)
    
    for c in res.data:
        fonte = p_map.get(c['ultima_pesquisa_id'], 'Desconhecida')
        nome = str(c.get('nome_completo') or 'N/A')
        cargo = str(c.get('cargo') or 'Candidato')
        intencao = str(c.get('intenção_voto') or '0.0')
        print(f"@{c['username']:<19} | {nome:<30} | {cargo:<15} | {intencao:>8}% | {fonte}")

if __name__ == "__main__":
    asyncio.run(report())
