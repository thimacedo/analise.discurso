#!/usr/bin/env python3

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
"""
Painel de Controle Interativo - Sentinela Democrática
v2.0 - Lista inteligente de pendências e seleção por número.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Garante o path do projeto
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.db import db_client
from core.instagram_headless import InstagramHeadlessScraper
from core.ai_service import ai_service
from core.orquestrador import Orchestrator


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("=" * 60)
    print("🎛️  PAINEL DE CONTROLE - SENTINELA DEMOCRÁTICA [v2.0]")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)


async def fetch_pending_targets(limit=50):
    """
    Busca alvos pendentes de raspagem, ordenados por prioridade decrescente,
    depois por last_scraped_at crescente (nunca raspados primeiro).
    """
    if not db_client.client:
        return []
    try:
        # Ordenação: prioridade DESC, last_scraped_at ASC (nulls first)
        res = db_client.client.table('candidatos')\
            .select('username', 'prioridade_coleta', 'cargo', 'last_scraped_at', 'nome_completo')\
            .order('prioridade_coleta', desc=True)\
            .order('last_scraped_at', asc=True, nullsfirst=True)\
            .limit(limit)\
            .execute()
        return res.data
    except Exception as e:
        print(f"❌ Erro ao buscar alvos: {e}")
        return []


async def show_status():
    """Exibe status resumido e lista de prioridades."""
    if not db_client.client:
        print("❌ Cliente Supabase não inicializado.")
        return

    # Filas gerais
    try:
        res = db_client.client.table('fila_coleta').select('*', count='exact').eq('status', 'PENDENTE').execute()
        count = res.count if res.count is not None else len(res.data)
        print(f"\n📋 Fila de coleta: {count} alvos agendados para hoje")
    except Exception as e:
        print(f"⚠️ Erro ao ler fila_coleta: {e}")

    # Pendentes de raspagem
    pendentes = await fetch_pending_targets(limit=100)
    if pendentes:
        prioridades = {}
        for p in pendentes:
            prio = p.get('prioridade_coleta', 1)
            prioridades[prio] = prioridades.get(prio, 0) + 1
        print(f"🎯 Alvos pendentes de raspagem: {len(pendentes)}")
        for prio in sorted(prioridades.keys(), reverse=True):
            print(f"   Prioridade {prio}: {prioridades[prio]} perfis")
        
        print("\n   🔝 Top 5 da fila:")
        for i, cand in enumerate(pendentes[:5], 1):
            nome = cand.get('nome_completo') or cand['username']
            last = cand.get('last_scraped_at')
            last_str = last[:10] if last else 'Nunca'
            print(f"   {i}. @{cand['username']} ({nome}) - Prio {cand['prioridade_coleta']} | Última: {last_str}")
    else:
        print("🎯 Nenhum alvo pendente (todos já raspados).")

    # Comentários pendentes
    try:
        res = db_client.client.table('comentarios').select('*', count='exact').eq('processado_ia', False).execute()
        count = res.count if res.count is not None else len(res.data)
        print(f"\n🧠 Comentários aguardando classificação IA: {count}")
    except:
        pass


async def select_and_scrape():
    """Lista alvos pendentes, permite selecionar por número e força raspagem."""
    pendentes = await fetch_pending_targets(limit=50)
    if not pendentes:
        print("✅ Nenhum alvo pendente.")
        return

    print("\n📋 Alvos pendentes de raspagem (selecione o número ou '0' para voltar):")
    for idx, cand in enumerate(pendentes, 1):
        nome = cand.get('nome_completo') or cand['username']
        last = cand.get('last_scraped_at')
        last_str = last[:10] if last else 'Nunca'
        print(f"{idx:2d}. @{cand['username']} ({nome}) - Prio {cand['prioridade_coleta']} | Última: {last_str}")

    try:
        escolha = input("\nNº do perfil (ou vários separados por vírgula): ").strip()
        if escolha == '0':
            return
        indices = [int(x.strip()) for x in escolha.split(',') if x.strip().isdigit()]
        targets = []
        for i in indices:
            if 1 <= i <= len(pendentes):
                targets.append(pendentes[i-1])
            else:
                print(f"⚠️ Número {i} inválido, ignorado.")

        if not targets:
            print("Nenhum perfil selecionado.")
            return

        scraper = InstagramHeadlessScraper()
        for cand in targets:
            res = db_client.client.table('candidatos').select('id').eq('username', cand['username']).execute()
            if not res.data:
                novo = {
                    'username': cand['username'],
                    'nome_completo': cand.get('nome_completo') or cand['username'],
                    'cargo': cand.get('cargo', 'Candidato'),
                    'status_monitoramento': 'Ativo',
                    'prioridade_coleta': cand.get('prioridade_coleta', 3),
                    'data_entrada': datetime.now(timezone.utc).isoformat()
                }
                insert_res = db_client.client.table('candidatos').insert(novo).execute()
                if insert_res.data:
                    cand['id'] = insert_res.data[0]['id']
                else:
                    print(f"❌ Não foi possível cadastrar @{cand['username']}. Pulando.")
                    continue
            else:
                cand['id'] = res.data[0]['id']

            print(f"🔄 Raspando @{cand['username']}...")
            await scraper.run(targets=[cand])
            print(f"✅ @{cand['username']} concluído.")
    except ValueError:
        print("❌ Entrada inválida.")


async def main():
    while True:
        # Proteção para execução em ambientes sem TTY (como este CLI)
        if not sys.stdin.isatty():
            print_header()
            await show_status()
            print("\n[PAINEL OPERANTE - MODO NÃO-INTERATIVO]")
            break

        clear_screen()
        print_header()
        await show_status()

        print("\n" + "-" * 40)
        print("OPÇÕES:")
        print("  1. Raspar perfil da lista de pendentes (seleção por número)")
        print("  2. Forçar classificação IA (lote)")
        print("  3. Alterar prioridade de um alvo")
        print("  4. Executar pipeline completo (orquestrador)")
        print("  5. Atualizar status (refresh)")
        print("  0. Sair")
        print("-" * 40)

        op = input("Escolha uma opção: ").strip()

        if op == '1':
            await select_and_scrape()
        elif op == '2':
            limit = input("📦 Quantos comentários? (200): ").strip()
            await ai_service.run_batch_classification(limit=int(limit) if limit.isdigit() else 200)
        elif op == '3':
            await adjust_priority()
        elif op == '4':
            await Orchestrator().run_full_pipeline()
        elif op == '5':
            continue
        elif op == '0':
            print("👋 Encerrando painel de controle.")
            break
        else:
            print("❌ Opção inválida.")

        input("\nPressione ENTER para continuar...")

async def adjust_priority():
    target = input("🎯 Nome do perfil: ").strip()
    if not target: return
    try:
        res = db_client.client.table('candidatos').select('username, prioridade_coleta').eq('username', target).execute()
        if not res.data:
            print(f"❌ @{target} não encontrado.")
            return
        atual = res.data[0]['prioridade_coleta']
        print(f"Prioridade atual de @{target}: {atual} (1-5)")
        nova = input("Nova prioridade (1-5): ").strip()
        if nova.isdigit() and 1 <= int(nova) <= 5:
            db_client.client.table('candidatos').update({'prioridade_coleta': int(nova)}).eq('username', target).execute()
            print(f"✅ @{target} atualizado para prioridade {nova}.")
        else:
            print("❌ Valor inválido.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
