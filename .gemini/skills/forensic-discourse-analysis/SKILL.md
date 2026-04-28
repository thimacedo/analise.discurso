---
name: forensic-discourse-analysis
description: Protocolo PASA v16.4 para analise forense de discurso politico e identificacao de crimes digitais. Use para classificar comentarios com alto rigor criminal e scanner de ironia.
---

# Protocolo PASA v16.4 (Diamond Edition)

## Matriz de Hostilidade (Categorias)

1. ODIO_IDENTITARIO: Raca, religiao, orientacao sexual, misoginia.
2. VIOLENCIA_GENERO: Ataques focados na condicao feminina (ex: "vaca", "puta", "louca").
3. AMEACA: Dano fisico, "tem que levar tiro", "paredao".
4. INSULTO_AD_HOMINEM: Baixo calao e desumanizacao (ex: "verme", "rato", "lixo").
5. ATAQUE_INSTITUCIONAL: Deslegitimacao do STF/TSE (ex: "ditadura da toga", "fraude", "comprado").
6. RIGOR_CRIMINAL: Imputacao de crime sem prova (ex: "ladrao", "traficante", "corrupto", "chefe de quadrilha").

## Scanner de Ironia e Sarcasmo
Identificar dissonancia semantica. 
- "Grande democrata esse ai" (em post sobre censura) -> ATAQUE_INSTITUCIONAL.
- "Parabens pelo roubo" -> RIGOR_CRIMINAL.

## Dicionario de Alta Hostilidade (Para Heuristica)
- Ofensas: lixo, escoria, lixo humano, verme, rato, jumento, gado, mortadela.
- Institucional: ditadura, golpe, fraude, urnas, Alexandre, Xandao, careca.
- Criminal: ladrao, condenado, quadrilha, desvio, propina, meliante.
- Ideologico: comunista, fascista, nazista, extrema-direita, esquerda caviar.

## Fluxo de Decisao
- Se contem termo de RIGOR_CRIMINAL -> is_hate: true.
- Se contem desumanizacao (verme, etc) -> is_hate: true.
- Se contem ataque a orgao de estado -> is_hate: true.
