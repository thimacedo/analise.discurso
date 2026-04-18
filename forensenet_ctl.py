import sys
import argparse
from sync_intelligence import sync_monitoring_flow
from full_apify_scraper import ApifyFullScraper
from cloud_classifier import run_cloud_classification

def main():
    parser = argparse.ArgumentParser(description="ForenseNet v3.0 - CLI de Controle")
    parser.add_argument('--mode', choices=['full', 'sync', 'scrape', 'classify'], help="Modo de operação")
    parser.add_argument('--profile', type=str, help="Username de um perfil específico para raspar")
    
    args = parser.parse_args()

    if args.mode == 'sync' or args.mode == 'full':
        print("🔄 Executando Sincronização de Perfis...")
        sync_monitoring_flow()

    if args.mode == 'scrape' or args.mode == 'full':
        scraper = ApifyFullScraper()
        if args.profile:
            print(f"🎯 Raspagem Direta: @{args.profile}")
            scraper.run_full_scrape(limit_profiles=None, targets=[{"username": args.profile}])
        else:
            print("🚀 Executando Raspagem Full de Perfis Ativos...")
            scraper.run_full_scrape()

    if args.mode == 'classify' or args.mode == 'full':
        print("🧠 Iniciando Classificação IA...")
        run_cloud_classification()

    if not args.mode:
        parser.print_help()

if __name__ == "__main__":
    main()
