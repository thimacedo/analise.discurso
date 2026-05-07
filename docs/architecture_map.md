# 🏛️ Mapa Arquitetural - Sentinela Democrática

Este documento mapeia a arquitetura, o fluxo de dados e os principais componentes do sistema Sentinela Democrática.

## 🔄 Fluxo de Dados (Pipeline)

A plataforma opera através de um pipeline assíncrono rigoroso:

1. **Scraper (Coleta)**: Módulo `sentinela_scraper/instagram.py` - Coleta bruta do Instagram.
2. **Armazenamento Inicial**: Supabase (Tabela `comentarios`).
3. **Processamento**: `processing/text_processor.py` - Limpeza e lematização.
4. **Classificação PASA**: `AIService` - Motor de IA PASA v16.4 (Qwen 2.5) avalia comentários para ódio, político, neutro, etc.
5. **Mineração**: `DataMiner` (`processing/data_miner.py`) - Clusterização (KMeans) e alertas de redes coordenadas.
6. **Interface / API**: Endpoint `api/index.py` e Dashboard Web.

## 🧩 Componentes Principais

- **Frontend / UI**: Dashboard interativo.
- **Backend / API**: Proxy FastAPI para todas as conexões seguras.
- **Banco de Dados**: Supabase (RLS ativado v25.0).
- **Notificações**: Firebase + Supabase (Tempo Real).
- **Workers**: Scripts em `processing/` que rodam em ciclo contínuo.

## 📐 Padrões de Código

- **Isolamento de Estado**: Alterações de arquitetura documentadas em `STATE.md`.
- **Commits Locais**: Mensagens descritivas baseadas no Conventional Commits.
- **Tolerância a Falhas**: Operações de BD devem ser idempotentes (UPSERTS) para prevenir duplicatas.
- **Classificação Estrita**: Toda avaliação de discurso DEVE passar pelo protocolo PASA.