# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto utiliza coleta massiva via RapidAPI e análise de linguagem (Protocolo PASA) para oferecer transparência sobre o clima político digital através de Dossiês Informativos e uma Matriz de Risco estatística.

## 📌 Status Atual
**Data:** 26 de Abril de 2026
**Fase:** v15.5.0 - Gestão de Alvos Resiliente
**Resumo:** 
- **Fonte da Verdade**: A lista de monitoramento foi desacoplada da conta do Instagram para evitar bloqueios. Agora, os alvos são geridos diretamente no Supabase.
- **Cérebro Linguístico**: Base de parâmetros integrada para detecção de dissonância e ironia em contextos jornalísticos.
- **Detecção de Coordenação**: Motor de N-Gramas ativo para identificar repetição de "frases feitas" e scripts em larga escala.
- **Matriz de Risco**: Visualização Bubble Chart ativa para identificar perfis sob fogo cruzado.

## 🎯 Próximos Passos (Prioridade Máxima)
1. [x] **Gestão de Alvos Segura**: Implementada a gestão via Supabase, removendo a dependência de `following` do perfil mestre.
2. [x] **Inteligência Híbrida**: Automação 24/7 de estados e narrativas.
3. [x] **Identificação de Redes Coordenadas (Ponto 2)**: Refinada a detecção de scripts de repetição linguística e mimetismo de massa.
4. [x] **Dossiês de Inteligência (Ponto 4)**: Implementada a exportação de PDF.
5. [ ] **Extensão UFRN**: Estruturar o laboratório de análise situacional para a turma de Linguística.

## 🛠️ Instruções de Execução e Blindagem Jurídica
- **Gestão de Alvos**: Use o script `scripts/manage_targets.py` para incluir ou remover perfis do monitoramento. O worker `pasa-worker.js` e os coletores agora consultam o banco de dados diretamente.
- **Definição de Termos:** Caso seja necessário explicar algum conceito do ecossistema político-eleitoral, deve-se utilizar obrigatoriamente as definições contidas no [Glossário Eleitoral do TSE](https://www.tse.jus.br/servicos-eleitorais/glossario/glossario-eleitoral).
- **Tom de Voz:** Estritamente jornalístico-informativo.
- **Frequência:** O worker `pasa-worker.js` garante a atualização do "Cérebro" a cada 60s.
