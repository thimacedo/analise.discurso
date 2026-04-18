import os
from instagram_collector import ForensicCollector
from dotenv import load_dotenv

def test_login():
    print("🚀 Iniciando teste de conexao ForenseNet/Instagram...")
    try:
        # Carrega .env do projeto
        load_dotenv()
        
        # Instancia o coletor (usa session.json por padrao)
        collector = ForensicCollector()
        
        # Tenta pegar informações do próprio perfil logado para testar
        me = collector.client.account_info()
        print(f"✅ Conexao estabelecida com sucesso!")
        print(f"👤 Usuario logado: @{me.username}")
        print(f"📝 Nome: {me.full_name}")
        
        # Teste de busca simples (perfil do Instagram oficial)
        print("🔍 Testando busca de perfil publico (instagram)...")
        insta_id = collector.client.user_id_from_username("instagram")
        print(f"✅ Busca concluida! ID do Instagram: {insta_id}")
        
        print("\n🏆 TESTE DE COLETOR PASSOU!")
        
    except Exception as e:
        print(f"\n❌ FALHA NO TESTE: {e}")
        if "login_required" in str(e).lower():
            print("⚠️ Sugestao: A sessao expirou. Delete o session.json e rode novamente para novo login.")

if __name__ == "__main__":
    test_login()
