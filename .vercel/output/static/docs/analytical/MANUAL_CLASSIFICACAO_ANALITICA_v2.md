# 📊 MANUAL DE CLASSIFICAÇÃO ANALÍTICA (MCA) v2.2
**Sistema:** Sentinela Democrática
**Protocolo Base:** PASA v44 / MSAL / CCF Framework
**Status:** OPERACIONAL E VINCULATIVO

---

## 1. Missão e Princípios
Classificar o discurso político com foco em **direção de risco** e **integridade institucional**. O MCA v2.2 introduz o mapeamento explícito do alvo do ataque para análise de clusters de ódio.

---

## 2. Taxonomia MTAD (v2.2)

| Categoria | Descrição |
| :--- | :--- |
| **ODIO_IDENTITARIO** | Ataques a grupos minoritários ou regiões. |
| **VIOLENCIA_GENERO** | Misoginia e ataques à dignidade da mulher. |
| **AMEACA** | Dano físico ou institucional iminente. |
| **ATAQUE_INSTITUCIONAL** | Deslegitimação da democracia ou órgãos de controle. |
| **RIGOR_CRIMINAL** | Imputação de crimes sem evidência jurídica. |
| **INSULTO_AD_HOMINEM** | Deshumanização direta do alvo. |
| **NEUTRO** | Crítica política legítima, sátira e apoio. |

---

## 3. Mapeamento Explícito de Direção (`direcao_odio`)

Todo comentário classificado como `hate` DEVE ter o campo `direcao_odio` preenchido:

| Categoria | Valores Comuns |
| :--- | :--- |
| **ODIO_IDENTITARIO** | Nordeste, Norte, Negro, LGBTQIA+, Judeu, Muçulmano |
| **VIOLENCIA_GENERO** | Mulheres, Feministas, [Nome da Candidata] |
| **AMEACA** | Alvo Monitorado, Opositores, Supremo, Estado |
| **ATAQUE_INSTITUCIONAL** | STF, TSE, Urnas, Democracia, Forças Armadas |
| **RIGOR_CRIMINAL** | Alvo Monitorado |
| **INSULTO_AD_HOMINEM** | Alvo Monitorado |

---

## 4. Framework CCF (Confidence Calculation)

O cálculo de `confianca_ia` deve seguir a fórmula:
`Confiança = (Densidade Léxica * 0.3) + (Coordenação/Sincronicidade * 0.4) + (Performatividade * 0.3)`

---

## 5. Proteção Jurídica e Acadêmica
As classificações geradas por este sistema são evidências situacionais destinadas à análise de tendências e não constituem juízo de valor jurídico definitivo sem perícia humana complementar.

---

## Changelog
- v2.2 (2026-05-15): Adicionado mapeamento explícito de `direcao_odio` e proteções jurídicas.
- v2.1 (2026-05-15): Renomeação metodológica (MSAL) e citações acadêmicas.
- v2.0 (2026-05-14): Integração do CCF e Blindagem contra Falsos Positivos.
