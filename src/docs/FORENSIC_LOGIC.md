# ⚖️ Lógica Forense e Processamento de Dados (Sentinela)

Este documento organiza os algoritmos e a lógica de processamento extraída do repositório de Linguística Forense (UFRN/Vichi) para integração no motor Sentinela.

## 🛠️ 1. Scripts e Algoritmos de Referência

### A. Extração de Termos (Words & POS Tagging)
Focado em extrair as categorias gramaticais mais relevantes para análise de intenção:
*   **Verbos:** Indicam ação e comando (ex: "voten", "ataquem", "defendam").
*   **Substantivos:** Identificam os alvos e tópicos centrais das narrativas.
*   **Adjetivos:** Medem a temperatura emocional e a polarização (pejorativos vs. laudatórios).

### B. Análise de N-Gramas (Sequências)
Essencial para detectar a "mão invisível" de campanhas coordenadas:
*   **Bigramas/Trigramas:** Capturam frases feitas e bordões políticos.
*   **Isolamento de Sentenças:** A lógica impede que palavras de frases diferentes se misturem, preservando a coerência forense do texto.

## 🧪 2. Protocolo de Normalização Forense

Para evitar ruído nas estatísticas, o motor deve seguir estes passos:
1.  **Remoção de Stopwords Políticas:** Filtrar palavras comuns (artigos, preposições) e termos de plataforma (ex: "link na bio").
2.  **Lemmatização via SpaCy (pt_core_news_lg):** Converter "roubaram", "roubar" e "roubo" para a base semântica para consolidar o volume da narrativa.
3.  **Filtragem de Comprimento:** Descartar tokens menores que 2 caracteres para evitar lixo de OCR ou digitação.

## 📈 3. Integração com o Dashboard

Os dados extraídos por estes scripts devem alimentar a **Matriz de Risco**:
*   **Alta frequência de adjetivos negativos + Bigramas repetitivos** = Gatilho de Ataque Coordenado.
*   **Mudança no Idioleto** = Alerta de mudança brusca de discurso.

---
*Referência Técnica: https://github.com/LeoVichi/linguistica_forense_UFRN*
