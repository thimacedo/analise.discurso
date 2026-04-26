---
name: situational-intelligence-sync
description: Protocolo de proteção e sincronização para o núcleo de inteligência Sentinela v15.5. Use para garantir que qualquer modificação no dashboard ou API respeite os filtros periciais PASA e a arquitetura Stealth estável.
---

# Sentinela Situational Intelligence Sync (v15.5 PROTECTED)

Este protocolo é obrigatório para qualquer operação de escrita ou refatoração no ecossistema Sentinela.

## 🔒 1. Núcleos Imutáveis (Core Lock)
NÃO modifique os seguintes arquivos sem validar contra a Baliza de Treinamento (docs/CRITERIOS_TREINAMENTO.md):
- `src/core/ui.js`: Motor de renderização e filtros anti-ruído (blindagem de aplausos).
- `src/core/state.js`: Gerenciador de estado reativo.
- `src/services/apiService.js`: Filtro universal de hostilidade.

## 🧠 2. Protocolo PASA v15.5 (IA Ethics)
Toda interação com LLMs (Llama/Groq) deve seguir o padrão:
- **Blindagem Semântica**: Proibido classificar elogios/aplausos como ódio.
- **Taxonomia Forense**: Use apenas labels oficiais (ÓDIO_IDENTITÁRIO, VIOLÊNCIA_GÊNERO, etc).
- **Rigor Dialetal**: Interprete gírias regionais conforme a cultura de origem.

## 🎨 3. Padrão Estético Stealth
- **Fontes**: Plus Jakarta Sans (Main) e JetBrains Mono (Data).
- **Cores**: Base #020617, Acentos #2563eb e #ef4444.
- **Gráficos**: Devem ser renderizados nativamente via DOM (HTML/CSS), sem bibliotecas de canvas externas.

## 🚀 4. Fluxo de Sincronização
1. Valide a identidade do alvo (remova prefixos raw_ ou extensões .json).
2. Verifique se comentarios_odio_count reflete apenas o ódio real (sem falsos positivos).
3. Sincronize o gráfico de Monitor de Impacto com o Feed de Alertas.
