# Design Spec: Módulo de Inteligência de Redes

**Data:** 2026-05-01  
**Status:** Aguardando Aprovação  
**Versão:** 1.0

## 1. Visão Geral
Implementação de um motor de detecção de comportamentos coordenados e visualização de redes de ataque para o Sentinela Democrática. O objetivo é identificar "tropas de choque" ou grupos que agem de forma sincronizada contra alvos específicos.

## 2. Requisitos de Negócio
- Identificar autores que atacam o mesmo alvo em janelas de tempo próximas.
- Visualizar a estrutura das redes de ataque (quem ataca quem).
- Alternar entre diferentes perspectivas de análise (Grafos, Timeline, Heatmap).
- Navegação integrada ao menu lateral existente.

## 3. Arquitetura Técnica

### A. Backend (FastAPI Proxy)
- **Novo Endpoint:** `GET /api/v1/networks`
- **Parâmetros:** `days` (padrão 7), `min_coordination` (padrão 2 ataques em comum).
- **Lógica de Processamento:**
    1. Buscar comentários marcados como `is_hate=True`.
    2. Agrupar por `autor_username`.
    3. Criar arestas entre autores que compartilham o mesmo `candidato_id` ou `post_id`.
    4. Calcular o "Peso da Conexão" baseado na proximidade temporal (`data_publicacao`).
- **Retorno JSON:**
    ```json
    {
      "nodes": [ { "id": "autor1", "type": "author", "val": 10 }, { "id": "candidatoA", "type": "target" } ],
      "links": [ { "source": "autor1", "target": "candidatoA", "weight": 5 } ],
      "coordinated_bursts": [ { "time_window": "2026-05-01 10:00", "authors": [...], "target": "..." } ]
    }
    ```

### B. Frontend (Vanilla JS)
- **Estado (`state.js`):** Adicionar `networkView` e `networkData`.
- **Navegação (`index.html` & `ui.js`):**
    - Transformar o item "Inteligência de Redes" em um sub-menu:
        - Cluster de Ataque (Grafos)
        - Fluxo Coordenado (Timeline)
        - Matriz de Colusão (Heatmap)
- **Componentes de Visualização:**
    - **Grafo:** Implementação usando `d3-force` (via CDN) para renderização em `<canvas>` (performance).
    - **Timeline:** Tabela cronológica com agrupamento visual de ataques simultâneos.
    - **Heatmap:** Grid CSS com cores dinâmicas representando a intensidade autor-vs-alvo.

## 4. Plano de Testes
- **Unitário:** Validar algoritmo de agrupamento em `api/index.py`.
- **Integração:** Verificar tempo de resposta da API com >1000 conexões.
- **E2E (Playwright):** Garantir que a troca de abas no sub-menu renderiza os componentes corretos.

## 5. Próximos Passos
1. Atualizar `api/index.py` com o endpoint `/networks`.
2. Modificar a estrutura do menu lateral em `index.html`.
3. Implementar os renderizadores em `ui.js`.
