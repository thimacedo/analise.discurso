# 🚀 Plano de Raspagem Massiva: Sentinela v15

Este plano visa complementar o corpus do projeto Sentinela Democrática, preenchendo as lacunas identificadas na análise de 24/04/2026.

## 📊 Resumo do Gap Analysis
- **Total de Perfis Monitorados:** 135
- **Ausentes no Banco (Zero Dados):** 42
- **Baixo Volume (<5 posts):** 93
- **Necessidade:** Coleta imediata para todos os 135 perfis.

## 🛠️ Estratégia de Coleta (Apify)
Utilizaremos o `apify/instagram-scraper` para uma coleta profunda.

### Configuração da Tarefa:
- **Actor:** `apify/instagram-scraper`
- **Targets:** Lista completa de 135 usernames.
- **Profundidade:** 
    - **Posts por Perfil:** 20 (últimos 20 posts para capturar o clima atual).
    - **Comentários por Post:** 100 (para análise PASA de sarcasmo e agressividade).
- **Estimativa de Dados:** ~2.700 posts e até 270.000 comentários.

## 📂 Classificação de Cenários (IA)
Os perfis foram pré-classificados para priorização:
- **Nacional (96):** Figuras de alto escalão (Lula, Bolsonaro, Ministros).
- **Estadual (19):** Foco em Rio Grande do Norte (Fátima Bezerra, etc).
- **Municipal (19):** Foco em Parnamirim/Natal (Vereadores locais).
- **Mídia/Informativo (1):** Blogs de notícias.

## 📅 Cronograma de Execução
1. **Lote 1 (Municipal & Estadual):** 38 perfis (Alta prioridade local).
2. **Lote 2 (Nacional - Parte 1):** 48 perfis.
3. **Lote 3 (Nacional - Parte 2):** 48 perfis + Blogs.

## 🚀 Comando para Iniciar Lote 1
```json
// Executar via mcp_apify_call-actor
{
  "actor": "apify/instagram-scraper",
  "input": {
    "directUrls": ["https://www.instagram.com/vereadoriraniguedes/", "...batch_urls..."],
    "resultsLimit": 20,
    "resultsType": "posts",
    "searchLimit": 1,
    "addParentData": true
  }
}
```

---
*Planejado em 24/04/2026 pelo Gemini Arquiteto*
