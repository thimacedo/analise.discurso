---
date: "2026-04-26"
problem_type: "analytical-bottleneck"
severity: "high"
symptoms:
  - "Lentidao na raspagem devido a analise de texto sincrona"
  - "Classificacao imprecisa via TextBlob"
  - "Dificuldade em categorizar tipos de discurso de odio"
root_cause: "synchronous-simple-nlp"
tags:
  - nlp
  - bertimbau
  - batch-processing
  - intelligence
---

# Solucao: Arquitetura de Inteligencia Assincrona em Lote

## Diagnostico
A analise de sentimentos era feita dentro do loop de raspagem, o que aumentava o tempo de execuçao e tornava o sistema dependente de uma unica biblioteca (TextBlob) sem treinamento para discurso politico em portugues.

## Acoes Tomadas
1. Desacoplamento: O raspador agora apenas salva o texto e marca como nao processado.
2. Motor BERTimbau: Implementado o worker `classificador.py` usando `pysentimiento` para detecçao especifica de Hate Speech (Racismo, Sexismo, Ideologia).
3. Processamento em Batch: O worker processa 50 registros por vez para otimizar memoria e velocidade de banco.
4. Schema Forense: Criada a tabela `classificacoes` para manter o histórico de auditoria do modelo de IA.

## Licoes Aprendidas
- Nunca misturar I/O de rede (raspagem) com CPU Bound (IA/NLP).
- Modelos Transformers exigem gerenciamento rigoroso de memoria (Batch Size controlado).
