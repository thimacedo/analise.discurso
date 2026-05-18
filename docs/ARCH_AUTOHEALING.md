# 🧠 DOCUMENTAÇÃO: AUTOCURA PROFUNDA (v50)

O sistema Sentinela Democrática v50 implementa uma arquitetura de **Autonomia Biológica**, onde cada componente é capaz de diagnosticar e tratar seus próprios sintomas antes de escalar uma falha para o nível superior.

---

## 🛡️ Camadas de Autocura

### 1. Nível de Infraestrutura (Watchdog)
*   **Médico de Plantão**: Analisa o `stderr` do servidor para diferenciar falhas.
*   **Gestão de OOM**: Interrompe o sistema e envia alerta fatal se a RAM esgotar.
*   **Cura de Dependências**: Executa `pip install` e limpa cache se detectar `ImportError`.
*   **Anti-Spam Categorizado**: Bloqueia alertas repetitivos no WhatsApp com cooldowns inteligentes.

### 2. Nível de Coleta (Instagram Workers)
*   **Regeneração de Navegador**: O motor Playwright (`scraper_headless.py`) reinicia o Chrome internamente se o grid vier vazio ou houver crash de processo.
*   **Rotação de Sessão**: Se o Worker detectar um *Login Wall*, ele invalida o cookie atual no Supabase e recruta uma nova sessão ativa automaticamente.
*   **Resiliência DB**: Inserção de dados com 3 retentativas e backoff exponencial.

### 3. Nível de Inteligência (AI Service)
*   **Cascata Cloud (Circuit Breaker)**: Ordem de execução `Groq -> Mistral -> OpenRouter`.
*   **Isolamento Local**: 100% cloud-only para evitar Out of Memory (OOM) no servidor local.

---

## 📊 Verificação de Persistência (Protocolo Diamond)

O sistema utiliza a tabela `worker_runs` como fonte de verdade para a saúde operacional:

1.  **Sucesso Honesto**: O worker só reporta `success=True` se persistir dados ou validar que não há novos itens.
2.  **Rastreabilidade de Erros**: O campo `error_details` no Supabase armazena o diagnóstico capturado pela autocura.
3.  **Idempotência**: Todos os `upserts` utilizam IDs determinísticos (UUID v5) para evitar duplicidade de comentários.

---

## 🚀 Como Testar a Autonomia

Para disparar um teste de validação manual:
```powershell
python run_worker.py --target lulaoficial --force
```

Monitore o comportamento em tempo real em: `http://localhost:8000`
