# 📜 Diretrizes de Treinamento e Classificação PASA v16.4

Este documento define os critérios para a classificação de discurso de ódio e hostilidade política do sistema Sentinela Democrática.

## 1. Matriz de Hostilidade (Categorias)

- **ODIO_IDENTITARIO**: Ataques baseados em raça, religião, orientação sexual ou misoginia.
- **VIOLENCIA_GENERO**: Ofensas focadas na condição feminina (ex: "vaca", "puta", "louca").
- **AMEACA**: Incitação a dano físico ou morte (ex: "tem que levar tiro", "paredão").
- **INSULTO_AD_HOMINEM**: Desumanização e baixo calão (ex: "verme", "rato", "lixo").
- **ATAQUE_INSTITUCIONAL**: Deslegitimação de órgãos de Estado (ex: "ditadura da toga", "fraude", "comprado").
- **RIGOR_CRIMINAL**: Imputação de crime sem prova ou trânsito em julgado (ex: "ladrão", "traficante", "corrupto").

## 2. Scanner de Ironia e Sarcasmo
A análise deve identificar dissonância semântica:
- *"Grande democrata esse aí"* (em contexto de crítica a decisões judiciais) → **ATAQUE_INSTITUCIONAL**.
- *"Parabéns pelo roubo"* → **RIGOR_CRIMINAL**.

## 3. Dicionário de Alta Hostilidade
- **Ofensas**: lixo, escória, verme, rato, jumento, gado, mortadela.
- **Institucional**: ditadura, golpe, fraude, urnas, Alexandre, Xandão, careca.
- **Ideológico**: comunista, fascista, nazista, extrema-direita, esquerda caviar.

## 4. Fluxo de Decisão (Heurística)
- Se contém termo de **RIGOR_CRIMINAL** → `is_hate: true`.
- Se contém desumanização → `is_hate: true`.
- Se contém ataque direto a órgãos de estado → `is_hate: true`.
- Comentários neutros ou de apoio político (mesmo que enfáticos) → `is_hate: false`.
