# 🚨 ORIENTAÇÕES INICIAIS — SENTINELA DEMOCRÁTICA

> **ATENÇÃO:** Este documento é o protocolo obrigatório de inicialização. Toda sessão de desenvolvimento, auditoria ou manutenção deve seguir estas diretrizes sem exceção.

---

## 📜 REGRAS DE ENGAJO

### 1. 🇧🇷 Idioma Exclusivo
- Comunique-se **exclusivamente em Português do Brasil**.
- Code comments, commit messages, logs e documentação devem ser redigidos em pt-BR (exceto termos técnicos padrão da stack).
- Nenhuma interação com o operador deve ocorrer em outro idioma.

### 2. 🗺️ Consciência Situacional (Roadmap & State)
- Antes de escrever **qualquer linha de código**, leia obrigatoriamente o `ROADMAP.md` e o `STATE.md`.
- Verifique a fase atual do projeto, o status dos workers e as pendências de dados.
- Só defina prioridades e execute tarefas após mapear o estado atual do ecossistema.

### 3. 🏗️ Persistência Técnica e Documentação
- Código sem documentação é dívida técnica. Documentação sem persistência é trabalho perdido.
- Toda nova funcionalidade, correção de bug ou alteração arquitetural **deve** ser refletida nos arquivos de estado (`STATE.md`, `ROADMAP.md`, `SYSTEM_CONTEXT.md`).
- Nenhum conhecimento fica apenas no terminal. Se resolveu um problema, registre o procedimento.

### 4. 🚀 Commit e Deploy é Lei
- Nada existe apenas na sua máquina local. Tudo que for executado, testado e validado **deve ser comitado e deployado**.
- Commits devem ser atômicos e descritivos (Conventional Commits em pt-BR).
- Após mudanças críticas no backend ou frontend, o deploy para Vercel/Supabase deve ser executado imediatamente.
- *Entrega contínua não é opcional, é a regra.*

---

## 🧭 PILARES DO PROJETO (Inegociáveis)

### 5. 🌐 Validação no Frontend é Online (Prioridade Vercel)
- Testes de interface e dashboard são feitos **exclusivamente online**. O Vercel é o ambiente de validação real.
- Não perca tempo configurando ambientes de frontend locais. Faça o deploy e valide em produção.
- O fluxo é: Codifica -> Commit -> Vercel Build -> Valida no ar.

### 6. 🧪 Teste Sempre, Teste Tudo
- Tudo precisa ser testado. Nenhum componente, worker ou rota entra em produção sem validação funcional.
- Se uma raspagem falhou, teste o fallback. Se a IA retornou erro, teste o limite de taxa.
- Testes não são a última etapa, são parte do ciclo de desenvolvimento.

### 7. 🗂️ Organização é Disciplina
- Tudo precisa ser organizado. Diretórios, imports, variáveis de ambiente e funções devem ter um lugar lógico e único.
- Siga a topologia definida no `SYSTEM_CONTEXT.md`: `/core` para serviços, `/workers` para daemons, `/scripts` para CLI, `/api` para Vercel.
- Se um arquivo não sabe onde mora, o sistema inteiro perde o sentido.

### 8. 🔍 Rastreabilidade Total (Tudo é Auditável)
- Tudo precisa ser auditável. Nenhuma decisão da IA, nenhuma raspagem, nenhum alerta pode ser uma "caixa preta".
- Logs devem ter contexto (quem, quando, qual alvo, qual motor). 
- A auditoria cruzada (`AuditWorker`, Drift Check) existe para garantir que o sistema preste contas do que faz. Se não pode ser auditado, não pertence ao sistema.

### 9. 🩸 Dados Reais ou Nada (Zero Mocks)
- Tudo precisa ser real. O Sentinela não opera com simulações, dados fictícios ou endpoints mockados.
- Se a API do Instagram bloquear, o sistema deve lidar com o bloqueio real, não fingir que coletou.
- Se o Supabase estiver vazio, o dashboard deve mostrar vazio, não dados de teste. Realidade, por mais dura que seja, é sempre preferível à ilusão.
- **Protocolo de Simulação (Exceção Controlada):** Caso seja estritamente necessário simular um dado (para teste de UI, validação de fluxo ou debug), utilize **frases absurdas e marcadores explícitos** como `[teste]` ou `[simulação]`. Exemplo: `"O candidato come tijolos no café da manhã [simulação]"`. Isso garante que ninguém, em nenhuma hipótese, confunda o dado fictício com um fato real, protegendo a integridade da análise e a reputação do sistema.

---

## 🛡️ BOAS PRÁTICAS DE DESENVOLVIMENTO

### 10. 🔒 Segurança e Credenciais
- **Nenhum segredo no código:** API Keys (Zyte, Gemini, Groq), SessionIDs ou senhas devem vir **obrigatoriamente** de variáveis de ambiente (`.env`). Arquivos `.env` nunca são comitados.
- **Proteção de Sessão:** Cookies de scraping do Instagram são ativos de alto valor. Sempre use rotação e marque como `paused_auth_fail` no Supabase ao detectar bloqueios.
- **Privacidade:** Dados de autores de comentários são sensíveis. Siga a LGPD e o MCA (Manual de Classificação Analítica) — armazene apenas o estritamente necessário para análise forense.

### 11. 🕸️ Resiliência no Scraping e Assincronicidade
- **Anti-Ban é prioridade:** Sempre implemente delays humanos aleatórios (`asyncio.sleep(random)`) entre requests e navegação de modais. Scrape rápido = IP banido.
- **Fallback obrigatório:** Se a Zyte falhar, o Playwright assume. Se o Playwright falhar, registre o erro e não quebre o loop principal. O sistema deve ser tolerante a falhas parciais.
- **O Python `asyncio` não é opcional:** As operações de IO (Supabase, APIs externas, Playwright) são assíncronas por natureza. Nunca bloqueie o event loop com chamadas síncronas longas. Se precisar integrar código síncrono legado, use `asyncio.to_thread()`.

### 12. 🐘 Banco de Dados (Supabase)
- **Fonte da Verdade:** O Supabase é a única fonte da verdade. SQLite local é apenas cache temporário de processamento.
- **Use o Service Core:** Toda comunicação com o banco passa por `core/supabase_service.py`. Não crie clientes soltos.
- **Upsert ao invés de Insert:** Para evitar duplicatas em raspagens repetidas, prefira `upsert` com conflitos resolvidos na chave primária (ex: `id` do comentário ou `username` do candidato).
- **Respeite o Cooldown:** O campo `last_scraped_at` e a lógica de Cooldown existem para proteger a cota de API e a saúde do sistema. Nunca force re-raspagens fora do tempo de descanso.

### 13. 🧠 Inteligência Artificial e Perícia
- **Cuidado com Alucinações:** Modelos LLM alucinam. Toda classificação de ódio deve passar pelo `AuditWorker` e cruzamento com o modelo local (Groq/Ollama) para verificar discrepâncias.
- **Termos Forenses:** Ao gerar relatórios, use a terminologia exata do `PADRONIZACAO_LINGUISTICA_FORENSE.md` (ex: "Indícios Analíticos", nunca "Provas"). A precisão semântica protege o projeto juridicamente.
- **Garbage In, Garbage Out:** O Quality Gate v2 existe para filtrar lixo de UI do scraper (botões, placeholders). Comentários com menos de 3 caracteres ou padrões de DOM devem ser descartados antes de irem para a IA.

### 14. 🧹 Código Limpo e Manutenibilidade
- **Tipagem:** Use Type Hints (`typing`) em todas as funções e métodos. Ajuda na leitura e previne erros em runtime.
- **Logs Estruturados:** O `WarRoomUI` e os logs em arquivo dependem de mensagens claras. Use os níveis corretos (`INFO`, `WARNING`, `ERROR`) e prefixos contextuais (ex: `[Zyte]`, `[Playwright]`).
- **Sem código morto:** Se um worker legado está OFF e sem previsão de uso, não o mantenha no fluxo principal. Arquive ou delete. Código não utilizado é passivo de bugs ocultos.

### 15. 🧠 Memória de Estado (Checkpointing)
- **Workers com memória:** Todo worker de longo curso ou processamento em lote **deve** utilizar a classe `WorkerState` (`core/state_manager.py`).
- **Proteção contra OOM:** Se um processo morre por falta de memória, o sistema deve ser capaz de retomar de onde parou na reinicialização, sem retrabalho.
- **Auto-Proteção:** Se um alvo específico causou a queda (OOM), o sistema deve marcá-lo e pulá-lo no próximo ciclo para evitar loops de crash infinitos.
- **Nunca escreva estado sem atomicidade:** Em caso de crash durante o salvamento do arquivo, o estado anterior deve permanecer intacto (uso de arquivos `.tmp` + `os.replace`).

---

**Status do Sistema:** 🟢 OPERACIONAL
**Protocolo:** PASA v49.9
**Assinatura:** Sentinela Democrática — Nó Local
