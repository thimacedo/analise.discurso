# PROTOCOLO DE ENGENHARIA - SENTINELA DEMOCRÁTICA

## 🆔 IDENTIDADE E ESCOPO
1. Diretório Raiz: O único caminho válido é .
2. Isolamento: Este projeto é independente. Sem scripts externos.
3. Verificação: Confirme o PWD antes de operações de arquivo/shell.

## 🧠 GESTÃO DE MEMÓRIA (Protocolo Diamond)
1. Leitura Obrigatória: Sempre leia STATE.md e ROADMAP.md antes de formalmente propor mudanças.
2. Externalização: Atualize STATE.md após mudanças bem-sucedidas.
3. Anti-Regressão: Proibido usar abordagens listadas como "DESCARTADAS" no STATE.md.
4. Commits Obsessivos: Commits detalhados (Conventional Commits) após cada tarefa validada. Sem acumular.
5. Estados Finitos: Divida tarefas em passos mínimos e valide cada um.

## 🛠 DIRETRIZES TÉCNICAS (PASA v46+)
- Arquitetura Real: 
  - Frontend: Vanilla JS + Supabase Client (Leitura) + Git JSON Sync.
  - Backend Local: Python (local_server.py) com Watchdog Guardião.
  - Banco: Supabase (Fonte da Verdade).
- Segurança: Chaves do Supabase ANON_KEY são usadas no frontend para leitura; SERVICE_KEY apenas no backend local.
- Proteção Jurídica: NUNCA use termos como "forense", "prova", "evidência". Use "informação", "indício", "análise analítica".
- Classificação: Seguir ESTRITAMENTE o MCA v2.2 em `docs/analytical/MANUAL_CLASSIFICACAO_ANALITICA_v2.md`.

## 🔄 FLUXO DE TRABALHO
1. Pesquisar (STATE.md + Git) -> 2. Propor Plano -> 3. Executar -> 4. Validar -> 5. Documentar -> 6. Commit.

## 🤖 INTEGRAÇÃO DE IA
- Classificação Primária: Gemini 1.5 Flash (google-genai SDK).
- Auditoria Cruzada: Groq (Llama 3).
- Metodologia: MSAL (Metodologia Sentinela de Análise Léxica) + Framework CCF.
