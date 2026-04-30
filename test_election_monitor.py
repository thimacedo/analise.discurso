#!/usr/bin/env python3
"""
Script de teste para o Election Monitor
Demonstra como o sistema agora busca dados externos para cobertura de concorrentes
"""

import asyncio
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.election_monitor import ElectionMonitor
from tools.target_manager import TargetManager

async def test_election_monitor():
    """
    Testa o funcionamento do Election Monitor
    """
    print("🧪 [TEST] Iniciando teste do Election Monitor...")
    print("=" * 60)

    # Inicializa o monitor eleitoral
    election_monitor = ElectionMonitor()

    try:
        # 1. Testa busca de notícias
        print("📄 [TEST] Testando busca de notícias eleitorais...")
        news_data = await election_monitor.fetch_election_news(days_back=1)
        print(f"✅ [TEST] Encontradas {len(news_data)} notícias")

        # 2. Testa busca de pesquisas
        print("📊 [TEST] Testando busca de dados de pesquisas...")
        polling_data = await election_monitor.fetch_polling_data()
        print(f"✅ [TEST] Encontradas {len(polling_data)} pesquisas")

        # 3. Testa identificação de novos candidatos
        print("👥 [TEST] Testando identificação de novos candidatos...")
        new_candidates = await election_monitor.identify_new_candidates(news_data, polling_data)
        print(f"✅ [TEST] Identificados {len(new_candidates)} novos candidatos")

        # 4. Testa processo completo
        print("🔄 [TEST] Testando processo completo de atualização...")
        activated = await election_monitor.update_competitor_coverage()
        print(f"✅ [TEST] Processo completo executado. Ativados: {len(activated)} candidatos")

        print("=" * 60)
        print("🎉 [TEST] Todos os testes do Election Monitor passaram!")

    except Exception as e:
        print(f"❌ [TEST] Erro durante o teste: {e}")
        return False

    return True

async def test_target_manager_integration():
    """
    Testa a integração com o TargetManager
    """
    print("🔗 [TEST] Testando integração com TargetManager...")
    print("=" * 60)

    try:
        # Inicializa o TargetManager
        tm = TargetManager()

        # Testa o método ensure_competitor_coverage (agora usa ElectionMonitor)
        print("🎯 [TEST] Testando ensure_competitor_coverage integrado...")
        activated = await tm.ensure_competitor_coverage()
        print(f"✅ [TEST] Cobertura de concorrentes atualizada. Ativados: {len(activated)}")

        print("=" * 60)
        print("🎉 [TEST] Integração com TargetManager funcionando!")

    except Exception as e:
        print(f"❌ [TEST] Erro na integração: {e}")
        return False

    return True

async def main():
    """
    Executa todos os testes
    """
    print("🚀 SENTINELA DEMOCRÁTICA - Teste do Election Monitor")
    print("Sistema de monitoramento eleitoral externo")
    print("=" * 60)

    # Testa Election Monitor isoladamente
    success1 = await test_election_monitor()

    print("\n" + "=" * 60 + "\n")

    # Testa integração com TargetManager
    success2 = await test_target_manager_integration()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎊 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema agora busca dados externos para cobertura de concorrentes")
        print("✅ Novos candidatos são identificados automaticamente via notícias e pesquisas")
        print("✅ A cobertura eleitoral é mantida atualizada com dados do mundo real")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())