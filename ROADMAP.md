# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma Independente de **Inteligência Situacional e Análise Forense**. O sistema utiliza o **Protocolo PASA v15.14** para monitoramento de crimes digitais e hostilidade política via Llama 3.1 e ScrapeGraphAI.

## 🚀 Status Atual: v15.14.0 (Resiliência Consolidada)
- [x] **Unificação de Projeto**: Resolvido o conflito entre múltiplos projetos Vercel sob o ID `prj_hbfDAwwIfrz6nJgIkZWLNacCWpeq`.
- [x] **Bypass de Automação**: Configurado segredo de elite para auditoria e testes de produção.
- [x] **Build Destravado**: Corrigido erro de BOM no `requirements.txt` e simplificação do backend FastAPI.
- [x] **Recuperação de Inteligência**: Motor de **Tendências Preditivas** e **Saúde do Sistema** restaurados.
- [x] **Painel de Controle v2**: Novo sistema de cadastro de alvos com e-mail de contato e auditoria rápida.

## 🛠️ Próximos Passos (Prioridade Máxima)
1. [!] **Sincronização de Schema**: Executar migração SQL para adicionar `classificacao_pasa` à tabela `comentarios`.
2. [ ] **Alimentação em Lote**: Ativar o script `tools/coletor_sgai.py` para popular alvos com 0 comentários.
3. [ ] **Dossiê em PDF**: Implementar geração de evidências forenses para uso jurídico.

## 🔒 Protocolo de Estabilidade (Persistência)
- **Estrutura**: Raiz plana para HTML (Estáticos Vercel), pasta `api/` exclusiva para Python (Funções Serverless).
- **Dados**: Uso obrigatório de cache-buster (`?t=ts`) em todas as chamadas de API do frontend.
- **Segurança**: Nunca comitar segredos. Usar bypass oficial para automação.

---
**Atualização Final:** 26/04/2026 | **Versão:** 15.14.0-stable
