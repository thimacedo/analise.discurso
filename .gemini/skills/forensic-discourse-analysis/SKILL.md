---
name: forensic-discourse-analysis
description: Protocolo PASA v15.16 para analise forense de discurso politico e identificacao de crimes digitais. Use quando precisar classificar comentarios, identificar ataques coordenados ou auditar evidencias periciais.
---

# Protocolo PASA v15.16 (Pericial Advanced Situational Analysis)

## Categorias de Classificacao Obrigatorias

1. ODIO_IDENTITARIO: Ataques baseados em raca, religiao, orientacao sexual ou origem.
2. VIOLENCIA_GENERO: Hostilidade direcionada especificamente a mulheres ou identidades de genero.
3. AMEACA: Intencao declarada de causar dano fisico ou material.
4. INSULTO_AD_HOMINEM: Ataques a pessoa em vez do argumento (baixo calao ou desumanizacao).
5. ATAQUE_INSTITUCIONAL: Tentativa de deslegitimar instituicoes democraticas (STF, TSE, etc).
6. NEUTRO: Comentarios de apoio, critica construtiva ou irrelevantes.

## Motores de Inteligencia

### 1. Scanner de Ironia (Dissonancia Semantica)
Identificar "elogios cinicos" que escondem ataques. 
Exemplo: "Parabens por destruir o pais com tanta competencia" -> Classificar como INSULTO_AD_HOMINEM ou ATAQUE_INSTITUCIONAL.

### 2. Rigor Criminal (Imputacao Sem Prova)
Ativar alerta critico para uso de termos como "ladrao", "traficante", "assassino" ou "corrupto" sem referencia a condenaçao transitada em julgado.
Regra: Imputacao de crime = is_hate: true.

## Fluxo de Analise
1. Extrair texto bruto e metadados (timestamp, alvo).
2. Aplicar Scanner de Ironia.
3. Verificar Rigor Criminal.
4. Atribuir Categoria PASA.
5. Salvar em classificacao_pasa e is_hate no banco.

## Regras de Evidencia
- Manter o texto original integro (texto_bruto).
- Registrar a versao do modelo (Llama 3.1) e do protocolo (v15.16).
