# Design Specification: Otimização de Ingestão e IA (PASA)

## Contexto e Objetivo
Baseado no PRD "Enhance Data Ingestion and Analysis Capabilities", o foco é otimizar a velocidade de ingestão de dados do Instagram em 25%, aplicar validação/limpeza prévia à análise e melhorar a precisão da IA (discurso de ódio) adicionando escores de confiança e extração de evidências, utilizando os modelos atuais (Gemini/Llama).

## Arquitetura e Decisões
Foi escolhida a abordagem de **Otimização In-Place**, visando resultados rápidos com baixo risco para a infraestrutura atual.

### 1. Coleta e Validação (InstagramWorker)
- **Validação Embutida:** A limpeza de dados (remoção de emojis excessivos, caracteres invisíveis, normalização de strings) será integrada diretamente no fluxo do `InstagramWorker` antes do envio ao Supabase. Dados inócuos ou ruídos (como comentários vazios após a limpeza) serão descartados prematuramente na origem para economizar I/O e uso de banco de dados.
- **Otimização de Performance (Meta: +25% de velocidade):** Redução de dead-times (esperas fixas longas) na raspagem (como no loop do `local_server.py` ou chamadas subjacentes do `scraper_headless.py`). O `SCRAPE_PAUSE` e as operações de I/O em banco serão analisados para remoção de gargalos sem violar os gatilhos de shadowban do proxy/Instagram.

### 2. Banco de Dados (Supabase)
Será necessária uma alteração de schema na tabela `comentarios` para comportar a nova estrutura analítica:
- **Nova coluna:** `confidence_score` (INT, 0-100).
- **Nova coluna:** `evidence_extracted` (TEXT, armazena o trecho que levou à classificação do risco).

### 3. Inteligência Artificial (Detecção Aprimorada)
- **Prompt Dinâmico e Output Estruturado:** O processo no script `mass_classify.py` será atualizado para exigir uma resposta JSON estruturada das APIs do Gemini/Llama (usando `response_mime_type="application/json"` ou Pydantic nas configurações). 
- O payload de retorno conterá obrigatoriamente as chaves:
  - `is_hate` (Boolean)
  - `categoria_ia` (String referenciando as categorias PASA v49)
  - `confidence_score` (Int)
  - `evidence_extracted` (String)

## Tratamento de Falhas (Error Handling)
- Caso a IA falhe em retornar o JSON validado (fallback), o sistema assumirá `confidence_score=0`, mantendo o `is_hate=False` e gravando um log de falha de parser na coluna `evidence_extracted`, para posterior acionamento da rotina de auditoria.
- Erros de normalização de strings e unicode corrompido no `InstagramWorker` serão resolvidos capturando a exceção e marcando o comentário para descarte (skip).

## Limites (Scope)
- A otimização foca estritamente no fluxo do Instagram e na infraestrutura atual.
- Nenhum modelo LLM local (Ollama) ou infraestrutura dedicada será introduzido nesta etapa.