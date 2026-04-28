## Fluxo de Processamento v16.3 (Forensic Edition)

1. **Extração**: `elite_collector.py` captura comentário + autor_username + post_id.
2. **Classificação Local**: `ollama_intelligence.py` rotula a evidência (ex: INSULTO_AD_HOMINEM).
3. **Persistência Híbrida**: Dados brutos em SQLite e vereditos periciais em Supabase Cloud.
4. **Enriquecimento UI**: 
   - O motor `ui.js` realiza o cruzamento de `candidato_id` com o `state.data` para exibir o nome do alvo.
   - Gera badges dinâmicos baseados no risco identificado pela IA.
   - Exibe a trilha: [Autor] atacou [Alvo] na [Postagem].