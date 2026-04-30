# PROTOCOLO DE ENGENHARIA - SENTINELA DEMOCRÁTICA

Este arquivo contém as regras imutáveis de desenvolvimento e gestão de memória técnica do projeto.

## 🧠 GESTÃO DE MEMÓRIA (Protocolo Diamond)

1.  **Leitura Obrigatória:** Antes de propor qualquer código ou mudança, leia os arquivos `STATE.md`, `ROADMAP.md` e o histórico recente do Git (`git log --oneline -5`).
2.  **Externalização de Estado:** Após cada mudança bem-sucedida, atualize o arquivo `STATE.md` com o novo estado funcional e quaisquer abordagens descartadas.
3.  **Anti-Regressão:** É terminantemente proibido sugerir tecnologias, padrões ou arquiteturas listadas como "DESCARTADAS" no `STATE.md`.
4.  **Commits Obsessivos:** Cada tarefa concluída e validada deve ser commitada imediatamente. Use mensagens de commit descritivas.
5.  **Estados Finitos:** Divida tarefas complexas em passos mínimos e exija confirmação de sucesso (ex: teste passando) antes de avançar para o próximo arquivo/serviço.

## 🛠 DIRETRIZES TÉCNICAS

- **Arquitetura:** Frontend (SPA) -> API Proxy (FastAPI) -> Banco de Dados (Supabase).
- **Segurança:** NUNCA exponha chaves de API ou segredos no frontend. Use o Proxy FastAPI para todas as requisições autenticadas.
- **Dados:** Prefira Views Materializadas e tabelas de métricas pré-computadas (`metricas_diarias`) para performance de dashboard.
- **PASA:** Todas as classificações de ódio devem seguir rigorosamente o Protocolo PASA v16.4 definido em `forensic-discourse-analysis/SKILL.md`.

## 🔄 FLUXO DE TRABALHO

1. `Pesquisar` (STATE.md + Git) -> 2. `Propor Plano` (Bite-sized) -> 3. `Executar` (Passo a passo) -> 4. `Validar` (Teste real) -> 5. `Documentar` (Update STATE.md) -> 6. `Commit`.

## 🤖 INTEGRAÇÃO DE IA

- **Local:** O modelo padrão para processamento local é o `qwen2.5:3b`.
- **Híbrido:** Para alternar entre o processamento local (Ollama) e nuvem (Gemini), utilize a variável `IA_PROVIDER` no seu arquivo `.env`.
- **Credenciais Gemini:** Certifique-se de que sua `GEMINI_API_KEY` está configurada no arquivo `.env` para habilitar as funções de nuvem.

