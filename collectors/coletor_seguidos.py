import json
import os
from instagram_collector import ForensicCollector

def scrape_following_safe():
    print("🚀 Iniciando raspagem SEGURA de perfis seguidos...")
    try:
        collector = ForensicCollector()
        
        # Pega o ID do próprio usuário logado (@monitoramento.discurso)
        user_id = collector.client.user_id
        print(f"🔍 Coletando perfis seguidos por ID: {user_id}...")
        
        # Raspagem de alta velocidade: Pega todos os seguidos em uma única chamada de sistema (sem API externa paga)
        following = collector.client.user_following(user_id)
        
        following_list = []
        for pk, user in following.items():
            following_list.append({
                "pk": user.pk,
                "username": user.username,
                "full_name": user.full_name,
                "is_private": user.is_private
            })
            
        # Salva em JSON para uso futuro (Diminui acessos à API no futuro)
        output_file = "perfis_monitorados.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(following_list, f, indent=4, ensure_ascii=False)
            
        print(f"✅ SUCESSO! {len(following_list)} perfis mapeados e smonitorados em '{output_file}'.")
        print("💡 ESTRATÉGIA: Agora o seu pipeline pode ler este arquivo JSON em vez de buscar IDs via API a cada execução.")
        
    except Exception as e:
        print(f"❌ ERRO NA RASPAGEM: {e}")

if __name__ == "__main__":
    scrape_following_safe()
