# 📋 Mapeamento de Workers: Sentinela Democrática

Este documento audita o status operacional, funcionalidade e necessidade de refatoração de todos os workers e componentes de processamento em background do sistema.

**Diretório Oficial:** `app/workers/` (Unificado em PASA v49.9)

---

## 🛠️ Workers de Coleta e Scraping

| Worker | Status | Função | Protocolo |
| :--- | :--- | :--- | :--- |
| `InstagramWorker` | 🟢 Ativo (Core) | Orquestrador principal (Zyte -> Playwright fallback). Imports resilientes. | Quality Gate Integrado |
| `InstagramScraperZyte` | 🟢 Ativo | Motor primário via API Zyte. | Retorna dados reais ou falha. |
| `InstagramScraperHeadless` | 🟢 Ativo | Motor fallback via Playwright com injeção de sessão e roleta ponderada. | Retorna dados reais ou falha. |
| `InstagramScrapyWorker` | 🟡 Standby | Arquitetura Scrapy para volumes massivos. | Mantido OFF até demanda de escala. |

## ⚙️ Workers de Processamento e Auditoria

| Worker | Status | Função | Protocolo |
| :--- | :--- | :--- | :--- |
| `quality_gate.py` | 🟢 Ativo | Filtragem obrigatória de lixo de UI e dados inválidos (Garbage In, Garbage Out). | Executado antes do Supabase |
| `audit_worker.py` | 🟢 Ativo | Auditoria cruzada anti-alucinação e verificação forense. | Consome dados do Supabase |

## 🏗️ Orquestradores e Daemonização

| Worker | Status | Função | Protocolo |
| :--- | :--- | :--- | :--- |
| `local_server.py` | 🟢 Ativo (Master) | Nó principal. Ciclo de raspagem, IA em batch, profiling e Git Sync. | Cooldown 12h, Roleta Ponderada |
| `watchdog.py` | 🟢 Ativo (Guardian) | Monitoramento, auto-cura inteligente, alertas WhatsApp com anti-spam. | Classifica erros (Code vs Runtime) |
| `main_orchestrator.py` | 🟡 Auditando | Orquestração legada. Avaliar se lógica foi absorvida por `local_server.py`. | - |
| `orchestrator_long_run.py` | 🟡 Auditando | Processos longos. Avaliar necessidade vs `local_server.py`. | - |
| `schedule_long_scrape.py` | 🟡 Auditando | Agendamento. Avaliar necessidade vs cooldown do `local_server.py`. | - |

---

## 📊 Registros de Ações (PASA v49.9)

### 1. Desduplicação de Caminhos ✅
* **Ação Executada:** Diretório `workers/` removido. Todos os workers migrados para `app/workers/`.
* **Impacto:** Imports unificados, fim de conflitos de módulos.

### 2. Higiene de Código ✅
* **Ação Executada:** `official_solenya_daemon.py` removido. `InstagramWorker` duplicado removido.
* **Impacto:** Base de código limpa, sem mocks ou fantasmas.

### 3. Integração de Auditoria ✅
* **Ação Executada:** `InstagramWorker._save_posts` agora chama `quality_gate.filter_comment()` antes de qualquer inserção no Supabase.
* **Impacto:** Garantia de "Dados Reais ou Nada", sem lixo de UI no banco.

### 4. Sincronização com Protocolo ✅
* **Ação Executada:** Políticas de dados simulados com marcadores `[teste]`/`[simulação]` formalizadas nas Orientações Iniciais.
* **Impacto:** Rastreabilidade total da origem dos dados.

---

**Status da Auditoria:** ✅ CONCLUÍDA
**Próximo Passo:** Avaliar se os orquestradores legados (`main_orchestrator`, etc.) devem ser deletados ou se possuem lógica de negócio não presente no `local_server.py`.
