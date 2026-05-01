# 🛡️ PERSISTÊNCIA TÉCNICA E GOVERNANÇA (MCP) - SENTINELA

Este documento serve como a "Memória Técnica" do projeto, garantindo que qualquer agente mantenha a integridade arquitetural v19.8.

## 🏗️ ARQUITETURA DIAMOND UNIFICADA (v19.8.0)
1. **Coleta**: `sentinela_scraper/` (Nativo Scrapy) e `core/instaloader_scraper.py`.
2. **Nuvem**: `Supabase` centralizado via `core/db.py` (Async DatabaseClient).
3. **Cérebro**: `orquestrador.py` coordena o ciclo completo de forma assíncrona.
4. **Motores (Folder: /processing)**:
   - `text_processor.py`: Limpeza e Lematização Forense.
   - `data_miner.py`: Clustering KMeans e Z-Score (Picos de Ódio).
   - `report_generator.py`: PDF FPDF2 com suporte nativo a UTF-8.
5. **Inteligência Híbrida**: `core/ai_service.py` unifica Gemini 2.0, Groq e Ollama (Qwen 2.5) com fallback automático.

## 📜 REGRAS INVIOLÁVEIS (GOVERNANÇA)
- **Código Integral**: Proibido omitir partes de código (`//...`). Entregar sempre o arquivo completo.
- **Protocolo PASA v16.4**: Classificação de ódio via `AIService` seguindo o `forensic-discourse-analysis/SKILL.md`.
- **Segurança Admin**: Acesso a `addalvo.html` protegido por TOTP.
- **Linguagem**: Comunicação estritamente em Português (Brasil), técnica e direta.
- **Async First**: Priorizar operações assíncronas para Banco de Dados e IA.

## 📡 CONFIGURAÇÕES DE PERSISTÊNCIA (MCP)
- **Scope**: `project`
- **Key Facts**: Arquitetura unificada Diamond, AI Fallback, Async DatabaseClient.
- **Trigger**: Sempre ler este arquivo ou `ROADMAP.md` ao iniciar nova sessão.
