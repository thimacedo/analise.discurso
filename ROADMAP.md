# ROADMAP - Sentinela DemocrÃ¡tica

## Status: v16.3.2 (Auth Secured)
- **Segurança**: Autenticação TOTP (Google Authenticator) implementada em `addalvo.html`.
- **Sessão**: Tokens HMAC com expiração de 2 horas.
- **IA**: Ollama (Qwen 2.5 Coder) local com suporte a categorias PASA detalhadas.
- **Trilha de EvidÃªncias**: Cards de alerta agora mapeiam Autor -> Alvo -> Postagem Original.
- **UX**: Design tÃ¡tico com badges de risco e badges de categoria (ex: INSULTO AD HOMINEM).
- **Dados**: Malha de 242 alvos monitorados com sincronizaÃ§Ã£o real-time de vereditos.

## HistÃ³rico de VersÃµes
- **v16.3.0**: ImplementaÃ§Ã£o de Forensic Cards e Mapeamento de Autor/Alvo.
- **v16.2.0**: Real-time Sync (60s) e Dashboard Diamond Premium.
- **v16.0.0**: MigraÃ§Ã£o para Arquitetura HÃ­brida (Ollama PortÃ¡til).

## Infraestrutura Atual
- **Local Host**: E:\projetos\ollama_bin\ollama.exe
- **Cloud Sync**: Supabase (Tabela: comentarios, is_hate=true).
- **Dashboard**: https://sentinela-democratica-ruby.vercel.app

- [x] Conclusão da Padronização Linguística Forense (Manual Técnico + Adendo Profundo).

- [x] Integração da Metodologia Vichi (N-Gramas) para detecção de coordenação.

- [x] Ativação dos Servidores (Ollama, FastAPI) e Workers (Elite, Intel).


## [2026-04-28] - Manutenção de Rotina
- Validação de integridade do ambiente v16.3.2.
- Sincronização de evidências confirmada.
